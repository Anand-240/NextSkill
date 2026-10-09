"""Fail if a generated number or document differs from what the saved data produces.

1. reports/final_results.json must equal a fresh offline rebuild from demo_data.
2. README.md, DEMO.md and reports/final_report.md must equal what render_docs makes from that file.
3. The hand-label and user-test reports must equal what their scripts make from the CSV files."""
import csv
import json
import sys
import tempfile
from pathlib import Path
from scripts import build_results, render_docs, score_labels, summarise_user_test

ROOT = Path(__file__).resolve().parents[1]


def problems() -> list[str]:
    found = []
    saved = json.loads((ROOT / "reports/final_results.json").read_text())
    fresh = json.loads(json.dumps(build_results.build(), ensure_ascii=False))
    if saved != fresh:
        differing = sorted(key for key in saved["pairs"] if saved["pairs"].get(key) != fresh["pairs"].get(key))
        found.append("reports/final_results.json differs from a fresh rebuild: " + (", ".join(differing) or "top level"))
    for path, body in render_docs.render(saved).items():
        if (ROOT / path).read_text() != body:
            found.append(f"{path} differs from render_docs output; run python -m scripts.render_docs")
    with tempfile.TemporaryDirectory() as directory:
        with open(ROOT / "evaluation/labels_template.csv", newline="") as handle:
            rows = list(csv.DictReader(handle))
        expected = score_labels.render(score_labels.score(rows), len(rows))
        if (ROOT / "reports/hand_label_eval.md").read_text() != expected:
            found.append("reports/hand_label_eval.md differs from score_labels output")
        with open(ROOT / "evaluation/user_test_template.csv", newline="") as handle:
            expected = summarise_user_test.summarise(list(csv.DictReader(handle)))
        if (ROOT / "reports/user_test.md").read_text() != expected:
            found.append("reports/user_test.md differs from summarise_user_test output")
    return found


if __name__ == "__main__":
    issues = problems()
    print(f"Consistency check: {len(issues)} problem(s)")
    for issue in issues:
        print(" -", issue)
    sys.exit(bool(issues))
