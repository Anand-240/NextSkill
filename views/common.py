"""Shared styling, saved-data helpers, input state and cached analysis for every NextSkill page."""
from __future__ import annotations

import json

import streamlit as st

import engine
import findings
import i18n
from engine import DEFAULT_THRESHOLD, EXPERIENCE_LEVELS, ROOT, SerpClient, canonical_manual_skills, run
from personas import saved_pairs
from resume_pdf import extract_pdf_text
from skills import extract_skills

MAX_PDF_BYTES = 5_000_000
STYLE = """<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=DM+Sans:wght@400;500;700&display=swap');
:root {--paper:#f6f1e7; --card:#fffaf0; --ink:#1f1b16; --muted:#6a6256; --line:#1f1b16; --mark:#f4c430; --green:#1f4d3a; --clay:#b4532a;}
html, body, .stApp, [class*="st-"] {font-family: 'DM Sans', system-ui, sans-serif;}
.stApp {background: var(--paper); color: var(--ink);}
[data-testid="stIconMaterial"], [class*="material-symbols"] {font-family: 'Material Symbols Rounded', 'Material Symbols Outlined' !important;}
h1, h2, h3, .serif {font-family: 'Fraunces', Georgia, serif !important; font-weight: 700; letter-spacing: -0.01em; color: var(--ink);}
.block-container {max-width: 1040px; padding-top: 4.5rem; padding-bottom: 5rem}
[data-testid="stHeader"] {background: var(--paper); border-bottom: 1.5px solid var(--ink);}
a[data-testid="stTopNavLink"] {font-weight: 500; border-radius: 0; background: transparent !important; color: var(--ink);}
a[data-testid="stTopNavLink"]:hover {background: var(--mark) !important;}
a[data-testid="stTopNavLink"][aria-current="page"], a[data-testid="stTopNavLink"][class*="active"] {box-shadow: inset 0 -3px 0 var(--ink); font-weight: 700;}
a {color: var(--ink); text-decoration-color: var(--mark); text-decoration-thickness: 2px; text-underline-offset: 3px;}
a:hover {background: var(--mark); color: var(--ink);}
.kicker {font-size: .78rem; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); font-weight: 700; margin: 0 0 .6rem}
.display {font-family: 'Fraunces', Georgia, serif; font-weight: 700; font-size: clamp(2.2rem, 6vw, 4rem); line-height: 1.04; letter-spacing: -0.02em; margin: 0 0 1rem}
.lede {font-size: 1.2rem; line-height: 1.5; max-width: 40rem; margin: 0 0 1.4rem}
.mark {background: linear-gradient(transparent 58%, var(--mark) 58%, var(--mark) 92%, transparent 92%); padding: 0 .1em}
.sticker {display: inline-block; background: var(--mark); border: 1.5px solid var(--ink); padding: .1rem .55rem; font-size: .8rem; font-weight: 700; transform: rotate(-2deg); margin-bottom: .5rem}
.rule {border: 0; border-top: 1.5px solid var(--ink); margin: 2.2rem 0 1.2rem}
.step-n {font-family: 'Fraunces', Georgia, serif; font-size: 2.6rem; font-weight: 700; line-height: 1; color: var(--clay)}
.step-t {font-weight: 700; margin: .2rem 0}
.stat {font-family: 'Fraunces', Georgia, serif; font-size: clamp(2.2rem, 5vw, 3.4rem); font-weight: 700; line-height: 1}
.stat-sm {font-size: 1.9rem; padding-top: .6rem}
.stat-l {color: var(--muted); font-size: .95rem; margin: .35rem 0 1rem}
.chip {display: inline-block; background: var(--card); color: var(--ink); border: 1.5px solid var(--ink); border-radius: 3px; padding: .08rem .55rem; margin: 0 .35rem .35rem 0; font-size: .9rem; font-weight: 500}
.chip-need {background: var(--mark)}
.pill {display: inline-block; border: 1.5px solid var(--ink); border-radius: 3px; padding: .05rem .5rem; font-size: .85rem; font-weight: 700}
.pill-strong {background: #bfe3c8}.pill-likely {background: var(--mark)}.pill-uncertain {background: #f0c9b4}
.bar {height: 8px; background: #e4dccb; border: 1.5px solid var(--ink); border-radius: 2px; margin: .35rem 0 .2rem}
.bar > span {display: block; height: 100%; background: var(--green)}
.jobtitle {font-weight: 700; font-size: 1.05rem; line-height: 1.3}
.jobmeta {color: var(--muted); font-size: .92rem}
[data-testid="stVerticalBlockBorderWrapper"] {background: var(--card); border: 1.5px solid var(--ink) !important; border-radius: 4px !important; transition: transform .12s, box-shadow .12s}
[data-testid="stVerticalBlockBorderWrapper"]:hover {transform: translate(-2px, -2px); box-shadow: 4px 4px 0 var(--ink)}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"] {box-shadow: none; transform: none}
.stButton > button, .stLinkButton a, [data-testid="stBaseButton-primary"], [data-testid="stBaseButton-secondary"] {border: 1.5px solid var(--ink); border-radius: 3px; background: var(--card); color: var(--ink); font-weight: 700; box-shadow: 3px 3px 0 var(--ink); transition: transform .1s, box-shadow .1s}
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"] {background: var(--ink); color: var(--paper)}
.stButton > button[kind="primary"] p {color: var(--paper)}
.stButton > button[kind="primary"]:hover p {color: var(--ink)}
.stButton > button:hover, .stLinkButton a:hover {transform: translate(2px, 2px); box-shadow: 1px 1px 0 var(--ink); background: var(--mark); color: var(--ink); border-color: var(--ink)}
[data-testid="stExpander"] {background: var(--card); border: 1.5px solid var(--ink); border-radius: 4px}
[data-testid="stExpander"] summary {font-weight: 700}
[data-baseweb="tab-list"] {gap: .4rem; border-bottom: 1.5px solid var(--ink)}
[data-baseweb="tab"] {font-weight: 700}
[data-baseweb="tab-highlight"] {background: var(--ink) !important; height: 4px !important}
[data-testid="stMetricValue"] {font-family: 'Fraunces', Georgia, serif; font-weight: 700}
[data-baseweb="select"] > div, [data-baseweb="input"], [data-baseweb="textarea"] {background: var(--card) !important; border: 1.5px solid var(--ink) !important; border-radius: 3px !important}
[data-testid="stCaptionContainer"] {color: var(--muted)}
[data-testid="stAlert"] {background: var(--card); border: 1.5px solid var(--ink); border-radius: 4px; color: var(--ink)}
[data-testid="stDataFrame"] {border: 1.5px solid var(--ink); border-radius: 4px}
@media (max-width: 640px) {.block-container {padding-top: 4rem} .display {font-size: 2.2rem}}
</style>"""


