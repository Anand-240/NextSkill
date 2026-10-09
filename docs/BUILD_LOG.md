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

## C2 (rest) - Seven more saved markets

- Research: reused the documented role and city requests and the shared course queries.
- Plan/acceptance: reach 15 pairs including more tier-2 and non-developer markets; every pair runs
  offline; limited data stays visible; every default Job Prep plan opens.
- Build: scripts/fetch_pairs.py --extended added Python Developer (Bengaluru, Kochi), Accountant (Mumbai,
  Indore), Digital Marketing Executive (Pune, Chennai) and Frontend Developer (Hyderabad), each with one
  page of the base, fresher and junior queries plus hours for the top candidate skills; one Git revision
  response. Six of the 15 markets are in tier-2 cities (Jaipur twice, Indore twice, Kochi, Dehradun).
  (Correction: an earlier draft of this line misdescribed Chennai.)
- Test: 97 tests pass with all 15 pairs (golden results, Job Prep defaults, scan_data: 109 files clean).
  Two markets, Data Analyst Indore and Digital Marketing Pune, have no listing asking for a skill the
  example profile holds, so their Job Prep plans only teach; a test pins exactly those two.
- Verify: honest flags kept: limited data in 8 markets; Pune and Chennai marketing also carry the dictionary
  warning. Fastest wins changed nothing in the first eight pairs. Remaining pairs in the original list
  were not collected (Mumbai/Chennai/Noida/Kochi for every role); the 15 saved pairs satisfy the Tier 1 target.
- Credits: Account 44 -> 71 used for this step and the Git revision (179 left). Ledger phase C: 52 of 105.

## A4 and A5 - Landscape and public courses

- Research: four existing tools read and linked (research/RESEARCH.md A4); A5 terms read and the site: test
  recorded (see D1).
- Plan/acceptance: honest comparison without uniqueness claims; links open.
- Verify: NCS, LinkedIn Skills Match and Skill India Digital Hub pages opened; SIDH counts not verified so not used.
  Zero searches for A4; A5 searches are accounted under D1.

## I2-I3 - README and demo script regenerated

- Research: the README order in the plan; every number must come from reports/final_results.json.
- Build: scripts/render_docs.py now writes the README in the plan's order (pitch, Try it live, Why this matters,
  key findings, next skill map, beyond big hubs, user test, hand-labelled accuracy, what the numbers mean, how it
  works, SerpApi usage, questions, limitations and future work, setup, data sources, timeline, AI tools used) and a
  DEMO.md with the opening line from the plan. findings.py computes the findings for both the site and the documents.
  Evidence sections read the generated hand-label and user-test reports and say pending. The NPTEL and SWAYAM result
  is stated plainly in the SerpApi usage section.
- Verify: check_consistency passes; the full suite passes.

## Phase H - Verification gates (run 2026-10-09 17:00 to 17:25 IST)

- H1: 101 offline tests pass; CI green at the last push before this section (see GitHub Actions).
- H2: scripts/check_consistency rebuilds all 15 pairs from saved data and matches reports/final_results.json,
  README, DEMO and the evidence reports: 0 problems.
- H3: fresh clone of origin/main into a temp folder, new virtualenv, requirements install, 97 tests pass,
  consistency check passes, app started with no .env: Home, Find, Job Prep, Compare, Methodology and About load with
  0 exceptions; no Live search link; /live falls back to Home.
- H4: scripts/security_scan: 488 history blobs scanned for the local key value and real-looking api_key values: 0
  findings; 109 response files: no emails or phone numbers; no contact patterns in tests, reports or evaluation files.
- H5: scripts/check_links: all relative links and images exist; web links resolve except two that need a note:
  labour.gov.in/ncs answers with a redirect to www (browser fine, opened and read earlier) and
  nextskill.streamlit.app answers with a cookie handshake redirect; both load in a browser.
