"""NextSkill job coverage, one-skill unlocks and course-length estimates."""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
import random
import re
import statistics
from collections import Counter
from datetime import date, datetime, timezone
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from skills import ALIASES, GENERIC, SKILLS, extract_skills, skill_mentions, negated_mention, preferred_mention, _BOUNDARY

ROOT = Path(__file__).resolve().parent
DEMO_DATA = ROOT / "demo_data"
VOCABULARY = {skill for group in SKILLS.values() for skill in group}
SUBSTITUTE_PREFERENCE = {"Power BI": 3, "React": 3, "AWS": 3,
                         "Tableau": 2, "Angular": 2, "Azure": 2,
                         "Looker": 1, "Vue.js": 1, "Google Cloud": 1}
LONG_VIDEO_SP = "EgIYAg=="  # YouTube Filters > Duration > Over 20 minutes, passed through SerpApi's `sp`.
COURSE_TITLE = re.compile(r"\b(?:full course|complete|course|masterclass|bootcamp)\b", re.I)
DEFAULT_THRESHOLD = 0.50
EXPERIENCE_LEVELS = {"Fresher": 0, "1-3 years": 1, "3+ years": 3}
ROLE_FIT_WARNING = "Your profile is far from this role. Recommendations show what this role needs, but it may be a big switch."
DICTIONARY_WARNING = "This role is outside NextSkill's strongest areas (tech, data, marketing, finance, design); results may be incomplete."
MOSTLY_READY_MESSAGE = "You already match most jobs here. Your best next step is applying, or exploring a more senior role."


def optional_serpapi_key() -> str | None:
    environment_key = os.environ.get("SERPAPI_KEY", "").strip()
    if environment_key and environment_key != "your_key_here":
        return environment_key
    path = ROOT / ".env"
    if not path.exists():
        return None
    for line in path.read_text().splitlines():
        if line.strip().startswith("SERPAPI_KEY="):
            key = line.split("=", 1)[1].strip().strip('"\'')
            if key and key != "your_key_here":
                return key
    return None


def _load_key() -> str:
    key = optional_serpapi_key()
    if key:
        return key
    raise RuntimeError("Missing usable SERPAPI_KEY")


def _scrub(value, key: str):
    if isinstance(value, dict):
        return {k: _scrub(v, key) for k, v in value.items() if k.lower() not in {"api_key", "account_email"}}
    if isinstance(value, list):
        return [_scrub(v, key) for v in value]
    if isinstance(value, str):
        return value.replace(key, "[REDACTED]")
    return value


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    temp.replace(path)


def retrieval_date(data: dict) -> date | None:
    raw = data.get("_retrieved_at") or (data.get("search_metadata") or {}).get("created_at")
    if not raw:
        return None
    try:
        stamp = datetime.fromisoformat(str(raw).replace(" UTC", "+00:00").replace("Z", "+00:00"))
        return stamp.astimezone(timezone.utc).date() if stamp.tzinfo else stamp.date()
    except ValueError:
        return None


def stamp_response(data: dict, fresh: bool = False) -> dict:
    """Preserve the source retrieval time; only a new response may use the clock."""
    stamp = data.get("_retrieved_at") or (data.get("search_metadata") or {}).get("created_at")
    if not stamp and fresh:
        stamp = datetime.now(timezone.utc).isoformat()
    return {**data, "_retrieved_at": stamp} if stamp else data


def read_response(path: Path) -> dict:
    return stamp_response(json.loads(path.read_text()))


def _request(endpoint: str, params: dict, key: str) -> dict:
    try:
        with urlopen(f"https://serpapi.com/{endpoint}?{urlencode({**params, 'api_key': key})}", timeout=75) as response:
            return _scrub(json.load(response), key)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        # urllib exceptions can contain the full secret-bearing URL.
        raise RuntimeError(f"SerpApi request failed ({type(exc).__name__})") from None


class BudgetExceeded(RuntimeError):
    """A live search would exceed this run's request budget; nothing was sent."""


class SerpClient:
    """Search source with fixture replay, persistent cache, a ledger cap and a per-run budget."""

    def __init__(self, offline: bool = False, cache_dir: Path | None = None, use_fixtures: bool = False,
                 cache_only: bool = False, ledger_name: str = "phase2_ledger.json", call_cap: int | None = 12,
                 budget: int | None = None):
        self.offline = offline
        self.use_fixtures = offline or use_fixtures
        self.cache_only = cache_only
        self.cache_dir = cache_dir or ROOT / "cache"
        self.ledger_name = ledger_name
        self.call_cap = call_cap
        self.budget = budget
        self.live_calls = 0
        self.budget_reached = False
        self.replay: list[dict] = []
        self.key: str | None = None

    def _fixture(self, params: dict, page: int) -> Path | None:
        if not self.use_fixtures:
            return None
        if params.get("engine") == "google_jobs":
            pair = (params.get("q", "").lower(), params.get("location", "").split(",")[0].lower())
            index = {("data analyst", "noida"): 1, ("python developer", "bengaluru"): 2, ("marketing intern", "pune"): 3}.get(pair)
            return DEMO_DATA / "fixtures" / f"jobs_{index}_page_{page}.json" if index else None
        if params.get("engine") == "youtube" and "power bi" in params.get("search_query", "").lower():
            index = 2 if "hindi" in params["search_query"].lower() else 1
            return DEMO_DATA / "fixtures" / f"youtube_{index}.json"
        return None

    def search(self, params: dict, page: int = 1) -> dict:
        fixture = self._fixture(params, page)
        if fixture and fixture.exists():
            self.replay.append({"query": dict(params), "source": "demo"})
            return read_response(fixture)
        digest = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()[:20]
        demo_path = DEMO_DATA / f"search_{digest}.json"
        if self.use_fixtures and demo_path.exists():
            self.replay.append({"query": dict(params), "source": "demo"})
            return read_response(demo_path)
        path = self.cache_dir / f"search_{digest}.json"
        if not self.use_fixtures and path.exists():
            self.replay.append({"query": dict(params), "source": "cache"})
            return read_response(path)
        if self.offline or self.cache_only:
            self.replay.append({"query": dict(params), "source": "cache missing"})
            return {}
        if self.budget is not None and self.live_calls >= self.budget:
            self.budget_reached = True
            self.replay.append({"query": dict(params), "source": "budget reached"})
            raise BudgetExceeded(f"Live search budget reached ({self.budget})")
        ledger_path = self.cache_dir / self.ledger_name
        ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {"real_calls": 0, "attempts": []}
        if self.call_cap is not None and ledger["real_calls"] >= self.call_cap:
            raise RuntimeError(f"SerpApi search cap reached ({self.call_cap})")
        ledger["real_calls"] += 1
        ledger["attempts"].append({"engine": params.get("engine"), "query": params.get("q") or params.get("search_query"), "location": params.get("location")})
        _write_json(ledger_path, ledger)  # Count first: timeouts may consume credit.
        self.live_calls += 1
        self.replay.append({"query": dict(params), "source": "live"})
        data = stamp_response(_request("search.json", params, self.key or _load_key()), fresh=True)
        _write_json(path, data)
        return data

    def account(self, label: str) -> dict:
        data = _request("account.json", {}, self.key or _load_key())
        _write_json(self.cache_dir / f"account_{label}.json", data)
        return {k: data.get(k) for k in ("this_month_usage", "total_searches_left", "plan_searches_left")}


