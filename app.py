"""NextSkill website entry point: a shared frame with one page per task."""
import streamlit as st

st.set_page_config(page_title="NextSkill", page_icon="🎯", layout="wide")

from views import common  # noqa: E402

common.style()
pages = [st.Page("views/home.py", title="Home", icon="🏠", default=True),
         st.Page("views/find.py", title="Job match", icon="🎯"),
         st.Page("views/prep.py", title="Job Prep", icon="📝"),
         st.Page("views/compare.py", title="Compare cities", icon="🗺️"),
         st.Page("views/methods.py", title="Methodology and evidence", icon="📊"),
         st.Page("views/about.py", title="About and privacy", icon="🔒")]
if common.live_key():
    pages.insert(4, st.Page("views/live.py", title="Live search", icon="⚡"))
st.navigation(pages, position="top").run()
