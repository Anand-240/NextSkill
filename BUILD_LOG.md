# NextSkill build verification

Started 2026-10-09 15:51 IST. Feature cutoff: 2026-10-10 12:00 IST.
Baseline: ae9c548; 69 offline tests pass; GitHub CI success at that commit.
Initial Account API: 250 searches left, this_month_usage 0. Search budget 160;
phase caps C 105 (revision 15), D 30, H 5; all other phases zero searches.
Current-key and real-looking api_key history scan: 409 objects, zero findings.
The existing app remains the entry point until replacement pages pass.

## A1 - Submission requirements

- Research: read the official rules and terms, linked in research/RESEARCH.md.
- Plan/acceptance: map submission, eligibility, public-material and rights requirements;
  mark participant actions pending rather than claiming compliance.
- Build: added the requirements map and this evidence log.
- Test: baseline full offline suite: 69 tests, OK (3.234 seconds).
- Verify: public repo and baseline CI checked; demo video and submission not verified.
  Reviewed documentation diff; no app changes. Account usage before A: 0 / 250 left.
- Record: this section accompanies the A1 commit; human actions remain explicit.

## A2 - API contracts

- Research: current Jobs, YouTube search/video, Google web search and Account docs;
  links and exact request/response contracts are in research/RESEARCH.md.
- Plan/acceptance: check names, pagination, filters, timeout and empty-result behavior
  against engine.py. Record unsupported assumptions explicitly.
- Build: added the API contract table. YouTube uses search_query, not q. Duration
  acceptance is checked locally; duration-token stability is not guaranteed by docs.
- Test: full offline suite remains 69 tests, OK.
- Verify: inspected fetch_jobs, course_videos, revision_params, _request, _check_error;
  existing transport parameters agree. B1/B3/B4 address product logic, not transport.
- Record: no search calls; diff reviewed before commit.

## A3 - Problem evidence

- Research: four primary institutional sources (ILO/IHD, World Bank, UNICEF) opened
  and linked; no unsupported price or employment statistic adopted.
- Plan/acceptance: three to five relevant credible sources, with scope and limitations.
- Build: documented four sources, separating institutional findings from our hypothesis.
- Test: full offline suite: 69 tests, OK.
- Verify: every source linked; no invented beneficiaries, outcome numbers or quotes.
  Diff reviewed. A1-A3 completed inside the one-hour timebox.
- Record: zero search calls. A4/A5 remain deferred per priority order.

### Phase A checkpoint (A1-A3)

Account before/after: usage 0 -> 0; searches left 250 -> 250. Search calls: 0.
A1 and A2 CI succeeded. A3 CI verified before proceeding. Applicable gates: H1
69 tests pass; H4 initial 409-object history scan clean; H5 research sources opened.
A4/A5 deferred by the requested priority order.

## B1 - Rank all saved measurable candidates

- Research: rank_skills and sensitivity checks sliced candidates before ranking.
- Plan/acceptance: a low-unlock skill outside the fetch shortlist must win when its
  saved course is shorter; preserve the cap on new requests.
- Build: rank every candidate, using cache-only lookup beyond the live shortlist;
  bootstrap and hour variation consider all measured candidates too.
- Test: new counterexample test (SQL +1 / 0.5h beats Python +2 / 10h); full suite 70 tests.
- Verify: unknown durations stay unscored; cache-only probe cannot call the network.
  Reviewed diff. Phase B uses zero searches; account baseline usage 0 / 250 left.
- Record: result changes will be regenerated and compared at B7.

B1 verification correction: the first run exposed budget-label gaps and an honest
Noida bootstrap change from 56.2% to 56.4%. Fixed unknown-hour budget labels,
regenerated golden results (generator introduced early for evidence), and updated
current prose. Archived the original golden file; no results tuned to preserve it.

## B2 - Stated must-haves

- Research: coverage treats all detected requirements equally; explicit wording was
  used only for Job Prep ordering. Read skills.py sentence and preference handling.
- Plan/acceptance: preserve coverage matches and report yes/no/none stated separately;
  test must, mandatory, required, essential, minimum, negation and alternatives.
