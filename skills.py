"""Conservative skill vocabulary for Indian tech, data, marketing, finance and design jobs."""

import re
from collections import defaultdict
from functools import lru_cache

# Canonical names are also searched, except for ambiguous short language names.
SKILLS = {
    "tech": "SQL|Excel|Power BI|Python|Tableau|Java|JavaScript|TypeScript|React|Node.js|Express.js|AWS|Git|HTML|CSS|Angular|Vue.js|Next.js|Spring Boot|Django|Flask|FastAPI|PHP|C++|C#|Go|R|C|Kotlin|Swift|Android|React Native|MySQL|PostgreSQL|MongoDB|Redis|Docker|Kubernetes|Jenkins|Terraform|Linux|Bash|REST API|GraphQL|Microservices|CI/CD|DevOps|Azure|Google Cloud|Selenium|Playwright|Agile|Scrum|Jira|Postman|Kafka|Spark|Airflow|Databricks|Snowflake|BigQuery|Oracle Database|SQL Server|NoSQL|Data Structures|Algorithms|System Design|Cybersecurity|API Testing|Unit Testing|ETL|Data Warehousing|Machine Learning|Deep Learning|NLP|Computer Vision|TensorFlow|PyTorch|Scikit-learn|Pandas|NumPy".split("|"),
    "data": "Data Analysis|Data Visualization|Statistics|A/B Testing|Business Intelligence|Data Modeling|Data Cleaning|Data Engineering|Predictive Modeling|Regression|Time Series|Power Query|DAX|Looker|Google Analytics|GA4|Google Tag Manager|Mixpanel|Amplitude|dbt".split("|"),
    "marketing": "SEO|SEM|Google Ads|Meta Ads|Facebook Ads|Performance Marketing|Content Marketing|Email Marketing|Social Media Marketing|Marketing Automation|CRM|HubSpot|Salesforce|Mailchimp|WordPress|Copywriting|Keyword Research|Google Search Console|Campaign Management|Conversion Rate Optimization|CRO|Lead Generation|Brand Management|Market Research|Digital Marketing|Canva".split("|"),
    "finance": "Tally|GST|Accounting|Bookkeeping|Financial Modeling|Financial Analysis|Financial Reporting|Budgeting|Forecasting|Auditing|Taxation|Income Tax|TDS|SAP FICO|SAP|ERP|QuickBooks|Zoho Books|Accounts Payable|Accounts Receivable|Reconciliation|Payroll|IFRS|Valuation|Risk Management|Compliance|KYC|AML|Equity Research".split("|"),
    "design": "Figma|Adobe Photoshop|Adobe Illustrator|Adobe XD|UI Design|UX Design|UI/UX|Wireframing|Prototyping|User Research|Usability Testing|Design Systems|Graphic Design|Typography|Adobe InDesign|Adobe After Effects|Adobe Premiere Pro|Blender|AutoCAD|Responsive Design|Web Design|Product Design".split("|"),
}

ALIASES = {
    "Excel": ["MS Excel", "Microsoft Excel", "Advanced Excel"],
    "Power BI": ["PowerBI", "Power-BI", "Microsoft Power BI"],
    "HTML": ["HTML5"], "CSS": ["CSS3"],
    "JavaScript": ["JS", "ES6", "ES2015", "ECMAScript"], "TypeScript": ["TS"],
    "Node.js": ["NodeJS", "Node JS", "Node"], "Next.js": ["NextJS", "Next JS"],
    "Vue.js": ["VueJS", "Vue JS", "Vue"], "Express.js": ["ExpressJS", "Express JS", "Express"],
    "React": ["ReactJS", "React JS", "React.js"],
    "AWS": ["Amazon Web Services"], "Google Cloud": ["GCP", "Google Cloud Platform"],
    "SQL Server": ["MS SQL Server", "Microsoft SQL Server", "MSSQL"],
    "PostgreSQL": ["Postgres"], "MongoDB": ["Mongo DB", "Mongo"],
    "CI/CD": ["CI CD", "continuous integration and continuous delivery"],
    "REST API": ["RESTful APIs", "RESTful API", "REST APIs", "REST services", "REST service", "RESTful services", "RESTful service"],
    "Scikit-learn": ["sklearn", "scikit learn"],
    "GA4": ["Google Analytics 4"],
    "Google Ads": ["Google AdWords", "AdWords"],
    "Meta Ads": ["Meta advertising"], "SEO": ["search engine optimization", "search engine optimisation"],
    "SEM": ["search engine marketing"], "CRM": ["customer relationship management"],
    "CRO": ["conversion rate optimisation"],
    "GST": ["goods and services tax"], "TDS": ["tax deducted at source"],
    "KYC": ["know your customer"], "AML": ["anti-money laundering"],
    "Figma": ["Figma design"], "Wireframing": ["wireframes", "wireframe"], "Adobe Photoshop": ["Photoshop"],
    "Adobe Illustrator": ["Illustrator"], "Adobe InDesign": ["InDesign"],
    "Adobe After Effects": ["After Effects"], "Adobe Premiere Pro": ["Premiere Pro"],
    "UI Design": ["user interface design"], "UX Design": ["user experience design"],
    "UI/UX": ["UX/UI", "UI UX", "UX UI"],
    "Go": ["Golang", "Go language", "Go programming", "Go developer"],
    "R": ["R language", "R programming", "RStudio", "R Studio"],
    "C": ["C language", "C programming", "C developer"],
}

