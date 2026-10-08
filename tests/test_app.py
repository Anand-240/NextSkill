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
                             "Your profile matches 8 of 19 saved listings in Bengaluru.")
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
                             "Your profile matches 8 of 19 listings found now in Bengaluru.")
            self.assertNotIn("ready for", app.subheader[0].value)


if __name__ == "__main__":
    unittest.main()