class FetchedJobs(list):
    """Merged listings that retain the pre-deduplication count for reporting."""

    def __init__(self, jobs: list[dict], raw_count: int):
        super().__init__(jobs)
        self.raw_count = raw_count


def safe_account(client: SerpClient, label: str) -> dict | None:
    """Account telemetry must never discard a search result."""
    try:
        return client.account(label)
    except (RuntimeError, OSError, ValueError):
        return None


def _check_error(data: dict) -> None:
    error = str(data.get("error") or "")
    if error and "hasn't returned any results" not in error.lower():
        raise RuntimeError("SerpApi returned a search error")


def fresher_queries(role: str, experience_level: str | None) -> list[tuple[str, str]]:
    base = role.strip()
    queries = [(base, "Base role")]
    if experience_level == "Fresher":
        queries.extend([(f"{base} fresher", "Fresher variant"),
                        (f"Junior {base}", "Junior variant")])
        if "intern" in base.lower():
            queries.append((f"{base} intern", "Intern variant"))
    return queries


def max_live_requests(role: str, pages: int, experience_level: str | None, include_hindi: bool = False,
                      learning_limit: int = 3) -> int:
    """Upper bound on new searches for one run; cached responses cost nothing."""
    job_searches = pages + len(fresher_queries(role, experience_level)) - 1
    # Course lengths for the shortlisted skills plus the two-skill plan.
    course_searches = (learning_limit + 2) * (2 if include_hindi else 1)
    return job_searches + course_searches


def fetch_jobs(role: str, city: str, pages: int = 3, client: SerpClient | None = None,
               experience_level: str | None = None) -> list[dict]:
    if not 1 <= pages <= 3:
        raise ValueError("pages must be 1 to 3")
    client = client or SerpClient()
    params = {"engine": "google_jobs", "location": f"{city.strip()}, India", "gl": "in", "hl": "en"}
    jobs = []
    for search_term, variant in fresher_queries(role, experience_level):
        token = None
        search_pages = pages if variant == "Base role" else 1
        for page in range(1, search_pages + 1):
            query = {**params, "q": search_term, **({"next_page_token": token} if token else {})}
            try:
                data = client.search(query, page=page)
            except BudgetExceeded:
                # Keep the listings already fetched rather than failing the whole search.
                return FetchedJobs(deduplicate(jobs), len(jobs))
            _check_error(data)
            batch = data.get("jobs_results") or []
            if client.replay:
                client.replay[-1].update({"variant": variant, "listing_count": len(batch)})
            retrieved = stamp_response(data).get("_retrieved_at")
            jobs.extend({**job, "_search_queries": [search_term], "_retrieved_at": retrieved} for job in batch)
            token = (data.get("serpapi_pagination") or {}).get("next_page_token")
            if not token:
                break
    return FetchedJobs(deduplicate(jobs), len(jobs))


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def deduplicate(jobs: list[dict]) -> list[dict]:
    unique = []
    for job in jobs:
        company = normalize(str(job.get("company_name") or ""))
        title = normalize(str(job.get("title") or ""))
        duplicate = next((old for old in unique if company and company == normalize(str(old.get("company_name") or "")) and
                          SequenceMatcher(None, title, normalize(str(old.get("title") or ""))).ratio() >= 0.86), None)
        if duplicate is not None:
            duplicate["_search_queries"] = list(dict.fromkeys([*(duplicate.get("_search_queries") or []), *(job.get("_search_queries") or [])]))
            continue
        unique.append(dict(job))
    return unique


def posted_text(job: dict) -> str:
    detected = (job.get("detected_extensions") or {}).get("posted_at")
    if detected:
        return str(detected)
    for extension in job.get("extensions") or []:
        value = str(extension)
        if re.search(r"\b(?:\d+\s+(?:seconds?|minutes?|hours?|days?|weeks?|months?|years?)\s+ago|today|yesterday|just now)\b", value, re.I):
            return value
    return "unknown"


def age_days(posted: str) -> float | None:
    text = posted.lower()
    if "yesterday" in text:
        return 1
    if any(x in text for x in ("today", "just now", "hour", "minute", "second")):
        return 0
    match = re.search(r"\b(\d+)\s+(day|week|month|year)s?\s+ago\b", text)
    if match:
        return int(match.group(1)) * {"day": 1, "week": 7, "month": 30.44, "year": 365}[match.group(2)]
    return None


def listing_age_days(job: dict, today: date | None = None) -> float | None:
    age = age_days(posted_text(job))
    retrieved = retrieval_date(job)
    if age is not None and retrieved is not None:
        age += max(0, ((today or datetime.now(timezone.utc).date()) - retrieved).days)
    return age


