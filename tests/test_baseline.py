import json
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

import findings

ROOT = Path(__file__).resolve().parents[1]
RESULTS = json.loads((ROOT / "reports/final_results.json").read_text())


class BaselineTests(unittest.TestCase):
    def test_every_market_with_a_pick_has_a_baseline_built_from_saved_data(self):
        for key, pair in RESULTS["pairs"].items():
            with self.subTest(pair=key):
                base = pair["baseline"]
                if pair["headline_skill"]:
                    self.assertIsNotNone(base)
                    self.assertEqual(base["headline_skill"], pair["headline_skill"])
                    self.assertEqual(base["agrees"], base["skill"] == pair["headline_skill"])
                    ranked = {row["skill"]: row for row in pair["ranked"]}
                    self.assertEqual(base["headline_unlocked"], ranked[pair["headline_skill"]]["unlocked"])

    def test_the_headline_pick_always_has_standard_course_confidence_unless_nothing_qualifies(self):
        for key, pair in RESULTS["pairs"].items():
            with self.subTest(pair=key):
                standard = [row for row in pair["ranked"] if row["course_confidence"] == "standard" and row["jobs_per_hour"]]
                if standard:
                    ranked = {row["skill"]: row for row in pair["ranked"]}
                    self.assertEqual(ranked[pair["headline_skill"]]["course_confidence"], "standard")
                    self.assertEqual(pair["fastest_win"], pair["headline_skill"])

    def test_summary_counts_match_the_rows_and_text_reports_them(self):
        summary = findings.baseline_summary(RESULTS)
        rows = findings.baseline_rows(RESULTS)
        self.assertEqual(summary["markets"], len(rows))
        self.assertEqual(summary["agree"] + len(summary["differ"]), summary["markets"])
        text = findings.baseline_text(RESULTS)
        self.assertIn(f"agree in {summary['agree']} of {summary['markets']} markets", text)
        for row in summary["differ"]:
            self.assertIn(f"| {row['market']} |", text)

    def test_methods_page_shows_the_comparison(self):
        with patch("engine.optional_serpapi_key", return_value=None), patch("engine._request", side_effect=AssertionError("network")):
            app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=120).run().switch_page("views/methods.py").run()
        self.assertFalse(app.exception)
        text = "\n".join(item.value for item in app.markdown)
        self.assertIn("Does jobs-per-hour change the answer?", text)
        self.assertIn(findings.baseline_text(RESULTS).strip().splitlines()[0], text)


if __name__ == "__main__":
    unittest.main()
