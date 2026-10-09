import unittest
from unittest.mock import patch

from engine import SerpClient, rank_skills, stated_must_haves, must_have_status, analyze_jobs


class TrustTests(unittest.TestCase):
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
