"""Run with: streamlit run nextskill/app.py"""
import altair as alt
import streamlit as st
import json
from resume_pdf import extract_pdf_text

from engine import (DEFAULT_THRESHOLD, DICTIONARY_WARNING, ROLE_FIT_WARNING, ROOT, SerpClient,
                    hours_range, is_old, no_unlock_message, optional_serpapi_key,
                    posted_text, run)

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
    threshold = st.slider("Within reach threshold", 0.2, 1.0, DEFAULT_THRESHOLD, 0.05)
    core_share = st.slider("Core skill frequency", 0.1, 0.5, 0.25, 0.05, help="A skill is core if it appears in at least this share of fetched jobs.")
    include_hindi = st.toggle("Include Hindi videos", False)
    exclude_old = st.toggle("Exclude jobs older than 30 days", False)
    pages = st.selectbox("Job pages", [1, 2, 3], index=2 if demo else 0)
    demo_ledger = ROOT / "cache" / "demo_ledger.json"
    demo_attempts = json.loads(demo_ledger.read_text()).get("real_calls", 0) if demo_ledger.exists() else 0
    last_account = ROOT / "cache" / "account_batch_d_after.json"
    if not last_account.exists():
        last_account = ROOT / "cache" / "account_batch_b_after.json"
    if not last_account.exists():
        last_account = ROOT / "cache" / "account_phase2_after.json"
    last_remaining = json.loads(last_account.read_text()).get("total_searches_left") if last_account.exists() else None
    st.caption(f"Demo live-search budget: {demo_attempts}/6 requests used." +
               (f" Last known SerpApi credits remaining: {last_remaining}." if last_remaining is not None else ""))
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
            client = SerpClient(use_fixtures=demo, cache_only=demo, ledger_name="demo_ledger.json", call_cap=6)
            if live:
                client.key = cloud_key or optional_serpapi_key()
                before = client.account("demo_before")
                try:
                    result = run(role, city, resume_input, manual, threshold, include_hindi,
                                 exclude_old, pages, False, client, core_share, learning_limit=3,
                                 experience_level=experience_level)
                finally:
                    after = client.account("demo_after")
                st.session_state["credit_update"] = {"before": before, "after": after}
            else:
                result = run(role, city, resume_input, manual, threshold, include_hindi,
                             exclude_old, pages, False, client, core_share,
                             experience_level=experience_level)
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
    st.subheader(f"Your profile matches {result['ready']} of {count} {source_label} in {result['city']}.")
    dates = result["retrieved_dates"]
    snapshot_date = dates[0] if len(dates) == 1 else f"{dates[0]} to {dates[-1]}" if dates else "unknown"
    st.caption(f"Snapshot date: {snapshot_date} (UTC). Posting ages include time elapsed since retrieval.")
    st.caption(f"{result['eligible_count']} eligible listings remain after experience and date filters; {count} have detected core requirements and are scored; {result['ignored']} have no detected core requirements.")
    st.caption(f"Based on {result['eligible_count']} listings · {result['listing_confidence']} confidence in sample size")
    if result["limited_data"]:
        st.warning("Limited data: fewer than 12 distinct jobs were found. Treat the ranking as exploratory.")
    if result["role_fit_warning"]:
        st.warning(ROLE_FIT_WARNING)
    if result["dictionary_warning"]:
        st.warning(DICTIONARY_WARNING)
    credit_update = st.session_state.get("credit_update")
    if credit_update:
        st.info(f"SerpApi credits used in this live run: {credit_update['after']['this_month_usage'] - credit_update['before']['this_month_usage']}. Remaining: {credit_update['after']['total_searches_left']}.")
    st.caption(f"{result['ignored']} jobs ignored because no core skills were detected. {result['raw'] - result['deduplicated']} likely duplicates removed. Core skills appear in at least {result['core_share']:.0%} of fetched jobs. These are matching signals, not a promise of hiring.")
    excluded = result["experience_excluded"]
    st.caption(f"{len(excluded)} jobs set aside because they need more experience than the selected level.")
    if excluded:
        with st.expander(f"Needs more experience ({len(excluded)})"):
            for row in excluded:
                job = row["job"]
                link = job.get("source_link") or job.get("share_link")
                label = f"{job.get('title') or 'Untitled'} — {job.get('company_name') or 'Unknown company'} · {row['reason']}"
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
    for index, item in enumerate(result["ranked"]):
        with st.container(border=True):
            display_skill = item.get("display_skill", item["skill"])
            title = f"🥇 {display_skill}" if index == 0 and item["score"] is not None and not result["limited_data"] else display_skill
            st.markdown(f"#### {title}")
            a, b, c = st.columns(3)
            a.metric("Jobs unlocked", f"+{item['unlocked_count']}")
            b.metric("Estimated learning hours", hours_range(item["hours"]))
            c.metric("Jobs per learning hour", f"{item['score']:.2f}" if item["score"] is not None else "Unavailable")
            if item["confidence"] == "low" and item["hours"] is not None:
                st.caption("Low confidence: fewer than two qualifying full courses; estimate uses videos of at least 30 minutes.")
            if item["videos"]:
                st.markdown("**Videos behind this hour estimate**")
                for video in item["videos"]:
                    st.markdown(f"- [{video['title']}]({video['link']}) — {video['channel']} · {video['duration']}")
            st.write(f"{display_skill} is requested in {item['appears_in']} of {count} jobs.")
            with st.expander(f"{item['unlocked_count']} jobs this skill could unlock"):
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
    st.caption("Each point shows how many eligible jobs would be within reach after learning the named skill; course length is only a study-time estimate.")
    if steps:
        st.dataframe([{"Step": step["step"], "Skill": display_names.get(step["skill"], step["skill"]),
                       "Hours range": hours_range(step["hours"]),
                       "Jobs gained": step["jobs_gained"], "Total jobs": step["total_jobs"]}
                      for step in steps], width="stretch", hide_index=True)
    else:
        st.info("No measured skill adds a reachable job at this threshold.")
    if opportunity["hours_unknown"]:
        st.caption("Hours unknown: " + ", ".join(opportunity["hours_unknown"]) + ". These skills are left out of the hours-based plan.")
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
