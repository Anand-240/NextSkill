"""About and privacy."""
import re

import streamlit as st

from engine import ROOT

st.header("About and privacy")
st.markdown("### What happens to your resume")
st.write("Pasted text and uploaded PDFs are read in memory by this app to find skill names. The PDF is parsed with pypdf in memory "
         "and is never written to disk. Only the list of recognised skills is used as the analysis cache key. "
         "No resume text is sent to SerpApi: queries contain only the role, the city and skill names.")
st.caption("This was checked in the code: the only file writes are saved search responses and the credit ledger. Streamlit and its "
           "host may keep session memory and platform logs outside this app's control, so do not put sensitive details in the public demo.")
st.markdown("### Data sources")
st.write("Job listings come from Google Jobs and course videos from YouTube, both retrieved through "
         "[SerpApi](https://serpapi.com). Descriptions and video metadata remain their publishers' content, and every "
         "result links back to its source. Contact details in saved responses are redacted.")
st.markdown("### Licence")
st.write("The code is released under the MIT licence, which does not cover third-party listing or video content. "
         "Source: [github.com/Anand-240/NextSkill](https://github.com/Anand-240/NextSkill).")
st.markdown("### Team")
st.write("NextSkill was built by Anand and Anjali.")
st.markdown("### AI tools disclosure")
readme = (ROOT / "README.md").read_text()
match = re.search(r"^## AI tools disclosure\n+(.*?)(?=^## |\Z)", readme, re.S | re.M)
st.write(match.group(1).strip() if match else "AI coding assistants helped write parts of the code, tests and documentation. The running app does not call an LLM.")