def is_old(job: dict, today: date | None = None) -> bool:
    age = listing_age_days(job, today)
    return age is not None and age > 30


EXPERIENCE_NUMBER = re.compile(r"(?<![\w.])(\d{1,2})(?:\.(\d))?\s*(?:(?:[-–—]|to)\s*\d{1,2}(?:\.\d)?\s*|\+\s*)?(?:years?|yrs?)\b", re.I)
EXPERIENCE_LOST_RANGE = re.compile(r"(?<!\d)(\d{1,2})\s+(\d{1,2})\s*(?:years?|yrs?)\b", re.I)
EXPERIENCE_CANDIDATE = re.compile(r"\b(?:experience|experienced|minimum|min\.?|at least|must have|required|requirements?|qualifications?|eligibility|hands.on|overall|industry|professional|working|development|engineering|coding)\b", re.I)
EXPERIENCE_SUBJECT = re.compile(r"\b(?:company|organisation|organization|firm|agency|brand|business|platform|provider|product|warranty|guarantee|legacy|history)\b", re.I)
EXPERIENCE_ACTIVITY = re.compile(r"\b(?:of|in|with)\s+(?:hands.on\s+)?(?:experience|development|engineering|coding|industry|professional|working)\b", re.I)
SENIOR_TITLE = re.compile(r"\b(?:principal|lead|manager|senior|sr\.?)\b", re.I)


def experience_evidence(job: dict) -> tuple[int, str]:
    """Return minimum candidate years and the exact title/description phrase supporting it."""
    title = str(job.get("title") or "")
    description = str(job.get("description") or "")
    evidence: list[tuple[int, str]] = []
    lost_ranges = []
    for match in EXPERIENCE_LOST_RANGE.finditer(description):
        lower, upper = int(match.group(1)), int(match.group(2))
        if lower < upper <= 15 and EXPERIENCE_CANDIDATE.search(description[max(0, match.start() - 65):match.start()] + description[match.end():match.end() + 40]):
            evidence.append((lower, match.group(0)))
            lost_ranges.append(match.span())
    for match in EXPERIENCE_NUMBER.finditer(description):
        if any(start <= match.start() and match.end() <= end for start, end in lost_ranges):
            continue
        years = int(match.group(1)) + bool(match.group(2) and int(match.group(2)) > 0)
        if years > 15:  # Implausible as an individual minimum; often a lost range hyphen.
            continue
        left = description[max(0, match.start() - 90):match.start()]
        right = description[match.end():match.end() + 55]
        # Keep company history and product guarantees out of candidate requirements.
        if re.search(r"\b(?:company|organisation|organization|firm|agency|brand|business|platform|provider|product|warranty|guarantee)\b[^.!?\n]{0,55}\b(?:with|has|having|over|more than|offers?)\s*$", left, re.I):
            continue
        if EXPERIENCE_SUBJECT.search(left[-35:] + match.group(0) + right[:35]) and not re.search(r"\b(?:candidate|applicant|you|your|role)\b", left[-50:], re.I):
            continue
        # A bare number in a metadata header is useful only when it is marked as experience.
        prefix = re.search(r"(?:\b(?:experience|minimum|min\.?|at least|overall|ideal experience)\s*[:\-]?\s*)$", left[-35:], re.I)
        strong = bool(prefix or EXPERIENCE_ACTIVITY.search(right[:40]) or
                      re.search(r"\b(?:hands.on|industry|professional)\s+(?:experience\s*)?$", left[-35:], re.I) or
                      re.search(r"(?:\+|[-–—]|\bto\b)", match.group(0)))
        section = bool(EXPERIENCE_CANDIDATE.search(left[-60:]))
        if not (strong or section):
            continue
        phrase_start = match.start() - len(prefix.group(0)) if prefix else match.start()
        phrase_end = match.end()
        suffix = EXPERIENCE_ACTIVITY.match(right)
        if suffix:
            phrase_end += suffix.end()
        evidence.append((years, description[phrase_start:phrase_end].strip()))
    if evidence:
        return max(evidence, key=lambda item: item[0])
    for entry in re.finditer(r"\b(?:freshers?\s+(?:welcome|can apply|may apply|eligible)|"
                             r"no\s+(?:prior\s+)?experience\s+(?:is\s+)?(?:required|needed|necessary)|"
                             r"experience\s*:\s*fresher|entry[ -]level)\b", description, re.I):
        if not re.search(r"\b(?:no|not)\s+(?:an?\s+)?$", description[max(0, entry.start() - 20):entry.start()], re.I):
            return 0, entry.group(0)
    title_match = SENIOR_TITLE.search(title)
    if title_match:
        word = title_match.group(0).lower()
        floor = 8 if word == "principal" else 5 if word in {"lead", "manager"} else 3
        return floor, title_match.group(0)
    return 0, "no minimum detected"


def experience_required(job: dict) -> tuple[int, str]:
    years, phrase = experience_evidence(job)
    return years, (f"at least {years} years — {phrase}" if years else "no minimum detected")


def canonical_manual_skills(text: str) -> set[str]:
    """Accept exact canonical names and aliases, plus natural language lists."""
    result = extract_skills(text, resume=True)
    for item in re.finditer(r"[^,;\n]+", text):
        value = item.group().strip().casefold()
        if not value or negated_mention(text, item.start(), item.end()):
            continue
        for skill in VOCABULARY:
            if value == skill.casefold() or value in {alias.casefold() for alias in ALIASES.get(skill, [])}:
                result.add(skill)
                break
    return result


# "A, B or C" is a choice only between interchangeable tools of one kind.
SKILL_FAMILIES = {"BI tools": {"Power BI", "Tableau", "Looker"},
                  "frontend frameworks": {"React", "Angular", "Vue.js", "Next.js"},
                  "cloud providers": {"AWS", "Azure", "Google Cloud"},
                  "databases": {"MySQL", "PostgreSQL", "MongoDB", "Oracle Database", "SQL Server", "Redis", "NoSQL"}}


