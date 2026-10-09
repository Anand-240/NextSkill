"""Result sections shared by the Find, Job Prep and Live pages."""
from __future__ import annotations

import html

import altair as alt
import pandas  # noqa: F401  Altair looks pandas up in sys.modules; import it before any chart.
import streamlit as st

from engine import (DICTIONARY_WARNING, SerpClient, ROLE_FIT_WARNING, headline_picks, hours_parts, hours_text, is_old, no_unlock_message,
                    posted_text)
from hindi import hindi_courses, hindi_revision
from job_prep import prep_candidates
from i18n import hindi_on, t
from views.common import confidence_pill


def snapshot_range(result: dict) -> str:
    dates = result["retrieved_dates"]
    return "unknown" if not dates else dates[0] if len(dates) == 1 else f"{dates[0]} to {dates[-1]}"


def job_line(job: dict, suffix: str = "") -> str:
    link = job.get("source_link") or job.get("share_link") or ""
    label = f"{job.get('title') or 'Untitled'} · {job.get('company_name') or 'Unknown company'}{suffix}"
    return f"- [{label}]({link})" if link else f"- {label}"


def video_lines(videos: list[dict]) -> None:
    for video in videos:
        st.markdown(f"- [{video['title']}]({video['link']}) · {video['channel']} · {video['duration']}")


def hindi_block(skill: str, saved: bool, revision: bool = False) -> None:
    """Hindi videos that pass the relevance filters for one skill, or a note that English videos are shown."""
    client = SerpClient(use_fixtures=saved, cache_only=True)
    videos, status = (hindi_revision if revision else hindi_courses)(skill, client)
    if videos:
        st.markdown(f"**{t('hindi_videos')}**")
        video_lines(videos)
        if not revision:
            st.caption("Hours above are estimated from the English courses listed.")
    else:
        st.caption(t("hindi_not_saved" if status == "not_saved" else "hindi_fallback", skill=skill))


def _missing_names(entry: dict, user: set[str]) -> list[str]:
    return sorted({" / ".join(sorted(req)) for req in entry["required_skills"] if not req & user})


def job_card(entry: dict, user: set[str], threshold: float, highlight: set[str] = frozenset()) -> None:
    """One listing: title, where, how much of it you cover, what is missing, and a link."""
    job = entry["job"]
    link = job.get("source_link") or job.get("share_link") or ""
    where = " · ".join(part for part in (html.escape(str(job.get("company_name") or "Unknown company")),
                                         html.escape(str(job.get("location") or "")),
                                         html.escape(posted_text(job)).replace("unknown", "")) if part)
    covered = round(entry["coverage"] * 100)
    missing = _missing_names(entry, user)
    with st.container(border=True):
        text, action = st.columns([4, 1])
        text.markdown(f'<div class="jobtitle">{html.escape(str(job.get("title") or "Untitled"))}</div><div class="jobmeta">{where}</div>'
                      f'<div class="bar" title="{covered}% of core skills covered"><span style="width:{covered}%"></span></div>'
                      f'<div class="jobmeta">You cover {covered}% of its core skills. A match needs {threshold:.0%}.</div>',
                      unsafe_allow_html=True)
        if missing:
            text.markdown("".join(f'<span class="chip chip-need">needs {html.escape(name)}</span>' for name in missing[:5]),
                          unsafe_allow_html=True)
        if link:
            action.link_button("Open listing", link)
        text.caption("Stated must-haves met: " + entry["must_haves_status"])


