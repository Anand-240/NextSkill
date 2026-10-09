"""Render every numerical claim in README.md, DEMO.md and reports/final_report.md from the generated result file."""
import json
import re
from collections import Counter
from pathlib import Path
from engine import hours_text
from findings import (baseline_text, compact_table, example_key, example_text, flag_text, gap_sentence, gap_table,
                      key_findings, map_table)
from personas import personas
ROOT = Path(__file__).resolve().parents[1]
TIER2 = {"Jaipur", "Indore", "Kochi", "Dehradun"}


def report_body(name: str) -> str:
    return re.sub(r"\A# .*\n+", "", (ROOT / name).read_text()).strip()


def evidence_text(name: str, label: str) -> str:
    body = report_body(name)
    if "Status: in progress" in body:
        return f"In progress. {label} has no results yet, so no figure is claimed."
    return body


def audit_sentence() -> str:
    lines = [line for line in (ROOT / "reports/matcher_audit.md").read_text().splitlines() if line.startswith("Precision")]
    return " ".join(lines)


def usage_sentence() -> str:
    path = ROOT / "reports/build_usage.json"
    attempts = json.loads(path.read_text())["attempts"] if path.exists() else []
    kinds = Counter(item["engine"] for item in attempts)
    return (f"This build recorded {len(attempts)} SerpApi search attempts "
            f"({kinds.get('google_jobs', 0)} Google Jobs, {kinds.get('youtube', 0)} YouTube, {kinds.get('google', 0)} Google web search) "
            "in reports/build_usage.json; the Account API figures are in docs/BUILD_LOG.md.")


