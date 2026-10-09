"""Job Prep: revise the skills you have and learn the ones you lack for one listing."""
import streamlit as st

from views import common
from views.prep_ui import prep_section

st.header("Job Prep")
st.write("Pick one listing. Revise the skills you already have with short videos, and learn the missing ones with full courses.")
pairs = common.pairs()
labels = [common.pair_label(pair) for pair in pairs]
pair = pairs[labels.index(st.selectbox("Role and city", labels, key=common.seed("prep_pair", common.start_label(labels))))]
profile = common.current_profile(pair)
st.markdown("**Your skills**")
common.chips(profile["skills"])
st.page_link("views/find.py", label="Change your skills on the Find page")
result = common.get_saved_result(pair["id"], profile["skills"], profile["threshold"], profile["core_share"],
                                 profile["experience"])
prep_section(result, saved=True, state_key=f"prep_{pair['id']}")
