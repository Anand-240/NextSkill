"""Job match: pick a job role and city, describe your skills, see the jobs you match and the skill that opens more."""
import streamlit as st

from i18n import t
from views import common
from views.render import render_full

common.language_bar()
st.header(t("find_header"))
st.write("Choose the job you want and your city, then add your skills. You will see how many local listings you already match, "
         "which jobs one skill would open, and the free course that gets you there.")
pairs = common.pairs()
labels = [common.pair_label(pair) for pair in pairs]
pair = pairs[labels.index(st.selectbox(t("find_role_city"), labels, key=common.seed("find_pair", common.start_label(labels)),
                                       help="Saved snapshots of Google Jobs listings. No search credits are used."))]
profile = common.current_profile(pair)
levels = common.experience_levels()
left, right = st.columns([3, 2])
resume = left.text_area(t("find_resume"), height=150,
                        key=common.seed(f"find_resume_{pair['role']}", profile["resume"]),
                        help="Example profile for this role. Replace it with yours. Your text is read in memory and never stored.")
manual = right.text_input(t("find_add_skills"), key=common.seed("find_manual", profile["manual"]))
experience = right.selectbox(t("find_experience"), levels, key=common.seed("find_experience", profile["experience"]),
                             help="Uses the minimum of each band: 0, 1 or 3 years. Explicit listing requirements take precedence over titles.")
if experience != "Fresher":
    st.caption("Saved samples come from fresher and junior searches, so results for other experience levels are approximate.")
with st.expander("Upload a PDF resume or change the match threshold"):
    pdf = st.file_uploader("PDF resume (selectable text, up to 5 MB)", type=["pdf"])
    threshold = st.slider("Match threshold", 0.2, 1.0, step=0.05, key=common.seed("find_threshold", float(profile["threshold"])),
                          help="A listing matches when your profile covers at least this share of its core skills.")
    core_share = st.slider("Core skill frequency", 0.1, 0.5, step=0.05, key=common.seed("find_core", float(profile["core_share"])),
                           help="A skill is core if it appears in at least this share of eligible listings.")

skills, warning = common.user_skills(resume, manual, pdf.getvalue() if pdf else None)
if warning:
    st.warning(warning)
st.markdown(f"**{t('skills_read')}**")
if skills:
    common.chips(skills)
else:
    st.info("No skills were recognised. Add some above, for example Excel, SQL or Python. The answer below then shows what to learn from scratch.")
st.session_state["profile"] = {"pair_id": pair["id"], "role": pair["role"], "resume": resume, "manual": manual,
                               "skills": skills, "threshold": threshold, "core_share": core_share, "experience": experience}
result = common.get_saved_result(pair["id"], skills, threshold, core_share, experience)
render_full(result, saved=True)
