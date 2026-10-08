import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


class PresentationTests(unittest.TestCase):
    def test_demo_and_live_headlines_describe_the_source_and_population(self):
        with patch("engine.optional_serpapi_key", return_value=None), \
             patch("engine._request", side_effect=AssertionError("network requested")):
            app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=120).run()
            self.assertFalse(app.exception)
            self.assertEqual(app.subheader[0].value,
                             "Your profile matches 5 of 19 saved listings in Bengaluru.")
            captions = "\n".join(item.value for item in app.caption)
            self.assertIn("Snapshot date: 2026-10-07 (UTC)", captions)
            self.assertIn("23 eligible listings", captions)
            self.assertIn("19 have detected core requirements and are scored", captions)
            self.assertTrue(app.sidebar.toggle[1].disabled)
            result = app.session_state["result"]
            with patch("engine.optional_serpapi_key", return_value="unit-test-placeholder"), \
                 patch("engine.run", return_value=result), \
                 patch("engine.SerpClient.account", return_value={"this_month_usage": 0, "total_searches_left": 0}):
                app.run()
                app.sidebar.toggle[1].set_value(True).run()
                app.sidebar.button[0].click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.subheader[0].value,
                             "Your profile matches 5 of 19 listings found now in Bengaluru.")
            self.assertNotIn("ready for", app.subheader[0].value)

    def test_fastest_win_and_biggest_unlock_cards(self):
        with patch("engine.optional_serpapi_key", return_value=None), \
             patch("engine._request", side_effect=AssertionError("network requested")):
            app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=120).run()
            self.assertFalse(app.exception)
            text = "\n".join(item.value for item in app.markdown)
            self.assertIn("**Fastest win: REST API**", text)
            self.assertIn("**Biggest unlock: React**", text)
            self.assertNotIn("Fastest win and biggest unlock", text)
            captions = "\n".join(item.value for item in app.caption)
            self.assertIn("A short course can win per hour even if it opens fewer jobs. Compare both before choosing.", captions)
            result = app.session_state["result"]
            single = {**result, "ranked": result["ranked"][:1]}
            with patch("engine.run", return_value=single):
                app.sidebar.button[0].click().run()
            self.assertFalse(app.exception)
            text = "\n".join(item.value for item in app.markdown)
            self.assertIn("**Fastest win and biggest unlock: REST API**", text)
            self.assertNotIn("**Biggest unlock: ", text)

    def test_readme_matcher_claim_retains_sample_size_and_recall_limit(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("16 of 20 sampled matches were correct; after filters, the 16 retained matches were all correct; recall not measured", readme)
        claim = next(line for line in readme.splitlines() if "matcher audit" in line)
        self.assertNotIn("100%", claim)


if __name__ == "__main__":
    unittest.main()