def render_jobs(result: dict, headline: dict | None) -> None:
    """Explorer for the jobs behind the answer: matches now, one skill away, or opened by the headline skill."""
    user, threshold = result["user_skills_set"], result["threshold"]
    matches = [entry for entry in result["jobs"] if entry["coverage"] >= threshold]
    near_rows = [row for row in prep_candidates(result) if row["status"] == "one_away"]
    near = [result["jobs"][row["index"]] for row in near_rows]
    opened = []
    if headline:
        by_id = {id(entry["job"]): entry for entry in result["jobs"]}
        opened = [by_id[id(job)] for job in headline["unlocked_jobs"] if id(job) in by_id]
    groups = {"Matches now": matches, "One skill away": near}
    if headline and opened:
        groups[f"Opened by {headline['display_skill']}"] = opened
    st.markdown("### Jobs behind this answer")
    st.caption("Tap a view. Every card links to the original listing.")
    choice = st.segmented_control("View", list(groups), default=list(groups)[0], label_visibility="collapsed",
                                  format_func=lambda name: f"{name} ({len(groups[name])})",
                                  key=f"jobs_view_{result['role']}_{result['city']}") or list(groups)[0]
    shown = groups.get(choice, [])
    if not shown:
        st.info("No listings in this view at the current threshold.")
    for entry in shown[:6]:
        job_card(entry, user, threshold)
    if len(shown) > 6:
        with st.expander(f"Show {len(shown) - 6} more"):
            for entry in shown[6:]:
                job_card(entry, user, threshold)


def elsewhere_count(result: dict) -> int:
    """Scored listings whose location text does not name the searched city (nearby cities, other states, remote)."""
    city = str(result["city"]).lower()
    return sum(bool(str(entry["job"].get("location") or "").strip()) and city not in str(entry["job"].get("location")).lower()
               for entry in result["jobs"])


def render_answer(result: dict, saved: bool) -> None:
    count = len(result["jobs"])
    picks = headline_picks(result["ranked"])
    fastest, headline = picks["fastest"], picks["headline"]
    source = "saved listings" if saved else "listings found now"
    if headline:
        gained = headline["unlocked_count"]
        listing_word = "listing" if gained == 1 else "listings"
        if fastest:
            number, unit = hours_parts(headline["hours"])
            st.subheader(t("headline", skill=headline["display_skill"], gained=gained, hours=number,
                           listing_word=listing_word, hour_word=unit))
        else:
            st.subheader(t("headline_no_hours", skill=headline["display_skill"], gained=gained, listing_word=listing_word))
    st.markdown(f"**{t('matches_line', ready=result['ready'], count=count, source=source, city=result['city'])}**")
    elsewhere = elsewhere_count(result)
    if elsewhere:
        st.caption(f"{elsewhere} of these {count} listings name another place in their location (nearby cities, other states or "
                   f"remote); Google Jobs returns them for {result['city']} searches.")
    robustness = result["robustness"]
    st.markdown(f"Pick stability: {confidence_pill(robustness['label'])} (based on {robustness['listings']} scored listings) "
                f"· Snapshot date: {snapshot_range(result)} (UTC)", unsafe_allow_html=True)
    if robustness.get("cap_note"):
        st.caption(robustness["cap_note"])
    st.caption(f"Among these matches: stated must-haves met in {result.get('must_haves_met', 0)}; "
               f"none stated in {result.get('must_haves_none', 0)}. Other matches still lack an explicit requirement. "
               "A match means your profile covers enough of a listing's core skills; it is not a hiring prediction.")
    if result["limited_data"]:
        st.warning("Limited data: fewer than 12 distinct listings were found. Treat the ranking as exploratory.")
    if result["role_fit_warning"]:
        st.warning(ROLE_FIT_WARNING)
    if result["dictionary_warning"]:
        st.warning(DICTIONARY_WARNING)
    if result.get("budget_reached"):
        st.info(f"Live search budget reached after {result['live_requests']} new searches. Results use the listings and "
                "course data fetched so far; skills without course data show hours unknown. Raise the budget to fetch more.")
    if result.get("request_failed"):
        st.warning("A live search failed (for example a timeout) and was not retried, so these results use what was fetched. "
                   "Skills without course data show hours unknown. Run again to fetch the rest.")
    if not result["ranked"]:
        st.info(no_unlock_message(result))

    def summary(row):
        return (f"+{row['unlocked_count']} matches · {hours_text(row['hours'])}" +
                (f" · {row['score']:.2f} matches per course hour" if row["score"] is not None else ""))

    if picks["same"]:
        with st.container(border=True):
            st.markdown(f"**Fastest win and biggest unlock: {fastest['display_skill']}**")
            st.caption(summary(fastest))
    elif picks["biggest"]:
        columns = st.columns(2)
        for column, key, name, note in ((columns[0], "fastest", t("fastest_win"), "Most new matches per course hour"),
                                        (columns[1], "biggest", t("biggest_unlock"), "Most new matches, regardless of hours")):
            row = picks[key]
            with column.container(border=True):
                st.markdown(f"**{name}: {row['display_skill']}**" if row else f"**{name}: none qualifies**")
                if row:
                    st.caption(f"{note}. " + summary(row))
                else:
                    st.caption("No skill has course lengths from at least two full courses, so none can lead on hours.")
    render_jobs(result, headline)
    lowest = [row for row in result["ranked"] if row["confidence"] == "low" and row["hours"] is not None]
    if lowest:
        st.caption("Low course confidence (fewer than two full courses, so these hours come from other videos and are "
                   "not used for the fastest win): " + ", ".join(row["display_skill"] for row in lowest[:4]) +
                   (" and more." if len(lowest) > 4 else "."))
    if picks["biggest"]:
        st.caption("A short course can win per hour even if it opens fewer matches. Compare both before choosing.")