def same_family(skills: set[str]) -> bool:
    return any(skills <= members for members in SKILL_FAMILIES.values())


def requirements_from_text(text: str) -> set[frozenset[str]]:
    """Only an explicit or/slash chain makes skills interchangeable in a listing."""
    return set(_requirements_from_text(text or ""))


@lru_cache(maxsize=8192)
def _requirements_from_text(text: str) -> frozenset[frozenset[str]]:
    # Skills marked as a plus or nice to have are preferred, not requirements.
    mentions = [mention for mention in skill_mentions(text) if not preferred_mention(text, mention[1], mention[2])]
    requirements = set()
    # Split mentions into comma, slash or "or" separated lists.
    lists = []
    previous_end = None
    for skill, start, end in mentions:
        joiner = None if previous_end is None else text[previous_end:start]
        if joiner is not None and re.fullmatch(r"\s*/\s*", joiner):
            lists[-1].append(("/", skill))
        elif joiner is not None and re.fullmatch(r"\s*,?\s*\bor\b\s*", joiner, re.I):
            lists[-1].append(("or", skill))
        elif joiner is not None and re.fullmatch(r"\s*,\s*", joiner):
            lists[-1].append((",", skill))
        else:
            lists.append([(None, skill)])
        previous_end = end
    for items in lists:
        # "A, B, or C" is one choice only for three tools of the same family;
        # longer or mixed lists such as "HTML, CSS, JavaScript or React" stay separate.
        # A slash ("JavaScript/TypeScript") is always an explicit choice.
        if len(items) > 2 and items[-1][0] == "or" and any(joiner == "," for joiner, _ in items):
            skills = {skill for _, skill in items}
            if len(items) == 3 and same_family(skills):
                requirements.add(frozenset(skills))
            else:
                requirements.update(frozenset({skill}) for skill in skills)
            continue
        group = set()
        for joiner, skill in items:
            if joiner in {"or", "/"}:
                group.add(skill)
            else:
                if group:
                    requirements.add(frozenset(group))
                group = {skill}
        requirements.add(frozenset(group))
    return frozenset(requirements)


def coverage(required: set[str] | set[frozenset[str]], user: set[str]) -> float:
    return sum(bool((req if isinstance(req, frozenset) else {req}) & user) for req in required) / len(required) if required else 0.0


def stated_must_haves(text: str) -> set[frozenset[str]]:
    """Conservative sentence-level explicit requirements, independent of market frequency."""
    result = set()
    for segment in _BOUNDARY.split(text or ""):
        if re.search(r"\b(?:must|mandatory|required|essential|minimum)\b", segment, re.I):
            if re.search(r"\b(?:not|no)\s+(?:mandatory|required|essential)\b", segment, re.I):
                continue
            result.update(requirements_from_text(segment))
    return result


def must_have_status(required: set[frozenset[str]], user: set[str]) -> str:
    return "none stated" if not required else "yes" if all(req & user for req in required) else "no"


def listing_confidence(count: int) -> str:
    return "High" if count >= 25 else "Medium" if count >= 12 else "Low"


def display_option(skill: str, members: frozenset[str]) -> str:
    return f"{skill} (or {' / '.join(sorted(members - {skill}))})" if len(members) > 1 else skill


def dictionary_coverage_warning(jobs: list[dict]) -> tuple[bool, float]:
    counts = [len(extract_skills(str(job.get("description") or ""))) for job in jobs]
    median = float(statistics.median(counts)) if counts else 0.0
    return bool(counts) and median < 3, median


def parse_duration(value: object) -> float | None:
    """Return hours from YouTube M:SS or H:MM:SS; reject live/malformed lengths."""
    if not isinstance(value, str) or not re.fullmatch(r"\d{1,3}:\d{2}(?::\d{2})?", value):
        return None
    parts = [int(x) for x in value.split(":")]
    if any(x >= 60 for x in parts[1:]):
        return None
    seconds = parts[0] * 60 + parts[1] if len(parts) == 2 else parts[0] * 3600 + parts[1] * 60 + parts[2]
    return seconds / 3600


VIDEO_LANGUAGES = {
    "english": r"english|अंग्रेजी",
    "hindi": r"hindi|हिंदी|हिन्दी",
    "tamil": r"tamil|தமிழ்", "telugu": r"telugu|తెలుగు",
    "kannada": r"kannada|ಕನ್ನಡ", "malayalam": r"malayalam|മലയാളം",
    "bengali": r"bengali|bangla|বাংলা", "marathi": r"marathi|मराठी",
    "gujarati": r"gujarati|ગુજરાતી", "punjabi": r"punjabi|ਪੰਜਾਬੀ",
    "odia": r"odia|oriya|ଓଡ଼ିଆ", "assamese": r"assamese|অসমীয়া",
    "urdu": r"urdu|اردو", "nepali": r"nepali|नेपाली", "bhojpuri": r"bhojpuri|भोजपुरी",
    "spanish": r"spanish|español", "french": r"french|français",
    "german": r"german|deutsch", "portuguese": r"portuguese|português",
    "russian": r"russian|русский", "arabic": r"arabic|العربية",
    "japanese": r"japanese|日本語", "korean": r"korean|한국어",
    "chinese": r"chinese|中文", "indonesian": r"indonesian|bahasa indonesia",
}


def indicated_languages(text: str) -> set[str]:
    return {language for language, pattern in VIDEO_LANGUAGES.items()
            if re.search(r"(?<!\w)(?:" + pattern + r")(?!\w)", text, re.I)}