AMBIGUOUS = {"R", "Go", "C"}
# "JS" and "TS" are suffixes in names such as Node.js or React JS, not a separate skill.
_FRAMEWORKS = "Node|Next|Nest|Nuxt|Vue|React|Express|Angular|Ember|Backbone|Three|D3|Chart|Svelte|Solid|Alpine|Deno".split("|")
_SUFFIX_GUARD = r"(?<!\.)" + "".join(f"(?<!{name} )(?<!{name}-)" for name in _FRAMEWORKS)
STANDALONE_ONLY = {"JS", "TS"}
# Short forms that are also ordinary words match only when capitalised as written here.
CASE_SENSITIVE = {"Node", "Mongo", "Express"}
_TERM_GUARDS = {"Express": r"(?<!American )"}
# A named stack stands for each of its member skills.
STACKS = {"MERN": ("MongoDB", "Express.js", "React", "Node.js"),
          "MEAN": ("MongoDB", "Express.js", "Angular", "Node.js")}
_LIST_LANGUAGE = re.compile(r"(?:^|[,|/;:(]\s*)(C|R|Go)(?=\s*(?:[,|/;)]|$))")
_STACK_PATTERN = re.compile(r"(?<!\w)(?:MERN|[Mm]ern|MEAN)(?:\s+[Ss]tack)?(?!\w)")
GENERIC = {"Data Analysis", "Business Intelligence", "Digital Marketing", "Graphic Design",
           "Compliance", "Machine Learning", "Communication", "Problem Solving",
           "Teamwork", "Analytical Skills", "UI/UX"}
_patterns = defaultdict(list)
for names in SKILLS.values():
    for canonical in names:
        terms = ([] if canonical in AMBIGUOUS else [canonical]) + ALIASES.get(canonical, [])
        for term in terms:
            # Unicode-aware boundaries prevent matching inside names such as PowerBIA or MySQL2.
            guard = (_SUFFIX_GUARD if term in STANDALONE_ONLY else "") + _TERM_GUARDS.get(term, "")
            flags = 0 if term in CASE_SENSITIVE else re.I
            _patterns[canonical].append(re.compile(r"(?<!\w)" + guard + re.escape(term) + r"(?!\w)", flags))


_ALL_TERMS = sorted({term for names in SKILLS.values() for canonical in names
                     for term in [canonical, *ALIASES.get(canonical, [])]} | set(STACKS), key=len, reverse=True)
# A run of skill names joined by commas, slashes, "or" or "and", so one cue covers the whole list.
_CHAIN = r"(?:(?:" + "|".join(re.escape(term) for term in _ALL_TERMS) + r")(?:\s+[Ss]tack)?\s*(?:,|/|\bor\b|\band\b)\s*)*"
# "no Tableau", "not Angular", "without SQL or Python", "currently learning Power BI".
_SHORT_NEGATION = re.compile(
    r"(?:\b(?:no|not|without)|(?<!machine )(?<!deep )(?<!e-)(?<!reinforcement )(?<!transfer )"
    r"\b(?:currently\s+|still\s+)?learning)(?:\s*[:\-]\s*|\s+)(?:(?:any|prior|much|formal|real)\s+)?" + _CHAIN + r"$", re.I)

_BOUNDARY = re.compile(r"(?<=[.!?;])\s+|\n+|[•●▪]|\b(?:but|however|whereas|although|yet)\b", re.I)
_NEGATION = re.compile(
    r"\b(?:no\s+(?:prior\s+)?(?:experience|knowledge)\s+(?:with|in|of)|"
    r"not\s+familiar\s+with|never\s+(?:used|worked\s+with)|"
    r"(?:don['’]t|do\s+not)\s+know|"
    r"(?:don['’]t|do\s+not|not)\s+need(?:\s+to\s+be\s+a)?|"
    r"(?:do\s+not|don['’]t)\s+require)\b", re.I)
_POSITIVE_RESET = re.compile(
    r"\b(?:and\s+)?(?:I\s+am|we\s+are|I\s+have|I\s+know|I\s+use|"
    r"proficient\s+in|experienced\s+in|familiar\s+with|skilled\s+in)\b", re.I)


