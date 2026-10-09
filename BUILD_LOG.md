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
