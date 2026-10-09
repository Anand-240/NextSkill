import json
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from views import common

ROOT = Path(__file__).resolve().parents[1]
APP = str(ROOT / "app.py")
PAGES = ["views/find.py", "views/prep.py", "views/compare.py", "views/methods.py", "views/about.py"]
RESULTS = json.loads((ROOT / "reports/final_results.json").read_text())["pairs"]


def offline():
    return (patch("engine.optional_serpapi_key", return_value=None),
            patch("engine._request", side_effect=AssertionError("network requested")))


class SiteTests(unittest.TestCase):
    def setUp(self):
        for p in offline():
            p.start()
            self.addCleanup(p.stop)

    def open(self, page=None):
        app = AppTest.from_file(APP, default_timeout=120).run()
        if page:
            app = app.switch_page(page).run()
        self.assertFalse(app.exception, [str(e.value) for e in app.exception])
        return app

    def test_every_page_loads_without_a_key_or_network(self):
        for page in [None] + PAGES:
            with self.subTest(page=page):
                self.open(page)

    def test_home_example_and_findings_come_from_results(self):
        app = self.open()
        text = "\n".join(item.value for item in app.markdown)
        bengaluru = RESULTS["frontend-developer-bengaluru"]
        self.assertIn(f"**{bengaluru['matches']} of {bengaluru['scored']}**", text)
        for finding in common.key_findings():
            self.assertIn(finding, text)
        self.assertEqual(len(common.key_findings()), 3)

    def test_find_page_headline_matches_the_generated_result_for_every_pair(self):
        app = self.open("views/find.py")
        for pair in common.pairs():
            with self.subTest(pair=pair["id"]):
                app.selectbox[0].select(common.pair_label(pair)).run()
                self.assertFalse(app.exception)
                row = RESULTS[pair["id"]]
                text = "\n".join(item.value for item in app.markdown)
                self.assertIn(f"matches {row['matches']} of {row['scored']} saved listings in {pair['city']}", text)
                if row["fastest_win"]:
                    self.assertTrue(app.subheader and row["fastest_win"] in app.subheader[0].value)
                self.assertIn(f"Pick stability: ", text)
                self.assertIn(row["retrieved_dates"][0], text)

    def test_find_page_accepts_added_skills_and_keeps_old_wording_out(self):
        app = self.open("views/find.py")
        app.text_input[0].set_value("SQL, Tableau").run()
        self.assertFalse(app.exception)
        self.assertTrue(any("SQL" in chip.value for chip in app.markdown if "chip" in chip.value))
        page = "\n".join(item.value for item in app.markdown) + "\n".join(item.value for item in app.caption)
        for old in ("today's jobs", "Or list skills"):
            self.assertNotIn(old, page)

    def test_job_prep_defaults_to_the_listing_in_the_results_file(self):
        app = self.open("views/prep.py")
        for pair in common.pairs():
            with self.subTest(pair=pair["id"]):
                app.selectbox[0].select(common.pair_label(pair)).run()
                self.assertFalse(app.exception)
                expected = RESULTS[pair["id"]]["job_prep_default"]
                self.assertEqual(app.subheader[0].value, f"{expected['title']} · {expected['company']}")

    def test_compare_page_lists_five_data_analyst_cities_and_states_reliability(self):
        app = self.open("views/compare.py")
        table = app.dataframe[0].value
        self.assertEqual(sorted(table["City"]), ["Hyderabad", "Indore", "Jaipur", "Noida", "Pune"])
        self.assertIn("Pages fetched", table.columns)
        notes = [item.value for item in app.info] + [item.value for item in app.success]
        reliable = [city for city in table["City"] if RESULTS[f"data-analyst-{city.lower()}"]["confidence"] != "Uncertain"
                    and not RESULTS[f"data-analyst-{city.lower()}"]["flags"]["limited_data"]]
        self.assertEqual(any("No reliable difference" in n for n in notes), not reliable)
        self.assertFalse(any("do not agree" in n for n in notes) and not reliable)
        warnings = " ".join(item.value for item in app.warning)
        self.assertIn("not collected the same way", warnings)

    def test_methods_page_reports_pending_evidence(self):
        app = self.open("views/methods.py")
        text = "\n".join(item.value for item in app.markdown)
        self.assertIn("Status: pending", text)
        self.assertIn("developer", text)

    def test_live_page_is_unavailable_without_a_key(self):
        app = AppTest.from_file(str(ROOT / "views/live.py"), default_timeout=120).run()
        self.assertFalse(app.exception)
        self.assertIn("only on a machine that has its own SerpApi key", app.info[0].value)
        self.assertEqual(len(app.button), 0)

    def test_skills_from_text_are_canonical_and_pdf_problems_are_reported(self):
        skills, warning = common.user_skills("I know html, css and JavaScript", "SQL")
        self.assertEqual(skills, ["CSS", "HTML", "JavaScript", "SQL"])
        self.assertIsNone(warning)
        _, warning = common.user_skills("", "", b"not a pdf")
        self.assertIn("paste your resume text", warning)
        _, warning = common.user_skills("", "", b"x" * (common.MAX_PDF_BYTES + 1))
        self.assertIn("5 MB", warning)

    def test_canonical_skill_path_matches_the_resume_path_in_the_engine(self):
        from engine import SerpClient, run
        for pair in common.pairs():
            with self.subTest(pair=pair["id"]):
                skills, _ = common.user_skills(pair["resume"])
                via_skills = common.get_saved_result(pair["id"], skills)
                direct = run(pair["role"], pair["city"], pair["resume"], pages=pair["pages"], experience_level="Fresher",
                             client=SerpClient(use_fixtures=True, cache_only=True))
                self.assertEqual(via_skills["ready"], direct["ready"])
                self.assertEqual([r["skill"] for r in via_skills["ranked"]], [r["skill"] for r in direct["ranked"]])


