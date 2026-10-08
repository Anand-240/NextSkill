# NextSkill Improvements Batch A — cached-data report

No SerpApi searches or Account API calls were made for this batch. All figures below use the saved Noida and Bengaluru job/course responses. The 12-test Phase 3 suite was run after the README copy. Offline tests were rerun after each subsequent numbered change; the final suite has 19 passing tests.

## What changed

1. Copied the validation report into this repository at [validation_check.md](../validation_check.md) and fixed the README link.
2. Added minimum-years parsing for numeric experience and seniority words in titles. The app separates jobs above the chosen experience level and excludes them from readiness and unlocks.
3. Added BI, frontend-framework, and cloud substitute groups, plus explicit `X or Y` / `X/Y` alternatives. Either member satisfies one requirement. The most-demanded group member names the recommendation. Two-skill plans never combine overlapping alternatives.
4. Added a ranking robustness panel for thresholds 0.4, 0.5, 0.6 and learning-hour factors 0.5 and 1.5, using only cached duration data. Hour estimates display an approximate ±25% range.
5. Added a sample-size badge: High at 25+ eligible listings, Medium at 12–24, Low below 12.
6. Added a dictionary-coverage warning when the median detected skills per eligible listing is below three.
7. Added pypdf resume upload. Text-based PDFs use the existing matcher; blank/scanned PDFs request pasted text.
8. Recomputed six personas, updated the README and captured new screenshots: [Noida](../../screenshots/batch_a_noida.png) and [Bengaluru](../../screenshots/batch_a_frontend.png).

## Before and after personas

The “before” column is the saved Phase 3 result at the 0.50 threshold, without experience filtering or substitute groups. “After” uses this batch, the same threshold and the experience level shown. The denominator is usable jobs with detected core requirements; experience exclusions are separate.

| Demo role | Persona | Selected experience | Before ready | After ready | Set aside for experience | Top scored skill after | Sample confidence |
|---|---|---|---:|---:|---:|---|---|
| Data Analyst, Noida | Fresher: Excel, basic Python | Fresher | 2/17 | 1/8 | 9 | Power BI +4 | Low, 10 eligible listings |
| Data Analyst, Noida | Mid: SQL, Excel, Python, Tableau | 1-3 years | 14/17 | 11/13 | 4 | No one-skill unlock | Medium, 15 eligible listings |
| Data Analyst, Noida | Frontend fresher: HTML, CSS, JavaScript | Fresher | 0/17 | 0/8 | 9 | Power BI +1 | Low, 10 eligible listings |
| Frontend Developer, Bengaluru | Fresher: Excel, basic Python | Fresher | 0/28 | 0/11 | 17 | React +2 | Medium, 12 eligible listings |
| Frontend Developer, Bengaluru | Mid: SQL, Excel, Python, Tableau | 1-3 years | 0/28 | 0/20 | 8 | React +3 | Medium, 21 eligible listings |
| Frontend Developer, Bengaluru | Frontend fresher: HTML, CSS, JavaScript | Fresher | 8/28 | 2/11 | 17 | React +5 | Medium, 12 eligible listings |

## Demo rankings and robustness

- **Data Analyst, Noida fresher:** Power BI (or Looker / Tableau) unlocks four jobs; median course length ~3.68 hours, displayed as **~2–5 hours**. SQL unlocks three; its median is ~4.34 hours, displayed as **~3–6 hours**. Two-skill plan: Power BI + SQL. The pick was unchanged across the five checked scenarios among skills with cached course durations. The eligible sample has fewer than 12 listings, so the UI suppresses the medal and warns that the ranking is exploratory.
- **Frontend Developer, Bengaluru frontend fresher:** React (or Angular / Vue.js) unlocks five jobs; median course length ~5.09 hours, displayed as **~3–7 hours**. The next scored skills were UI/UX and TypeScript in this historical run. Two-skill plan: React + REST API, with a combined hour estimate unavailable in the cached courses. The pick was unchanged across the five checked scenarios among skills with cached course durations.

The hours multipliers scale every available duration equally, so a ranking change under those two settings is mathematically impossible; threshold changes can alter unlock counts and ranks. The historical check covered scored skills with cached course durations, not unmeasured skills. Neither demo matching persona triggered the dictionary-coverage warning. Cross-role personas remain poor fits and receive the role-fit warning.

## Verification

The final offline suite passed **19 tests**. It covers experience parsing and exclusion, substitute and explicit alternatives, ranking robustness, hour ranges, sample confidence boundaries, dictionary warning, PDF text extraction and scanned fallback, plus the earlier engine behavior. Screenshots were captured in Demo data mode; the live-search ledger remains untouched.
