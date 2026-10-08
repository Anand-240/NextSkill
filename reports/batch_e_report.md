# Batch E: corrected matching and claims

All runs used bundled responses with the network request function blocked. No SerpApi search or Account API calls were made. The readiness threshold remains 0.50 and the core-frequency threshold remains 0.25. No figures were tuned to preserve the previous story.

## Before and after

| Demo | Matches before / after | Top pick before / after | Additional matches before / after | Course hours before / after | Recommendation confidence before / after |
|---|---|---|---|---|---|
| Noida | 1/17 / 1/17 | SQL / Data Cleaning | 8 / 2 | 4.34 / 1.54 | Likely / Uncertain |
| Bengaluru | 7/19 / 8/19 | REST API / REST API | 8 / 8 | 2.33 / 3.12 | Strong / Likely |

Noida now recommends Data Cleaning, with two additional matches. SQL now adds five, but its longer course estimate puts it second on the existing jobs-per-hour rule. Bengaluru still recommends REST API, with eight additional matches; React adds nine but has a longer course estimate. These are threshold crossings in the saved sample, not hiring outcomes.

## Confidence and sample sizes

| Demo | Eligible / scored / ignored | Experience exclusions | Bootstrap top-pick share | Independent hour/threshold retention | Combined label |
|---|---|---:|---:|---:|---|
| Noida | 20 / 17 / 3 | 14 | 49.2% | 86.1% | Uncertain |
| Bengaluru | 23 / 19 / 4 | 22 | 77.2% | 66.1% | Likely |

Bootstrap uses 500 seeded resamples. Sensitivity independently varies each measured skill from 0.75x to 1.5x its hours in 500 seeded draws, evaluated at thresholds 0.4, 0.5 and 0.6 (1,500 checks). Seed: 2026. A different selected threshold is also checked. The recommendation label uses the lower of the two shares: Strong at 85% or more, Likely at 60% or more, otherwise Uncertain. These are sensitivity labels, not accuracy estimates.

| Demo | Retention at 0.4 | Retention at 0.5 | Retention at 0.6 |
|---|---:|---:|---:|
| Noida | 98.8% | 68.6% | 91.0% |
| Bengaluru | 82.2% | 68.8% | 47.4% |

## Updated plans

### Noida

| Step | Skill | Estimated course hours | Additional matches | Total matches |
|---:|---|---:|---:|---:|
| 1 | Data Cleaning | 1.54 | 2 | 3 |
| 2 | SQL | 4.34 | 8 | 11 |
| 3 | Tableau | 6.00 | 2 | 13 |

Curve: 0h -> 1; 1.54h -> 3; 5.89h -> 11; 11.89h -> 13.

Distance counts: 0: 1, 1: 11, 2: 5, 3+: 0, Unknown: 3.

### Bengaluru

| Step | Skill | Estimated course hours | Additional matches | Total matches |
|---:|---|---:|---:|---:|
| 1 | REST API | 3.12 | 8 | 16 |
| 2 | Responsive Design | 2.80 | 2 | 18 |
| 3 | React | 5.09 | 1 | 19 |

Curve: 0h -> 8; 3.12h -> 16; 5.92h -> 18; 11.01h -> 19.

Distance counts: 0: 8, 1: 10, 2: 1, 3+: 0, Unknown: 4.

## Greedy versus exact

| Demo | Measured candidates | 5-hour gain, greedy / exact | 10-hour gain | 15-hour gain |
|---|---:|---|---|---|
| Noida | 5 | 2/5 (40.0%) | 11/11 (100.0%) | 12/12 (100.0%) |
| Bengaluru | 3 | 8/8 (100.0%) | 10/11 (90.9%) | 11/11 (100.0%) |

Noida greedy reaches only 40% of the exact additional-match gain at five hours. Bengaluru reaches 90.9% at ten hours. Each budget check reruns greedy under that budget; it is not necessarily a prefix of the unrestricted curve. No broader optimality claim is supported.

## All available cached course estimates

| Skill | Before hours | After hours | Course confidence |
|---|---:|---:|---|
| Data Analysis | 7.19 | 7.19 | standard |
| Data Cleaning | 3.49 | 1.54 | standard |
| Data Visualization | 5.46 | 5.46 | standard |
| Power BI | 3.68 | 3.68 | standard |
| REST API | 2.33 | 3.12 | standard |
| React | 5.09 | 5.09 | standard |
| Responsive Design | 2.80 | 2.80 | standard |
| SQL | 4.34 | 4.34 | standard |
| Tableau | 6.00 | 6.00 | standard |
| TypeScript | 3.90 | 3.90 | standard |
| UI/UX | 10.78 | 10.78 | standard |

Titles and channels indicating unrequested languages are excluded before both primary selection and fallback. Unlabelled audio language is unknown, so this does not prove that every retained video is English. With fewer than two qualifying one-hour courses, the existing thirty-minute fallback remains low confidence. Full source videos are preserved in [the result data](batch_e_results.json).

## Fixes and verification

- Negation scopes exclude skills from resumes and descriptions, including lists joined by or or slashes; positive clauses remain usable.
- Only explicit listing choices create alternatives. Independently required React and Angular may both matter to a plan; they are not globally interchangeable.
- A comma list that ends in or, such as "React, Angular, or Vue.js", is one alternative requirement. Three saved Bengaluru listings use this form. The fix changed only the Bengaluru bootstrap share, from 78.8% to 77.2%; the label stays Likely.
- Explicit minimum years override title estimates. Freshers welcome, entry level and zero-year ranges override title fallback. User bands conservatively use 0, 1 and 3 years.
- All 42 bundled responses preserve their original retrieval timestamp. Both job snapshots were retrieved on 2026-10-07 UTC. Posted age adds elapsed UTC calendar days; missing dates are not invented.
- Demo headlines say saved listings, and live-mode headlines say listings found now. Snapshot dates and eligible versus scored counts appear beside the result.
- Matcher audit wording retains the sample denominators and explicitly states that recall was not measured.
- 43 offline tests passed, including new regression tests for every requested correction and demo/live presentation. The live presentation test mocks the result and account methods and performs no live request.

Screenshots: [Noida](../screenshots/batch_e_noida.png), [Bengaluru](../screenshots/batch_e_frontend.png), [Noida curve](../screenshots/batch_e_noida_plan.png), [Bengaluru curve](../screenshots/batch_e_frontend_plan.png), [Noida distance](../screenshots/batch_e_noida_distance.png), [Bengaluru distance](../screenshots/batch_e_frontend_distance.png).
