"""Run with: streamlit run nextskill/app.py"""
import altair as alt
import streamlit as st
import hashlib
from resume_pdf import extract_pdf_text

from engine import (DEFAULT_THRESHOLD, DICTIONARY_WARNING, ROLE_FIT_WARNING, ROOT, BudgetExceeded, SerpClient,
                    max_live_requests,
                    headline_picks, hours_range, is_old, no_unlock_message, optional_serpapi_key,
                    posted_text, run, course_videos)
from job_prep import (REVISION_LABEL, build_plan, default_prep_index, is_cached, prep_candidates,
                      revision_params, revision_videos, time_range)

def demo_data_version() -> tuple:
    """Changes whenever a bundled response is added, removed or rewritten."""
    return tuple(sorted((path.name, path.stat().st_size, path.stat().st_mtime_ns)
                        for path in (ROOT / "demo_data").rglob("*.json")))


@st.cache_data(show_spinner=False, max_entries=64)
def cached_demo_run(role, city, resume_input, manual, threshold, include_hindi, exclude_old, pages,
                    core_share, experience_level, data_version):
    """Saved-data analysis is deterministic, so identical inputs reuse the full result."""
    client = SerpClient(use_fixtures=True, cache_only=True, ledger_name="demo_ledger.json", call_cap=6)
    return run(role, city, resume_input, manual, threshold, include_hindi, exclude_old, pages, False,
               client, core_share, experience_level=experience_level)