- H6: scripts/time_pages (server-side, AppTest): Bengaluru frontend, Jaipur analyst, Mumbai accountant: first load
  0.04 to 0.39 s, adding a skill 0.13 to 0.22 s, repeat 0.04 s. Browser rendering time is not included.
- H7: one local live run, Data Analyst in Kochi, 1 page. The first attempt (budget 3) stalled: a request timed out and
  the whole run was lost although one response was saved. That was a real fault, fixed (commit after this section):
  a failed request after earlier successes now keeps the partial results, is not retried, is shown in Search Replay
  as failed and explained in the answer. Re-run with budget 2: Search Replay showed the live requests, the cached
  base query and the skipped course search; the counter read "used 1, remaining 175"; partial results rendered with
  limited-data and budget notes; 0 exceptions. Searches in H7: 4 of the cap of 5 (Account API after H7: 75 used, 175 left;
  the ledger shows 2 + 2 attempts). Screenshot: screenshots/live_run.png.
- H8: the hosted app loads Home, Find, Job Prep, Compare, Methodology and About in a fresh browser context with 0
  exceptions and no Live search link. It was still serving stale saved numbers (8 markets, "unknown date") after the
  last pushes: a cached results file survived the redeploy. The cache is now keyed by the file's modified time
  (commit 'Key the saved results cache...'), but the human must reboot the Streamlit app and recheck in incognito.

## Phase I - Documentation, demo, freeze

- I1: no filled hand labels or user-test rows exist, so both reports say pending; nothing was generated by an assistant.
- I2/I3: README and DEMO.md regenerated from reports/final_results.json (section above).
- I4: screenshots re-captured for every page (site_*.png at 1280 px, mobile_home and mobile_find at 390 px,
  live_run.png from the H7 run). Consistency check passes; CI green at the last push.
- Budget: Account API final: 75 searches used this month, 175 left (plan cap 160; floor 90). Phase caps: C 57 recorded
  attempts of 105 (revision 7 of 15), D 16 of 30, H 4 of 5.
- I5: freeze after this commit; no feature work is pending.

# Batch 2: winning finish

Four independent strict reviews scored the first build 28 to 33 of 50. This batch fixes what they caught.
No SerpApi call was needed for Part 1.

## 1.1 Headline metric

- Fastest win now needs standard course confidence (two relevant full courses of an hour or more). A skill
  with weaker video evidence stays in the ranking, marked low course confidence, and cannot lead the answer.
  With no qualifying skill the headline is the biggest unlock and says no course length is reliable.
- Course relevance: videos that lead with a different product (a Figma talk for Responsive Design), talks,
  webinars and videos under 10 minutes are dropped before hours are estimated.
- One wording for hours: "about 1 hour" for 0.84 h, "about 4 hours" for 3.73 h, minutes below 45 minutes.
  The old "~1-2 hours" range could exclude the estimate it described.
- Pick stability and its bootstrap use only standard-confidence skills, so the label describes the headline.
- Re-run all 15 markets. Headlines that changed:

| Market | Fastest win before | after | Biggest unlock |
|---|---|---|---|
| Frontend Developer, Bengaluru | Responsive Design | REST API | React (unchanged) |
| Frontend Developer, Hyderabad | Responsive Design | REST API | REST API (unchanged) |
| Digital Marketing, Pune | Market Research | Email Marketing | Market Research (unchanged) |

  The other 12 markets keep their pick. Responsive Design stays in the Bengaluru ranking with low course
  confidence (0.71 h after the Figma talk was dropped).
- Tests: course relevance, low confidence cannot lead, hours wording contains the estimate, headline fallback.

## 1.2 Pick stability

"Confidence" is now "Pick stability", shown with the number of scored listings. Strong needs 15 or more scored
listings, a headline pick with standard course confidence and both stability shares at 85% or more. Under 15
scored listings the label is at most Likely; limited-data markets are at most Uncertain.