def select_course_videos(results: list[dict], query: str,
                         requested_languages: set[str] | None = None) -> tuple[float | None, list[dict], str]:
    """Prefer named full courses >=1h; weaker >=30m fallback is labelled."""
    parsed = []
    allowed = requested_languages if requested_languages is not None else {"english"} | indicated_languages(query)
    for item in results:
        hours = parse_duration(item.get("length"))
        if hours is None:
            continue
        channel = item.get("channel") or {}
        channel_name = str(channel.get("name") or "") if isinstance(channel, dict) else str(channel)
        title = item.get("title") or "untitled"
        if indicated_languages(title + " " + channel_name) - allowed:
            continue
        parsed.append({"title": title, "channel": channel_name,
                       "duration": item.get("length"), "hours": hours, "link": item.get("link") or "", "language_query": query})
    primary = [video for video in parsed if video["hours"] >= 1 and COURSE_TITLE.search(video["title"])]
    if len(primary) >= 2:
        chosen, confidence = primary[:3], "standard"
    else:
        chosen, confidence = [video for video in parsed if video["hours"] >= .5][:3], "low"
    hours = statistics.median(video["hours"] for video in chosen) if chosen else None
    return hours, chosen, confidence


def course_videos(skill: str, client: SerpClient, include_hindi: bool = False) -> tuple[float | None, list[dict], str]:
    queries = [f"{skill} full course for beginners"]
    if include_hindi:
        queries.append(f"{skill} tutorial in Hindi")
    results = []
    for query in queries:
        try:
            data = client.search({"engine": "youtube", "search_query": query, "gl": "in", "hl": "en", "sp": LONG_VIDEO_SP})
        except BudgetExceeded:
            if not results:
                return None, [], "budget"
            break
        _check_error(data)
        results.extend(data.get("video_results") or [])
    return select_course_videos(results, ", ".join(queries), {"english", "hindi"} if include_hindi else {"english"})


def select_core_skills(jobs: list[dict], share: float = 0.25) -> set[str]:
    if not 0 < share <= 1:
        raise ValueError("core skill share must be between 0 and 1")
    if not jobs:
        return set()
    counts = Counter(req for job in jobs for req in requirements_from_text(str(job.get("description") or "")))
    return set().union(*(req for req, count in counts.items() if count / len(jobs) >= share)) if counts else set()


def analyze_jobs(jobs: list[dict], user_skills: set[str], threshold: float = DEFAULT_THRESHOLD,
                 exclude_old: bool = False, core_share: float = 0.25,
                 experience_level: str | None = None) -> dict:
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")
    raw_count = getattr(jobs, "raw_count", len(jobs))
    unique = deduplicate(jobs)
    if exclude_old:
        unique = [job for job in unique if not is_old(job)]
    all_listings = unique.copy()
    if experience_level is not None and experience_level not in EXPERIENCE_LEVELS:
        raise ValueError("unknown experience level")
    experience_excluded = []
    if experience_level is not None:
        limit = EXPERIENCE_LEVELS[experience_level]
        for job in unique:
            years, phrase = experience_evidence(job)
            if years > limit:
                experience_excluded.append({"job": job, "minimum_years": years,
                                            "reason": f"at least {years} years — {phrase}", "phrase": phrase})
        excluded_ids = {id(row["job"]) for row in experience_excluded}
        unique = [job for job in unique if id(job) not in excluded_ids]
    core = select_core_skills(unique, core_share)
    dictionary_warning, median_skills = dictionary_coverage_warning(unique)
    usable = []
    ignored = 0
    for job in unique:
        all_skills = extract_skills(str(job.get("description") or ""))
        required = {req for req in requirements_from_text(str(job.get("description") or "")) if req & core}
        if not required:
            ignored += 1
            continue
        mandatory = stated_must_haves(str(job.get("description") or ""))
        usable.append({"job": job, "required_skills": required, "nice_to_have": all_skills - core,
                       "must_haves": mandatory, "must_haves_status": must_have_status(mandatory, user_skills),
                       "coverage": coverage(required, user_skills)})
    ready = [entry for entry in usable if entry["coverage"] >= threshold]
    demand = Counter(skill for entry in usable for skill in extract_skills(str(entry["job"].get("description") or "")))
    options = {req for entry in usable for req in entry["required_skills"] if not req & user_skills}
    representatives = {req: max(req, key=lambda skill: (demand[skill], SUBSTITUTE_PREFERENCE.get(skill, 0), skill)) for req in options}
    option_members = {}
    for req, name in representatives.items():
        option_members[name] = option_members.get(name, frozenset()) | req
    display_members = {}
    for name in option_members:
        matching = {req for entry in usable for req in entry["required_skills"] if name in req}
        display_members[name] = next(iter(matching)) if len(matching) == 1 else frozenset({name})
    counts = Counter({name: sum(any(name in req for req in entry["required_skills"]) for entry in usable)
                      for name in option_members})
    unlocked = {}
    for skill, members in option_members.items():
        gained = [entry["job"] for entry in usable if entry["coverage"] < threshold and coverage(entry["required_skills"], user_skills | {skill}) >= threshold]
        unlocked[skill] = gained
    recommendable = {skill for skill in option_members if skill not in GENERIC}
    candidates = sorted((skill for skill in recommendable if unlocked[skill]), key=lambda skill: (-len(unlocked[skill]), -counts[skill], skill))
    top8 = sorted(recommendable, key=lambda skill: (-len(unlocked[skill]), -counts[skill], skill))[:8]
    pair_options = []
    for first, second in itertools.combinations(top8, 2):
        if all((first in req) == (second in req) for entry in usable for req in entry["required_skills"]):
            continue
        gained = [entry["job"] for entry in usable if entry["coverage"] < threshold and coverage(entry["required_skills"], user_skills | {first, second}) >= threshold]
        pair_options.append((first, second, gained))
    pair = max(pair_options, key=lambda row: (len(row[2]), len(unlocked[row[0]]) + len(unlocked[row[1]]), row[0], row[1])) if pair_options else None
    return {"raw": raw_count, "deduplicated": len(unique) + len(experience_excluded), "limited_data": len(unique) < 12,
            "eligible_count": len(unique), "listing_confidence": listing_confidence(len(unique)),
            "dictionary_warning": dictionary_warning, "median_detected_skills": median_skills,
            "experience_excluded": experience_excluded, "experience_level": experience_level,
            "all_listings": all_listings,
            "jobs": usable, "ready": len(ready), "ignored": ignored, "core_skills": core, "core_share": core_share,
            "must_haves_met": sum(row["must_haves_status"] == "yes" for row in ready),
            "must_haves_none": sum(row["must_haves_status"] == "none stated" for row in ready),
            "skill_counts": counts, "unlocked": unlocked, "candidates": candidates, "pair": pair,
            "option_members": option_members, "display_members": display_members,
            "eligible_jobs": unique, "user_skills_set": user_skills,
            "threshold": threshold}