- Build: explicit sentence requirements independent of market frequency; headline
  counts among coverage matches, listing evidence and Job Prep status; README definition.
- Test: 72 full-suite tests pass; Excel-only profile matches SQL-required/Excel listing
  at 50% but correctly gets must-haves status no. Every phrase and OR choice tested.
- Verify: generated golden results; no coverage counts changed. Diff reviewed.
- Record: no search requests; heuristic limitation retained.

## B3 - Nonfatal account telemetry

- Research: account requests before and in finally could prevent result assignment.
- Plan/acceptance: account failure must leave successful live results in session state
  and show Credit balance unavailable; mocked UI test, no real search.
- Build: safe_account returns unavailable on transport/parser errors. Store result
  before the trailing account check; both pre/post balance failures are nonfatal.
- Test: mocked live UI account failure added; full suite 73 tests passes.
- Verify: result remains rendered and retained, no app exception. Diff reviewed.
- Record: zero searches.

## B4 - Course title relevance

- Research: the old selector admitted any course-like title and duration, including
  titles that did not name the requested skill. Reviewed saved selected videos.
- Plan/acceptance: guarded skill/alias title match, duplicate-link removal, low
  confidence below two full courses, new relevance test and removal report.
- Build: shared names_skill check for course/revision titles; preserved language and
  fallback rules. Generated documents/results introduced early to avoid stale claims.
- Test: 74 tests; changed old assertions that assumed the pre-fix winners. Mocked
  budget fixtures now return the requested skill so they test budgets independently.
- Verify: removed selected videos listed in reports/course_relevance.md. Bengaluru
  winner now Responsive Design at 0.84h (low course confidence); Noida winner SQL.
  An exact title match still does not prove stack suitability or audio language.
  Golden-result test and UI agree. Diff reviewed; no claims tuned to old numbers.
- Record: no searches. Old results preserved in reports/archive/pre_complete_build.json.

## B5 - Shortest route and full prep

- Research: build_plan totals every missing core skill even when one crosses the
  selected threshold; course lookup already supports saved hours.
- Plan/acceptance: separate minimum measured course hours from complete prep; a
  known four-requirement example must choose the cheapest sufficient skill.
- Build: exact subset search over up to 12 measured missing skills; already-match,
  unknown-duration and no-measured-route states; full plan stays visible.
- Test: cheapest-sufficient-skill regression added; full suite 75 tests passes.
- Verify: UI exposes both plans and candidate-bound caveat. No live lookup added;
  existing prep uses cache-only clients. Diff reviewed.
- Record: zero searches.

## B6 - Clear and qualified wording

- Research: additive skills field said Or; headline caveats were separated; exact
  comparison label omitted its candidate limit.
- Plan/acceptance: requested local-listings pitch, Add more skills, snapshot and
  confidence together beside headline, exact among measured skills throughout active UI.
- Build: updated labels and explanatory text; generated README/DEMO already use
  local snapshots and qualified exact comparisons.
- Test: full suite 75 tests passes; active app/README/DEMO grep has no old pitch,
  today's jobs, Or list skills or unqualified exact-budget heading.
- Verify: AppTest headline/caption checks pass; historical files retained as history.
  Diff reviewed. Zero searches.

## B7 - Recomputed demos

Research: compared original golden data with all B fixes. Plan/acceptance: regenerate
from saved inputs, retain changed winners, pass golden tests and update documents.
Build: ran build_results and render_docs. Test: full offline suite, 75 tests pass.
Verify: engine, generated JSON, README and DEMO share the same current results.

| City | Matches before/after | Winner before | Winner after | Bootstrap after | Hour variation after |
|---|---|---|---|---|---|
| Bengaluru | 9/9 | REST API | Responsive Design | 90.4% | 95.7% |
| Noida | 1/1 | Data Cleaning | SQL | 57.6% | 47.3% |

Diff reviewed. No search calls. Current requirements and videos remain linked;
old screenshots are historical and will be replaced at the page screenshot gates.

### Phase B checkpoint

B7 CI succeeded at 466b991. Account usage 0 -> 0, searches left 250 -> 250.
H1: 75 tests pass; H2: both golden demos pass; H4: every push staged scan passed.
No network search was used. Ranking and course-rule result changes are retained.

