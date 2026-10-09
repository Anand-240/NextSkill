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