def has_role_fit_warning(analysis: dict) -> bool:
    jobs = analysis.get("jobs") or []
    return bool(jobs) and sum(entry["coverage"] < .2 for entry in jobs) > len(jobs) / 2


def no_unlock_message(analysis: dict) -> str:
    if not analysis.get("candidates") and analysis.get("jobs") and analysis.get("ready", 0) > len(analysis["jobs"]) / 2:
        return MOSTLY_READY_MESSAGE
    return "No one-skill unlocks found for this search and threshold. Try a different threshold or role."


def rank_skills(analysis: dict, client: SerpClient, include_hindi: bool = False, learning_limit: int = 5) -> list[dict]:
    ranked = []
    saved = SerpClient(use_fixtures=client.use_fixtures, cache_only=True, cache_dir=client.cache_dir)
    for index, skill in enumerate(analysis["candidates"]):
        # Limit new searches, never the ranking of already measured candidates.
        source = client if index < learning_limit else saved
        hours, videos, confidence = course_videos(skill, source, include_hindi)
        if hours is None and client.budget_reached:
            confidence = "budget"
        unlocked = len(analysis["unlocked"][skill])
        ranked.append({"skill": skill, "unlocked_count": unlocked, "unlocked_jobs": analysis["unlocked"][skill], "appears_in": analysis["skill_counts"][skill], "hours": hours, "confidence": confidence, "score": unlocked / hours if hours else None, "videos": videos})
        members = analysis.get("display_members", {}).get(skill, frozenset({skill}))
        ranked[-1]["display_skill"] = display_option(skill, members)
    return sorted(ranked, key=lambda row: (row["score"] is None, -(row["score"] or 0), -row["unlocked_count"], row["skill"]))


def headline_picks(ranked: list[dict]) -> dict:
    """Fastest win is the best jobs per hour; biggest unlock ignores hours."""
    fastest = next((row for row in ranked if row["score"] is not None), None)
    biggest = min(ranked, key=lambda row: (-row["unlocked_count"], row["score"] is None,
                                           -(row["score"] or 0), row["skill"])) if ranked else None
    return {"fastest": fastest, "biggest": biggest,
            "same": fastest is not None and biggest is not None and fastest["skill"] == biggest["skill"]}


def two_skill_plan(analysis: dict, hours_by_skill: dict[str, float | None] | None = None,
                   videos_by_skill: dict[str, list[dict]] | None = None) -> dict | None:
    pair = analysis.get("pair")
    if not pair or not pair[2]:
        return None
    first, second, jobs = pair
    hours_by_skill = hours_by_skill or {}
    first_hours, second_hours = hours_by_skill.get(first), hours_by_skill.get(second)
    combined = first_hours + second_hours if first_hours is not None and second_hours is not None else None
    return {"skills": (first, second), "unlocked_count": len(jobs), "unlocked_jobs": jobs,
            "hours": combined, "score": len(jobs) / combined if combined else None,
            "display_skills": tuple(display_option(skill, analysis.get("display_members", {}).get(skill, frozenset({skill})))
                                    for skill in (first, second)),
            "source_videos": {skill: (videos_by_skill or {}).get(skill, []) for skill in (first, second)}}


def hours_range(hours: float | None) -> str:
    if hours is None:
        return "Unavailable"
    low = max(1, math.floor(hours * .75))
    high = max(low + 1, math.ceil(hours * 1.25))
    return f"~{low}–{high} hours"


def _ready_indices(analysis: dict, added: set[str]) -> set[int]:
    owned = analysis["user_skills_set"] | added
    return {index for index, row in enumerate(analysis["jobs"])
            if coverage(row["required_skills"], owned) >= analysis["threshold"]}


def greedy_opportunity(analysis: dict, hours_by_skill: dict[str, float | None],
                       budget: float | None = None, max_skills: int = 5) -> list[dict]:
    """Choose the best marginal jobs/hour until no positive gain remains."""
    available = {skill: value for skill, value in hours_by_skill.items()
                 if skill in analysis["option_members"] and skill not in GENERIC and value and value > 0}
    chosen: set[str] = set()
    ready = _ready_indices(analysis, chosen)
    spent = 0.0
    steps = []
    for _ in range(max_skills):
        options = []
        for skill, skill_hours in available.items():
            if skill in chosen or (budget is not None and spent + skill_hours > budget + 1e-9):
                continue
            gained = _ready_indices(analysis, chosen | {skill}) - ready
            if gained:
                options.append((skill, skill_hours, gained))
        if not options:
            break
        skill, skill_hours, gained = min(options, key=lambda row: (-len(row[2]) / row[1], -len(row[2]), row[1], row[0]))
        chosen.add(skill)
        spent += skill_hours
        ready |= gained
        steps.append({"step": len(steps) + 1, "skill": skill, "hours": skill_hours,
                      "cumulative_hours": spent, "jobs_gained": len(gained), "total_jobs": len(ready)})
    return steps


