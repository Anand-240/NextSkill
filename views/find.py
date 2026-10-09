"""Job match: pick a job role and city, tap your skills, see the jobs you match and the skill that opens more."""
import streamlit as st

from i18n import t
from views import common
from views.render import render_full

common.language_bar()
st.markdown('<p class="kicker">Step 1 of 2: tell us what you know</p>', unsafe_allow_html=True)
st.header(t("find_header"))
st.write("Choose the job you want and your city, then tap your skills. You will see how many local listings you already match, "
         "which jobs one skill would open, and the free course that gets you there.")
pairs = common.pairs()
labels = [common.pair_label(pair) for pair in pairs]
pair = pairs[labels.index(st.selectbox(t("find_role_city"), labels, key=common.seed("find_pair", common.start_label(labels)),
                                       help="Saved snapshots of Google Jobs listings. No search credits are used."))]
profile = common.current_profile(pair)
saved = st.session_state.get("profile")
saved = saved if saved and saved["role"] == pair["role"] else None

# Skills the market asks for, plus the sample profile's own, as tap targets.
market_skills = sorted(common.get_saved_result(pair["id"], [])["core_skills"])
sample_skills = common.user_skills(pair["resume"])[0]
options = sorted(set(market_skills) | set(sample_skills))  # fixed per market, so the widget keeps its state
pills_key = common.seed(f"find_pills_{pair['id']}", [skill for skill in profile["skills"] if skill in options])
tapped = st.pills("Tap the skills you already have", options, selection_mode="multi", key=pills_key,
                  help="These are the skills the listings in this market ask for most. The sample profile starts selected.")

left, right = st.columns([3, 2])
manual = left.text_input(t("find_add_skills"), key=common.seed("find_manual", profile["manual"]),
                         placeholder="For example Excel, SQL, Tally")
levels = common.experience_levels()
experience = right.selectbox(t("find_experience"), levels, key=common.seed("find_experience", profile["experience"]),
                             help="Uses the minimum of each band: 0, 1 or 3 years. Explicit listing requirements take precedence over titles.")
if experience != "Fresher":
    st.caption("Saved samples come from fresher and junior searches, so results for other experience levels are approximate.")
with st.expander("Paste a resume, upload a PDF, or change the match threshold"):
    resume = st.text_area(t("find_resume"), height=130, key=common.seed(f"find_resume_{pair['role']}", saved["resume"] if saved else ""),
                          placeholder="Your text is read in memory and never stored.")
    pdf = st.file_uploader("PDF resume (selectable text, up to 5 MB)", type=["pdf"])
    threshold = st.slider("Match threshold", 0.2, 1.0, step=0.05, key=common.seed("find_threshold", float(profile["threshold"])),
                          help="A listing matches when your profile covers at least this share of its core skills.")
    core_share = st.slider("Core skill frequency", 0.1, 0.5, step=0.05, key=common.seed("find_core", float(profile["core_share"])),
                           help="A skill is core if it appears in at least this share of eligible listings.")

extra, warning = common.user_skills(resume, manual, pdf.getvalue() if pdf else None)
skills = sorted(set(tapped or []) | set(extra))
if warning:
    st.warning(warning)
st.markdown(f"**{t('skills_read')}**")
if skills:
    common.chips(skills)
else:
    st.info("No skills yet. Tap some above or add a few, for example Excel, SQL or Python. The answer below then shows what to learn from scratch.")
st.session_state["profile"] = {"pair_id": pair["id"], "role": pair["role"], "resume": resume, "manual": manual,
                               "skills": skills, "threshold": threshold, "core_share": core_share, "experience": experience}
st.markdown('<hr class="rule">', unsafe_allow_html=True)
st.markdown('<p class="kicker">Step 2 of 2: your answer</p>', unsafe_allow_html=True)
result = common.get_saved_result(pair["id"], skills, threshold, core_share, experience)
render_full(result, saved=True)
