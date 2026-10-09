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
.block-container {max-width: 1120px; padding-top: 4.5rem}
.hero {background:#122b3a;color:#fff;padding:2rem;border-radius:18px;margin-bottom:1.2rem}
.hero h1 {font-size:2.3rem;margin:0 0 .3rem;color:#fff}
.hero p {font-size:1.05rem;color:#dbe8ed;margin:0}
.chip {display:inline-block;background:#e3eef2;color:#123c41;border-radius:999px;padding:.15rem .7rem;margin:0 .3rem .3rem 0;font-size:.9rem}
.pill {display:inline-block;border-radius:6px;padding:.1rem .5rem;font-size:.85rem;font-weight:600}
.pill-strong {background:#d8f0dc;color:#14501f}.pill-likely {background:#e6f0cf;color:#3d4f0c}.pill-uncertain {background:#fbe9c9;color:#6b4300}
@media (max-width: 640px) {.hero {padding:1.2rem}.hero h1 {font-size:1.7rem}}
</style>"""


def style() -> None:
    st.markdown(STYLE, unsafe_allow_html=True)


def language_bar() -> None:
    """Top-right Hindi switch shown on every page; labels change only for human-approved strings."""
    _, right = st.columns([5, 1])
    right.toggle(i18n.t("toggle_hindi"), key="hindi_toggle")
    if i18n.hindi_on() and not i18n.approved_count():
        st.caption(i18n.HINDI_WAITING)


def hero(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def chips(values: list[str]) -> None:
    st.markdown("".join(f'<span class="chip">{value}</span>' for value in values) or "None", unsafe_allow_html=True)


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
    """The profile last used on the Find page for this role, or the role's example profile."""
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
