# Final demo results

Both saved demos were re-run offline with SerpApi requests blocked. No SerpApi search or Account API calls were made. Settings: Fresher, match threshold 0.50, core-skill share 0.25, seed 2026. Both job snapshots were retrieved on 2026-10-07 UTC. Full figures are in [final_results.json](final_results.json).

## What changed in the last matcher update

- **Versioned and short names.** HTML5, CSS3, ES6, ES2015 and ECMAScript, Node, Mongo and Express now map to their skills, and MERN and MEAN expand to their member skills. Six of 23 eligible Bengaluru listings say HTML5 or CSS3; three of them previously lost HTML or CSS entirely.
- **Resume headings.** A resume line such as "Python Developer" now counts Python. Job listings still skip bare role headings.
- **Negation.** "no Tableau", "not Angular", "without SQL", "Tableau: no" and "currently learning Power BI" no longer count as skills.
- **Alternatives.** "A, B or C" is one choice only for three tools of one family (BI tools, frontend frameworks, cloud providers, databases); a slash is always a choice. This fixed a Bengaluru listing that had merged "HTML5, CSS3, JavaScript/TypeScript" into one interchangeable requirement.
- **Preferred skills.** "is a plus", "nice to have" and "preferred" make a skill nice to have, not core, for that listing.
- **Experience.** "No experience required" and "freshers welcome" override title words such as Lead.

## Before and after

| Demo | Matches | Fastest win | Biggest unlock | Bootstrap / hour variation | Confidence |
|---|---|---|---|---|---|
| Bengaluru before | 5 of 19 | REST API: +7 at 3.12 h | React: +10 at 5.09 h | 63.0% / 58.9% | Uncertain |
| Bengaluru after | **9 of 19** | REST API: **+8** at 3.12 h | React: +10 at 5.09 h | 62.2% / **48.5%** | Uncertain |
| Noida before | 1 of 17 | Data Cleaning: +2 at 1.54 h | SQL: +5 at 4.34 h | 49.2% / 86.1% | Uncertain |
| Noida after | 1 of 17 | Data Cleaning: +2 at 1.54 h | SQL: +5 at 4.34 h | **56.4%** / 86.5% | Uncertain |

The Bengaluru fresher now matches four more listings, mostly because HTML5 and CSS3 are recognised. The fastest win and biggest unlock did not change in either demo. Noida changed only in its sensitivity shares, after some Noida skills were marked preferred rather than core.

## Samples

| Demo | Raw listings | After deduplication | Set aside for experience | Eligible | Scored | No core skill detected |
|---|---:|---:|---:|---:|---:|---:|
| Bengaluru | 49 | 45 | 22 | 23 | 19 | 4 |
| Noida | 40 | 34 | 14 | 20 | 17 | 3 |

## Ranked skills

| Demo | Skill | New matches | Course hours | Matches per hour |
|---|---|---:|---:|---:|
| Bengaluru | REST API | 8 | 3.12 | 2.57 |
| Bengaluru | Responsive Design | 6 | 2.80 | 2.14 |
| Bengaluru | React | 10 | 5.09 | 1.96 |
| Bengaluru | Git | 5 | unavailable | |
| Noida | Data Cleaning | 2 | 1.54 | 1.29 |
| Noida | SQL | 5 | 4.34 | 1.15 |
| Noida | Power BI | 2 | 3.68 | 0.54 |
| Noida | Tableau | 2 | 6.00 | 0.33 |
| Noida | Data Visualization | 1 | 5.46 | 0.18 |

Git has no saved course results, so the app shows it without an hours estimate and does not score it.

## Plans

| Demo | Opportunity curve: cumulative hours → matching listings | Two-skill plan |
|---|---|---|
| Bengaluru | 0 h → 9; REST API 3.12 h → 17; React 8.21 h → 19 | React + REST API: +10 at 8.21 h |
| Noida | 0 h → 1; Data Cleaning 1.54 h → 3; SQL 5.89 h → 11; Tableau 11.89 h → 13 | SQL + Tableau: +10 at 10.35 h |

| Demo | Measured candidates | 5 h greedy / exact | 10 h greedy / exact | 15 h greedy / exact |
|---|---:|---|---|---|
| Bengaluru | 3 | 8 / 8 | 10 / 10 | 10 / 10 |
| Noida | 5 | **2 / 5** | 11 / 11 | 12 / 12 |

Exact search beats greedy once: in Noida at 5 hours, greedy takes Data Cleaning (+2) while SQL alone gives +5. Before this update, exact search also beat greedy in Bengaluru at 10 hours; with the corrected matches, greedy now reaches the exact gain there.

Skill distance, Bengaluru: 0 skills 9, 1 skill 10, 2 skills 0, 3+ none, unknown 4. Noida: 0 skills 1, 1 skill 11, 2 skills 5, 3+ none, unknown 3.

## Job Prep demo listing

For "Frontend Developer (Fresher)" at Team Geek Solutions the profile covers 3 of 7 core skills; REST API, React or Responsive Design alone would make it a match. The suggested order is React (mentioned 3 times; 13 of 23 eligible listings), then revising JavaScript (17 of 23), HTML (16 of 23) and CSS (15 of 23), then REST API, Responsive Design and UI/UX. The time plan is about 8.9 to 14.4 hours: 39 minutes of revision videos plus 11.0 hours of full courses.

## Earlier change: JS inside framework names

The alias `JS` used to match inside Node.js, Next.js, Vue.js and React JS, adding a JavaScript requirement those listings never stated. Fixing it moved the Bengaluru demo from 8 to 5 matches and its confidence from Likely to Uncertain; Noida did not change. The numbers above include that fix.

## Speed

Analysis caches skill matching by text and the app caches saved-data results by input. In an offline app test a demo run took 2.4 seconds on first load and 0.1 seconds when repeated, down from 13 to 15 seconds.

## Verification

- 69 offline tests pass, including 47 realistic resume lines, live-budget tests with a mocked client, and the Job Prep plan for the demo listing.
- Screenshots: [Bengaluru](../screenshots/final_frontend.png), [Noida](../screenshots/final_noida.png), [Bengaluru curve](../screenshots/final_frontend_plan.png), [Noida curve](../screenshots/final_noida_plan.png), [Bengaluru distance](../screenshots/final_frontend_distance.png), [Noida distance](../screenshots/final_noida_distance.png), [Job Prep](../screenshots/final_jobprep.png), [Search Replay](../screenshots/final_replay.png).
- Earlier iterations are recorded in the [archive](archive/README.md).