class LiveWithKeyTests(unittest.TestCase):
    def test_live_page_keeps_results_when_the_credit_check_fails(self):
        from engine import SerpClient, run
        saved = run("Frontend Developer", "Bengaluru", "HTML, CSS", pages=3, experience_level="Fresher",
                    client=SerpClient(use_fixtures=True, cache_only=True))
        with patch("engine.optional_serpapi_key", return_value="unit-test-placeholder"), \
             patch("engine.run", return_value=saved), patch("views.live.run", return_value=saved), \
             patch("engine.SerpClient.account", side_effect=RuntimeError("account unavailable")), \
             patch("engine._request", side_effect=AssertionError("network requested")):
            app = AppTest.from_file(str(ROOT / "views/live.py"), default_timeout=120).run()
            self.assertFalse(app.exception)
            app.button[0].click().run()
            self.assertFalse(app.exception, [str(e.value) for e in app.exception])
            self.assertEqual(app.session_state["live_result"]["ready"], saved["ready"])
            self.assertIn("Credit balance unavailable", [x.value for x in app.info])

    def test_failed_live_request_is_explained_and_results_are_kept(self):
        from engine import SerpClient, run
        saved = run("Frontend Developer", "Bengaluru", "HTML, CSS", pages=3, experience_level="Fresher",
                    client=SerpClient(use_fixtures=True, cache_only=True))
        saved["request_failed"] = True
        with patch("engine.optional_serpapi_key", return_value="unit-test-placeholder"), \
             patch("engine.run", return_value=saved), \
             patch("engine.SerpClient.account", return_value={"this_month_usage": 1, "total_searches_left": 9}), \
             patch("engine._request", side_effect=AssertionError("network requested")):
            app = AppTest.from_file(str(ROOT / "views/live.py"), default_timeout=120).run()
            app.button[0].click().run()
            self.assertFalse(app.exception)
            self.assertTrue(any("was not retried" in w.value for w in app.warning))
            self.assertEqual(app.session_state["live_result"]["ready"], saved["ready"])


if __name__ == "__main__":
    unittest.main()
