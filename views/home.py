"""Home: mirrors the README first screen. Every number is generated from the results files."""
import streamlit as st

import findings
from i18n import t
from personas import personas
from views import common

results = common.final_results()
star = results["pairs"][findings.example_key(results)]

common.language_bar()
common.hero("NextSkill", t("hero_tagline"))
st.markdown("**NextSkill shows a fresher which listings in their own city they are one skill away from, and the free course "
            "that gets them there, with every number linked to its source.**")
st.markdown("### Who it helps")
st.write("Freshers and early-career job seekers choosing what to learn next, especially outside the biggest hubs, where local "
         "listings are thin. It counts what local listings ask for instead of guessing from national trends.")
st.markdown("### Worked example")
st.markdown(findings.example_text(results, personas()[star["role"]]["resume"]))
st.caption(f"Snapshot: {star['retrieved_dates'][0]}. Sample profile for {star['role']} in {star['city']}.")
if st.button("Try it with this sample profile", type="primary"):
    st.session_state["find_pair"] = common.pair_label(common.pair_by_id(findings.example_key(results)))
    st.switch_page("views/find.py")

st.markdown("### Key finding: the job-information gap")
st.write(findings.gap_sentence(common.job_gap()))
st.page_link("views/compare.py", label="See the chart on Compare cities")
st.caption("Generated from reports/job_gap.json: listings visible through Google Jobs in one equal-query snapshot, not the "
           "number of jobs in a city.")

st.markdown("### Explore")
columns = st.columns(4)
for column, (path, label, note) in zip(columns, (
        ("views/find.py", "Job match", "Choose a job and city, add your skills"),
        ("views/prep.py", "Job Prep", "Revise and learn for one listing"),
        ("views/compare.py", "Compare cities", "Job-information gap and city differences"),
        ("views/methods.py", "Methodology and evidence", "What the numbers mean"))):
    with column.container(border=True):
        st.page_link(path, label=label)
        st.caption(note)
