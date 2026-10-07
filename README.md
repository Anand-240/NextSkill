# NextSkill

**Learn the one skill that unlocks the most real jobs, in the least time.**

## The problem

Students in smaller cities often guess what to learn next. Job descriptions list many skills, and a long list of courses does not answer the useful question: which **one** skill would put more nearby jobs within reach?

## How it works

NextSkill searches local Google Jobs listings, sets aside jobs above the selected experience level, extracts named skills, and marks a requirement as *core* when it appears in at least 25% of the eligible jobs. Fresher searches combine the base role with `<role> fresher` and `Junior <role>` first pages, then remove duplicate listings. The Search Replay shows which query produced each listing. It compares core requirements with a pasted resume, uploaded PDF, or manual skill list. BI tools, frontend frameworks, cloud providers, and explicit “X or Y” wording count as alternatives. For each missing, teachable skill, it counts jobs that cross the readiness threshold if that skill is added. It estimates study time from free YouTube courses and ranks by jobs unlocked per learning hour. A two-skill plan is also shown.

```mermaid
flowchart LR
    A[Role + city] --> B[Google Jobs via SerpApi]
    B --> C[Extract and count skills]
    C --> D[Core skills and resume coverage]
    D --> E[Jobs unlocked by one skill or a pair]
    E --> F[YouTube courses via SerpApi]
    F --> G[Estimated hours and jobs per hour]
```

The default readiness threshold is **50%**. The slider lets users choose a different threshold. Broad terms such as “Data Analysis” can contribute to coverage, but are excluded from recommendations. Listings with no detected core skills are ignored. Experience parsing is conservative: numeric minimums and seniority words in titles are used; ambiguous listings remain eligible. The robustness panel checks thresholds **0.4 / 0.5 / 0.6** and study-time multipliers **0.5 / 1.5**. The visible learning-hour range is an approximate ±25% band around the median course length.

## Why SerpApi is essential

The product needs current, local job descriptions and current free-course results. Without those two feeds, it cannot say which skills appear in jobs or estimate learning hours.

| SerpApi engine | Use |
|---|---|
| `google_jobs` | Fetch job titles, companies, descriptions, links, posting dates, and pagination for the selected Indian city. |
| `youtube` | Find free beginner courses and parse each video result's `length`, title, channel, and link. |

