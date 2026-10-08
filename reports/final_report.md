# Final demo results after the JS matcher fix

Both saved demos were re-run offline with SerpApi requests blocked. No SerpApi search or Account API calls were made. Settings: Fresher, readiness threshold 0.50, core-skill share 0.25, seed 2026. Both job snapshots were retrieved on 2026-10-07 UTC. Full figures are in [final_results.json](final_results.json).

## What changed

The alias `JS` was matching inside framework names such as Node.js, Next.js and Vue.js, and after a space in React JS or Node JS. Each of those listings gained a JavaScript requirement it never stated. Every demo resume includes JavaScript, so the phantom requirement made Bengaluru listings look closer than they are. `JS` now counts only as a standalone token. The app also shows the **fastest win** (most jobs unlocked per learning hour) next to the **biggest unlock** (most jobs unlocked, regardless of hours). No calculation changed for that display.

## Before and after

| Demo | Matches | Fastest win | Biggest unlock | Bootstrap / hour variation | Confidence |
|---|---|---|---|---|---|
| Bengaluru before | 8 of 19 | REST API: +8 at 3.12 h | React: +9 at 5.09 h | 77.2% / 66.1% | Likely |
| Bengaluru after | **5 of 19** | REST API: **+7** at 3.12 h | React: **+10** at 5.09 h | **63.0% / 58.9%** | **Uncertain** |
| Noida before | 1 of 17 | Data Cleaning: +2 at 1.54 h | SQL: +5 at 4.34 h | 49.2% / 86.1% | Uncertain |
| Noida after | 1 of 17 | Data Cleaning: +2 at 1.54 h | SQL: +5 at 4.34 h | 49.2% / 86.1% | Uncertain |

The Bengaluru fastest win is still REST API, but its confidence is now Uncertain. React wins 27.8% of the listing resamples. At threshold 0.6, REST API stays first in only 26.4% of hour-variation draws. Noida did not change: none of its saved listings used the affected aliases.

## Samples

| Demo | Raw listings | After deduplication | Set aside for experience | Eligible | Scored | No core skill detected |
|---|---:|---:|---:|---:|---:|---:|
| Bengaluru | 49 | 45 | 22 | 23 | 19 | 4 |
| Noida | 40 | 34 | 14 | 20 | 17 | 3 |

## Ranked skills

| Demo | Skill | Jobs unlocked | Course hours | Jobs per hour |
|---|---|---:|---:|---:|
| Bengaluru | REST API | 7 | 3.12 | 2.24 |
| Bengaluru | React | 10 | 5.09 | 1.96 |
| Bengaluru | Responsive Design | 3 | 2.80 | 1.07 |
| Bengaluru | Angular | 4 | unavailable | |
| Bengaluru | Git | 3 | unavailable | |
| Noida | Data Cleaning | 2 | 1.54 | 1.29 |
| Noida | SQL | 5 | 4.34 | 1.15 |
| Noida | Power BI | 2 | 3.68 | 0.54 |
| Noida | Tableau | 2 | 6.00 | 0.33 |
| Noida | Data Visualization | 1 | 5.46 | 0.18 |

Angular and Git have no saved course results, so the app shows them without an hours estimate and does not score them.

## Plans

| Demo | Opportunity curve: cumulative hours → matching listings | Two-skill plan |
|---|---|---|
| Bengaluru | 0 h → 5; REST API 3.12 h → 12; Responsive Design 5.92 h → 17; React 11.01 h → 19 | React + Responsive Design: +14 at 7.89 h |
| Noida | 0 h → 1; Data Cleaning 1.54 h → 3; SQL 5.89 h → 11; Tableau 11.89 h → 13 | SQL + Tableau: +10 at 10.35 h |

| Demo | Measured candidates | 5 h greedy / exact | 10 h greedy / exact | 15 h greedy / exact |
|---|---:|---|---|---|
| Bengaluru | 3 | 7 / 7 | **12 / 14** | 14 / 14 |
| Noida | 5 | **2 / 5** | 11 / 11 | 12 / 12 |

Exact search beats greedy twice. In Bengaluru at 10 hours, greedy takes REST API then Responsive Design (+12, 5.92 h). The exact optimum is React plus Responsive Design (+14, 7.89 h). In Noida at 5 hours, greedy takes Data Cleaning (+2), while SQL alone gives +5.

Skill distance, Bengaluru: 0 skills 5, 1 skill 11, 2 skills 3, 3+ none, unknown 4. Noida: 0 skills 1, 1 skill 11, 2 skills 5, 3+ none, unknown 3.

## Verification

- 46 offline tests pass, including standalone `JS` matching and both the same-skill and different-skill pick layouts.
- Screenshots: [Bengaluru](../screenshots/final_frontend.png), [Noida](../screenshots/final_noida.png), [Bengaluru curve](../screenshots/final_frontend_plan.png), [Noida curve](../screenshots/final_noida_plan.png), [Bengaluru distance](../screenshots/final_frontend_distance.png), [Noida distance](../screenshots/final_noida_distance.png), [Search Replay](../screenshots/final_replay.png).
- Earlier behaviour is recorded in the [Batch E report](batch_e_report.md).
