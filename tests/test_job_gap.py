import json
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

import findings
from scripts import job_gap

ROOT = Path(__file__).resolve().parents[1]
GAP = json.loads((ROOT / "reports/job_gap.json").read_text())


class JobGapTests(unittest.TestCase):
    def test_saved_file_equals_an_offline_rebuild_and_needs_no_network(self):
        with patch("engine._request", side_effect=AssertionError("network requested")):
            self.assertEqual(json.loads(json.dumps(job_gap.build())), GAP)

    def test_every_query_is_equal_and_counts_are_consistent(self):
        rows = GAP["rows"]
        self.assertEqual(len(rows), len(job_gap.ROLES) * len(job_gap.CITIES))
        for row in rows:
            with self.subTest(row=(row["role"], row["city"])):
                self.assertEqual(row["status"], "ok")
                self.assertLessEqual(row["pages_fetched"], job_gap.MAX_PAGES)
                self.assertLessEqual(row["in_city"] + row["remote"], row["listings"])
                self.assertLessEqual(row["distinct_employers"], row["listings"])
                self.assertTrue(row["snapshot_dates"])
        query = job_gap.query("Accountant", "Pune")
        self.assertEqual(query, {"engine": "google_jobs", "location": "Pune, India", "gl": "in", "hl": "en", "q": "Accountant"})

    def test_sentence_and_table_use_only_file_numbers(self):
        sentence = findings.gap_sentence(GAP)
        low = min(GAP["rows"], key=lambda row: row["in_city"] / row["listings"])
        self.assertIn(f"only {low['in_city']} of {low['listings']}", sentence)
        for row in GAP["rows"]:
            self.assertIn(f"| {row['role']} | {row['city']} | {row['listings']} | {row['in_city']} |", findings.gap_table(GAP))

    def test_compare_page_shows_the_gap_with_its_caveat(self):
        with patch("engine.optional_serpapi_key", return_value=None), patch("engine._request", side_effect=AssertionError("network")):
            app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=120).run().switch_page("views/compare.py").run()
        self.assertFalse(app.exception)
        text = "\n".join(item.value for item in app.markdown) + "\n".join(item.value for item in app.caption)
        self.assertIn("Job-information gap", text)
        self.assertIn("not the number of jobs in a city", text)
        self.assertTrue(any(findings.gap_sentence(GAP) == item.value for item in app.markdown))


if __name__ == "__main__":
    unittest.main()