def render_sample(result: dict) -> None:
    excluded, count = result["experience_excluded"], len(result["jobs"])
    with st.expander("About this sample"):
        st.caption(f"{result['eligible_count']} eligible listings remain after experience and date filters; {count} have detected core requirements and are scored; {result['ignored']} have no detected core requirements.")
        st.caption(f"Based on {result['eligible_count']} listings · {result['listing_confidence']} confidence in sample size. {result['raw'] - result['deduplicated']} likely duplicates removed. Core skills appear in at least {result['core_share']:.0%} of eligible listings.")
        st.caption(f"{len(excluded)} listings set aside because they need more experience than the selected level.")
        st.caption("The experience level changes the sample: Fresher searches also run fresher and junior versions of the role, and each level keeps listings whose stated minimum is at most 0, 1 or 3 years.")
        for row in excluded:
            st.markdown(job_line(row["job"], f" · {row['reason']}"))


def render_evidence(result: dict, extra=None) -> None:
    """Skill cards with listings, must-have status and the free courses behind each hour estimate."""
    count = len(result["jobs"])
    if not result["ranked"]:
        st.info(no_unlock_message(result))
    confident = result["robustness"]["label"] in {"Strong", "Likely"}
    headline = headline_picks(result["ranked"])["headline"]
    for item in result["ranked"]:
        with st.container(border=True):
            name = item.get("display_skill", item["skill"])
            medal = bool(headline) and item["skill"] == headline["skill"] and confident and not result["limited_data"]
            st.markdown(f"#### {'🥇 ' if medal else ''}{name}")
            a, b, c = st.columns(3)
            a.metric("More matches", f"+{item['unlocked_count']}")
            b.metric("Course length", hours_text(item["hours"]))
            c.metric("Matches per course hour", f"{item['score']:.2f}" if item["score"] is not None else "Unavailable")
            if item["confidence"] in {"budget", "failed"}:
                st.caption("Hours unknown (" + ("live budget reached" if item["confidence"] == "budget" else "the course search failed") + ").")
            if item["confidence"] == "low" and item["hours"] is not None:
                st.caption("Low course confidence: fewer than two qualifying full courses, so this skill cannot be the fastest win. "
                           "The estimate uses relevant videos of at least 30 minutes.")
            if item["videos"]:
                st.markdown("**Free YouTube courses behind this hour estimate**")
                video_lines(item["videos"])
            if extra:
                extra(item)
            st.write(f"{name} is requested in {item['appears_in']} of {count} scored listings.")
            with st.expander(f"{item['unlocked_count']} listings this skill would add as matches"):
                for job in item["unlocked_jobs"]:
                    st.markdown(job_line(job, f" · {posted_text(job)}{' · older than 30 days' if is_old(job) else ''}"))
                    entry = next((row for row in result["jobs"] if row["job"] is job), None)
                    if entry:
                        st.caption("Stated must-haves met: " + entry["must_haves_status"])
                        if entry["nice_to_have"]:
                            st.caption("Nice to have: " + ", ".join(sorted(entry["nice_to_have"])))


