"""Job Prep plans for one listing, built from an existing NextSkill result."""
from __future__ import annotations

import hashlib
import json
import re
from typing import Callable

from engine import (ROOT, coverage, experience_evidence, extract_skills, indicated_languages,
                    parse_duration, stated_must_haves, must_have_status)
from skills import GENERIC, _BOUNDARY, _patterns, skill_mentions, names_skill

MEDIUM_VIDEO_SP = "EgIYAw=="  # YouTube Filters > Duration > 4-20 minutes, passed through SerpApi's `sp`.
REVISION_TITLE = re.compile(r"\b(?:revision|revise|crash course|one[ -]?shot|quick|"
                            r"in \d+\s*(?:min|mins|minutes)|interview questions)\b", re.I)
# School and exam revision (for example the CSS civil service exam) is a different subject.
OFF_TOPIC = re.compile(r"\b(?:exams?|syllabus|subjects|strategy|mcqs?|board|a level|plus two|class \d+)\b|preparation", re.I)
EMPHASIS = re.compile(r"\b(?:must|required|strong|strongly|mandatory)\b", re.I)
MIN_REVISION_MINUTES, MAX_REVISION_MINUTES = 5, 25
REVISION_LABEL = "Quick revision videos. Not a full course and not a guarantee."
# Bengaluru demo listing that is one skill away; opened by default so visitors see a full plan.
DEMO_JOB = ("Team Geek Solutions", "Frontend Developer (Fresher)")


def revision_params(skill: str) -> dict:
    return {"engine": "youtube", "search_query": f"{skill} revision", "gl": "in", "hl": "en", "sp": MEDIUM_VIDEO_SP}


def is_cached(params: dict, demo: bool) -> bool:
    """Mirror SerpClient's response file naming without touching the network."""
    digest = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()[:20]
    return (ROOT / ("demo_data" if demo else "cache") / f"search_{digest}.json").exists()


def select_revision_videos(results: list[dict], skill: str,
                           requested_languages: set[str] | None = None) -> list[dict]:
    """Keep up to two 5 to 25 minute videos about this skill with a revision-style title."""
    allowed = requested_languages or {"english"}
    chosen = []
    for item in results:
        hours = parse_duration(item.get("length"))
        title = str(item.get("title") or "")
        channel = item.get("channel") or {}
        channel_name = str(channel.get("name") or "") if isinstance(channel, dict) else str(channel)
        if hours is None or not MIN_REVISION_MINUTES <= hours * 60 <= MAX_REVISION_MINUTES:
            continue
        if not REVISION_TITLE.search(title) or not names_skill(title, skill):
            continue
        if OFF_TOPIC.search(title):
            continue
        if indicated_languages(title + " " + channel_name) - allowed:
            continue
        chosen.append({"title": title, "channel": channel_name, "duration": item.get("length"),
                       "minutes": hours * 60, "link": item.get("link") or ""})
        if len(chosen) == 2:
            break
    return chosen


def revision_videos(skill: str, client, requested_languages: set[str] | None = None) -> tuple[list[dict], str]:
    """Return (videos, status); status is found, none or not_saved. Cache-only clients never spend credits."""
    data = client.search(revision_params(skill))
    if not data:
        return [], "not_saved"
    videos = select_revision_videos(data.get("video_results") or [], skill, requested_languages)
    return videos, "found" if videos else "none"


def prep_candidates(analysis: dict) -> list[dict]:
    """Scored listings that match now or are one skill away."""
    user, threshold = analysis["user_skills_set"], analysis["threshold"]
    rows = []
    for index, entry in enumerate(analysis["jobs"]):
        requirements = entry["required_skills"]
        if entry["coverage"] >= threshold:
            rows.append({"index": index, "job": entry["job"], "status": "match", "unlock_skills": []})
            continue
        missing = set().union(*(req for req in requirements if not req & user))
        singles = sorted(skill for skill in missing if coverage(requirements, user | {skill}) >= threshold)
        if singles:
            # Broad labels never get a course in the plan, so they are not offered as the one skill.
            named = [skill for skill in singles if skill not in GENERIC]
            rows.append({"index": index, "job": entry["job"], "status": "one_away", "unlock_skills": named,
                         "broad_only": sorted(set(singles) - set(named)) if not named else []})
    return rows


