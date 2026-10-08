"""Reproduce the 20-match precision audit from validation fixtures."""
import json
import random
import re
from pathlib import Path

from scripts import validation_skills as old
from skills import extract_skills

ROOT = Path(__file__).resolve().parents[1]

# Human review of the fixed seeded sample: these are mentions, not requirements.
FALSE_MATCH_INDICES = {2, 6, 17, 19}


def audit() -> tuple[list[dict], float, float]:
    jobs = []
    for path in sorted((ROOT / "tests" / "fixtures").glob("jobs_*.json")):
        jobs.extend(json.loads(path.read_text()).get("jobs_results", []))
    candidates = []
    for job in jobs:
        for sentence in re.split(r"(?<=[.!?])\s+|\n+|[•●▪]", job.get("description", "")):
            sentence = sentence.strip()
            if 20 <= len(sentence) <= 300:
                for skill in sorted(old.extract_skills(sentence)):
                    candidates.append((skill, job.get("title"), sentence))
    random.Random(20261008).shuffle(candidates)
    rows = []
    for index, (skill, title, sentence) in enumerate(candidates[:20], 1):
        rows.append({"index": index, "skill": skill, "job": title, "sentence": sentence, "false_before": index in FALSE_MATCH_INDICES, "retained": skill in extract_skills(sentence)})
    true_before = 20 - len(FALSE_MATCH_INDICES)
    retained = [row for row in rows if row["retained"]]
    true_after = sum(not row["false_before"] for row in retained)
    return rows, true_before / 20, true_after / len(retained) if retained else 0


if __name__ == "__main__":
    rows, before, after = audit()
    path = ROOT / "reports" / "matcher_audit.md"
    lines = ["# Matcher precision audit", "", "20 seeded random (skill, job) matches from validation job descriptions. Human review flags mentions that do not state a skill requirement.", "", "| # | Skill | Job | Sentence | False before? | Kept after? |", "|---:|---|---|---|---|---|"]
    for row in rows:
        cell = lambda s: str(s).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {row['index']} | {cell(row['skill'])} | {cell(row['job'])} | {cell(row['sentence'])} | {'yes' if row['false_before'] else 'no'} | {'yes' if row['retained'] else 'no'} |")
    lines += ["", f"Precision before: {(before * 100):.1f}% (16/20).", f"Precision after: {(after * 100):.1f}% on retained sampled matches.", "", "Context filters remove bare role headings, explicit ‘don't need’ statements, illustrative examples, and vendor compliance metrics. This is a small, hand-reviewed sample; it does not establish recall.", ""]
    path.parent.mkdir(exist_ok=True)
    path.write_text("\n".join(lines))
    print(f"before={before:.3f} after={after:.3f} retained={sum(r['retained'] for r in rows)}/20")