def render_plan(result: dict) -> None:
    pair = result.get("two_skill_plan")
    if pair:
        with st.container(border=True):
            names = pair.get("display_skills", pair["skills"])
            st.markdown(f"### Two-skill plan: {names[0]} + {names[1]}")
            st.write(f"Together these could add {pair['unlocked_count']} matches. Combined course length: " +
                     (f"{hours_text(pair['hours'])}; matches per hour: {pair['score']:.2f}." if pair["hours"] is not None
                      else "unavailable from current video data."))
            if pair["hours"] is not None:
                for skill, videos in pair["source_videos"].items():
                    st.markdown(f"**{skill} course sources**")
                    video_lines(videos)
    st.markdown("### Opportunity curve")
    opportunity, steps = result["opportunity"], result["opportunity"]["steps"]
    names = {row["skill"]: row["display_skill"] for row in result["ranked"]}
    points = [{"hours": 0.0, "matches": result["ready"], "label": "Current profile"}]
    points.extend({"hours": step["cumulative_hours"], "matches": step["total_jobs"],
                   "label": names.get(step["skill"], step["skill"])} for step in steps)
    data = alt.Data(values=points)
    line = alt.Chart(data).mark_line(point=True).encode(
        x=alt.X("hours:Q", title="Cumulative learning hours"),
        y=alt.Y("matches:Q", title="Listings matching the threshold", scale=alt.Scale(zero=True)),
        tooltip=["label:N", "hours:Q", "matches:Q"])
    text = alt.Chart(data).mark_text(dy=-14).encode(x="hours:Q", y="matches:Q", text="label:N")
    st.altair_chart(line + text, width="stretch")
    st.caption("Each point shows how many listings would match after learning the named skill; course length is only a study-time estimate.")
    if steps:
        st.dataframe([{"Step": step["step"], "Skill": names.get(step["skill"], step["skill"]),
                       "Course length": hours_text(step["hours"]), "Matches gained": step["jobs_gained"],
                       "Total matches": step["total_jobs"]} for step in steps], width="stretch", hide_index=True)
    else:
        st.info("No measured skill adds a reachable match at this threshold.")
    if opportunity["hours_unknown"]:
        st.caption("Hours unknown: " + ", ".join(opportunity["hours_unknown"]) +
                   ". These skills are left out of the hours-based plan.")