## C1 - Fill existing unknown course hours

- Research: offline analysis found only Git without saved hours in the existing
  demos. Current YouTube contract documented at A2.
- Plan/acceptance: fetch that missing response once, redact it, rerun both demos,
  and disclose any changed winner. Durable attempt counter guards phase/total caps.
- Build: added budgeted build-only client; reuses exact saved responses and local
  cache; counts before requests and never retries. Saved Git course response.
- Test: regenerated golden data/documents; full offline suite 75 tests passes.
- Verify: Git 3.726111 hours, three qualifying videos, standard duration confidence.
  New calls: 1. Fastest winners remain Responsive Design and SQL. Diff reviewed.
- Record: C Account baseline usage 0 / 250 left; phase cap 105, total 160.

## C2 - Eight-pair priority snapshot collection

- Research: used documented role/city Jobs requests and shared course queries;
  reused the two existing snapshots and saved courses.
- Plan/acceptance: at least eight pairs, tier-2 cities, non-developer work and an
  honest limited-data case; all run offline. Remaining seven pairs deferred.
- Build: added six pairs, saved manifest and budgeted collection script. Dehradun
  deliberately uses one base page; this scope is disclosed, not presented as a census.
- Test: every saved pair runs with network blocked; golden data regenerated.
- Verify: eligible counts: Bengaluru frontend 23, Noida analyst 20, Hyderabad analyst
  16, Pune analyst 14, Jaipur analyst 17, Indore analyst 5, Jaipur accountant 14,
  Dehradun marketing 5. Limited-data flags on Indore and Dehradun.
- Record: step uses durable phase ledger; exact attempts in reports/build_usage.json.
  Responses redacted before saving. Diff reviewed. Extra pairs deferred by priority.

## C3 - Redacted responses and provenance

- Research: response text can contain recruiter contacts; source URLs and opaque IDs
  may contain digits that are not phone numbers. Retrieval dates drive age calculations.
- Plan/acceptance: strip key/account fields, redact email/Indian phone text, preserve
  source links, require retrieval timestamps and scan all responses.
- Build: added repeatable response scanner and redaction/budget regression tests.
- Test: 78 full-suite tests pass, including redaction and stopping before a cap breach.
- Verify: 67 demo/fixture response files scanned; zero contact/timestamp findings.
  Existing URLs are preserved and excluded only from phone-pattern detection, not
  email checks. New data is scrubbed before disk writes. Diff reviewed.
- Record: no additional searches.

## C4 - Shared sample personas

- Research: sample resumes were duplicated in UI, collection and result scripts.
- Plan/acceptance: one role-default config, consumed by UI, collection, tests and
  golden generation; sample personas must not be described as real participants.
- Build: config/personas.json and personas.saved_pairs merge defaults with manifest;
  removed duplicated resume fields from manifest and collection script.
- Test: 78 full-suite tests pass; all eight saved pairs use configured defaults.
- Verify: legacy app still opens correctly; collection and generator share config.
  Diff reviewed. No searches.

## Handoff to a new agent

Taken over 2026-10-09 16:26 IST. Feature freeze: 2026-10-10 12:00 IST (about 19.5 hours).
Last pushed commit: 4235a58 (local main equals origin/main). CI at that commit: success.
Offline suite at takeover: 78 tests, OK. Uncommitted at takeover: research/RESEARCH.md
(14 added lines of Streamlit implementation references, correct, kept).

Credits (Account API, free call): this_month_usage 23, total_searches_left 227.
The plan's 160 cap leaves 137; the 90-search floor also leaves 137. Remaining budget: 137.
Ledger (reports/build_usage.json): 23 attempts, all phase C (16 jobs, 7 course).
Phase C remaining: 82 (of 105), of which revision videos 15.

