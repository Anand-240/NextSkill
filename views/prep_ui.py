"""Job Prep section: choose a listing, then revise skills you have and learn the ones you lack."""
from __future__ import annotations

import streamlit as st

from engine import BudgetExceeded, SerpClient, course_videos, hours_text
from i18n import hindi_on, t
from job_prep import (REVISION_LABEL, build_plan, default_prep_index, is_cached, prep_candidates, revision_params,
                      revision_videos, time_range)
from views.common import live_key
from views.render import hindi_block


def _status_text(row: dict) -> str:
    if row["status"] == "match":
        return "Matches now"
    if row["unlock_skills"]:
        return "1 skill away: " + " or ".join(row["unlock_skills"])
    return "1 skill away through a broad skill (" + ", ".join(row["broad_only"]) + ")"


def _time_cell(item: dict, saved: bool) -> str:
    if item["action"] == "revise":
        if item["revision_status"] == "found":
            return " + ".join(video["duration"] for video in item["revision_videos"]) + " revision"
        if item["revision_status"] == "none":
            return "No good short revision video found"
        return "Not in the saved data" if saved else "Revision videos not fetched yet"
    if item["broad"]:
        return "Broad skill, no single course"
    return hours_text(item["hours"]) + " course" if item["hours"] else "Hours unknown"


def prep_section(result: dict, saved: bool, state_key: str, budget: int | None = None) -> None:
    candidates = prep_candidates(result)
    signature = (result["role"], result["city"], tuple(result["user_skills"]), result["threshold"], len(result["jobs"]))
    st.caption("Listings that match your profile now or are one skill away. Choose one for a prep plan built from this search's own data.")
    with st.expander(f"Choose a listing ({len(candidates)})", expanded=False):
        if not candidates:
            st.caption("No listing matches now or is one skill away at this threshold.")
        for row in candidates:
            job = row["job"]
            left, right = st.columns([4, 1])
            left.markdown(f"**{job.get('title') or 'Untitled'}** · {job.get('company_name') or 'Unknown company'} · {_status_text(row)}")
            if right.button("Prepare", key=f"{state_key}_prep_{row['index']}"):
                st.session_state[f"{state_key}_choice"] = (signature, row["index"])
    choice = st.session_state.get(f"{state_key}_choice")
    index = choice[1] if choice and choice[0] == signature else default_prep_index(result)
    if index is None:
        st.info("No listing in this search holds a skill you have and asks for one you lack, so there is nothing to prepare for.")
        return
    client = SerpClient(use_fixtures=saved, cache_only=True)
    plan = build_plan(result, index, lambda skill: course_videos(skill, client),
                      lambda skill: revision_videos(skill, client))
    _render_plan(plan, saved, budget)