| Market | Label before | after |
|---|---|---|
| Frontend Developer, Bengaluru | Strong | Likely (hour variation 75.6%) |
| Accountant, Indore | Strong | Uncertain (limited data) |
| Digital Marketing, Pune | Likely | Uncertain (limited data) |
| Digital Marketing, Chennai | Likely | Uncertain (limited data) |

No market is Strong now. The label is honest, not tuned.

## 1.3 to 1.6 Interface fixes

- The Hindi switch sat under the Streamlit header at desktop width (a 1.2 rem top padding override). The padding
  is now 4.5 rem. Playwright clicked the switch on all six pages at 1280 px and 390 px, no overflow, no exception.
  It is now "Prefer Hindi videos". The interface stays English: the 23 Hindi strings are unapproved and not shown.
- Compare cities: if every city is Uncertain or has limited data it says "No reliable difference between these
  cities in this snapshot". It shows pages fetched and snapshot date per city and warns when they differ.
- Job Prep: revise and learn steps are numbered separately. The shortest route tries standard-confidence skills
  first and says so when it must use a weaker one. A title that names a tool the plan or route lacks gets a note.
- The "outside strongest areas" warning (which fired for marketing) now says few skills were detected.
  Experience levels other than Fresher show a note that the saved samples came from fresher and junior searches.

## 2.1 and 2.2 Job-information gap

- Research: SerpApi Google Jobs documentation read again before any call (`q`, `location`, `gl`, `hl`, `next_page_token`,
  ten results per page, `start` discontinued). 75 s timeout, no retry, durable attempt counter (phase J, cap 35).
- Account API before: 75 used, 175 left. After: 98 used, 152 left (floor 90). Ledger: 25 attempts in phase J; the
  Account API counted 23, so two were not billed. Saved pages already on disk were reused (page 1 for five markets).
- Equal queries: the plain role names "Data Analyst" and "Accountant", no fresher or junior variants, in Bengaluru,
  Pune, Jaipur, Indore and Dehradun, up to three pages following `next_page_token`. Responses redacted before saving.