_TERM_GROUP = "(?:" + "|".join(re.escape(term) for term in _ALL_TERMS) + ")"
# "SQL is a plus", "Power BI or Tableau (preferred)", "AWS will be an added advantage".
_PREFERRED_AFTER = re.compile(
    r"(?:\s*(?:,|/|\bor\b|\band\b)\s*" + _TERM_GROUP + r")*\s*(?:"
    r"\(\s*(?:preferred|optional|a plus|nice to have|good to have)\s*\)|"
    r"(?:is|are|would be|will be)\s+(?:an?\s+)?(?:added\s+|big\s+|strong\s+)?(?:plus|advantage|bonus)\b|"
    r"(?:is|are)\s+(?:preferred|desirable|nice to have|good to have)\b|"
    r"(?:preferred|nice to have|good to have)\b)", re.I)
# "Nice to have: SQL", "Preferred Skills ... React"; a later required/must cancels the header.
_PREFERRED_BEFORE = re.compile(
    r"\b(?:preferred|nice[- ]to[- ]have|good[- ]to[- ]have|bonus|desirable)\b"
    r"(?:(?!\b(?:required|requirements?|must|mandatory|essential)\b)[\s\S])*$", re.I)


def preferred_mention(text: str, start: int, end: int) -> bool:
    """True when the sentence marks this skill as a plus rather than a requirement."""
    boundaries = list(_BOUNDARY.finditer(text, 0, start))
    left = text[boundaries[-1].end() if boundaries else 0:start]
    following = next((m.start() for m in _BOUNDARY.finditer(text, end)), len(text))
    return bool(_PREFERRED_BEFORE.search(left[-100:]) or _PREFERRED_AFTER.match(text, end, following))


def negated_mention(text: str, start: int, end: int) -> bool:
    boundaries = list(_BOUNDARY.finditer(text, 0, start))
    left = text[boundaries[-1].end() if boundaries else 0:start]
    negatives = list(_NEGATION.finditer(left))
    return bool((negatives and not _POSITIVE_RESET.search(left, negatives[-1].end())) or
                _SHORT_NEGATION.search(left[-160:]) or
                re.match(r"\s*:\s*(?:no|none|nil)\b", text[end:end + 10], re.I) or
                re.match(r"\s+(?:is\s+|are\s+)?(?:not\s+required|not\s+needed)\b", text[end:end + 25], re.I))


def skill_mentions(text: str, skip_headings: bool = True) -> list[tuple[str, int, int]]:
    """Return affirmative skill mentions and their offsets in the original text."""
    # The same descriptions are scanned many times per analysis, so cache by text.
    return list(_skill_mentions(text or "", skip_headings))


@lru_cache(maxsize=8192)
def _skill_mentions(text: str, skip_headings: bool) -> tuple[tuple[str, int, int], ...]:
    found = set()
    starts = [0]
    segments = []
    for boundary in _BOUNDARY.finditer(text):
        segments.append((starts[-1], boundary.start()))
        starts.append(boundary.end())
    segments.append((starts[-1], len(text)))
    for start, end in segments:
        segment = text[start:end]
        if not segment:
            continue
        # In a job listing a bare role heading names the vacancy, not a requirement.
        # In a resume the same line ("Python Developer") is evidence of the skill.
        if skip_headings and len(segment) < 85 and re.search(r"\b(intern|internship|developer|analyst|designer)\s*$", segment, re.I) and not re.search(r"[:.;]", segment):
            continue
        for name, patterns in _patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(segment):
                    left = segment[:match.start()].lower()
                    # Negation extends over a skill list until a new positive clause.
                    if negated_mention(segment, match.start(), match.end()):
                        continue
                    if name == "Graphic Design" and re.search(r"\b(?:e\.g\.|ex:)\s*[^.]{0,60}$", left):
                        continue
                    if name == "Compliance" and re.search(r"\bvendor\s*$", left):
                        continue
                    found.add((name, start + match.start(), start + match.end()))
        if not skip_headings and any(item[1] >= start and item[2] <= end for item in found):
            # In a resume skills list, a bare "C", "R" or "Go" item beside other skills is a language.
            for match in _LIST_LANGUAGE.finditer(segment):
                if not negated_mention(segment, match.start(1), match.end(1)):
                    found.add((match.group(1), start + match.start(1), start + match.end(1)))
        for match in _STACK_PATTERN.finditer(segment):
            if negated_mention(segment, match.start(), match.end()):
                continue
            stack = match.group(0).split()[0].upper()
            found.update((name, start + match.start(), start + match.end()) for name in STACKS[stack])
    # Aliases can contain the canonical name. Keep the widest occurrence once.
    return tuple(sorted((item for item in found if not any(
        other[0] == item[0] and other != item and other[1] <= item[1] and other[2] >= item[2]
        for other in found)), key=lambda item: (item[1], -(item[2] - item[1]), item[0])))


def extract_skills(text: str, resume: bool = False) -> set[str]:
    """Return canonical skills supported by affirmative mentions."""
    return {name for name, _, _ in skill_mentions(text, skip_headings=not resume)}


def skill_count() -> int:
    return sum(map(len, SKILLS.values()))
