"""Methodology and evidence: what the numbers mean, how they are checked, and what is still pending."""
import re

import streamlit as st

import findings
from views import common

from engine import ROOT


def read(path: str) -> str:
    try:
        return (ROOT / path).read_text()
    except OSError:
        return ""


def section(text: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}.*?\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return match.group(1).strip() if match else ""


def body(path: str) -> str:
    """A generated report without its title line."""
    return re.sub(r"\A# .*\n+", "", read(path)).strip()


st.header("Methodology and evidence")
st.markdown("### What the numbers mean")
st.markdown("""
- **Match:** your profile covers at least the selected share (default 50%) of a listing's detected core skills. It is not hiring eligibility or a prediction.
- **Stated must-haves met:** yes, no or none stated, for skills near explicit words such as must, mandatory or required. Checked separately from the match.
- **Course hours:** the median length of up to three free videos whose titles name the skill. Duration is not mastery.
- **Fastest win:** the missing skill that adds the most matches per course hour. **Biggest unlock:** the skill that adds the most matches, whatever the hours.
- **Pick stability:** how stable the headline pick is when listings are resampled and course hours vary. Strong needs at least 15 scored listings and a pick with standard course confidence; limited-data markets are never above Uncertain. It measures sensitivity, not accuracy.
- **Standard course confidence:** at least two relevant full courses of an hour or more. Only such a skill can be the fastest win.
- **Exact among measured skills:** every combination of up to eight skills with known course hours was tried. It is not a global optimum.
""")
st.markdown("### How it works")
st.write("SerpApi Google Jobs supplies listings for a role and city. The engine removes duplicates, sets aside listings that ask "
         "for more experience than your level, detects required skills and either/or choices, and compares them with your skills. "
         "SerpApi YouTube supplies course and short revision videos. Everything is counted from the saved or fetched responses, "
         "and each recommendation links back to the listings and videos that produced it.")
st.markdown("### Does jobs-per-hour change the answer?")
st.markdown(findings.baseline_text(common.final_results()))
st.markdown("### Validation")
audit = read("reports/matcher_audit.md")
lines = [line for line in audit.splitlines() if line.startswith("Precision")]
st.write("Developer-written check of skill detection: " + " ".join(lines) + " This is a 20-match sample reviewed by the "
         "developer, not an independent evaluation, and it does not measure recall.")
st.markdown("#### Hand-labelled accuracy")
st.markdown(body("reports/hand_label_eval.md"))
st.markdown("#### User test")
st.markdown(body("reports/user_test.md"))
st.markdown("### Limitations")
st.markdown("""
- Small, biased snapshots of Google Jobs listings; nearby-city results appear (see the job-information gap on Compare cities).
- Required versus preferred wording is parsed imperfectly, and qualifications outside the skill vocabulary are not seen.
- Posting ages and course audio languages are often unknown.
- A title that names a skill does not prove the course is good or suits every technology stack.
- No learning outcomes or hiring outcomes have been measured.
""")
st.markdown("### Research sources")
st.markdown(section(read("research/RESEARCH.md"), "A3 - Problem evidence"))
st.markdown("### Existing tools")
st.markdown(section(read("research/RESEARCH.md"), "A4 - Landscape and what NextSkill does differently"))
st.markdown("### Tried and dropped")
st.markdown(section(read("research/RESEARCH.md"), "A5 - NPTEL and SWAYAM through Google search"))
st.caption("Full notes, API contracts and the requirements map are in research/RESEARCH.md in the repository.")
