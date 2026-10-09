# NextSkill Phase 2: number check

## Credits and data

Account API `this_month_usage`: 228 → 238 (change 10).
Phase 2 real search requests attempted: 12 of 12 maximum; all search responses are cached. Account checks were free.
The four headline course skills were Data Analysis, Power BI, React and TypeScript. Power BI reused the saved validation response. Additional cached course searches for Tableau and UI/UX support the two-skill plans; SQL supports the analyst-fresher sanity check.
Noida: 20 raw results, 19 distinct listings. A third page was requested but returned zero results. Frontend Bengaluru: 30 raw results, 29 distinct listings across three pages. Neither query triggers the <12-job limited-data warning.

## Noida before and after

Same resume: Excel, SQL basics, Python basics. Same 0.4 readiness threshold; Phase 1 used the two saved Noida pages, and the Phase 2 third page added no listings.

| Measure | Phase 1 | Phase 2 |
|---|---|---|
| Ready jobs | 1 of 16 usable | 10 of 17 usable |
| Power BI learning estimate | ~0.51h from short tutorials | ~3.68h from three qualifying course videos |
| Top 3 ranked skills | Power BI (+4); Data Visualization (+3, hours unavailable); Tableau (+3, hours unavailable) | Power BI (+4, ~3.68h, 1.09 jobs/h); Tableau (+5, ~6.00h, 0.83 jobs/h); Data Analysis (+2, ~7.19h, 0.28 jobs/h) |
| Best two-skill plan | not available | Tableau + Machine Learning unlocks 7 jobs; combined hours unavailable because one skill lacks cached course data |

The 0.4 pair's hours remain unavailable under the 12-call cap because Machine Learning has no cached qualifying course search. At the required default 0.7 threshold, Phase 2 has 1 of 17 ready; its two-skill plan is Data Analysis + Tableau unlocks 9 jobs; ~13.19 combined hours; 0.68 jobs/hour.

## Demo rankings

- **Data Analyst, Noida** (sample resume, 0.4): ready 10/17. Power BI (+4, ~3.68h, 1.09 jobs/h); Tableau (+5, ~6.00h, 0.83 jobs/h); Data Analysis (+2, ~7.19h, 0.28 jobs/h); Data Visualization (+4, hours unavailable); Machine Learning (+4, hours unavailable). Pair: Tableau + Machine Learning unlocks 7 jobs; combined hours unavailable because one skill lacks cached course data.
- **Frontend Developer, Bengaluru** (frontend fresher, 0.7): ready 1/28. React (+3, ~5.09h, 0.59 jobs/h); TypeScript (+2, ~3.90h, 0.51 jobs/h); UI/UX (+1, ~10.78h, 0.09 jobs/h); Angular (+1, hours unavailable); CI/CD (+1, hours unavailable). Pair: React + UI/UX unlocks 8 jobs; ~15.88 combined hours; 0.50 jobs/hour.

## Persona sanity check (default threshold 0.7)

| Role | Persona | Ready | Top skills | Two-skill plan |
|---|---|---:|---|---|
| Data Analyst | Fresher | 0/17 | Power BI (+1, ~3.68h, 0.27 jobs/h); SQL (+1, ~4.34h, 0.23 jobs/h); Tableau (+1, ~6.00h, 0.17 jobs/h) | SQL + Data Analysis unlocks 5 jobs; ~11.53 combined hours; 0.43 jobs/hour |
| Data Analyst | Mid | 3/17 | Power BI (+6, ~3.68h, 1.63 jobs/h); Data Analysis (+7, ~7.19h, 0.97 jobs/h); Machine Learning (+3, hours unavailable) | Power BI + Machine Learning unlocks 11 jobs; combined hours unavailable because one skill lacks cached course data |
| Data Analyst | Frontend fresher | 0/17 | Tableau (+1, ~6.00h, 0.17 jobs/h); Machine Learning (+2, hours unavailable) | Machine Learning + Tableau unlocks 3 jobs; combined hours unavailable because one skill lacks cached course data |
| Frontend Developer | Fresher | 0/28 | React (+1, ~5.09h, 0.20 jobs/h); UI/UX (+1, ~10.78h, 0.09 jobs/h) | React + UI/UX unlocks 2 jobs; ~15.88 combined hours; 0.13 jobs/hour |
| Frontend Developer | Mid | 0/28 | React (+1, ~5.09h, 0.20 jobs/h); UI/UX (+1, ~10.78h, 0.09 jobs/h) | React + UI/UX unlocks 2 jobs; ~15.88 combined hours; 0.13 jobs/hour |
| Frontend Developer | Frontend fresher | 1/28 | React (+3, ~5.09h, 0.59 jobs/h); TypeScript (+2, ~3.90h, 0.51 jobs/h); UI/UX (+1, ~10.78h, 0.09 jobs/h) | React + UI/UX unlocks 8 jobs; ~15.88 combined hours; 0.50 jobs/hour |

### Sanity flags

- Analyst fresher has SQL and Power BI among scored suggestions; the mid analyst has Power BI and Data Analysis. Frontend fresher has React and TypeScript. Those match the intended roles.
- Default 0.7 coverage remains stringent: the analyst fresher is ready for 0/17 and frontend fresher for 1/28. The model follows the requested core-skill formula; it should not be described as a hiring probability.
- A frontend-only resume applied to analyst jobs produces an irrelevant Tableau suggestion because one job has few core requirements. The app should treat cross-role recommendations cautiously.
- The broad Data Analysis query includes Excel-focused courses. Its hour estimate is useful as a rough curriculum length, but course-topic relevance needs further review before a public demo.
- Some valid unlocks have no course estimate after the capped searches (for example Machine Learning). They remain visible with unavailable hours, rather than receiving invented scores.