def exact_opportunity(analysis: dict, hours_by_skill: dict[str, float | None],
                      budget: float, top_n: int = 8) -> dict:
    """Exhaust all subsets of the top measurable missing skills for a budget."""
    candidates = sorted((skill for skill, hours in hours_by_skill.items()
                         if skill in analysis["option_members"] and skill not in GENERIC and hours and hours > 0),
                        key=lambda skill: (-len(analysis["unlocked"].get(skill, [])),
                                           -analysis["skill_counts"].get(skill, 0), skill))[:top_n]
    baseline = _ready_indices(analysis, set())
    best = {"skills": (), "hours": 0.0, "jobs_gained": 0, "total_jobs": len(baseline), "candidates": candidates}
    for size in range(1, len(candidates) + 1):
        for subset in itertools.combinations(candidates, size):
            spent = sum(hours_by_skill[skill] for skill in subset)
            if spent > budget + 1e-9:
                continue
            ready = _ready_indices(analysis, set(subset))
            gained = len(ready - baseline)
            if gained > best["jobs_gained"] or (gained == best["jobs_gained"] and spent < best["hours"]):
                best = {"skills": subset, "hours": spent, "jobs_gained": gained,
                        "total_jobs": len(ready), "candidates": candidates}
    return best


def opportunity_quality(analysis: dict, hours_by_skill: dict[str, float | None],
                        budgets: tuple[int, ...] = (5, 10, 15)) -> list[dict]:
    rows = []
    for budget in budgets:
        optimum = exact_opportunity(analysis, hours_by_skill, budget)
        candidate_hours = {skill: hours_by_skill[skill] for skill in optimum["candidates"]}
        greedy = greedy_opportunity(analysis, candidate_hours, budget)
        greedy_gained = (greedy[-1]["total_jobs"] - analysis["ready"]) if greedy else 0
        optimal_gained = optimum["jobs_gained"]
        rows.append({"budget": budget, "greedy_gained": greedy_gained,
                     "optimal_gained": optimal_gained,
                     "ratio": greedy_gained / optimal_gained if optimal_gained else None,
                     "greedy_skills": [step["skill"] for step in greedy],
                     "optimal_skills": list(optimum["skills"]),
                     "candidate_count": len(optimum["candidates"])})
    return rows


def skill_distance(analysis: dict) -> dict:
    """Minimum added skills to cross the selected readiness threshold, capped at 3+."""
    counts = {"0": 0, "1": 0, "2": 0, "3+": 0, "Unknown": analysis["ignored"]}
    one_away: dict[str, list[dict]] = {}
    user = analysis["user_skills_set"]
    for row in analysis["jobs"]:
        requirements = row["required_skills"]
        if row["coverage"] >= analysis["threshold"]:
            counts["0"] += 1
            continue
        missing = set().union(*(req for req in requirements if not req & user))
        singles = {skill for skill in missing if coverage(requirements, user | {skill}) >= analysis["threshold"]}
        if singles:
            counts["1"] += 1
            display_skills = [skill for skill in analysis["option_members"] if skill in singles and skill not in GENERIC]
            if not display_skills:
                one_away.setdefault("Other core requirement", []).append(row["job"])
            else:
                for skill in sorted(display_skills):
                    label = display_option(skill, analysis["display_members"].get(skill, frozenset({skill})))
                    one_away.setdefault(label, []).append(row["job"])
            continue
        if any(coverage(requirements, user | set(pair)) >= analysis["threshold"]
               for pair in itertools.combinations(sorted(missing), 2)):
            counts["2"] += 1
        else:
            counts["3+"] += 1
    return {"counts": counts, "one_away": one_away}


@lru_cache(maxsize=64)
def _bootstrap_cached(snapshot: tuple, user_skills: tuple[str, ...], measured_hours: tuple,
                      threshold: float, core_share: float, samples: int, seed: int,
                      learning_limit: int) -> tuple[tuple[str, int], ...]:
    """Resample pre-extracted eligible jobs; no regex or network work inside the loop."""
    if not snapshot:
        return (("No scored pick", samples),)
    prepared = [(frozenset(frozenset(req) for req in requirements), frozenset(skills))
                for requirements, skills in snapshot]
    user = frozenset(user_skills)
    hours = dict(measured_hours)
    randomizer = random.Random(seed)
    winners = Counter()
    size = len(prepared)
    for _ in range(samples):
        sampled = [prepared[randomizer.randrange(size)] for _ in range(size)]
        req_counts = Counter(req for requirements, _ in sampled for req in requirements)
        core = set().union(*(req for req, count in req_counts.items() if count / size >= core_share)) if req_counts else set()
        usable = [(frozenset(req for req in requirements if req & core), skills) for requirements, skills in sampled]
        usable = [(requirements, skills) for requirements, skills in usable if requirements]
        demand = Counter(skill for _, skills in usable for skill in skills)
        options = {req for requirements, _ in usable for req in requirements if not req & user}
        representatives = {req: max(req, key=lambda skill: (demand[skill], SUBSTITUTE_PREFERENCE.get(skill, 0), skill))
                           for req in options}
        names = set(representatives.values()) - GENERIC
        results = []
        for skill in names:
            unlocked = sum(coverage(requirements, user) < threshold and
                           coverage(requirements, user | {skill}) >= threshold for requirements, _ in usable)
            if not unlocked:
                continue
            appears = sum(any(skill in req for req in requirements) for requirements, _ in usable)
            results.append((skill, unlocked, appears))
        # Match the product rule: shortlist by unlocked count, then rank by jobs/hour.
        scored = [row for row in results if hours.get(row[0])]
        winner = min(scored, key=lambda row: (-row[1] / hours[row[0]], -row[1], row[0]))[0] if scored else "No scored pick"
        winners[winner] += 1
    return tuple(sorted(winners.items(), key=lambda row: (-row[1], row[0])))


def confidence_label(share: float, robustness_share: float | None = None) -> str:
    if robustness_share is not None:
        share = min(share, robustness_share)
    return "Strong" if share >= .85 else "Likely" if share >= .60 else "Uncertain"


