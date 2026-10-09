"""Home: mirrors the README first screen. Every number is generated from the results files."""
import streamlit as st

import findings
from engine import hours_text
from i18n import t
from personas import personas
from views import common

results = common.final_results()
pairs = common.pairs()
labels = [common.pair_label(pair) for pair in pairs]
default_key = findings.example_key(results)

common.language_bar()
st.markdown('<p class="kicker">For freshers across India</p>'
            '<h1 class="display">Which job are you <span class="mark">one skill</span> away from?</h1>',
            unsafe_allow_html=True)
st.markdown('<p class="lede">NextSkill shows a fresher which listings in their own city they are one skill away from, and '
            'the free course that gets them there, with every number linked to its source.</p>', unsafe_allow_html=True)

st.markdown('<span class="sticker">Try it: pick a job and city</span>', unsafe_allow_html=True)
with st.container(border=True):
    chosen = st.selectbox("Job role and city", labels, index=[p["id"] for p in pairs].index(default_key),
                          key="home_market", label_visibility="collapsed")
    pair = pairs[labels.index(chosen)]
    row = results["pairs"][pair["id"]]
    head = next((item for item in row["ranked"] if item["skill"] == row["headline_skill"]), None)
    left, middle, right = st.columns(3)
    left.markdown(f'<div class="stat">{row["matches"]} of {row["scored"]}</div>'
                  f'<div class="stat-l">listings a sample fresher already matches</div>', unsafe_allow_html=True)
    if head:
        middle.markdown(f'<div class="stat">+{head["unlocked"]}</div>'
                        f'<div class="stat-l">more with {head["display_skill"]}, {hours_text(head["hours"])} of free courses</div>',
                        unsafe_allow_html=True)
    else:
        middle.markdown('<div class="stat">none</div><div class="stat-l">too few listings to name one skill</div>',
                        unsafe_allow_html=True)
    right.markdown(f'<div class="stat">{row["confidence"]}</div>'
                   f'<div class="stat-l">pick stability, based on {row["stability_listings"]} listings</div>',
                   unsafe_allow_html=True)
    if st.button("Open this market in Job match", type="primary"):
        st.session_state["find_pair"] = chosen
        st.switch_page("views/find.py")
st.markdown(findings.example_text(results, personas()[row["role"]]["resume"], pair["id"]))
st.caption(f"Snapshot: {common.snapshot_text(pair['id'])}. The profile is a sample for {row['role']} in {row['city']}, not a real person.")

st.markdown('<hr class="rule">', unsafe_allow_html=True)
st.markdown("## How it works")
steps = st.columns(3)
for column, (number, title, text) in zip(steps, (
        ("1", "Pick a job and a city", "Choose from the saved snapshots of Google Jobs listings."),
        ("2", "Tap what you know", "Add skills or paste your resume. It stays in your browser session."),
        ("3", "See the jobs you are close to", "The one skill that opens the most listings, and the free course to learn it."))):
    column.markdown(f'<div class="step-n">{number}</div><div class="step-t">{title}</div><div>{text}</div>',
                    unsafe_allow_html=True)

st.markdown('<hr class="rule">', unsafe_allow_html=True)
st.markdown("## What we found about local jobs")
gap = common.job_gap()
low = min(gap["rows"], key=lambda r: (r["in_city"] / r["listings"], r["role"], r["city"]))
high = max(gap["rows"], key=lambda r: (r["in_city"] / r["listings"], r["role"], r["city"]))
a, b = st.columns(2)
a.markdown(f'<div class="stat">{low["in_city"]} of {low["listings"]}</div>'
           f'<div class="stat-l">{low["role"]} listings for {low["city"]} were actually located there</div>', unsafe_allow_html=True)
b.markdown(f'<div class="stat">{high["in_city"]} of {high["listings"]}</div>'
           f'<div class="stat-l">{high["role"]} listings for {high["city"]} were located there</div>', unsafe_allow_html=True)
st.write(findings.gap_sentence(gap))
st.page_link("views/compare.py", label="See the chart on Compare cities")
st.caption("Listings visible through Google Jobs in one equal-query snapshot, not the number of jobs in a city.")
