# NextSkill

**NextSkill shows a fresher which listings in their own city they are one skill away from, and the free course that gets
them there, with every number linked to its source.**

[Try it live](https://nextskill.streamlit.app) (saved snapshots, no key, no credits) | [Demo script](DEMO.md) | [Build log](docs/BUILD_LOG.md)

**Who it helps.** Freshers and early-career job seekers choosing what to learn next, especially outside the biggest hubs,
where local listings are thin. It counts what local listings ask for instead of guessing from national trends.

**Worked example.** Priya is a sample profile, not a real person. She knows HTML, CSS and JavaScript and wants a Frontend Developer job in Bengaluru. In **19** scored local listings pulled through SerpApi, her profile meets the core skills of **9**. **REST API** would add **8** more, for about 3 hours of free courses. Pick stability: Likely, based on 19 listings. Every listing and course behind that estimate is linked.

**Key finding: the job-information gap.** Asked the same plain question for 2 roles in 5 cities, Google Jobs returned between 26 and 30 listings every time (the three-page limit). How many were located in the named city varied a lot: only 3 of 28 for Accountant in Dehradun (most of the rest were in New Delhi, Gurugram and Noida), against 27 of 28 for Data Analyst in Jaipur. A fresher outside the biggest hubs can see far less local evidence than the length of the list suggests.

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

| Role | City | Visible listings | Located in the city | Distinct employers | Pages | Snapshot |
|---|---|---:|---:|---:|---:|---|
| Data Analyst | Bengaluru | 26 | 22 | 25 | 3 | 2026-10-09 |
| Data Analyst | Pune | 29 | 6 | 28 | 3 | 2026-10-09 |
| Data Analyst | Jaipur | 28 | 27 | 26 | 3 | 2026-10-09 |
| Data Analyst | Indore | 28 | 23 | 27 | 3 | 2026-10-09 |
| Data Analyst | Dehradun | 29 | 21 | 29 | 3 | 2026-10-09 |
| Accountant | Bengaluru | 29 | 26 | 28 | 3 | 2026-10-09 |
| Accountant | Pune | 28 | 8 | 27 | 3 | 2026-10-09 |
| Accountant | Jaipur | 30 | 9 | 29 | 3 | 2026-10-09 |
| Accountant | Indore | 29 | 17 | 29 | 3 | 2026-10-09 |
| Accountant | Dehradun | 28 | 3 | 27 | 3 | 2026-10-09 |

Where fewer listings are local, a city's answer rests on less evidence, and NextSkill flags small samples instead of
guessing. The chart is on the Compare cities page; the data is in [reports/job_gap.json](reports/job_gap.json).

## Does jobs-per-hour change the answer?

A simple alternative is to recommend the missing core skill that the most scored listings ask for, with no course hours. The two methods agree in 4 of 14 markets that have a headline pick. In the other 10, the headline pick unlocks at least as many extra listings as the frequency-only pick in 5 and needs less course time in 9. So including course hours does change the answer, but it trades off listings against hours, and it rests on video lengths that are only a proxy for study time.

| Market | Most asked skill (extra listings, course time) | Headline pick (extra listings, course time) | Reading |
|---|---|---|---|
| Frontend Developer / Bengaluru | React (+10, 5.1 h) | REST API (+8, 2.5 h) | headline unlocks fewer listings in less course time |
| Data Analyst / Hyderabad | SQL (+7, 4.3 h) | Data Cleaning (+4, 2.3 h) | headline unlocks fewer listings in less course time |
| Data Analyst / Pune | Statistics (+4, 8.2 h) | Power BI (+3, 3.7 h) | headline unlocks fewer listings in less course time |
| Data Analyst / Jaipur | SQL (+4, 4.3 h) | Power BI (+4, 3.7 h) | headline unlocks as many listings in less course time |
| Digital Marketing Executive / Dehradun | Google Ads (+3, 5.4 h) | SEO (+2, 1.9 h) | headline unlocks fewer listings in less course time |
| Python Developer / Bengaluru | Django (+1, 3.3 h) | REST API (+1, 2.5 h) | headline unlocks as many listings in less course time |
| Python Developer / Kochi | HTML (+2, 5.4 h) | PostgreSQL (+3, 4.1 h) | headline unlocks more listings in less course time |
| Accountant / Indore | GST (+2, 4.8 h) | TDS (+2, 1.6 h) | headline unlocks as many listings in less course time |
| Digital Marketing Executive / Pune | Market Research (+2, 0.9 h) | Email Marketing (+1, 2.3 h) | headline unlocks fewer listings |
| Frontend Developer / Hyderabad | Git (+3, 3.7 h) | REST API (+3, 2.5 h) | headline unlocks as many listings in less course time |

## All markets

- 15 saved markets across 10 cities, 163 scored listings in total. Each answer is counted from the listings saved for that market, not from a national dataset.
- The fastest win differs from the biggest unlock in 5 of the 14 markets with a measured pick, so a short course can beat a big skill per hour.
- Pick stability is Strong in 0, Likely in 3 and Uncertain in 12 markets; 8 markets are flagged as limited data. The example profile matched between 0% (Data Analyst, Indore) and 55% (Frontend Developer, Hyderabad) of scored listings.

| Market | Scored listings | Headline pick | Pick stability | Flags |
|---|---:|---|---|---|
| Frontend Developer / Bengaluru | 19 | REST API | Likely | none |
| Data Analyst / Noida | 17 | SQL | Uncertain | none |
| Data Analyst / Hyderabad | 14 | Data Cleaning | Uncertain | none |
| Data Analyst / Pune | 11 | Power BI | Uncertain | none |
| Data Analyst / Jaipur | 14 | Power BI | Uncertain | none |
| Data Analyst / Indore | 4 | none | Uncertain | limited data |
| Accountant / Jaipur | 12 | Bookkeeping | Likely | none |
| Digital Marketing Executive / Dehradun | 5 | SEO | Uncertain | limited data |
| Python Developer / Bengaluru | 11 | REST API | Uncertain | limited data |
| Python Developer / Kochi | 7 | PostgreSQL | Uncertain | limited data |
| Accountant / Mumbai | 15 | Tally | Likely | none |
| Accountant / Indore | 9 | TDS | Uncertain | limited data |
| Digital Marketing Executive / Pune | 5 | Email Marketing | Uncertain | limited data, few skills detected |
| Digital Marketing Executive / Chennai | 9 | SEO | Uncertain | limited data, few skills detected |
| Frontend Developer / Hyderabad | 11 | REST API | Uncertain | limited data |

Each market is one role in one city, counted from the listings saved for it. Full columns are in
[reports/final_report.md](reports/final_report.md).

## Evidence

- User test: In progress. The user test has no results yet, so no figure is claimed.
- Hand-labelled accuracy: In progress. The hand-labelled evaluation has no results yet, so no figure is claimed.

The only accuracy check so far was written by the developer: Precision before: 80.0% (16/20). Precision after: 100.0% on retained sampled matches. The matching rules were changed after
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
what was live, cached or skipped. This build recorded 98 SerpApi search attempts (61 Google Jobs, 29 YouTube, 8 Google web search) in reports/build_usage.json; the Account API figures are in docs/BUILD_LOG.md.

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
