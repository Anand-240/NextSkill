"""Hindi video preference: Hindi videos that pass the same relevance filters, or an explicit English fallback."""
from __future__ import annotations

from engine import LONG_VIDEO_SP, indicated_languages, select_course_videos
from job_prep import revision_videos


def course_params(skill: str) -> dict:
    return {"engine": "youtube", "search_query": f"{skill} tutorial in Hindi", "gl": "in", "hl": "en", "sp": LONG_VIDEO_SP}


def _states_hindi(video: dict) -> bool:
    return "hindi" in indicated_languages(f"{video['title']} {video.get('channel') or ''}")


def hindi_courses(skill: str, client) -> tuple[list[dict], str]:
    """Hindi full courses whose title or channel says Hindi and whose title names the skill. Status found, none or not_saved."""
    data = client.search(course_params(skill))
    if not data:
        return [], "not_saved"
    stated = [item for item in data.get("video_results") or []
              if "hindi" in indicated_languages(f"{item.get('title') or ''} {(item.get('channel') or {}).get('name', '')}")]
    _, chosen, _ = select_course_videos(stated, f"{skill} tutorial in Hindi", {"hindi", "english"}, skill)
    return chosen, "found" if chosen else "none"


def hindi_revision(skill: str, client) -> tuple[list[dict], str]:
    videos, status = revision_videos(skill, client, {"hindi", "english"}, hindi=True)
    videos = [video for video in videos if _states_hindi(video)]
    return videos, ("found" if videos else "none") if status != "not_saved" else status