| Step | Status | Evidence / gap |
|---|---|---|
| A1 | DONE | research/RESEARCH.md A1, commit 1b69d2e |
| A2 | DONE | A2 contract table, c95181f |
| A3 | DONE | four primary sources, 6502c59 |
| A4 | NOT STARTED | landscape comparison |
| A5 | NOT STARTED | NPTEL/SWAYAM site: check |
| B1-B7 | DONE | sections above; tests 75 at B7; golden data regenerated |
| C1 | DONE | Git hours filled, 1 call |
| C2 | PARTIAL | 8 pairs saved (needs tier-2, non-dev, low-data: all present); about 7 of the 15 target pairs not collected |
| C3 | DONE | scan_data.py, redaction tests |
| C4 | DONE | config/personas.json |
| C5 | NOT STARTED | revision videos |
| C6 | NOT STARTED | default Job Prep listing per pair |
| D1, D2 | NOT STARTED | |
| E1-E8 | NOT STARTED | app.py is still the single page |
| F1-F3 | NOT STARTED | no evaluation/ directory |
| G1 | PARTIAL | scripts/build_results.py exists and writes reports/final_results.json |
| G2 | NOT STARTED | no check_consistency.py, not in CI |
| H1 | PASS now | 78 tests, CI green |
| H2-H8 | NOT STARTED | |
| I1-I5 | NOT STARTED | README/DEMO exist from earlier phases |

## C5 - Revision videos for persona skills

- Research: Job Prep marks a held skill "revise" and looks up `<skill> revision` with the
  4-20 minute YouTube duration filter (A2 table). Only skills the saved personas already
  hold can appear as revise items, and CSS and JavaScript were already saved.
- Plan/acceptance: fetch only the missing persona skills (deduplicated across pairs),
  redact and save, then every saved persona skill has a revision response. Cap 15.
- Build: scripts/fetch_revision.py computes the missing list from the saved pairs and uses
  the budgeted build client. Fetched Accounting, Canva, Excel, HTML, Python, Social Media
  Marketing. Git (Python Developer persona) is not fetched because no saved pair uses it yet.
