import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import build_results, check_consistency

ROOT = Path(__file__).resolve().parents[1]


class ConsistencyTests(unittest.TestCase):
    def test_saved_results_and_documents_agree(self):
        self.assertEqual(check_consistency.problems(), [])

    def test_a_changed_number_is_reported(self):
        data = copy.deepcopy(json.loads((ROOT / "reports/final_results.json").read_text()))
        data["pairs"]["frontend-developer-bengaluru"]["matches"] += 1
        with patch.object(build_results, "build", return_value=data):
            issues = check_consistency.problems()
        self.assertTrue(any("frontend-developer-bengaluru" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