def style() -> None:
    st.markdown(STYLE, unsafe_allow_html=True)


def language_bar() -> None:
    """Top-right Hindi switch shown on every page; labels change only for human-approved strings."""
    _, right = st.columns([3, 1])
    right.toggle(i18n.t("toggle_hindi"), key="hindi_toggle")
    if i18n.hindi_on() and not i18n.approved_count():
        st.caption(i18n.HINDI_WAITING)


def hero(title: str, subtitle: str) -> None:
    """Page title block: a small label, a big serif line and one sentence."""
    st.markdown(f'<p class="kicker">NextSkill</p><h1 class="display">{title}</h1><p class="lede">{subtitle}</p>',
                unsafe_allow_html=True)


def chips(values: list[str], need: bool = False) -> None:
    css = "chip chip-need" if need else "chip"
    st.markdown("".join(f'<span class="{css}">{value}</span>' for value in values) or "None", unsafe_allow_html=True)


def confidence_pill(label: str) -> str:
    return f'<span class="pill pill-{label.lower()}">{label}</span>'


def demo_data_version() -> tuple:
    """Changes whenever a bundled response is added, removed or rewritten."""
    return tuple(sorted((path.name, path.stat().st_size, path.stat().st_mtime_ns)
                        for path in (ROOT / "demo_data").rglob("*.json")))


@st.cache_data(show_spinner=False)
def _read_results(version: int) -> dict:
    return json.loads((ROOT / "reports/final_results.json").read_text())


def final_results() -> dict:
    """Generated results for every saved pair; the single source for headline numbers.
    The cache key is the file's modification time, so a redeploy never serves stale numbers."""
    return _read_results((ROOT / "reports/final_results.json").stat().st_mtime_ns)


@st.cache_data(show_spinner=False)
def _read_gap(version: int) -> dict:
    return json.loads((ROOT / "reports/job_gap.json").read_text())