def bootstrap_confidence(analysis: dict, hours_by_skill: dict[str, float | None],
                         top_skill: str | None, samples: int = 500, seed: int = 2026,
                         learning_limit: int = 5) -> dict:
    """Share of bootstrap resamples won by each skill; cached by data and inputs."""
    snapshot = tuple((tuple(sorted(tuple(sorted(req)) for req in requirements_from_text(str(job.get("description") or "")))),
                      tuple(sorted(extract_skills(str(job.get("description") or "")))))
                     for job in analysis["eligible_jobs"])
    measured = tuple(sorted((skill, value) for skill, value in hours_by_skill.items() if value and value > 0))
    wins = dict(_bootstrap_cached(snapshot, tuple(sorted(analysis["user_skills_set"])), measured,
                                  analysis["threshold"], analysis["core_share"], samples, seed, learning_limit))
    share = wins.get(top_skill, 0) / samples if top_skill else 0.0
    label = confidence_label(share)
    return {"wins": wins, "shares": {skill: count / samples for skill, count in wins.items()},
            "top_skill": top_skill, "top_share": share, "samples": samples,
            "label": label}


def assess_robustness(jobs: list[dict], user_skills: set[str], top_skill: str | None,
                      hours_by_skill: dict[str, float | None], exclude_old: bool = False,
                      core_share: float = .25, experience_level: str | None = None,
                      base_threshold: float = .5, samples: int = 500, seed: int = 2026,
                      learning_limit: int = 5) -> dict:
    """Independently perturb each measured skill's hours across threshold settings."""
    if samples < 1:
        raise ValueError("samples must be positive")
    randomizer = random.Random(seed)
    measured = sorted(skill for skill, hours in hours_by_skill.items() if hours and hours > 0)
    draws = [{skill: hours_by_skill[skill] * randomizer.uniform(.75, 1.5) for skill in measured}
             for _ in range(samples)]
    changes = []
    wins = Counter()
    by_threshold = []
    for threshold in sorted({.4, .5, .6, round(base_threshold, 10)}):
        analysis = analyze_jobs(jobs, user_skills, threshold, exclude_old, core_share, experience_level)
        candidates = [skill for skill in analysis["candidates"] if skill in measured]
        counts = {skill: len(analysis["unlocked"][skill]) for skill in candidates}
        local = Counter()
        for hours in draws:
            winner = min(candidates, key=lambda skill: (-counts[skill] / hours[skill], -counts[skill], skill)) if candidates else "No scored pick"
            local[winner] += 1
        wins.update(local)
        share = local.get(top_skill, 0) / samples if top_skill else 0.0
        by_threshold.append({"threshold": threshold, "top_share": share, "wins": dict(sorted(local.items()))})
        if share < 1:
            alternatives = ", ".join(f"{skill}: {count / samples:.1%}" for skill, count in sorted(local.items()) if skill != top_skill)
            changes.append(f"Threshold {threshold:g}: top pick retained {share:.1%}; {alternatives}")
    total = samples * len(by_threshold)
    return {"label": "Changes with settings" if changes else "Consistent across checked settings", "changes": changes,
            "top_share": wins.get(top_skill, 0) / total if top_skill else 0.0, "wins": dict(sorted(wins.items())),
            "samples": total, "draws_per_threshold": samples, "by_threshold": by_threshold, "seed": seed}


def run(role: str, city: str, resume: str = "", manual_skills: str = "", threshold: float = DEFAULT_THRESHOLD,
        include_hindi: bool = False, exclude_old: bool = False, pages: int = 3, offline: bool = False,
        client: SerpClient | None = None, core_share: float = 0.25, learning_limit: int = 5,
        experience_level: str | None = None) -> dict:
    client = client or SerpClient(offline=offline)
    jobs = fetch_jobs(role, city, pages=pages, client=client, experience_level=experience_level)
    user = extract_skills(resume, resume=True) | canonical_manual_skills(manual_skills)
    analysis = analyze_jobs(jobs, user, threshold, exclude_old, core_share, experience_level)
    ranked = rank_skills(analysis, client, include_hindi, learning_limit)
    hours = {row["skill"]: row["hours"] for row in ranked}
    videos = {row["skill"]: row["videos"] for row in ranked}
    pair = analysis.get("pair")
    if pair:
        for skill in pair[:2]:
            if skill not in hours:
                hours[skill], videos[skill], _ = course_videos(skill, client, include_hindi)
    # Cached-only duration lookups for alternative threshold candidates never spend credits.
    cached_client = SerpClient(use_fixtures=client.use_fixtures, cache_only=True, cache_dir=client.cache_dir)
    for tested_threshold in (.4, .5, .6):
        variant = analyze_jobs(jobs, user, tested_threshold, exclude_old, core_share, experience_level)
        for skill in variant["candidates"]:
            if skill not in hours:
                hours[skill], _, _ = course_videos(skill, cached_client, include_hindi)
    for skill in analysis["option_members"]:
        if skill not in GENERIC and skill not in hours:
            hours[skill], _, _ = course_videos(skill, cached_client, include_hindi)
    top_skill = ranked[0]["skill"] if ranked and ranked[0]["score"] is not None else None
    threshold_check = assess_robustness(jobs, user, top_skill, hours, exclude_old,
                                        core_share, experience_level, threshold, learning_limit=learning_limit)
    bootstrap = bootstrap_confidence(analysis, hours, top_skill, learning_limit=learning_limit)
    opportunity = {"steps": greedy_opportunity(analysis, hours),
                   "quality": opportunity_quality(analysis, hours),
                   "hours_unknown": sorted(skill for skill in analysis["option_members"]
                                           if skill not in GENERIC and not hours.get(skill))}
    distances = skill_distance(analysis)
    analysis.update({"role": role, "city": city, "user_skills": sorted(user), "ranked": ranked,
                     "two_skill_plan": two_skill_plan(analysis, hours, videos), "replay": client.replay,
                     "role_fit_warning": has_role_fit_warning(analysis),
                     "robustness": {**threshold_check,
                                    "label": confidence_label(bootstrap["top_share"], threshold_check["top_share"]),
                                    "threshold_label": threshold_check["label"]},
                     "retrieved_dates": sorted({retrieval_date(job).isoformat() for job in analysis["all_listings"]
                                                 if retrieval_date(job) is not None}),
                     "bootstrap": bootstrap, "opportunity": opportunity, "distance": distances,
                     "budget_reached": client.budget_reached, "live_requests": client.live_calls})
    return analysis