def render(data):
    pairs = data["pairs"]
    gap = json.loads((ROOT / "reports/job_gap.json").read_text())
    key = example_key(data)
    star = pairs[key]
    resume = personas()[star["role"]]["resume"]
    example = example_text(data, resume)
    head = next(item for item in star["ranked"] if item["skill"] == star["headline_skill"])
    findings = "\n".join(f"- {line}" for line in key_findings(data)) + "\n"
    readme = f"""# NextSkill

**NextSkill shows a fresher which listings in their own city they are one skill away from, and the free course that gets
them there, with every number linked to its source.**

[Try it live](https://nextskill.streamlit.app) (saved snapshots, no key, no credits) | [Demo script](DEMO.md) | [Build log](docs/BUILD_LOG.md)

**Who it helps.** Freshers and early-career job seekers choosing what to learn next, especially outside the biggest hubs,
where local listings are thin. It counts what local listings ask for instead of guessing from national trends.

**Worked example.** {example}

**Key finding: the job-information gap.** {gap_sentence(gap)}

## How it works

SerpApi Google Jobs supplies listings for a role and city. The engine removes duplicates, sets aside listings that need more
experience than your level, detects requirements and either/or choices, and compares them with your skills. Every missing
skill with saved course hours competes for the Fastest win (most new matches per course hour). Only a skill with standard
course confidence can lead; otherwise the headline is the Biggest unlock. SerpApi YouTube supplies the free courses behind
the hours. Job Prep turns one listing into a plan: revise skills you have with short videos, learn missing skills with full
courses, and see the shortest route next to the full plan. The Hindi switch prefers Hindi videos where they pass the same
filters; the interface itself is English only.

## What the numbers mean

- Match: coverage reaches the selected fraction of detected core requirements; the default is 50%. It is not hiring
  eligibility or a prediction.
- Stated must-haves met: yes, no or none stated, for skills near explicit wording such as must, mandatory or required.
  None stated does not count as yes.
- Course hours: median duration of up to three free videos whose title names the skill, not time to mastery. Talks,
  webinars, videos under 10 minutes and videos led by a different product are dropped. Hours are shown rounded, for example
  "about 3 hours".
- Standard course confidence: at least two relevant full courses of an hour or more. A skill without it stays in the ranking
  but cannot be the fastest win.
- Pick stability: how stable the headline pick is under listing resampling and independent hour variation. Strong needs at
  least 15 scored listings, standard course confidence and both shares at 85% or more; under 15 scored listings the label is
  at most Likely; limited-data markets are at most Uncertain. It is not accuracy. The example above is the market with the
  best label and, among equals, the most scored listings.
- Exact among measured skills: every combination of up to eight skills with known course hours. Not a global optimum.

## Job-information gap

Equal queries (the plain role name, no fresher or junior variants, up to three pages) for two roles in five cities. Every
query filled all three pages, so the page limit sets the total of visible listings. What differs is how many of those listings
are located in the named city (its name appears in the listing's location text; suburbs under other names do not count).
These are listings visible through Google Jobs in one snapshot, not the number of jobs in a city.

{gap_table(gap)}
Where fewer listings are local, a city's answer rests on less evidence, and NextSkill flags small samples instead of
guessing. The chart is on the Compare cities page; the data is in [reports/job_gap.json](reports/job_gap.json).

## Does jobs-per-hour change the answer?

{baseline_text(data)}
## All markets

{findings}
{compact_table(data)}
Each market is one role in one city, counted from the listings saved for it. Full columns are in
[reports/final_report.md](reports/final_report.md).

## Evidence

- User test: {evidence_text("reports/user_test.md", "The user test")}
- Hand-labelled accuracy: {evidence_text("reports/hand_label_eval.md", "The hand-labelled evaluation")}

The only accuracy check so far was written by the developer: {audit_sentence()} The matching rules were changed after
seeing those 20 matches, so the second figure is not an independent measure and recall was not measured
([matcher audit](reports/matcher_audit.md), [initial API validation](reports/validation_check.md)). A 20-listing labelling kit
and a user-test sheet are in [evaluation/](evaluation/README.md); a person must fill them.

## SerpApi usage

- [Google Jobs](https://serpapi.com/google-jobs-api): listings, descriptions, links, posting signals and pagination, including
  the equal-query snapshot behind the job-information gap. Without it there is no local evidence at all.
- [YouTube](https://serpapi.com/youtube-search-api): free full courses for course hours and short revision videos for Job
  Prep. Without it a skill has no study-time estimate.
- [Google web search](https://serpapi.com/search-api): tried for NPTEL and SWAYAM pages with site: filters. The filters
  returned none of those hosts, so the feature was dropped and nothing in the product depends on it.
- [Account API](https://serpapi.com/account-api): shows remaining credits in live mode; a failure never discards results.

Requests time out after 75 seconds and are not retried. Live runs have a per-run budget and a Search Replay that shows
what was live, cached or skipped. {usage_sentence()}

## Judge FAQ

**Why not just ask ChatGPT?** NextSkill shows a reproducible count and links the exact listings and videos behind it, and
it measures how stable its pick is. An assistant with search can also cite evidence; the difference here is a transparent,
repeatable calculation over saved data, not a claim that assistant advice cannot be checked.

**How is this different from the National Career Service or LinkedIn Skills Match?** Those services already do related things
([NCS](https://labour.gov.in/ncs), [Skills Match](https://www.linkedin.com/help/linkedin/answer/a793433)). NextSkill adds a
counted, linked comparison for one role in one city and says how stable its pick is. We make no claim that nothing similar
exists. Sources and scope: [research/RESEARCH.md](research/RESEARCH.md).

**Why does this matter?** [ILO and IHD](https://www.ilo.org/publications/india-employment-report-2024-youth-employment-education-and-skills)
examine youth employment, education and skills, and [UNICEF](https://www.unicef.org/india/economic-opportunities-young-people)
describes gaps in job awareness, information and employment support. These sources motivate the problem; they do not show that
NextSkill helps.

**Does a match mean an interview?** No. Coverage ignores qualifications outside the skill vocabulary, and course length does
not establish competence.

**Are the numbers about all of India?** No. Each answer comes from a few dozen saved listings in one city.

**Why is no market rated Strong?** Pick stability needs at least 15 scored listings and standard course confidence, and most
markets here have fewer listings or hours that move the pick. We report that instead of tuning it.

**Who is Priya?** A sample profile that stands for a fresher in a saved market. She is not a real person and no user data
appears anywhere in this project.

## Limitations

Small, biased snapshots; nearby-city results appear in every market; the experience selector works on samples collected with
fresher and junior searches, so other levels are approximate; imperfect required-versus-preferred parsing; unknown posting ages
and course audio languages; a title that names a skill does not prove the course is good; the skill vocabulary covers tech,
data, marketing, finance and design, not every role; no measured learning or hiring outcomes.

## Future work

Independent hand labels and a real user test; more saved cities and roles; human-reviewed Hindi interface labels; NPTEL or
SWAYAM courses once a reliable source exists; a hosted live mode with a rate-limited key.

## Setup and tests

```sh
git clone https://github.com/Anand-240/NextSkill.git
cd NextSkill
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
python -m unittest discover -s tests -q
python -m scripts.check_consistency
```

PDF resumes need selectable text; scanned PDFs need pasted text. Live search is for local use with your own authorized
key in `.env`; the public hosted app must never receive a key. `.env` and `cache/` are ignored.

## Data sources

Job descriptions and video metadata remain their publishers' content. The MIT license covers our code, not third-party
material. Contact data in saved responses is redacted. Resume text is read in memory and never written to disk or sent in
SerpApi queries; Streamlit and its host may keep session memory or logs, so do not use the public demo for sensitive
resumes. [License](LICENSE).

## Development timeline

The repository began on October 8, 2026 after a separate validation run. October 9: trust fixes, 15 saved markets, revision
videos, a seven-page site, Hindi videos and the evidence kits. A second batch followed: a stricter headline rule, pick
stability, the job-information gap and the baseline comparison. [docs/BUILD_LOG.md](docs/BUILD_LOG.md) records each verified
step and the API budget.

## AI tools used

OpenAI Codex and Claude Code assisted with implementation, tests, analysis and documentation. The running app does not call
an LLM. Human labels, user feedback and Hindi approvals have not been collected, and an assistant must never generate them.
"""
    skills_phrase = resume.replace(", ", ", ")
    listing = star["job_prep_default"]
    route = ", ".join(listing["shortest_route"]) if listing and listing["shortest_route"] else "the shortest route"
    low = min(gap["rows"], key=lambda row: (row["in_city"] / row["listings"], row["role"], row["city"]))
    demo = f"""# NextSkill local demo (2 minutes 40 seconds)

Run `streamlit run app.py` locally. Keep the public hosted app key-free. Rehearse on saved data.
Record the live part (1:45 to 2:15) first with a small budget of 3 searches; retry it if a request times out.
Never show the key.

| Time | Show and say |
|---|---|
| 0:00-0:20 | Home page. "Meet Priya, a sample fresher in {star['city']} who knows {natural_list_text(skills_phrase)}. In {star['scored']} local listings pulled through SerpApi, she meets the core skills of {star['matches']}. NextSkill counts which one skill unlocks the most extra listings, and shows every listing and free course behind that number." |
| 0:20-0:55 | Job match, {star['role']} in {star['city']}. The headline pick is {head['display_skill']}: +{head['unlocked']} listings, {hours_text(head['hours'])} of free courses. Open Evidence: the listings it adds, stated must-haves met in {star['must_haves_met']} of the {star['matches']} matches, and the free YouTube courses. Pick stability is {star['confidence']}, based on {star['stability_listings']} listings. Course length is not mastery. |
| 0:55-1:20 | Job Prep for one listing{(' (' + listing['title'] + ')') if listing else ''}: shortest route ({route}) versus the full plan, revise with short videos, learn with full courses. |
| 1:20-1:45 | Compare cities, Job-information gap chart. Google Jobs returned {low['listings']} listings for {low['role']} in {low['city']}, but only {low['in_city']} were located there. Fewer local listings means less evidence, and NextSkill flags small samples instead of guessing. |
| 1:45-2:15 | Live search (local only, budget 3): Search Replay shows what was live and what was cached, the credit counter updates, partial results are handled. |
| 2:15-2:40 | Honest limits, one sentence each: a match is coverage, not hiring eligibility; samples are small and nearby cities leak in; the user test and independent labels are in progress; the interface is English with Hindi videos preferred on request. |

The video must be under three minutes, show the local app, and open without sign-in.
This file is a script, not evidence that a public video has been submitted.
"""
    report = ('# Current saved results\n\nGenerated from final_results.json; historical reports are in archive/.\n\n'
              + findings + "\n" + map_table(pairs))
    return {'README.md': readme, 'DEMO.md': demo, 'reports/final_report.md': report}


def natural_list_text(resume: str) -> str:
    from findings import natural_list
    return natural_list([part.strip() for part in resume.split(",") if part.strip()])


if __name__ == '__main__':
    for path, body in render(json.loads((ROOT / 'reports/final_results.json').read_text())).items():
        (ROOT / path).write_text(body)
