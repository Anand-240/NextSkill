import unittest
from unittest.mock import patch

from engine import SerpClient, rank_skills, stated_must_haves, must_have_status, analyze_jobs, select_course_videos, course_videos


class TrustTests(unittest.TestCase):
    def test_shortest_route_chooses_cheapest_sufficient_skill(self):
        from job_prep import shortest_route
        req = {frozenset({s}) for s in ['HTML','CSS','React','SQL']}
        route = shortest_route(req, {'HTML'}, .5, lambda s: ({'CSS':1,'React':5,'SQL':3}[s], [], 'standard'))
        self.assertEqual(route['skills'], ['CSS'])
        self.assertEqual(route['hours'], 1)

    def test_course_title_requires_skill_or_alias(self):
        videos = [{'title':'Figma full course','length':'2:00:00'},
                  {'title':'ReactJS full course','length':'1:00:00'},
                  {'title':'ReactJSX full course','length':'3:00:00'}]
        hours, chosen, confidence = select_course_videos(videos, 'React full course')
        self.assertEqual(hours, 1)
        self.assertEqual(len(chosen), 1)
        self.assertEqual(confidence, 'low')

    def test_must_have_phrases_and_alternatives(self):
        for phrase in ['Must know SQL', 'SQL mandatory', 'SQL required', 'SQL essential', 'Minimum skills: SQL']:
            with self.subTest(phrase=phrase):
                req = stated_must_haves(phrase)
                self.assertEqual(req, {frozenset({'SQL'})})
                self.assertEqual(must_have_status(req, set()), 'no')
                self.assertEqual(must_have_status(req, {'SQL'}), 'yes')
        self.assertEqual(must_have_status(stated_must_haves('Python is a plus.'), set()), 'none stated')
        self.assertEqual(must_have_status(stated_must_haves('Must know Power BI or Tableau.'), {'Tableau'}), 'yes')
        self.assertFalse(stated_must_haves('SQL not required.'))

    def test_coverage_match_does_not_imply_mandatory_match(self):
        r = analyze_jobs([{'description':'SQL required. Excel.', 'title':'Analyst','company_name':'A'}], {'Excel'})
        self.assertEqual(r['ready'], 1)
        self.assertEqual(r['must_haves_met'], 0)
        self.assertEqual(r['jobs'][0]['must_haves_status'], 'no')

    def test_short_saved_course_outside_fetch_shortlist_wins(self):
        analysis = {"candidates": ["Python", "SQL"],
                    "unlocked": {"Python": [{}, {}], "SQL": [{}]},
                    "skill_counts": {"Python": 2, "SQL": 1}}
        def courses(skill, client, hindi):
            if skill == "SQL":
                self.assertTrue(client.cache_only)
            return (10 if skill == "Python" else .5), [], "standard"
        with patch("engine.course_videos", side_effect=courses):
            ranked = rank_skills(analysis, SerpClient(offline=True), learning_limit=1)
        self.assertEqual(ranked[0]["skill"], "SQL")


class PartialFailureTests(unittest.TestCase):
    """A timeout after earlier successes keeps what was fetched and is never retried."""

    def make_client(self, fail_on):
        calls = []

        class Client(SerpClient):
            def search(self, params, page=1):
                calls.append(params)
                if len(calls) in fail_on:
                    raise RuntimeError("SerpApi request failed (TimeoutError)")
                job = {"title": "Analyst", "company_name": "A", "description": "SQL required. Excel."}
                if params["engine"] == "google_jobs":
                    return {"jobs_results": [job], "_retrieved_at": "2026-10-09T00:00:00+00:00"}
                return {"video_results": []}
        client = Client(offline=True)
        return client, calls

    def test_later_jobs_failure_keeps_earlier_listings(self):
        from engine import fetch_jobs
        client, calls = self.make_client({2})
        jobs = fetch_jobs("Data Analyst", "Pune", pages=1, client=client, experience_level="Fresher")
        self.assertEqual(len(jobs), 1)
        self.assertTrue(client.request_failed)
        self.assertEqual(len(calls), 2)  # no retry and no third query
        self.assertEqual(client.replay[-1]["source"], "failed")

    def test_first_jobs_failure_still_raises(self):
        from engine import fetch_jobs
        client, _ = self.make_client({1})
        with self.assertRaises(RuntimeError):
            fetch_jobs("Data Analyst", "Pune", pages=1, client=client, experience_level="Fresher")

    def test_course_failure_marks_hours_unknown_not_a_crash(self):
        client, _ = self.make_client({1})
        self.assertEqual(course_videos("SQL", client), (None, [], "failed"))
        self.assertTrue(client.request_failed)