def _render_plan(plan: dict, saved: bool, budget: int | None) -> None:
    job = plan["job"]
    link = job.get("source_link") or job.get("share_link")
    title = f"{job.get('title') or 'Untitled'} · {job.get('company_name') or 'Unknown company'}"
    st.subheader(title)
    if link:
        st.markdown(f"[Open the listing]({link})")
    st.markdown("**Readiness for this job**")
    ready, after, musts = st.columns(3)
    ready.markdown(f'<div class="stat">{plan["covered_now"]} of {plan["core_total"]}</div>'
                   f'<div class="stat-l">core skills you cover now ({plan["coverage_now"]:.0%}; a match needs {plan["threshold"]:.0%})</div>',
                   unsafe_allow_html=True)
    after.markdown(f'<div class="stat">{plan["covered_after"]} of {plan["core_total"]}</div>'
                   f'<div class="stat-l">after learning every skill below</div>', unsafe_allow_html=True)
    musts.markdown(f'<div class="stat stat-sm">{plan["must_haves_status"].capitalize()}</div>'
                   f'<div class="stat-l">stated must-haves met ({", ".join(plan["must_haves"]) or "none stated"})</div>',
                   unsafe_allow_html=True)
    if plan["coverage_now"] >= plan["threshold"]:
        st.write("This listing already matches your profile.")
    elif plan["unlock_skills"]:
        st.write(f"Learning {' or '.join(plan['unlock_skills'])} alone would make it a match.")
    for note in plan["title_notes"]:
        st.caption(note)
    if plan["experience_years"]:
        st.write(f"Experience: this listing asks for at least {plan['experience_years']} years (\"{plan['experience_phrase']}\").")
    elif plan["experience_phrase"] != "no minimum detected":
        st.write(f"Experience: no minimum (\"{plan['experience_phrase']}\").")
    else:
        st.write("Experience: no requirement detected in this listing.")
    for alternative in plan["alternatives"]:
        st.write(f"Alternatives: {alternative['text']}")
    short, full = st.columns(2)
    with short.container(border=True):
        route = plan["shortest_route"]
        st.markdown(f"**{t('shortest_route')}**")
        if route["skills"]:
            st.write(", ".join(route["skills"]) + f" · {hours_text(route['hours'])} of courses")
        else:
            st.write(route["status"][0].upper() + route["status"][1:])
        st.caption("Unknown hours may hide a shorter route. Coverage is not eligibility.")
        if route.get("low_confidence"):
            st.caption("Low course confidence for: " + ", ".join(route["low_confidence"]) + ".")
    with full.container(border=True):
        st.markdown(f"**{t('full_plan')}**")
        if plan["revision_minutes"] or plan["learning_hours"]:
            st.write(f"{time_range(plan)}: {hours_text(plan['revision_minutes'] / 60) if plan['revision_minutes'] else 'no'} "
                     f"of revision videos plus {hours_text(plan['learning_hours']) if plan['learning_hours'] else 'no'} of full courses.")
        else:
            st.write("No measured route: this listing has no saved revision videos or course lengths to add up.")
        st.caption(REVISION_LABEL)
    if plan["hours_unknown"] or plan["broad"]:
        st.caption("Not in the time plan: " + ", ".join(
            [f"{skill} (no saved course)" for skill in plan["hours_unknown"]] +
            [f"{skill} (broad skill, no single course)" for skill in plan["broad"]]) + ".")
    st.markdown("**Suggested order**")
    st.caption("Ranked by importance in this listing (mentions, plus 2 if near must, required, strong or mandatory), then by how many eligible listings in this search ask for the skill.")
    st.dataframe([{"Order": f"{item['action'].title()} {item['order']}", "Skill": item["skill"], "Action": item["action"].title(),
                   "In this listing": f"{item['mentions']} mention{'s' if item['mentions'] != 1 else ''}" +
                                      (", marked required or strong" if item["emphasised"] else ""),
                   "Listings asking": f"{item['market']} of {item['market_total']}",
                   "Also unlocks": f"{item['other_unlocks']} other listings" if item["action"] == "learn" else "",
                   "Time": _time_cell(item, saved)} for item in plan["items"]], hide_index=True, width="stretch")
    for action, heading in (("revise", t("revise_heading")), ("learn", t("learn_heading"))):
        rows = [item for item in plan["items"] if item["action"] == action]
        section = st.expander(f"{heading} ({len(rows)})", expanded=action == "learn")
        with section:
            if not rows:
                st.caption("None.")
            for item in rows:
                detail = f"{item['order']}. **{item['skill']}** · asked by {item['market']} of {item['market_total']} eligible listings"
                if action == "learn":
                    detail += f" · would also unlock {item['other_unlocks']} other listings in this search"
                st.markdown(detail)
                if item["evidence"]:
                    st.caption(f"From this listing: \"{item['evidence']}\"")
                for video in (item.get("revision_videos") if action == "revise" else item.get("course_videos")) or []:
                    st.markdown(f"- [{video['title']}]({video['link']}) · {video['channel']} · {video['duration']}")
                if action == "revise" and item["revision_status"] != "found":
                    st.caption(_time_cell(item, saved) + ".")
                if hindi_on() and not item.get("broad"):
                    hindi_block(item["skill"], saved, revision=action == "revise")
    missing = [item["skill"] for item in plan["items"] if item["action"] == "revise"
               and item["revision_status"] == "not_saved" and not is_cached(revision_params(item["skill"]), False)]
    if missing and not saved and live_key():
        allowed = min(len(missing), budget or 1)
        st.caption(f"Fetching revision videos for {', '.join(missing)} needs {len(missing)} new SerpApi searches; "
                   f"the live search budget allows {allowed} now.")
        if st.button(f"Fetch revision videos (up to {allowed} searches)", key="prep_fetch"):
            fetcher = SerpClient(ledger_name="demo_ledger.json", call_cap=None, budget=allowed)
            fetcher.key = live_key()
            try:
                for skill in missing:
                    fetcher.search(revision_params(skill))
            except BudgetExceeded:
                pass  # Keep what was fetched; the rest stays "not fetched yet".
            except RuntimeError as exc:
                st.error(str(exc))
            st.rerun()
    st.caption("A prep plan shows what this listing asks for. It does not promise an interview or a job.")
