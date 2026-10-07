# Batch C: learning plan, bootstrap confidence, and skill distance

All figures below use bundled job and video responses. **SerpApi calls: 0.** No account balance was queried or changed during this batch.

## Fresher demo results

| Saved role and persona | Eligible listings | Usable for readiness | Ready now | Top pick | One-skill unlocks | Bootstrap wins | Label |
|---|---:|---:|---:|---|---:|---:|---|
| Data Analyst, Noida · Excel and basic Python | 20 | 17 | 1 | SQL | 8 | 70.4% | Met prior 70% cutoff |
| Frontend Developer, Bengaluru · HTML, CSS and JavaScript | 23 | 19 | 7 | React | 8 | 93.0% | Met prior 70% cutoff |

Bootstrap uses 500 seeded resamples of eligible listings per input and recomputes core skills and the scored top pick. Noida shares: SQL **70.4%**, Power BI **27.2%**, no scored pick **2.4%**. Bengaluru shares: React **93.0%**, UI/UX **4.8%**, no scored pick **2.2%**. The bootstrap calculation itself took under one second per demo on this machine; the full app run includes separate parsing and course lookups. The earlier cutoff was 70% of samples; Batch D replaces it with three confidence levels. This is a sample-sensitivity measure, not a hiring probability. The older threshold stress check still notes that Power BI leads in Noida at threshold 0.6.

## Opportunity curve and exact budget check

The greedy planner picks the missing core skill with the most additional jobs per cached course hour, stopping after five skills or when no positive gain remains. Alternative tools satisfy the same requirement, and the experience filter is applied first. It never includes skills whose course hours are unknown.

| Demo | Greedy plan | Cumulative hours | Ready after plan | Hours unknown |
|---|---|---:|---:|---|
| Noida | SQL (+8), Power BI (+2) | 4.34, then 8.02 | 9, then 11 | Data Cleaning, Data Visualization |
| Bengaluru | React (+8), UI/UX (+3) | 5.09, then 15.88 | 15, then 18 | Git, REST API, Responsive Design |

The exact check exhausts all subsets of the top eight *measurable* missing core skills. Each bundled demo currently has only two such candidates. Values below count **additional** jobs, above those ready now.

| Budget | Noida greedy / exact | Noida ratio | Bengaluru greedy / exact | Bengaluru ratio |
|---:|---:|---:|---:|---:|
| 5 hours | 8 / 8 | 100% | 0 / 0 | N/A; no measured course fits |
| 10 hours | 10 / 10 | 100% | 8 / 8 | 100% |
| 15 hours | 10 / 10 | 100% | 8 / 8 | 100% |

The greedy algorithm is not guaranteed to be exact for other job sets. An offline hand-made test demonstrates a 75% greedy/optimal ratio at a two-hour budget.

## Skill distance

Distance is the minimum number of added core skills needed to cross the selected 0.5 readiness threshold, after alternatives. Only experience-eligible listings are counted. **Unknown** is a separate bin for listings with no detected core requirement; they do not enter readiness calculations.

| Demo | Ready (0) | 1 skill | 2 skills | 3+ skills | Unknown |
|---|---:|---:|---:|---:|---:|
| Noida | 1 | 14 | 2 | 0 | 3 |
| Bengaluru | 7 | 10 | 2 | 0 | 4 |

The app lists the one-skill-away jobs under their qualifying skill; a job can appear under more than one alternative skill while counting once in the distance bar.

## Three personas on both saved roles

The fresher and frontend fresher personas use the Fresher experience level; Mid uses 1–3 years. Ready counts are out of listings with detected core requirements.

| Saved role | Persona | Eligible | Ready | Top scored skill | Jobs unlocked |
|---|---|---:|---:|---|---:|
| Data Analyst, Noida | Fresher: Excel, basic Python | 20 | 1/17 | SQL | 8 |
| Data Analyst, Noida | Mid: SQL, Excel, Python, Tableau | 15 | 11/13 | None; apply or explore a senior role | 0 |
| Data Analyst, Noida | Frontend fresher: HTML, CSS, JavaScript | 20 | 0/17 | Power BI | 1 |
| Frontend Developer, Bengaluru | Fresher: Excel, basic Python | 23 | 0/19 | React | 2 |
| Frontend Developer, Bengaluru | Mid: SQL, Excel, Python, Tableau | 21 | 0/20 | React | 2 |
| Frontend Developer, Bengaluru | Frontend fresher: HTML, CSS, JavaScript | 23 | 7/19 | React | 8 |

The cross-role personas have low readiness, which is expected from their listed skills. The analyst Mid persona already matches most usable analyst listings, so the no-unlock message is more useful than another course recommendation.

## Verification and screenshots

- Offline tests: **29 passed** (including known greedy/optimal, alternatives plus experience, seeded bootstrap, and known distance counts).
- Streamlit cached demo rendered without an exception for both roles; chart captures are [Noida opportunity](../screenshots/batch_c_noida_plan.png), [Noida distance](../screenshots/batch_c_noida_distance.png), [Bengaluru opportunity](../screenshots/batch_c_frontend_plan.png), and [Bengaluru distance](../screenshots/batch_c_frontend_distance.png).
- Course hours and listing samples are saved snapshots; no live freshness is implied.