def default_prep_index(analysis: dict) -> int | None:
    for row in prep_candidates(analysis):
        job = row["job"]
        if row["status"] == "one_away" and (job.get("company_name"), job.get("title")) == DEMO_JOB:
            return row["index"]
    return None


def evidence_line(text: str, start: int, end: int, width: int = 70) -> str:
    """The exact description segment around a mention, shortened only at its ends."""
    left = max([0] + [m.end() for m in _BOUNDARY.finditer(text, 0, start)])
    right = next((m.start() for m in _BOUNDARY.finditer(text, end)), len(text))
    segment_start, segment_end = left, right
    if start - segment_start > width:
        segment_start = text.rfind(" ", segment_start, start - width) + 1 or start - width
    if segment_end - end > width:
        cut = text.find(" ", end + width, segment_end)
        segment_end = cut if cut != -1 else segment_end
    line = readable(text[segment_start:segment_end].strip())
    return ("…" if segment_start > left else "") + line + ("…" if segment_end < right else "")


# Words that are written as one camel-case word and must not be split.
CAMEL_WORDS = re.compile(r"\b(?:GitHub|GitLab|LinkedIn|YouTube|WordPress|PowerPoint|HubSpot|QuickBooks|SharePoint|"
                         r"ServiceNow|DataFrame|PySpark|jQuery|JQuery|McKinsey|DeepMind|AdWords|InDesign|WhatsApp|"
                         r"iPhone|macOS|iOS|OpenAI|ChatGPT|DevOps|FastAPI|GraphQL|BigQuery|NumPy|PyTorch|TensorFlow)\b")


def readable(line: str) -> str:
    """Add a space where scraped text runs words together ("DevelopmentBasic"), never inside skill names."""
    protected = [(start, end) for _, start, end in skill_mentions(line, skip_headings=False)]
    protected += [match.span() for match in CAMEL_WORDS.finditer(line)]
    joins = [match.start() for match in re.finditer(r"(?<=[a-z]{3})(?=[A-Z][a-z]{2})|(?<=[a-z)][.!?;:)])(?=[A-Z][a-z])", line)]
    for position in reversed(joins):
        if not any(start < position < end for start, end in protected):
            line = line[:position] + " " + line[position:]
    return line


def _mentions(description: str) -> dict[str, list[tuple[int, int]]]:
    found: dict[str, list[tuple[int, int]]] = {}
    for skill, start, end in skill_mentions(description):
        found.setdefault(skill, []).append((start, end))
    return found


def _segment(text: str, start: int, end: int) -> str:
    left = max([0] + [m.end() for m in _BOUNDARY.finditer(text, 0, start)])
    right = next((m.start() for m in _BOUNDARY.finditer(text, end)), len(text))
    return text[left:right]