def render_checks(result: dict) -> None:
    robustness, bootstrap = result["robustness"], result["bootstrap"]
    st.markdown("### How we checked this")
    if bootstrap["top_skill"]:
        top = next((row["display_skill"] for row in result["ranked"] if row["skill"] == bootstrap["top_skill"]),
                   bootstrap["top_skill"])
        others = [(skill, share) for skill, share in bootstrap["shares"].items()
                  if skill not in {bootstrap["top_skill"], "No scored pick"}]
        runner = max(others, key=lambda row: row[1]) if others else None
        st.write(f"**Resampling:** {top} is the top pick in {bootstrap['top_share']:.1%} of {bootstrap['samples']} "
                 "resamples of the listings" + (f" ({runner[0]} {runner[1]:.1%})." if runner else "."))
    st.write(f"**Hour variation:** the top pick stays first in {robustness['top_share']:.1%} of {robustness['samples']} "
             "checks where each skill's hours vary from 0.75x to 1.5x, at thresholds 0.4, 0.5 and 0.6 plus yours.")
    for change in robustness["changes"]:
        st.write(f"- {change}")
    st.write(f"**Pick stability: {robustness['label']}** (based on {robustness['listings']} scored listings). The label uses the "
             "lower of the two shares. Strong needs both at least 85%, at least 15 scored listings and a pick with standard course "
             "confidence; Likely needs both at least 60%; otherwise Uncertain. Limited-data markets are never above Uncertain. "
             "These checks measure sensitivity, not recommendation accuracy or hiring chances.")
    if robustness.get("cap_note"):
        st.caption(robustness["cap_note"])
    with st.expander("Greedy plan vs exact among measured skills"):
        st.dataframe([{"Budget": f"{row['budget']} hours", "Greedy matches gained": row["greedy_gained"],
                       "Exact best matches gained": row["optimal_gained"],
                       "Greedy / exact": f"{row['ratio']:.0%}" if row["ratio"] is not None else "No feasible gain"}
                      for row in result["opportunity"]["quality"]], width="stretch", hide_index=True)
        st.caption("The exact check among measured skills tries every combination of up to eight measurable missing skills; the greedy plan picks the best next matches-per-hour step.")
    st.markdown("#### Skill distance")
    distance = result["distance"]
    names = {"0": "0 · matches", "1": "1 skill", "2": "2 skills", "3+": "3+ skills", "Unknown": "Unknown"}
    bars = [{"distance": names[key], "listings": distance["counts"][key]} for key in names]
    chart = alt.Chart(alt.Data(values=bars)).mark_bar().encode(
        x=alt.X("distance:N", title="Skills needed to reach threshold", sort=[row["distance"] for row in bars]),
        y=alt.Y("listings:Q", title="Eligible listings", scale=alt.Scale(zero=True)),
        tooltip=["distance:N", "listings:Q"])
    st.altair_chart(chart, width="stretch")
    st.caption("This counts the fewest added core skills needed to reach your selected threshold. Unknown means no core requirement was detected.")
    st.markdown("**Listings one skill away**")
    if not distance["one_away"]:
        st.caption("None at this threshold.")
    for skill, jobs in sorted(distance["one_away"].items()):
        with st.expander(f"{skill} · {len(jobs)} listings"):
            for job in jobs:
                st.markdown(job_line(job))
    with st.expander("How the numbers are calculated"):
        st.write("We set aside listings that ask for more experience than the minimum of your selected band: 0, 1 or 3 years. Explicit description requirements override title-based estimates. We ignore negated skill mentions. Skills are alternatives only where the listing explicitly offers an 'or' or slash choice. Skills found in at least the selected share of eligible listings are core. A profile matches a listing when it meets the selected fraction of core requirements. Broad umbrella terms can count for matching but are never recommended.")
        st.write("Course hours are the median length of up to three free videos whose titles name the skill. Talks, webinars and videos about a different product are dropped. With fewer than two course-like videos of at least an hour, we fall back to relevant videos of at least 30 minutes and mark low course confidence; such a skill stays in the ranking but cannot be the fastest win. Hours are shown rounded, for example 'about 4 hours'. These estimates do not establish competence or promise a job.")


def render_replay(result: dict) -> None:
    labels = {"demo": "Bundled demo data", "fixture": "Demo cache (validation fixture)", "cache": "Local cache",
              "live": "Live SerpApi request", "cache missing": "No cached response",
              "budget reached": "Skipped (live budget reached)", "failed": "Failed (not retried)"}
    with st.expander("Search replay"):
        for event in result["replay"]:
            query = event["query"].get("q") or event["query"].get("search_query")
            location = event["query"].get("location")
            variant, listings = event.get("variant"), event.get("listing_count")
            st.write(f"{labels.get(event['source'], event['source'])}: {event['query']['engine']} · {query}" +
                     (f" · {location}" if location else "") + (f" · {variant}" if variant else "") +
                     (f" · {listings} listings" if listings is not None else ""))
        st.markdown("**Listing origins**")
        st.dataframe([{"Title": job.get("title") or "Untitled", "Company": job.get("company_name") or "Unknown",
                       "Search variant(s)": ", ".join(job.get("_search_queries") or [])}
                      for job in result["all_listings"]], width="stretch", hide_index=True)


def render_full(result: dict, saved: bool) -> None:
    answer, evidence, plan, checks = st.tabs([t("tab_answer"), t("tab_evidence"), t("tab_plan"), t("tab_checks")])
    with answer:
        render_answer(result, saved)
        render_sample(result)
    with evidence:
        render_evidence(result, (lambda item: hindi_block(item['skill'], saved)) if hindi_on() else None)
    with plan:
        render_plan(result)
    with checks:
        render_checks(result)
    render_replay(result)
