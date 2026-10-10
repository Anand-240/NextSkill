import json
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

import findings
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

    def test_home_example_and_gap_come_from_results(self):
        app = self.open()
        text = "\n".join(item.value for item in app.markdown)
        results = json.loads((ROOT / "reports/final_results.json").read_text())
        star = RESULTS[findings.example_key(results)]
        self.assertIn(f"**{star['scored']}** scored listings", text)
        self.assertIn(f"of **{star['matches']}**", text)
        self.assertIn("Priya is a sample profile, not a real person", text)
        gap = json.loads((ROOT / "reports/job_gap.json").read_text())
        self.assertIn(findings.gap_sentence(gap), text)
        self.assertIn("Pick stability: " + star["confidence"], text)

    def test_find_page_headline_matches_the_generated_result_for_every_pair(self):
        app = self.open("views/find.py")
        for pair in common.pairs():
            with self.subTest(pair=pair["id"]):
                app.selectbox[0].select(common.pair_label(pair)).run()
                self.assertFalse(app.exception)
                row = RESULTS[pair["id"]]
                text = "\n".join(item.value for item in app.markdown)
                self.assertIn(f"matches {row['matches']} of {row['scored']} saved listings for {pair['city']} searches", text)
                if row["fastest_win"]:
                    self.assertTrue(app.subheader and row["fastest_win"] in app.subheader[0].value)
                self.assertIn(f"Pick stability: ", text)
                self.assertIn(row["retrieved_dates"][0], text)

    def test_job_match_page_lists_the_jobs_the_headline_skill_would_open(self):
        app = self.open("views/find.py")
        self.assertEqual(app.header[0].value, "Job match and next skill")
        star = RESULTS["frontend-developer-bengaluru"]
        head = next(row for row in star["ranked"] if row["skill"] == star["headline_skill"])
        control = app.segmented_control[0]
        self.assertEqual(control.options[0], f"Matches now ({star['matches']})")
        opened = [option for option in control.options if option.startswith(f"Opened by {head['display_skill']}")]
        self.assertEqual(opened, [f"Opened by {head['display_skill']} ({head['unlocked']})"])
        control.set_value(f"Opened by {head['display_skill']}").run()
        self.assertFalse(app.exception, [str(e.value) for e in app.exception])
        text = "\n".join(item.value for item in app.markdown)
        self.assertEqual(text.count('class="jobtitle"'), head["unlocked"])  # six shown plus the rest in "Show more"

    def test_tapping_a_skill_changes_the_answer_and_untapping_returns_it(self):
        app = self.open("views/find.py")
        before = app.subheader[0].value
        pills = app.pills[0]
        self.assertEqual(sorted(pills.value), ["CSS", "HTML", "JavaScript"])
        pills.set_value(["HTML"]).run()
        self.assertFalse(app.exception)
        self.assertNotEqual(app.subheader[0].value, before)
        app.pills[0].set_value(["CSS", "HTML", "JavaScript"]).run()
        self.assertEqual(app.subheader[0].value, before)

    def test_find_page_accepts_added_skills_and_keeps_old_wording_out(self):
        app = self.open("views/find.py")
        app.text_input[0].set_value("SQL, Tableau").run()
        self.assertFalse(app.exception)
        self.assertTrue(any("SQL" in chip.value for chip in app.markdown if "chip" in chip.value))
        page = "\n".join(item.value for item in app.markdown) + "\n".join(item.value for item in app.caption)
        for old in ("today's jobs", "Or list skills"):
            self.assertNotIn(old, page)

    def test_hindi_switch_only_on_pages_where_it_changes_something(self):
        for page in ("views/find.py", "views/prep.py"):
            with self.subTest(page=page):
                self.assertEqual(len(self.open(page).toggle), 1)
        for page in (None, "views/compare.py", "views/methods.py", "views/about.py"):
            with self.subTest(page=page):
                self.assertEqual(len(self.open(page).toggle), 0)

    def test_opportunity_curve_says_which_skills_it_leaves_out(self):
        app = self.open("views/find.py")
        captions = [item.value for item in app.caption]
        self.assertIn("The curve uses only skills with known course hours; skills marked Unavailable are left out.", captions)

    def test_job_prep_defaults_to_the_listing_in_the_results_file(self):
        app = self.open("views/prep.py")
        for pair in common.pairs():
            with self.subTest(pair=pair["id"]):
                app.selectbox[0].select(common.pair_label(pair)).run()
                self.assertFalse(app.exception)
                expected = RESULTS[pair["id"]]["job_prep_default"]
                self.assertEqual(app.subheader[0].value, f"{expected['title']} · {expected['company']}")

    def test_job_prep_times_are_rounded_and_never_degenerate(self):
        import re
        app = self.open("views/prep.py")
        for pair in common.pairs():
            with self.subTest(pair=pair["id"]):
                app.selectbox[0].select(common.pair_label(pair)).run()
                text = "\n".join(item.value for item in app.markdown) + "\n" + "\n".join(item.value for item in app.caption)
                self.assertIsNone(re.search(r"about (\d+) to \1 ", text), text[:300])
                for bad in ("0.0 hours", "course hours", " no of ", "0.00"):
                    self.assertNotIn(bad, text)

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

    def test_methods_page_reports_evidence_in_progress(self):
        app = self.open("views/methods.py")
        text = "\n".join(item.value for item in app.markdown)
        self.assertIn("Status: in progress", text)
        self.assertIn("Informal check: 3 friends (students and freshers) tried NextSkill and rated it 4.33 out of 5", text)
        self.assertIn("not a structured study", text)
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


class CreditMessageTests(unittest.TestCase):
    def test_used_comes_from_the_run_not_from_the_account_reading(self):
        text = common.credit_message({"live_requests": 1}, {"this_month_usage": 5, "total_searches_left": 144})
        self.assertIn("used in this live run: 1", text)
        self.assertIn("Remaining as reported by SerpApi: 144", text)
        self.assertIn("may lag", text)

    def test_missing_account_reading_still_shows_the_count(self):
        text = common.credit_message({"live_requests": 2}, None)
        self.assertIn("used in this live run: 2", text)
        self.assertIn("unavailable", text)


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
            self.assertTrue(any("Credit balance unavailable" in x.value for x in app.info))

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
            self.assertTrue(any("may lag" in x.value for x in app.info))
            self.assertEqual(app.session_state["live_result"]["ready"], saved["ready"])


if __name__ == "__main__":
    unittest.main()