The free [Account API](https://serpapi.com/account-api) checks credit usage before and after a live run. Queries use the documented [Google Jobs](https://serpapi.com/google-jobs-api) and [YouTube](https://serpapi.com/youtube-search-api) parameters. YouTube's `sp` long-video filter helps narrow results; the app also checks titles and durations itself.

## Example output

With fresher query expansion, the saved Noida demo for an Excel and basic Python fresher has **20 eligible listings**, **17** with detected core requirements, and **1/17** within reach; **14** listings need more experience. **SQL** could unlock **8** jobs. It is a **Likely** pick, winning **60.4%** of 500 resamples with the expanded course set. The saved Bengaluru demo for an HTML/CSS/JavaScript fresher has **23 eligible listings**, **19** with detected core requirements, and **7/19** within reach; **22** need more experience. **REST API** could unlock **8** jobs and is a **Strong** pick, winning **93.6%** of resamples. These are saved job snapshots, not a current live search.

![Data Analyst, Noida demo](screenshots/batch_d_noida.png)

![Frontend Developer, Bengaluru demo](screenshots/batch_d_frontend.png)

![Noida opportunity curve](screenshots/batch_d_noida_plan.png)

![Bengaluru opportunity curve](screenshots/batch_d_frontend_plan.png)

[Noida skill distance](screenshots/batch_c_noida_distance.png) · [Bengaluru skill distance](screenshots/batch_c_frontend_distance.png)

The [Batch D report](reports/batch_d_report.md) contains the expanded plan, exact budget comparison, confidence shares, and credit usage. Earlier [Batch C](reports/batch_c_report.md), [Batch B](reports/batch_b_report.md), and [Batch A](reports/batch_a_report.md) reports preserve the results from those stages.

The [Search Replay screenshot](screenshots/batch_b_replay.png) shows cached query variants and listing origins.

## How NextSkill plans your learning

The opportunity curve starts with jobs already within reach. At each step, it adds the missing core skill that opens the most *additional* jobs per estimated learning hour, for up to five skills. Alternative tools satisfy the same requirement, and jobs above the selected experience level are excluded. Skills without a cached course duration appear under **Hours unknown** and do not enter this hours-based plan. The plan table shows each step, an approximate hour range, jobs gained, and the running total.

For a quality check, NextSkill tries every subset of the top eight measurable missing skills under budgets of **5, 10, and 15 hours**. The current saved Noida demo has **four** measurable candidates; greedy reaches **100% / 90.9% / 100%** of the exact additional-job gain at those budgets. Bengaluru has **three** measurable candidates; greedy reaches **100% / 91.7% / 100%**. These figures describe only these saved listings, candidate skills, course lengths, and budgets. They show that the greedy choice can miss a better combination.

The bootstrap confidence line samples eligible listings with replacement **500 times**, with a fixed seed, and reruns core-skill selection and the top-pick ranking. With the expanded saved course set, SQL wins **60.4%** of Noida resamples and REST API wins **93.6%** of Bengaluru resamples. Labels are **Strong** (at least 85%), **Likely** (60% to below 85%), and **Uncertain** (below 60%). This measures sensitivity to the sampled listings, not the chance of getting hired. UI/UX counts for matching but is too broad to recommend as a course; the skill-distance chart counts jobs that are already within reach or need one, two, or at least three extra core skills. **Unknown** means the dictionary found no core requirement in that job.

| Saved role | Persona | Ready / usable jobs | Top scored skill | Jobs unlocked |
|---|---|---:|---|---:|
| Noida analyst | Fresher: Excel, basic Python | 1/17 | SQL | 8 |
| Noida analyst | Mid: SQL, Excel, Python, Tableau | 11/13 | None; focus on applications | 0 |
| Noida analyst | Frontend fresher: HTML, CSS, JavaScript | 0/17 | Power BI | 1 |
| Bengaluru frontend | Fresher: Excel, basic Python | 0/19 | React | 2 |
| Bengaluru frontend | Mid: SQL, Excel, Python, Tableau | 0/20 | React | 2 |
| Bengaluru frontend | Frontend fresher: HTML, CSS, JavaScript | 7/19 | REST API | 8 |

Fresher personas use the Fresher experience filter; Mid uses 1–3 years. The mismatched cross-role personas show low readiness, as expected.

## Validation

- The initial **GREEN** check found **19 / 15 / 19** unique listings for Data Analyst Noida, Python Developer Bengaluru, and Marketing Intern Pune; all **19 / 15 / 19** had descriptions of at least 300 characters. YouTube returned parseable durations for the checked videos. See the [validation report](reports/validation_check.md).
- A 20-match, hand-reviewed skill audit improved precision from **16/20 (80%)** to **16/16 retained matches (100%)** after context filters. See the [matcher audit](reports/matcher_audit.md). This small audit does not measure recall.
- Requiring course-like titles and longer videos changed the saved Power BI learning estimate from **~0.51 to ~3.68 hours**.
- On the same Noida resume at a 0.4 threshold, core-skill coverage changed readiness from **1/16 to 10/17** usable jobs. At the newer default 0.5 threshold, the analyst fresher is ready for **2/17** and the frontend fresher for **8/28** jobs on their matching roles.
- Batch A adds experience filtering and substitute skills. At the 0.5 threshold, the saved analyst fresher changes from **2/17** to **1/8** usable jobs (**9** experience exclusions); the frontend fresher changes from **8/28** to **2/11** (**17** exclusions). These denominators changed because ineligible jobs are now shown separately. Its threshold checks preceded the current bootstrap confidence labels.
- Batch B spot-checked 15 previous experience exclusions: **14/15 (93.3%)** had defensible trigger evidence; after removing one malformed “25 Years” trigger, **14/14 retained (100%)** did. This is evidence precision on a small sample, not a measure of actual hiring eligibility. Fresher query expansion changed the current cached demos to **1/17 ready** for Noida and **7/19 ready** for Bengaluru, with **20** and **23** eligible listings respectively. The four new Google Jobs searches used four credits, leaving eight.
- Batch C adds the opportunity curve, exact budget check, bootstrap confidence, and skill-distance map using bundled data only. Its figures used two measured candidates per role. See the [Batch C report](reports/batch_c_report.md).
- Batch D adds four cached course searches. With four measurable Noida skills and three Bengaluru skills, greedy is below the exact maximum at the 10-hour budget in both demos. The searches used **4 credits**, leaving **4** in the checked account. See the [Batch D report](reports/batch_d_report.md).
- A [match sanity check](reports/match_sanity_check.md) lists the exact cached-job text behind every Bengaluru REST API and Responsive Design match and every Noida Data Cleaning match. It found no ordinary-word “rest” false match; the two demo plans were unchanged.

## Limitations

- Learning hours are estimates from free course lengths; watching a course does not prove mastery.
- Job descriptions rarely separate required skills from nice-to-have skills, so keyword matches and readiness are approximate.
- City samples can be small. The app warns when fewer than 12 distinct jobs are found; Noida's third page returned no listings in the Phase 2 check.
- A job being “within reach” does **not** promise an interview or a job.
- Broad course queries can return adjacent topics; review the linked videos before following a plan.
- Experience minimums inferred from requirement-style text or titles can miss unusual wording, and “3+ years” is an open-ended input bucket. An unlabelled job is kept eligible. Search locations can include nearby cities.
- PDF extraction works on PDFs with selectable text. Scanned image PDFs need pasted text; no OCR is included.
- The robustness label uses only skills with cached, parseable course durations. The confidence badge measures sample size, not prediction accuracy.
- The exact budget comparison covers at most eight skills with known course lengths. In the current bundled demos, only four Noida and three Bengaluru candidates have usable hours. The bootstrap percentages describe variation in these saved listings, not a hiring probability.

## Setup

Requires Python 3.10+.

```sh
cd nextskill
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
# Put your SerpApi key in .env as SERPAPI_KEY=your_key
.venv/bin/streamlit run app.py
```

**Demo data** is selected by default and reads bundled JSON from `demo_data/`, including Noida and Bengaluru base jobs, fresher/junior variants and YouTube course durations. It works on a fresh clone without `.env` or `cache/`, and makes no SerpApi calls. Choose a demo role, use the sample resume, paste your own, list skills, or upload a text-based PDF; select an experience level and then **Find my next skill**. Without a key, Live search is disabled and the app says “Live search needs a SerpApi key. Demo data is shown.” With a key in `.env`, the `SERPAPI_KEY` environment variable or Streamlit secrets, **Live search** lets you enter another role and city. It spends credits only when you start a search; the sidebar shows the live request budget and the app shows account credits before and after. Live responses are cached and replayed on repeated queries. The demo live-request cap is six attempted searches, with a 75-second timeout and no retry on timeout. `.env` and `cache/` are Git-ignored.

## Streamlit Community Cloud

Deploy `app.py` from the repository root. Demo mode requires no secrets. To enable Live search, add `SERPAPI_KEY` as a private app secret in Streamlit Community Cloud. Do not put the key in the repository.

## Tech stack and tests

Python standard library for the engine and HTTP client, Streamlit and Altair for the UI charts, pypdf for resume PDFs, and local JSON fixtures for offline tests. To run the tests from `nextskill/`:

```sh
PYTHONPATH=. .venv/bin/python -m unittest discover -s tests -q
```

The test suite runs without SerpApi calls. Playwright is used only to capture screenshots for the demo; install `requirements-dev.txt` for that workflow.

GitHub Actions runs the offline suite on every push and pull request using `.github/workflows/tests.yml`.

## AI tools used

OpenAI Codex assisted with implementation, test writing, analysis, and documentation. The running app does not call an LLM. Skill matching and ranking are deterministic Python code.

## Licence

[MIT](LICENSE).