def build_plan(analysis: dict, index: int,
               course_lookup: Callable[[str], tuple[float | None, list[dict], str]],
               revision_lookup: Callable[[str], tuple[list[dict], str]]) -> dict:
    """Readiness, ordered revise/learn skills, alternatives, evidence and time for one listing."""
    entry = analysis["jobs"][index]
    job = entry["job"]
    description = str(job.get("description") or "")
    user, threshold = analysis["user_skills_set"], analysis["threshold"]
    core = entry["required_skills"]
    # Only core requirements drive readiness, so only they enter the plan.
    requirements = core
    mentions = _mentions(description)
    eligible = analysis["eligible_jobs"]
    eligible_skills = [extract_skills(str(other.get("description") or "")) for other in eligible]

    def market(skill: str) -> int:
        return sum(skill in skills for skills in eligible_skills)

    def other_unlocks(skill: str) -> int:
        return sum(row["coverage"] < threshold and coverage(row["required_skills"], user | {skill}) >= threshold
                   for position, row in enumerate(analysis["jobs"]) if position != index)

    course_cache: dict[str, tuple[float | None, list[dict], str]] = {}

    def course(skill: str):
        if skill not in course_cache:
            course_cache[skill] = course_lookup(skill)
        return course_cache[skill]

    # Unmet single requirements must be learned; an unmet "A or B" needs only one member.
    learn: set[str] = {next(iter(req)) for req in requirements if len(req) == 1 and not req & user}
    alternatives = []
    for req in sorted((req for req in requirements if len(req) > 1), key=lambda req: sorted(req)):
        options = " / ".join(sorted(req))
        owned = sorted(req & user)
        if owned:
            alternatives.append({"options": sorted(req), "status": "satisfied", "skill": owned[0],
                                 "text": f"This listing accepts {options}. You already have {', '.join(owned)}."})
            continue
        planned = sorted(req & learn)
        if planned:
            pick = min(planned, key=lambda skill: (-market(skill), skill))
            reason = "this listing also asks for it separately, so it is already in your plan"
        else:
            pick = min(req, key=lambda skill: (-market(skill), course(skill)[0] or float("inf"), skill))
            reason = f"asked by {market(pick)} of {len(eligible)} eligible listings"
            learn.add(pick)
        alternatives.append({"options": sorted(req), "status": "pick", "skill": pick,
                             "text": f"This listing accepts {options}. Pick {pick}: {reason}."})

    revise = sorted(user & set().union(*requirements)) if requirements else []
    items = []
    for skill in sorted(set(revise) | learn):
        spans = mentions.get(skill, [])
        emphasised = [span for span in spans if EMPHASIS.search(_segment(description, *span))]
        evidence_span = (emphasised or spans or [None])[0]
        item = {"skill": skill, "action": "revise" if skill in user else "learn",
                "core": any(skill in req for req in core),
                "mentions": len(spans), "emphasised": bool(emphasised),
                "importance": len(spans) + (2 if emphasised else 0),
                "market": market(skill), "market_total": len(eligible),
                "evidence": evidence_line(description, *evidence_span) if evidence_span else ""}
        if item["action"] == "learn" and skill in GENERIC:
            # Broad labels count for matching but never get a course, as in the main ranking.
            item.update({"hours": None, "course_videos": [], "course_confidence": None, "broad": True,
                         "other_unlocks": other_unlocks(skill)})
        elif item["action"] == "learn":
            hours, videos, confidence = course(skill)
            item.update({"hours": hours, "course_videos": videos, "course_confidence": confidence,
                         "broad": False, "other_unlocks": other_unlocks(skill)})
        else:
            videos, status = revision_lookup(skill)
            item.update({"revision_videos": videos, "revision_status": status})
        items.append(item)
    items.sort(key=lambda item: (-item["importance"], -item["market"], item["skill"]))
    for position, item in enumerate(items, 1):
        item["order"] = position

    learned = {item["skill"] for item in items if item["action"] == "learn"}
    covered_now = sum(bool(req & user) for req in core)
    covered_after = sum(bool(req & (user | learned)) for req in core)
    revision_minutes = sum(video["minutes"] for item in items if item["action"] == "revise"
                           for video in item["revision_videos"])
    learning_hours = sum(item["hours"] for item in items if item["action"] == "learn" and item["hours"])
    years, phrase = experience_evidence(job)
    return {"index": index, "job": job, "items": items, "alternatives": alternatives,
            "must_haves_status": must_have_status(stated_must_haves(description), user),
            "must_haves": [" or ".join(sorted(req)) for req in sorted(stated_must_haves(description), key=lambda r: sorted(r))],
            "core_total": len(core), "covered_now": covered_now, "covered_after": covered_after,
            "coverage_now": entry["coverage"], "threshold": threshold,
            "unlock_skills": sorted(skill for skill in learned - GENERIC if coverage(core, user | {skill}) >= threshold)
            if entry["coverage"] < threshold else [],
            "also_mentioned": sorted(extract_skills(description) - set().union(*core, set()),
                                     key=lambda skill: (-market(skill), skill)),
            "experience_years": years, "experience_phrase": phrase,
            "revision_minutes": revision_minutes, "learning_hours": learning_hours,
            "hours_unknown": sorted(item["skill"] for item in items
                                    if item["action"] == "learn" and not item["hours"] and not item["broad"]),
            "broad": sorted(item["skill"] for item in items if item["action"] == "learn" and item["broad"]),
            "missing_revision": sorted(item["skill"] for item in items
                                       if item["action"] == "revise" and item["revision_status"] != "found")}


def time_range(plan: dict) -> str:
    """Revision minutes are exact video lengths; course hours keep the app's rough 25% band."""
    revision = plan["revision_minutes"] / 60
    low = revision + plan["learning_hours"] * .75
    high = revision + plan["learning_hours"] * 1.25
    if high < 1:
        return f"about {round(low * 60)} to {round(high * 60)} minutes"
    return f"about {low:.1f} to {high:.1f} hours"