st.set_page_config(page_title="NextSkill", page_icon="🎯", layout="wide")
st.markdown("""<style>
.block-container {max-width: 1120px; padding-top: 2rem}
.hero {background:#122b3a;color:#fff;padding:2rem;border-radius:18px;margin-bottom:1.4rem}
.hero h1 {font-size:2.5rem;margin:0 0 .3rem}
.hero p {font-size:1.05rem;color:#dbe8ed;margin:0}
.metric {font-size:2.1rem;font-weight:750;color:#123c41}
</style>""", unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>NextSkill</h1><p>Learn the one skill that unlocks the most real jobs, in the least time.</p></div>', unsafe_allow_html=True)

try:
    cloud_key = st.secrets.get("SERPAPI_KEY")
except Exception:
    cloud_key = None
if cloud_key == "your_key_here":
    cloud_key = None
live_available = bool(optional_serpapi_key() or cloud_key)


def key_id() -> str:
    """Cache key for the credit balance that never contains the key itself."""
    key = cloud_key or optional_serpapi_key() or ""
    return hashlib.sha256(key.encode()).hexdigest()[:12]


@st.cache_data(ttl=300, show_spinner=False)
def live_credit_balance(key_hash: str) -> int | None:
    """Current SerpApi balance from the Account API (account lookups do not use search credits)."""
    client = SerpClient()
    client.key = cloud_key or optional_serpapi_key()
    try:
        return client.account("sidebar").get("total_searches_left")
    except RuntimeError:
        return None
if not live_available:
    st.session_state.live_mode = False
    st.session_state.demo_mode = True

with st.sidebar:
    st.header("Your search")
    if not live_available:
        st.info("Live search needs a SerpApi key. Demo data is shown.")
    def _demo_on():
        if st.session_state.demo_mode:
            st.session_state.live_mode = False

    def _live_on():
        if st.session_state.live_mode:
            st.session_state.demo_mode = False

    demo = st.toggle("Demo data", value=True, key="demo_mode", on_change=_demo_on,
                     help="Replays the saved Noida and Bengaluru job responses with no SerpApi calls.")
    live = st.toggle("Live search", value=False, key="live_mode", on_change=_live_on,
                     disabled=not live_available,
                     help="Uses SerpApi for a new role and city when you press the search button.")
    if not demo and not live:
        st.info("Choose Demo data or Live search.")
    if demo:
        preset = st.selectbox("Demo role", ["Frontend Developer, Bengaluru", "Data Analyst, Noida"])
        role, city = ("Data Analyst", "Noida") if preset.startswith("Data Analyst") else ("Frontend Developer", "Bengaluru")
    else:
        role = st.text_input("Role", "Data Analyst")
        city = st.text_input("City", "Noida")
    default_resume = "HTML, CSS, JavaScript" if demo and role == "Frontend Developer" else "Excel, basic Python"
    resume = st.text_area("Paste resume text", default_resume, height=140,
                          key=f"resume_{role.lower().replace(' ', '_')}")
    pdf = st.file_uploader("Or upload a PDF resume", type=["pdf"])
    manual = st.text_area("Or list skills (comma separated)", "", height=80)
    experience_level = st.selectbox("Experience level", ["Fresher", "1-3 years", "3+ years"],
                                   help="Uses the minimum of each band: 0, 1 or 3 years. Explicit listing requirements take precedence over titles.")
    threshold = st.slider("Match threshold", 0.2, 1.0, DEFAULT_THRESHOLD, 0.05,
                          help="A listing matches when your profile covers at least this share of its core skills.")
    core_share = st.slider("Core skill frequency", 0.1, 0.5, 0.25, 0.05, help="A skill is core if it appears in at least this share of eligible listings.")
    include_hindi = st.toggle("Include Hindi videos", False)
    exclude_old = st.toggle("Exclude jobs older than 30 days", False)
    pages = st.selectbox("Job pages", [1, 2, 3], index=2 if demo else 0)
    budget = None
    if live:
        budget = int(st.number_input("Live search budget", min_value=1, max_value=30, value=6, step=1,
                                     help="Maximum new SerpApi searches for one run. Saved responses are reused at no cost."))
        estimate = min(budget, max_live_requests(role, pages, experience_level, include_hindi))
        st.caption(f"This search may use up to {estimate} credit{'s' if estimate != 1 else ''}. Saved responses are reused at no cost.")
        remaining = live_credit_balance(key_id())
        st.caption(f"SerpApi credits remaining (Account API): {remaining}." if remaining is not None
                   else "SerpApi credit balance unavailable.")
    go = st.button("Find my next skill", type="primary", use_container_width=True, disabled=not (demo or live))

auto_demo = demo and not st.session_state.get("demo_initial_search_done", False)
if go or auto_demo:
    if auto_demo:
        st.session_state["demo_initial_search_done"] = True
    try:
        pdf_text = extract_pdf_text(pdf.getvalue()) if pdf else ""
        if pdf and not pdf_text:
            st.warning("No selectable text was found in this PDF. If it is scanned, please paste your resume text instead.")
            if resume.strip() == default_resume.strip():
                st.stop()
        resume_input = "\n".join(part for part in (resume if resume.strip() != default_resume.strip() else "", pdf_text) if part) if pdf else resume
        with st.spinner("Checking job requirements and course lengths…"):
            client = SerpClient(use_fixtures=demo, cache_only=demo, ledger_name="demo_ledger.json", call_cap=None,
                                budget=budget if live else None)
            if live:
                client.key = cloud_key or optional_serpapi_key()
                before = client.account("demo_before")
                try:
                    result = run(role, city, resume_input, manual, threshold, include_hindi,
                                 exclude_old, pages, False, client, core_share, learning_limit=3,
                                 experience_level=experience_level)
                finally:
                    after = client.account("demo_after")
                    live_credit_balance.clear()
                st.session_state["credit_update"] = {"before": before, "after": after}
            else:
                result = cached_demo_run(role, city, resume_input, manual, threshold, include_hindi,
                                         exclude_old, pages, core_share, experience_level, demo_data_version())
                st.session_state["credit_update"] = None
        st.session_state["result"] = result
        st.session_state["replay_mode"] = demo
    except Exception as exc:
        # Engine exceptions are designed not to include the SerpApi key.
        st.error(str(exc))

result = st.session_state.get("result")
if result:
    count = len(result["jobs"])
    source_label = "saved listings" if st.session_state.get("replay_mode") else "listings found now"
    picks = headline_picks(result["ranked"])
    fastest = picks["fastest"]
    if fastest:
        gained, course_hours = fastest["unlocked_count"], max(1, round(fastest["hours"]))
        st.subheader(f"Learn {fastest['display_skill']} next: +{gained} more matching listing{'s' if gained != 1 else ''}, "
                     f"about {course_hours} hour{'s' if course_hours != 1 else ''} of free courses.")
    st.markdown(f"**Your profile matches {result['ready']} of {count} {source_label} in {result['city']}.**")
    dates = result["retrieved_dates"]
    snapshot_date = dates[0] if len(dates) == 1 else f"{dates[0]} to {dates[-1]}" if dates else "unknown"
    st.caption(f"Snapshot date: {snapshot_date} (UTC). A match means your profile covers enough of a listing's core skills; it is not a hiring prediction.")
    if result["limited_data"]:
        st.warning("Limited data: fewer than 12 distinct jobs were found. Treat the ranking as exploratory.")
    if result["role_fit_warning"]:
        st.warning(ROLE_FIT_WARNING)
    if result["dictionary_warning"]:
        st.warning(DICTIONARY_WARNING)
    if result.get("budget_reached"):
        st.info(f"Live search budget reached after {result['live_requests']} new searches. Results use the listings and "
                "course data fetched so far; skills without course data show hours unknown. Raise the budget to fetch more.")
    credit_update = st.session_state.get("credit_update")
    if credit_update:
        st.info(f"SerpApi credits used in this live run: {credit_update['after']['this_month_usage'] - credit_update['before']['this_month_usage']}. Remaining: {credit_update['after']['total_searches_left']}.")
    excluded = result["experience_excluded"]
    with st.expander("About this sample"):
        st.caption(f"{result['eligible_count']} eligible listings remain after experience and date filters; {count} have detected core requirements and are scored; {result['ignored']} have no detected core requirements.")
        st.caption(f"Based on {result['eligible_count']} listings · {result['listing_confidence']} confidence in sample size. {result['raw'] - result['deduplicated']} likely duplicates removed. Core skills appear in at least {result['core_share']:.0%} of eligible listings.")
        st.caption(f"{len(excluded)} jobs set aside because they need more experience than the selected level.")
        st.caption("The experience level changes the sample: Fresher searches also run fresher and junior versions of the role, and each level keeps listings whose stated minimum is at most 0, 1 or 3 years.")
        if excluded:
            st.markdown(f"**Needs more experience ({len(excluded)})**")
            for row in excluded:
                job = row["job"]
                link = job.get("source_link") or job.get("share_link")
                label = f"{job.get('title') or 'Untitled'} · {job.get('company_name') or 'Unknown company'} · {row['reason']}"
                st.markdown(f"- [{label}]({link})" if link else f"- {label}")
    st.markdown("### Skills that could open more jobs")
    robustness = result["robustness"]
    bootstrap = result["bootstrap"]
    if bootstrap["top_skill"]:
        top_label = result["ranked"][0].get("display_skill", bootstrap["top_skill"])
        others = [(skill, share) for skill, share in bootstrap["shares"].items()
                  if skill != bootstrap["top_skill"] and skill != "No scored pick"]
        runner = max(others, key=lambda row: row[1]) if others else None
        st.caption(f"{top_label} is the top pick in {bootstrap['top_share']:.1%} of {bootstrap['samples']} resamples" +
                   (f" ({runner[0]} {runner[1]:.1%})." if runner else "."))
    with st.expander(f"Recommendation confidence: {robustness['label']}"):
        st.write("The label uses the lower of two shares: how often the top pick wins in 500 listing resamples, and how often it stays first when each skill's hours vary independently across thresholds. Strong means both shares are at least 85%; Likely means both are at least 60%; otherwise Uncertain. These checks measure sensitivity, not recommendation accuracy or hiring chances.")
        st.write(f"Independent hour variation retains the top pick in {robustness['top_share']:.1%} of {robustness['samples']} checks. Each skill's hours vary from 0.75x to 1.5x in 500 seeded draws, tested at thresholds 0.4, 0.5 and 0.6, plus your selected threshold if different.")
        if robustness["changes"]:
            for change in robustness["changes"]:
                st.write(f"- {change}")
        else:
            st.write("The top scored skill stays first in every checked setting.")
    if not result["ranked"]:
        st.info(no_unlock_message(result))

    def pick_summary(row):
        return (f"+{row['unlocked_count']} matches · {hours_range(row['hours'])}" +
                (f" · {row['score']:.2f} matches per course hour" if row["score"] is not None else ""))

    if picks["same"]:
        with st.container(border=True):
            st.markdown(f"**Fastest win and biggest unlock: {picks['fastest']['display_skill']}**")
            st.caption(pick_summary(picks["fastest"]))
    elif picks["biggest"]:
        columns = st.columns(2)
        for column, key, label, note in ((columns[0], "fastest", "Fastest win", "Most new matches per course hour"),
                                         (columns[1], "biggest", "Biggest unlock", "Most new matches, regardless of hours")):
            row = picks[key]
            with column.container(border=True):
                st.markdown(f"**{label}: {row['display_skill']}**" if row else f"**{label}: unavailable**")
                st.caption(f"{note}. " + (pick_summary(row) if row else "No course hours were found."))
    if picks["biggest"]:
        st.caption("A short course can win per hour even if it opens fewer jobs. Compare both before choosing.")
    for index, item in enumerate(result["ranked"]):
        with st.container(border=True):
            display_skill = item.get("display_skill", item["skill"])
            confident = result["robustness"]["label"] in {"Strong", "Likely"}
            title = f"🥇 {display_skill}" if index == 0 and confident and item["score"] is not None and not result["limited_data"] else display_skill
            st.markdown(f"#### {title}")
            a, b, c = st.columns(3)
            a.metric("More matches", f"+{item['unlocked_count']}")
            b.metric("Estimated learning hours", hours_range(item["hours"]))
            c.metric("Matches per course hour", f"{item['score']:.2f}" if item["score"] is not None else "Unavailable")
            if item["confidence"] == "budget":
                st.caption("Hours unknown (live budget reached).")
            if item["confidence"] == "low" and item["hours"] is not None:
                st.caption("Low confidence: fewer than two qualifying full courses; estimate uses videos of at least 30 minutes.")
            if item["videos"]:
                st.markdown("**Videos behind this hour estimate**")
                for video in item["videos"]:
                    st.markdown(f"- [{video['title']}]({video['link']}) — {video['channel']} · {video['duration']}")
            st.write(f"{display_skill} is requested in {item['appears_in']} of {count} scored listings.")
            with st.expander(f"{item['unlocked_count']} listings this skill would add as matches"):
                for job in item["unlocked_jobs"]:
                    link = job.get("source_link") or job.get("share_link") or ""
                    age_label = " · older than 30 days" if is_old(job) else ""
                    label = f"{job.get('title') or 'Untitled'} — {job.get('company_name') or 'Unknown company'} · {posted_text(job)}{age_label}"
                    if link:
                        st.markdown(f"- [{label}]({link})")
                    else:
                        st.markdown(f"- {label}")
                    nice = result["jobs"]
                    entry = next((row for row in nice if row["job"] is job), None)
                    if entry and entry["nice_to_have"]:
                        st.caption("Nice to have: " + ", ".join(sorted(entry["nice_to_have"])))
    pair = result.get("two_skill_plan")
    if pair:
        with st.container(border=True):
            pair_names = pair.get("display_skills", pair["skills"])
            st.markdown(f"### Two-skill plan: {pair_names[0]} + {pair_names[1]}")
            st.write(f"Together these could unlock {pair['unlocked_count']} jobs. Combined learning hours: " +
                     (f"{hours_range(pair['hours'])}; jobs per hour: {pair['score']:.2f}." if pair["hours"] is not None else "unavailable from current video data."))
            if pair["hours"] is not None:
                for skill, videos in pair["source_videos"].items():
                    st.markdown(f"**{skill} course sources**")
                    for video in videos:
                        st.markdown(f"- [{video['title']}]({video['link']}) — {video['channel']} · {video['duration']}")
    st.markdown("### Opportunity curve")
    opportunity = result["opportunity"]
    steps = opportunity["steps"]
    display_names = {row["skill"]: row["display_skill"] for row in result["ranked"]}
    points = [{"hours": 0.0, "jobs": result["ready"], "label": "Current profile"}]
    points.extend({"hours": step["cumulative_hours"], "jobs": step["total_jobs"],
                   "label": display_names.get(step["skill"], step["skill"])} for step in steps)
    curve_data = alt.Data(values=points)
    line = alt.Chart(curve_data).mark_line(point=True).encode(
        x=alt.X("hours:Q", title="Cumulative learning hours"),
        y=alt.Y("jobs:Q", title="Listings matching the threshold", scale=alt.Scale(zero=True)),
        tooltip=["label:N", "hours:Q", "jobs:Q"])
    labels = alt.Chart(curve_data).mark_text(dy=-14).encode(
        x="hours:Q", y="jobs:Q", text="label:N")
    st.altair_chart(line + labels, width="stretch")
    st.caption("Each point shows how many listings would match after learning the named skill; course length is only a study-time estimate.")
    if steps:
        st.dataframe([{"Step": step["step"], "Skill": display_names.get(step["skill"], step["skill"]),
                       "Hours range": hours_range(step["hours"]),
                       "Jobs gained": step["jobs_gained"], "Total jobs": step["total_jobs"]}
                      for step in steps], width="stretch", hide_index=True)
    else:
        st.info("No measured skill adds a reachable job at this threshold.")
    if opportunity["hours_unknown"]:
        st.caption("Hours unknown" + (" (live budget reached)" if result.get("budget_reached") else "") + ": " +
                   ", ".join(opportunity["hours_unknown"]) + ". These skills are left out of the hours-based plan.")
    with st.expander("Greedy plan vs exact budgets"):
        st.dataframe([{"Budget": f"{row['budget']} hours", "Greedy jobs gained": row["greedy_gained"],
                       "Exact best jobs gained": row["optimal_gained"],
                       "Greedy / optimal": f"{row['ratio']:.0%}" if row["ratio"] is not None else "No feasible gain"}
                      for row in opportunity["quality"]], width="stretch", hide_index=True)
        st.caption("The exact check tries every combination of up to eight measurable missing skills; the greedy plan picks the best next jobs-per-hour step.")
    st.markdown("### Skill distance")
    distance = result["distance"]
    distance_labels = {"0": "0 · matches", "1": "1 skill", "2": "2 skills", "3+": "3+ skills", "Unknown": "Unknown"}
    bars = [{"distance": distance_labels[key], "jobs": distance["counts"][key]}
            for key in ("0", "1", "2", "3+", "Unknown")]
    chart = alt.Chart(alt.Data(values=bars)).mark_bar().encode(
        x=alt.X("distance:N", title="Skills needed to reach threshold", sort=[row["distance"] for row in bars]),
        y=alt.Y("jobs:Q", title="Eligible jobs", scale=alt.Scale(zero=True)),
        tooltip=["distance:N", "jobs:Q"])
    st.altair_chart(chart, width="stretch")
    st.caption("This counts the fewest added core skills needed to reach your selected threshold. Unknown means no core requirement was detected.")
    st.markdown("**Jobs one skill away**")
    if not distance["one_away"]:
        st.caption("None at this threshold.")
    for skill, jobs in sorted(distance["one_away"].items()):
        with st.expander(f"{skill} · {len(jobs)} jobs"):
            for job in jobs:
                link = job.get("source_link") or job.get("share_link")
                label = f"{job.get('title') or 'Untitled'} — {job.get('company_name') or 'Unknown company'}"
                st.markdown(f"- [{label}]({link})" if link else f"- {label}")
    st.markdown("### Prepare for a specific job")
    candidates = prep_candidates(result)
    replay_mode = bool(st.session_state.get("replay_mode"))
    st.caption("Listings that match your profile now or are one skill away. Choose one for a prep plan built from this search's own data.")
    with st.expander(f"Choose a listing ({len(candidates)})"):
        if not candidates:
            st.caption("No listing matches now or is one skill away at this threshold.")
        for row in candidates:
            job = row["job"]
            status = "Matches now" if row["status"] == "match" else "1 skill away: " + " or ".join(row["unlock_skills"])
            left, right = st.columns([4, 1])
            left.markdown(f"**{job.get('title') or 'Untitled'}** · {job.get('company_name') or 'Unknown company'} · {status}")
            if right.button("Prepare for this job", key=f"prep_{row['index']}"):
                st.session_state["prep_choice"] = (id(result), row["index"])
    choice = st.session_state.get("prep_choice")
    prep_index = choice[1] if choice and choice[0] == id(result) else (default_prep_index(result) if replay_mode else None)
    if prep_index is not None:
        prep_client = SerpClient(use_fixtures=replay_mode, cache_only=True)
        languages = {"english", "hindi"} if include_hindi else {"english"}
        plan = build_plan(result, prep_index, lambda skill: course_videos(skill, prep_client, include_hindi),
                          lambda skill: revision_videos(skill, prep_client, languages))
        job = plan["job"]
        with st.expander(f"Job Prep: {job.get('title') or 'Untitled'} · {job.get('company_name') or 'Unknown company'}", expanded=True):
            st.markdown(f"**Readiness for this job:** you cover {plan['covered_now']} of {plan['core_total']} core skills "
                        f"({plan['coverage_now']:.0%}; a match needs {plan['threshold']:.0%}).")
            if plan["coverage_now"] >= plan["threshold"]:
                st.write("This listing already matches your profile.")
            elif plan["unlock_skills"]:
                st.write(f"Learning {' or '.join(plan['unlock_skills'])} alone would make it a match.")
            st.write(f"After learning every skill listed below: {plan['covered_after']} of {plan['core_total']} core skills.")
            if plan["experience_years"]:
                st.write(f"Experience: this listing asks for at least {plan['experience_years']} years (\"{plan['experience_phrase']}\").")
            elif plan["experience_phrase"] != "no minimum detected":
                st.write(f"Experience: no minimum (\"{plan['experience_phrase']}\").")
            else:
                st.write("Experience: no requirement detected in this listing.")
            if plan["alternatives"]:
                for alternative in plan["alternatives"]:
                    st.write(f"Alternatives: {alternative['text']}")
            else:
                st.caption("This listing offers no either/or skill choices.")
            st.markdown(f"**Time plan:** {time_range(plan)}: {plan['revision_minutes']:.0f} minutes of revision videos "
                        f"plus {plan['learning_hours']:.1f} hours of full courses.")
            st.caption(REVISION_LABEL)
            if plan["hours_unknown"] or plan["broad"]:
                st.caption("Not in the time plan: " + ", ".join(
                    [f"{skill} (no saved course)" for skill in plan["hours_unknown"]] +
                    [f"{skill} (broad skill, no single course)" for skill in plan["broad"]]) + ".")

            def time_cell(item):
                if item["action"] == "revise":
                    if item["revision_status"] == "found":
                        return " + ".join(video["duration"] for video in item["revision_videos"]) + " revision"
                    if item["revision_status"] == "none":
                        return "No good short revision video found"
                    return "Revision videos available in live search" if replay_mode else "Revision videos not fetched yet"
                if item["broad"]:
                    return "Broad skill, no single course"
                return hours_range(item["hours"]) + " course" if item["hours"] else "Hours unknown"

            st.markdown("**Suggested order**")
            st.caption("Ranked by importance in this listing (mentions, plus 2 if near must, required, strong or mandatory), then by how many eligible listings in this search ask for the skill.")
            st.dataframe([{"Order": item["order"], "Skill": item["skill"], "Action": item["action"].title(),
                           "In this listing": f"{item['mentions']} mention{'s' if item['mentions'] != 1 else ''}" +
                                              (", marked required or strong" if item["emphasised"] else ""),
                           "Listings asking": f"{item['market']} of {item['market_total']}",
                           "Also unlocks": f"{item['other_unlocks']} other listings" if item["action"] == "learn" else "",
                           "Time": time_cell(item)} for item in plan["items"]],
                         hide_index=True, use_container_width=True)
            for action, heading in (("revise", "Revise: skills you have that this job asks for"),
                                    ("learn", "Learn: skills this job asks for that you lack")):
                rows = [item for item in plan["items"] if item["action"] == action]
                st.markdown(f"**{heading}**")
                if not rows:
                    st.caption("None.")
                for item in rows:
                    detail = f"{item['order']}. **{item['skill']}** · asked by {item['market']} of {item['market_total']} eligible listings"
                    if action == "learn":
                        detail += f" · would also unlock {item['other_unlocks']} other listings in this search"
                    st.markdown(detail)
                    if item["evidence"]:
                        st.caption(f"From this listing: \"{item['evidence']}\"")
                    videos = item.get("revision_videos") if action == "revise" else item.get("course_videos")
                    for video in videos or []:
                        st.markdown(f"- [{video['title']}]({video['link']}) · {video['channel']} · {video['duration']}")
                    if action == "revise" and item["revision_status"] != "found":
                        st.caption(time_cell(item) + ".")
            missing = [item["skill"] for item in plan["items"] if item["action"] == "revise"
                       and item["revision_status"] == "not_saved" and not is_cached(revision_params(item["skill"]), False)]
            if missing and not replay_mode:
                prep_budget = budget or 1
                st.caption(f"Fetching revision videos for {', '.join(missing)} needs {len(missing)} new SerpApi searches; "
                           f"the live search budget allows {min(len(missing), prep_budget)} now.")
                if st.button(f"Fetch revision videos (up to {min(len(missing), prep_budget)} searches)", key="prep_fetch"):
                    fetch_client = SerpClient(ledger_name="demo_ledger.json", call_cap=None, budget=prep_budget)
                    fetch_client.key = cloud_key or optional_serpapi_key()
                    try:
                        for skill in missing:
                            fetch_client.search(revision_params(skill))
                    except BudgetExceeded:
                        pass  # Keep what was fetched; the rest stays "not fetched yet".
                    except RuntimeError as exc:
                        st.error(str(exc))
                    st.rerun()
            st.caption("A prep plan shows what this listing asks for. It does not promise an interview or a job.")
    with st.expander("How this is calculated"):
        st.write("We set aside listings that ask for more experience than the minimum of your selected band: 0, 1 or 3 years. Explicit description requirements override title-based estimates. We ignore negated skill mentions in resumes and job text. Skills are alternatives only where the listing explicitly offers an 'or' or slash choice. Skills found in at least the selected share of eligible listings are core; less common skills are shown as nice to have. Eligible listings pass the experience and date filters. Scored listings also have detected core requirements; others are Unknown. A profile matches a listing when it meets the selected fraction of core requirements. We count additional matches after adding one skill or the suggested pair. Broad umbrella terms can count for matching but are never recommended.")
        st.write("Course hours are the median length of up to three qualifying free videos. Titles and channel names indicating an unrequested language are excluded; unlabelled videos are not proof of English audio. With fewer than two course-like videos of at least an hour, we fall back to videos of at least 30 minutes and mark low confidence. The displayed range is a rough 25% band, not a measured learning-time interval. The opportunity curve adds the measured skill with the most extra matches per course hour, stopping after five skills or no gain. Exact checks try every subset of up to eight measured candidates at 5, 10 and 15 hours. Confidence uses the lower of bootstrap win share and independent per-skill hour-variation retention across thresholds. The distance chart counts extra skills needed to cross the threshold. Posting age includes elapsed days since retrieval. These estimates do not establish competence or promise a job.")
    with st.expander("Search replay"):
        for event in result["replay"]:
            query = event["query"].get("q") or event["query"].get("search_query")
            location = event["query"].get("location")
            source = {"demo": "Bundled demo data", "fixture": "Demo cache (validation fixture)",
                      "cache": "Local cache", "live": "Live SerpApi request",
                      "cache missing": "No cached response"}.get(event["source"], event["source"])
            variant = event.get("variant")
            listings = event.get("listing_count")
            st.write(f"{source}: {event['query']['engine']} · {query}" + (f" · {location}" if location else "") +
                     (f" · {variant}" if variant else "") + (f" · {listings} listings" if listings is not None else ""))
        st.markdown("**Listing origins**")
        st.dataframe([{"Title": job.get("title") or "Untitled", "Company": job.get("company_name") or "Unknown",
                       "Search variant(s)": ", ".join(job.get("_search_queries") or [])}
                      for job in result["all_listings"]], width="stretch", hide_index=True)
else:
    st.info("Choose a role and city, add your skills, then select “Find my next skill”.")
