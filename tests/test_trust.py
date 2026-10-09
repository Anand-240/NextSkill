import unittest
from unittest.mock import patch

from engine import SerpClient, rank_skills


class TrustTests(unittest.TestCase):
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
