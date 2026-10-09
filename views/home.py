"""Home: the pitch, one worked example and where to go next."""
import streamlit as st

from views import common

results = common.final_results()["pairs"]
priya = results["frontend-developer-bengaluru"]
fastest = next(row for row in priya["ranked"] if row["skill"] == priya["fastest_win"])

common.hero("NextSkill", "Your next skill, counted from local job listings in your city.")
st.markdown("### An example")
st.write(f"Priya knows HTML, CSS and JavaScript and wants a frontend job in Bengaluru. NextSkill checked local listings "
         f"through SerpApi. Her profile matches **{priya['matches']} of {priya['scored']}** scored listings. "
         f"**{fastest['display_skill']}** could add **{fastest['unlocked']}** more, with about {max(1, round(fastest['hours']))} "
         f"hour of free courses. Every listing and every course behind that estimate is one click away.")
st.caption(f"Priya is an example profile, not a real person. Confidence: {priya['confidence']}. "
           f"Snapshot: {priya['retrieved_dates'][0]}.")
if st.button("Try it with Priya's profile", type="primary"):
    st.switch_page("views/find.py")

left, right = st.columns(2)
with left:
    st.markdown("### Who it helps")
    st.write("Freshers and early-career job seekers choosing what to learn next, especially outside the biggest "
             "tech hubs. It shows which missing skill appears in the most local listings and which has the shortest "
             "free course, so the choice rests on evidence you can open.")
with right:
    st.markdown("### What it does")
    st.write("Reads Google Jobs listings and YouTube course data through SerpApi, compares them with your skills, and "
             "recommends a fastest win and a biggest unlock. Job Prep turns one listing into a revise-and-learn plan.")

st.markdown("### Three findings from the saved markets")
for finding in common.key_findings():
    st.markdown(f"- {finding}")
st.caption("These sentences are generated from reports/final_results.json whenever the page loads.")

st.markdown("### Explore")
columns = st.columns(4)
for column, (path, label, note) in zip(columns, (
        ("views/find.py", "Find my next skill", "Pick a market, add your skills"),
        ("views/prep.py", "Job Prep", "Revise and learn for one listing"),
        ("views/compare.py", "Compare cities", "Does the answer change by city?"),
        ("views/methods.py", "Methodology and evidence", "What the numbers mean"))):
    with column.container(border=True):
        st.page_link(path, label=label)
        st.caption(note)
