"""Interface strings. English lives here; Hindi lives in i18n/hi.json and is shown only once a person approves it."""
from __future__ import annotations

import json

import streamlit as st

from engine import ROOT

STRINGS = {
    "toggle_hindi": "हिंदी",
    "hero_tagline": "Your next skill, counted from local job listings in your city.",
    "find_header": "Find my next skill",
    "find_role_city": "Role and city",
    "find_resume": "Paste your resume text or list your skills",
    "find_add_skills": "Add more skills (comma separated)",
    "find_experience": "Experience level",
    "skills_read": "Skills we read from your text",
    "tab_answer": "Answer",
    "tab_evidence": "Evidence",
    "tab_plan": "Learning plan",
    "tab_checks": "How we checked this",
    "headline": "Learn {skill} next: +{gained} more matching {listing_word}, about {hours} {hour_word} of free courses.",
    "matches_line": "Your profile matches {ready} of {count} {source} in {city}.",
    "fastest_win": "Fastest win",
    "biggest_unlock": "Biggest unlock",
    "prep_header": "Job Prep",
    "shortest_route": "Shortest route to match this listing",
    "full_plan": "Full plan",
    "revise_heading": "Revise: skills you have that this job asks for",
    "learn_heading": "Learn: skills this job asks for that you lack",
    "hindi_videos": "Hindi videos",
    "hindi_not_saved": "Hindi videos for {skill} are not in the saved data, so English videos are shown.",
    "hindi_fallback": "No Hindi video passed the filters for {skill} in the saved data, so English videos are shown.",
}
HINDI_WAITING = ("Hindi interface labels are waiting for human review, so English is shown. "
                 "Hindi videos are shown where they pass the same filters.")


def hindi_entries() -> dict:
    return json.loads((ROOT / "i18n/hi.json").read_text())["strings"]


def hindi_on() -> bool:
    return bool(st.session_state.get("hindi_toggle"))


def approved_count() -> int:
    return sum(bool(entry.get("approved")) for entry in hindi_entries().values())


def t(key: str, **values) -> str:
    """Hindi only when the toggle is on and a person has approved that string; otherwise English."""
    text = STRINGS[key]
    if hindi_on() and key != "toggle_hindi":
        entry = hindi_entries().get(key) or {}
        if entry.get("approved") and entry.get("hi"):
            text = entry["hi"]
    return text.format(**values)
