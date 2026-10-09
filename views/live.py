"""Live search (local only): a new role and city through SerpApi, with a small explicit budget."""
import hashlib

import streamlit as st

from engine import DEFAULT_THRESHOLD, SerpClient, max_live_requests, run, safe_account
from personas import personas
from views import common
from views.prep_ui import prep_section
from views.render import render_full

st.header("Live search")
key = common.live_key()
if not key:
    st.info("Live search is available only on a machine that has its own SerpApi key. This hosted site uses saved data.")
    st.stop()


@st.cache_data(ttl=300, show_spinner=False)
def credit_balance(key_hash: str) -> int | None:
    client = SerpClient()
    client.key = common.live_key()
    try:
        return client.account("page").get("total_searches_left")
    except RuntimeError:
        return None


st.write("Fetches a new market now. Saved responses are reused at no cost; every new request uses one SerpApi credit.")
role = st.text_input("Role", "Data Analyst")
city = st.text_input("City", "Noida")
examples = personas()
resume = st.text_area("Your skills", examples.get(role, examples["Data Analyst"])["resume"], height=100)
manual = st.text_input("Add more skills (comma separated)")
experience = st.selectbox("Experience level", common.experience_levels())
pages = st.selectbox("Job pages", [1, 2, 3], index=0)
budget = int(st.number_input("Live search budget", min_value=1, max_value=30, value=3, step=1,
                             help="Maximum new SerpApi searches for this run."))
estimate = min(budget, max_live_requests(role, pages, experience, False))
st.caption(f"This run may use up to {estimate} credit{'s' if estimate != 1 else ''}.")
balance = credit_balance(hashlib.sha256(key.encode()).hexdigest()[:12])
st.caption(f"SerpApi credits remaining (Account API): {balance}." if balance is not None else "Credit balance unavailable.")
if st.button("Run live search", type="primary"):
    skills, warning = common.user_skills(resume, manual)
    client = SerpClient(ledger_name="demo_ledger.json", call_cap=None, budget=budget)
    client.key = key
    try:
        with st.spinner("Searching listings and course lengths…"):
            before = safe_account(client, "page_before")
            result = run(role, city, "", ", ".join(skills), DEFAULT_THRESHOLD, False, False, pages, False, client,
                         0.25, learning_limit=3, experience_level=experience)
            st.session_state["live_result"] = result
            after = safe_account(client, "page_after")
        credit_balance.clear()
        st.session_state["live_credit"] = {"before": before, "after": after}
    except Exception as exc:  # Engine errors are written not to include the key.
        st.error(str(exc))
result = st.session_state.get("live_result")
if result:
    credit = st.session_state.get("live_credit")
    if credit and credit["before"] and credit["after"]:
        used = credit["after"]["this_month_usage"] - credit["before"]["this_month_usage"]
        st.info(f"SerpApi credits used in this live run: {used}. Remaining: {credit['after']['total_searches_left']}.")
    elif credit:
        st.info("Credit balance unavailable")
    render_full(result, saved=False)
    st.markdown("### Job Prep")
    prep_section(result, saved=False, state_key="live_prep", budget=budget)