def job_gap() -> dict:
    """Equal-query listing counts per city; cached by the file's modification time."""
    return _read_gap((ROOT / "reports/job_gap.json").stat().st_mtime_ns)


def pairs() -> list[dict]:
    return saved_pairs()


def pair_by_id(pair_id: str) -> dict:
    return next((pair for pair in pairs() if pair["id"] == pair_id), pairs()[0])


def snapshot_text(pair_id: str) -> str:
    dates = final_results()["pairs"].get(pair_id, {}).get("retrieved_dates") or []
    return "unknown date" if not dates else dates[0] if len(dates) == 1 else f"{dates[0]} to {dates[-1]}"


def pair_label(pair: dict) -> str:
    return f"{pair['role']} · {pair['city']} (saved {snapshot_text(pair['id'])})"


def live_key() -> str | None:
    """A key exists only on a local machine with a .env file or environment variable."""
    return engine.optional_serpapi_key()


def user_skills(resume_text: str, manual: str = "", pdf_bytes: bytes | None = None) -> tuple[list[str], str | None]:
    """Canonical skill list from pasted text, an optional PDF and extra skills, plus a warning if any."""
    warning = None
    text = resume_text or ""
    if pdf_bytes:
        if len(pdf_bytes) > MAX_PDF_BYTES:
            warning = "This PDF is larger than 5 MB. Please paste your resume text instead."
        else:
            try:
                pdf_text = extract_pdf_text(pdf_bytes)
            except ValueError as exc:
                pdf_text, warning = "", str(exc)
            if pdf_bytes and not pdf_text and not warning:
                warning = "No selectable text was found in this PDF. If it is scanned, please paste your resume text instead."
            text = "\n".join(part for part in (text, pdf_text) if part)
    skills = extract_skills(text, resume=True) | canonical_manual_skills(manual)
    return sorted(skills), warning


@st.cache_data(show_spinner=False, max_entries=128)
def saved_result(pair_id: str, skills: tuple[str, ...], threshold: float, core_share: float,
                 experience_level: str, data_version: tuple) -> dict:
    """Saved-data analysis is deterministic. The key holds only canonical skills, never resume text."""
    pair = pair_by_id(pair_id)
    client = SerpClient(use_fixtures=True, cache_only=True, ledger_name="demo_ledger.json", call_cap=6)
    return run(pair["role"], pair["city"], "", ", ".join(skills), threshold, False, False, pair["pages"], False,
               client, core_share, experience_level=experience_level)


def get_saved_result(pair_id: str, skills: list[str], threshold: float = DEFAULT_THRESHOLD,
                     core_share: float = 0.25, experience_level: str = "Fresher") -> dict:
    return saved_result(pair_id, tuple(skills), threshold, core_share, experience_level, demo_data_version())


def experience_levels() -> list[str]:
    return list(EXPERIENCE_LEVELS)


def current_profile(pair: dict) -> dict:
    """The profile last used on the Job match page for this role, or the role's example profile."""
    saved = st.session_state.get("profile")
    if saved and saved["role"] == pair["role"]:
        return saved
    skills, _ = user_skills(pair["resume"])
    return {"pair_id": pair["id"], "role": pair["role"], "resume": pair["resume"], "manual": "", "skills": skills,
            "threshold": DEFAULT_THRESHOLD, "core_share": 0.25, "experience": pair.get("experience_level", "Fresher")}


def key_findings() -> list[str]:
    """Three headline findings, computed from the generated results file."""
    return findings.key_findings(final_results())


def seed(key: str, value) -> str:
    """Give a widget its starting value through session state, so its identity never changes between runs."""
    st.session_state.setdefault(key, value)
    return key


def start_label(labels: list[str]) -> str:
    """The market chosen last time, or the first one."""
    profile = st.session_state.get("profile")
    return next((label for label, pair in zip(labels, pairs()) if profile and pair["id"] == profile["pair_id"]), labels[0])


def credit_message(result: dict, account: dict | None) -> str:
    """Credits used come from this run's own request count; SerpApi's balance is shown apart, because it can lag."""
    used = result.get("live_requests", 0)
    text = f"SerpApi credits used in this live run: {used} (counted by this app from its own requests). "
    if account and account.get("total_searches_left") is not None:
        return text + (f"Remaining as reported by SerpApi: {account['total_searches_left']} "
                       "(may lag by a few seconds).")
    return text + "Credit balance unavailable from SerpApi right now."