## Course evidence

Titles must include full course, complete, course, masterclass, or bootcamp and run at least 60 minutes. The median uses up to the first three qualifying results. If fewer than two qualify, videos of at least 30 minutes supply a low-confidence estimate. The SerpApi YouTube `sp` long-video filter was used on new queries and local checks enforce the stricter rule.

### Power BI — ~3.68h (standard confidence)

- [Power BI for Data Analytics - Full Course for Beginners](https://www.youtube.com/watch?v=FwjaHCVNBWA) — Luke Barousse, 8:24:31
- [Power BI FULL COURSE for Beginners | Learn Dashboards & Reports Fast!](https://www.youtube.com/watch?v=Dk25lwdTKow) — Pragmatic Works, 3:40:48
- [Power BI Full Course 2025: Complete Beginner to Advanced Tutorial in English](https://www.youtube.com/watch?v=_76bzIuz-dU) — WsCube Tech! ENGLISH, 3:26:00

### Tableau — ~6.00h (standard confidence)

- [Tableau Ultimate Full Course (21 Hours) for Beginners - From Zero to HERO](https://www.youtube.com/watch?v=K3pXnbniUcM) — Data with Baraa, 20:47:05
- [Tableau Full Course - Learn Tableau in 6 Hours | Tableau Training for Beginners | Edureka](https://www.youtube.com/watch?v=aHaOIvR00So) — edureka!, 6:00:14
- [Tableau Full Course - Learn Tableau In 6 Hours | Tableau Training for Beginners | Simplilearn](https://www.youtube.com/watch?v=HGMrIZq5dq0) — Simplilearn, 5:34:49

### Data Analysis — ~7.19h (standard confidence)

- [Excel for Data Analytics - Full Course for Beginners](https://www.youtube.com/watch?v=pCJ15nGFgVg) — Luke Barousse, 10:59:43
- [Data Analytics Tutorial For Beginners Complete Course | Foundations: Data, Data, Everywhere, Google](https://www.youtube.com/watch?v=vqZ1C2elmac) — My Lesson, 2:35:41
- [Excel Data Analysis Full Course Tutorial (7+ Hours)](https://www.youtube.com/watch?v=qrbf9DtR3_c) — Learn Skills Daily, 7:11:22

### React — ~5.09h (standard confidence)

- [React Tutorial Full Course - Beginner to Pro (React 19, 2025)](https://www.youtube.com/watch?v=TtPXvEcE11E) — SuperSimpleDev, 11:32:04
- [React Full Course for free ⚛️](https://www.youtube.com/watch?v=CgkZ7MvWUAA) — Bro Code, 4:43:02
- [Learn React JS - Full Course for Beginners - Tutorial 2019](https://www.youtube.com/watch?v=DLX62G4lc44) — freeCodeCamp.org, 5:05:34

### TypeScript — ~3.90h (standard confidence)

- [Learn TypeScript - Full Course for Beginners](https://www.youtube.com/watch?v=SpwzRDUQ1GI) — freeCodeCamp.org, 2:06:13
- [TypeScript Full Course for Beginners | Complete All-in-One Tutorial | 8 Hours](https://www.youtube.com/watch?v=gieEQFIfgYc) — Dave Gray, 8:21:57
- [TypeScript Full Course - From Beginner to Advanced](https://www.youtube.com/watch?v=iJkaAJUzeWQ) — Tech With Tim, 3:54:02

### UI/UX — ~10.78h (standard confidence)

- [The 2025 UI/UX Crash Course for Beginners - Learn Figma](https://www.youtube.com/watch?v=cvm_ECH94x4) — DesignCourse, 1:04:56
- [UI UX Design Full Course (2026) | UI/UX Design Course For Beginners | Intellipaat](https://www.youtube.com/watch?v=NeUEctMZ6_g) — Intellipaat, 10:47:03
- [UI/UX Design Course For Beginners | UI/UX Design Tutorial For Beginners](https://www.youtube.com/watch?v=pyQAiRuqUSM) — Nerd's Academy, 11:50:38

### SQL — ~4.34h (standard confidence)

- [SQL Course for Beginners [Full Course]](https://www.youtube.com/watch?v=7S_tz1z_5bA) — Programming with Mosh, 3:10:19
- [SQL Tutorial - Full Database Course for Beginners](https://www.youtube.com/watch?v=HXV3zeQKqGY) — freeCodeCamp.org, 4:20:39
- [SQL Full Course for Beginners (30 Hours) – From Zero to Hero](https://www.youtube.com/watch?v=SSKVgrwhzus) — Data with Baraa, 29:48:28

## Verification

Nine offline unit tests passed, covering core selection, pair planning, course filtering and fallback, limited data, matching, freshness, deduplication and ranking. Run: `PYTHONPATH=nextskill python3 -m unittest discover -s nextskill/tests -q`.
Streamlit rendered both cached demos end to end: [Noida screenshot](../../screenshots/archive/phase2_noida.png) and [Frontend screenshot](../../screenshots/archive/phase2_frontend.png).

Documentation checked: [Google Jobs API](https://serpapi.com/google-jobs-api), [YouTube Search API](https://serpapi.com/youtube-search-api), [SerpApi filter guidance](https://serpapi.com/blog/youtube-sp-filters-paginating-sorting-and-filtering-with-the-youtube-api/), [YouTube video fields](https://serpapi.com/youtube-video-results).
