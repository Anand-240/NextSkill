# Batch D: expanded course hours and learning plan

SerpApi's free Account API showed **8 credits before** and **4 credits after**. Monthly usage moved from **242 to 246**: **4 real YouTube search calls**, no Google Jobs calls. Each response is cached and bundled into `demo_data/`, so Demo mode can replay it with no key. The account checks did not consume search credits. The searches used SerpApi's documented `youtube` engine, `search_query`, India `gl`, English `hl`, and `sp` long-video filter; video lengths came from `video_results.length`. See the [YouTube API](https://serpapi.com/youtube-search-api), [video result fields](https://serpapi.com/youtube-video-results), and [Account API](https://serpapi.com/account-api).

## Added course estimates

Each estimate is the median duration of the first three matching course-like videos at least one hour long. All four have standard confidence under the app's video filter.

| Demo role | Missing core skill | Estimated hours | Search calls |
|---|---|---:|---:|
| Data Analyst, Noida | Data Cleaning | 3.49 | 1 |
| Data Analyst, Noida | Data Visualization | 5.47 | 1 |
| Frontend Developer, Bengaluru | REST API | 2.33 | 1 |
| Frontend Developer, Bengaluru | Responsive Design | 2.80 | 1 |

UI/UX is now treated as a generic umbrella skill: it can contribute to coverage, but it cannot appear in a recommendation, pair, opportunity curve, or bootstrap win. A specific named tool such as Figma remains recommendable if a listing supports it.

## Updated fresher plans and curve points

At the default 0.5 readiness threshold, the Noida Excel/basic Python fresher is ready for **1 of 17** usable jobs; the Bengaluru HTML/CSS/JavaScript fresher is ready for **7 of 19**. Jobs above Fresher experience are excluded before these calculations.

| Demo | Curve points: cumulative hours → jobs within reach | Final plan gain | Hours still unknown |
|---|---|---:|---|
| Noida | 0h → 1; SQL 4.34h → 9; Data Cleaning 7.84h → 11; Power BI 11.52h → 13 | +12 | None among current missing core options |
| Bengaluru | 0h → 7; REST API 2.33h → 15; Responsive Design 5.13h → 18; React 10.22h → 19 | +12 | Git |

The plan takes the largest *additional jobs per hour* at each step. The UI shows rounded hour ranges and the source videos next to course estimates; course length is not a promise of mastery or a job.

## Greedy vs exact budget check

The exact comparison tests every subset of **four measurable Noida candidate skills** and **three measurable Bengaluru candidate skills**. These are the current candidate counts, not a general benchmark. Gains are additional jobs beyond those ready now.

| Budget | Noida greedy / exact | Greedy share | Bengaluru greedy / exact | Greedy share |
|---:|---:|---:|---:|---:|
| 5 hours | 8 / 8 | 100% | 8 / 8 | 100% |
| 10 hours | 10 / 11 | **90.9%** | 11 / 12 | **91.7%** |
| 15 hours | 12 / 12 | 100% | 12 / 12 | 100% |

At 10 hours, Noida's exact set is SQL + Data Visualization; greedy chooses SQL + Data Cleaning. Bengaluru's exact set is React + Responsive Design; greedy chooses REST API + Responsive Design. This demonstrates the expected limitation of a stepwise greedy plan on these saved listings.

## Bootstrap confidence

Bootstrap resamples the same eligible listings 500 times with a fixed seed and recomputes the top scored skill. Labels now use **Strong ≥85%**, **Likely 60% to below 85%**, and **Uncertain <60%**. They describe stability across saved listing samples, not hiring probability.

| Demo | Top scored skill | Wins | Other outcomes | Label |
|---|---|---:|---|---|
| Noida | SQL | 60.4% | Power BI 22.8%; Data Cleaning 15.2%; no scored pick 1.2%; Data Visualization 0.4% | Likely |
| Bengaluru | REST API | 93.6% | Responsive Design 4.8%; React 1.6% | Strong |

## Verification

- **32 offline tests passed**, including bundled course replay, the confidence thresholds, UI/UX exclusion, alternatives, experience filtering, greedy vs exact on a known counterexample, and bootstrap reproducibility.
- Both saved Streamlit demos rendered without an exception. See [Noida overview](../screenshots/batch_d_noida.png), [Noida curve](../screenshots/batch_d_noida_plan.png), [Bengaluru overview](../screenshots/batch_d_frontend.png), and [Bengaluru curve](../screenshots/batch_d_frontend_plan.png).
- **4 credits remain** for the demo recording as checked after these calls; no further SerpApi calls were made in this batch.