- Result: every one of the 10 queries filled all three pages (26 to 30 listings). The page limit, not the city, sets
  the total, so total visible listings cannot show a gap. What differs is how many of those listings are located in
  the named city (its name in the listing's location text):

| Role | Bengaluru | Pune | Jaipur | Indore | Dehradun |
|---|---:|---:|---:|---:|---:|
| Data Analyst | 22 of 26 | 6 of 29 | 27 of 28 | 23 of 28 | 21 of 29 |
| Accountant | 26 of 29 | 8 of 28 | 9 of 30 | 17 of 29 | 3 of 28 |

  Google Jobs fills the list with nearby cities: 10 of 28 Pune accountant listings are in Mumbai and 6 of 28 Dehradun
  accountant listings are in New Delhi (and 6 more in Gurugram or Noida). This is stated as visible listings in an equal-query snapshot,
  never as the number of jobs in a city. The in-city test is conservative: suburbs under other names are not counted.
- Built `scripts/job_gap.py` (offline rebuild, `--plan`, `--fetch`), `reports/job_gap.json`, a section on the Compare
  cities page with a chart, table and caveat, and tests (`tests/test_job_gap.py`). `check_consistency` rebuilds the file.
- Verified: 113 tests pass; consistency check 0 problems; security scan: 529 history blobs, 134 response files, 0 findings.

## 3.1 and 3.2 Does jobs-per-hour change the answer?

- For every market with a headline pick, compared it with a frequency-only baseline: the non-generic missing core
  skill that the most scored listings ask for, with no course hours (`baseline` in reports/final_results.json,
  rebuilt offline by `scripts/build_results.py`).
- Result: the two methods agree in 4 of 14 markets (Data Analyst Noida, Accountant Jaipur, Accountant Mumbai, Digital
  Marketing Chennai). In the other 10, the headline pick unlocks at least as many extra listings in 5 and needs less course
  time in 9. In 4 markets it unlocks fewer listings in less time (for example Frontend Developer Bengaluru: React +10 in
  5.1 h against REST API +8 in 2.5 h), and in Digital Marketing Pune it unlocks fewer listings for more time because the
  most asked skill has low course confidence. The honest reading: course hours do change the answer, as a trade between
  listings and hours, and hours come from video lengths that are only a proxy.
- Shown on the Methodology page and in the README, generated from the results file. Tests: `tests/test_baseline.py`.

## 4 README, Home page and file moves

- README rewritten by `scripts/render_docs.py` in the requested order. The first screen has the pitch, the live link,
  who it helps, one worked example and one key finding (the job-information gap). The worked example is the market with
  the best pick-stability label and, among equals, the most scored listings: Frontend Developer in Bengaluru (Likely,
  19 scored listings). No market is Strong, so the README says why in the Judge FAQ.
- The Home page now mirrors that first screen from the same generated text; the three-findings list moved into the
  README's All markets section. The old "Beyond big hubs" table was dropped because the gap section covers it.
- Moved BUILD_LOG.md to docs/ and 37 older screenshots to screenshots/archive/; relative links in the archived reports
  were updated and checked (0 missing files).

## 5 Evidence hooks

`evaluation/labels_template.csv` has 20 drawn listings and no labels; `evaluation/user_test_template.csv` has a header
and no rows. Both reports now read "Status: in progress" and the README says no figure is claimed. Nothing was filled by
this repository. `scripts/score_labels.py` and `scripts/summarise_user_test.py` turn real rows into figures when a person
adds them, and `check_consistency` re-derives both reports.

## 6 Demo script

DEMO.md is generated for 2 minutes 40 seconds with the sample profile, headline, Job Prep, job-information gap, one live
local search with a budget of 3, and the limits. The live segment is to be recorded first and retried if a request times out.

## 7 Verification (batch 2)

- 7.1 Offline suite: 117 tests pass (17 s). `scripts.check_consistency`: 0 problems (results, job-gap file, README, DEMO,
  final report, hand-label and user-test reports all rebuilt and compared). CI green on the latest push.
- 7.2 Fresh clone of origin/main into a temporary folder with a new virtualenv and no `.env`: 117 tests pass, consistency
  check passes, the app starts, and `/live` falls back to Home with no Live search link in the navigation.
- 7.3 Playwright, Chromium, 1280 px and 390 px, all six pages: 0 exceptions, 0 px horizontal overflow, the "Prefer Hindi
  videos" switch clickable on every page, Home button opens Find, every market on the Find page renders. Screenshots
  re-captured (screenshots/site_*.png, mobile_home.png, mobile_find.png). Correction to an earlier review note: the market
  dropdown shows 11 entries because Streamlit virtualises the list; there are 15 markets.
- Live path (one run, local key, never shown): Data Analyst in Nagpur, 1 page, budget 3. Search Replay showed 3 live Google
  Jobs requests, 1 cached course search and 2 skipped (budget), the credit counter read "used 2, remaining 148", partial
  results rendered, 0 exceptions. The Account API counts later than the ledger: from 98 used after the gap fetch the
  account reached 103 used (147 left) after this run, so the batch moved the account by 28 credits (25 gap attempts and 3
  live), which matches the 28 attempts recorded. The cap for the batch was 40; the floor of 90 remaining was never close.
- 7.4 Security: full-history scan, 604 blobs, 0 findings for the key value and api_key patterns; 134 response files with
  no emails or phone numbers; every commit's staged diff was checked for the key before pushing.
- 7.5 README links: all relative files exist; web links answer 200 except two that redirect and need a browser or a
  follow-up (labour.gov.in/ncs redirects to www.labour.gov.in; nextskill.streamlit.app answers with a cookie handshake).
- 7.6 Open for the human: the hosted app still served the old build when checked (8 saved markets, "unknown date" on three
  markets). Reboot the Streamlit app, then open it in a private window and check Home shows the worked example for
  Frontend Developer in Bengaluru and Compare cities shows the job-information gap section.

## Job match page naming

The page "Find my next skill" did not say it was about jobs. It is now "Job match" (header "Job match and next skill") with
a one-sentence intro, the field "Job role and city", and a "Jobs <skill> would open" list on the Answer tab that links the
first five listings the headline skill would turn into matches. Home, DEMO.md and the tests use the new name; the layout was
re-captured at 1280 px and 390 px.

## Visual redesign

The first design (dark rounded hero, emoji icons, blue-grey cards) read as generated. Reference points: Awwwards pages for
career and editorial layouts (cream canvas, black type, one bright accent, newspaper-like structure) and Dribbble job-board
collections (plain job cards in a list). Principles were borrowed; no design was copied.

- Look: cream paper background, ink-black text, one marigold accent, Fraunces serif headings with DM Sans body, thin ink
  borders with a small hard shadow on hover, text-only navigation with an underline for the current page, no emoji icons.
- Home: one big question as the headline, an interactive "pick a job and city" card with three big numbers, three plain
  steps and the job-information gap as two large numbers. Every number still comes from the results files.
- Job match: tap-to-select skill pills built from the skills that market asks for most, then a "Jobs behind this answer"
  explorer (Matches now, One skill away, Opened by the headline skill) with a card per listing: coverage bar, what is
  missing, must-haves and a link. Resume paste, PDF and thresholds moved into one expander.
- Job Prep: readiness as three large numbers; revise and learn lists in expanders.
- Tests: 119 pass (new tests for tapping skills and for the jobs explorer). Browser check at 1280 px and 390 px: 0
  exceptions, 0 px overflow; Home market picker, Home button to Job match, skill toggle, view switch, Job Prep and Compare
  cities all clicked through in Chromium. Icon glyphs needed an explicit font rule after the body font override broke them.

## Final fix batch (October 10)

Fixes from a full workflow review of 048573e, then a freeze.

- Live credit counter: credits used now come from the run's own request count; the SerpApi balance is shown apart as
  "as reported by SerpApi (may lag by a few seconds)". The review saw "used 0" for a run that spent 1 credit because the
  Account API read lagged.
- Job Prep time text uses the same rounding as Job match ("about 3 hours"), equal ends collapse ("about 1 hour"), and a
  listing with nothing measured says "No measured route". The README baseline table uses the same wording, and a row whose
  two times round to the same text now reads "about the same course time" (the count of "less course time" fell from 9 to 7).
- Revision filter: titles about version control revisions (rev-parse, reflog), interview-question lists, OOP-only videos,
  school literature (a play called "Tally's Blood") and CA, CMA or CS exam classes are skipped. The saved responses are kept
  as received; the filter drops those videos when they are read.
- Revision videos for eight more skills (SQL, Tally, GST, React, Tableau, Google Ads, SEO, Django): 8 searches, build phase
  K. Google Ads has no video that passes the filters, so Job Prep says so. Account API: 108 used and 142 left before,
  116 used and 134 left after.
- Wording: the AI note names Claude (chat) for planning, prompts and reviews; "the most common other places were"; listing
  counts read "for Bengaluru searches" with a note counting listings that name another place; "Find page" is now "Job match".
- Pick stability notes show a cap only when it changes the label.
- Methodology tables scroll sideways at 390 px; Job Prep names stated must-haves that are not in the plan; the gap chart has
  a lead sentence and a note on why saved markets are smaller.
- Tests: 125 pass; scripts.check_consistency reports 0 problems. Screenshots re-captured at 1280 px and 390 px from a keyless
  copy of the committed tree (0 px horizontal overflow on every page). The old live_run.png is unchanged.
