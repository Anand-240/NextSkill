import unittest
from pathlib import Path
from unittest.mock import patch

import streamlit as st
from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


class PresentationTests(unittest.TestCase):
    def test_demo_and_live_headlines_describe_the_source_and_population(self):
        with patch("engine.optional_serpapi_key", return_value=None), \
             patch("engine._request", side_effect=AssertionError("network requested")):
            app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=120).run()
            self.assertFalse(app.exception)
            self.assertEqual(app.subheader[0].value,
                             "Learn REST API next: +8 more matching listings, about 3 hours of free courses.")
            self.assertIn("**Your profile matches 9 of 19 saved listings in Bengaluru.**",
                          [item.value for item in app.markdown])
            self.assertIn("About this sample", [item.label for item in app.expander])
            self.assertFalse(any("🥇" in item.value for item in app.markdown))  # Uncertain pick: no medal.
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
                sidebar = "\n".join(item.value for item in app.sidebar.caption)
                self.assertIn("This search may use up to 6 credits.", sidebar)
                self.assertIn("SerpApi credits remaining (Account API): 0.", sidebar)
                self.assertNotIn("Last known", sidebar)
                app.sidebar.button[0].click().run()
            self.assertFalse(app.exception)
            text = [item.value for item in app.markdown]
            self.assertIn("**Your profile matches 9 of 19 listings found now in Bengaluru.**", text)
            self.assertFalse(any("ready for" in value or "within reach" in value for value in text))

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
            single = {**result, "ranked": result["ranked"][:1],
                      "robustness": {**result["robustness"], "label": "Likely"}}
            st.cache_data.clear()  # The demo result is cached; force the patched run.
            with patch("engine.run", return_value=single):
                app.sidebar.button[0].click().run()
            self.assertFalse(app.exception)
            text = "\n".join(item.value for item in app.markdown)
            self.assertIn("**Fastest win and biggest unlock: REST API**", text)
            self.assertIn("#### 🥇 REST API", text)  # Likely confidence keeps the medal.
            self.assertNotIn("**Biggest unlock: ", text)

    def test_job_prep_section_defaults_to_the_demo_job_and_switches(self):
        with patch("engine.optional_serpapi_key", return_value=None), \
             patch("engine._request", side_effect=AssertionError("network requested")):
            app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=120).run()
            self.assertFalse(app.exception)
            labels = [item.label for item in app.expander]
            self.assertIn("Job Prep: Frontend Developer (Fresher) · Team Geek Solutions", labels)
            text = "\n".join(item.value for item in app.markdown)
            self.assertIn("you cover 3 of 7 core skills", text)
            self.assertIn("[JavaScript Basics in 10 Minutes]", text)
            self.assertIn("[CSS in 5 minutes]", text)
            captions = "\n".join(item.value for item in app.caption)
            self.assertIn("Quick revision videos. Not a full course and not a guarantee.", captions)
            self.assertIn("Revision videos available in live search.", captions)
            self.assertIn("**Your profile matches 9 of 19 saved listings in Bengaluru.**", [item.value for item in app.markdown])
            prep_buttons = [button for button in app.button if button.key and button.key.startswith("prep_")]
            self.assertEqual(len(prep_buttons), 19)
            target = next(button for button in prep_buttons if button.key != "prep_1")
            target.click().run()
            self.assertFalse(app.exception)
            self.assertEqual(sum(item.label.startswith("Job Prep: ") for item in app.expander), 1)
            self.assertNotIn("Job Prep: Frontend Developer (Fresher) · Team Geek Solutions",
                             [item.label for item in app.expander])

    def test_readme_matcher_claim_retains_sample_size_and_recall_limit(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("16 of 20 sampled matches were correct; after filters, the 16 retained matches were all correct; recall not measured", readme)
        claim = next(line for line in readme.splitlines() if "matcher audit" in line)
        self.assertNotIn("100%", claim)


if __name__ == "__main__":
    unittest.main()