- Test/verify: existing selector (5-25 minutes, skill/alias in title, revision-style wording,
  no exam topics, language filter) kept; 79 tests pass; scan_data: 73 files, zero findings.
  Every persona skill of all 8 pairs now resolves to at least one video. The selector's
  wording rule is loose for a few titles (for example "Create an Ebook in 30 Minutes with
  Canva" matches "in N minutes"); kept as specified, noted as a limitation.
- Credits: Account 23 -> 28 used (222 left). Ledger counts 6 attempts (29 total); one query
  was apparently not billed by SerpApi. Revision calls this phase: 6 of 15.

## C6 - Default Job Prep listing per pair

- Research: the default listing was one hard-coded Bengaluru job.
- Plan/acceptance: choose it by rule for every pair: one named skill away, most skills
  to revise, then fewest to learn; fall back to the closest listing. Every pair needs one.
- Build: default_prep_index implements the rule; DEMO_JOB removed; the chosen listing, its
  revise/learn skills and shortest route are written to reports/final_results.json.
- Test: new test opens a plan for all 8 pairs offline with no missing revision videos.
  7 of 8 show both revise and learn sections. Indore (5 eligible, 0 matches) has no listing
  with a skill the persona holds, so its plan is learn-only; this is disclosed, not hidden.
  Bengaluru's choice is unchanged (Team Geek Solutions). 79 tests pass.

## F1-F3 - Evidence kits

- Research: matcher rules were written from the validation fixtures and the Bengaluru and
  Noida demos (git log for skills.py: last rule change before the C2 data existed).
- Plan/acceptance: 20 random eligible listings unseen by rule writing, empty label columns,
  scoring and user-test scripts that run on dummy files in tests, "pending" everywhere until real data.
- Build: evaluation/labels_template.csv (seed 20261009, pool of 70 eligible listings from the six
  later markets), evaluation/user_test_template.csv (header only), instructions in
  evaluation/README.md, scripts/make_label_template.py, score_labels.py, summarise_user_test.py.
  reports/hand_label_eval.md and reports/user_test.md both say pending.
- Test: tests/test_evaluation.py with dummy rows (precision/recall/must-have/experience counts, quote
  permission gating, pending states, template has no labels or contact data); full suite below.
- Verify: no label was filled by this repository. Row counts only when all three label cells are filled.
  Zero searches.

## E1-E8 - The website (one commit, pages built beside the old app, then switched)

- Research: Streamlit st.navigation (position="top"), st.cache_data and file_uploader docs are
  linked in research/RESEARCH.md. Streamlit widget identity includes its default arguments, so
  defaults are seeded through session state (a first version reset the market selection on rerun;
  the per-pair headline test caught it).
- Plan/acceptance: pages Home, Find my next skill, Job Prep, Compare cities, Live search (only with a
  key), Methodology and evidence, About and privacy; one shared engine; no exception without .env;
  numbers equal reports/final_results.json; analysis cached; readable at 390 px.
- Build: app.py is now the router; views/ holds the pages, shared state (common.py), result sections
  (render.py) and Job Prep UI (prep_ui.py). The cache key holds canonical skills, never resume text.
  Home findings and the Priya example are generated from final_results.json. Compare cities
  recomputes each city with the same engine for the visitor's profile; Methodology reads the generated
  reports (hand labels and user test say pending). .streamlit/config.toml: light theme, 5 MB uploads.
  The single-page app and its tests were removed after every new page passed.
- Test: tests/test_site.py (11 tests): every page loads with no key and network blocked; headline and
  default Job Prep listing match the results file for all 8 pairs; added skills; five-city table and
  agreement note; pending evidence; live page hidden without a key and keeps results when the credit
  check fails; canonical-skill path equals the resume path. Full suite: 89 tests pass.
- Verify: screenshots/site_*.png (1280 px) and mobile_home/mobile_find (390 px); horizontal overflow
  0 px on all pages; no tracebacks. Medal shown only for Strong or Likely. Zero searches.

## G1-G2 - Single source of truth

- Research: README, DEMO.md and reports/final_report.md are written only by scripts/render_docs.py
  from reports/final_results.json, which scripts/build_results.py rebuilds offline from demo_data.
- Plan/acceptance: a check that fails when any generated number or document differs; run in CI.
- Build: scripts/check_consistency.py rebuilds results and compares them with the saved file,
  re-renders the documents and compares them, and re-derives the hand-label and user-test reports.
  Added as a CI step. Residual risk: prose typed by hand into render_docs.py (for example the
  historical audit sentence) is not number-checked; it is replaced when README is rewritten in I2.
- Test: tests/test_consistency.py (clean state passes; a changed number is reported). Zero searches.

## D1 - NPTEL and SWAYAM courses: tried, not built

- Research: read NPTEL and SWAYAM terms (research/RESEARCH.md A5); keep titles and links only.
- Plan/acceptance: results from those hosts for each recommended skill, shown by provider.
- Build/test: three queries with an OR of two site: filters returned unrelated pages, a fourth timed out
  (no retry, counted). Single-site queries for SQL and Python on nptel.ac.in, onlinecourses.nptel.ac.in
  and swayam.gov.in also returned no page from those hosts. Saved YouTube data has no NPTEL or SWAYAM channel.
- Verify: acceptance cannot be met honestly. Removed the module, script and responses; no claim is made.
  Credits: 8 searches in phase D (ledger).

## D2 - Hindi

- Research: engine already detects a stated language in a video title or channel.
- Plan/acceptance: a "हिंदी" toggle; every Hindi string in i18n/hi.json, none shown until a person approves it;
  Hindi videos that pass the same filters, otherwise a note that English is shown; saved Hindi results for
  Excel, SQL, Python and JavaScript.
- Build: i18n.py (t() shows Hindi only for approved strings), i18n/hi.json (22 draft strings, all approved=false),
  hindi.py (courses and revision videos must state Hindi and name the skill), toggle on every page, Hindi
  video blocks in Evidence and Job Prep. Hour estimates still come from English courses and say so.
  Fetched 4 Hindi course and 4 Hindi revision responses (8 searches).
- Test: tests/test_hindi.py (saved Hindi results pass filters; unsaved skills never request; every Hindi
  key and placeholder matches English; unapproved strings never display; approved strings translate
  the headline while skill names stay English and typed input survives the toggle). 91 tests pass.
- Credits: Account 36 -> 44 used for these 8 (206 left after phase D). Human review of i18n/hi.json is pending.
