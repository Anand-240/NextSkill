"""Score the matcher against hand labels in evaluation/labels_template.csv (or a path you pass).

A row counts only when all three label cells are filled. Write "none" for an empty list.
Labels are never created by this repository."""
import csv
import sys
from pathlib import Path
from engine import ROOT, VOCABULARY, canonical_manual_skills, experience_evidence, extract_skills, stated_must_haves

OUTPUT = ROOT / 'reports/hand_label_eval.md'
LABELS = ('skills_required', 'skills_mandatory', 'min_years_experience')

def parse_skills(cell):
    return set() if cell.strip().casefold() in {'', 'none'} else canonical_manual_skills(cell.replace(';', ','))

def labelled(rows):
    return [row for row in rows if all(str(row.get(c) or '').strip() for c in LABELS)]

def score(rows):
    rows = labelled(rows)
    tp = fp = fn = in_vocab_fn = in_vocab_gold = 0
    must_ok = exp_ok = 0
    for row in rows:
        text, job = row['description_text'], {'title': row['title'], 'description': row['description_text']}
        found, gold = extract_skills(text), parse_skills(row['skills_required'])
        tp, fp, fn = tp + len(found & gold), fp + len(found - gold), fn + len(gold - found)
        in_vocab = gold & set(VOCABULARY)
        in_vocab_gold, in_vocab_fn = in_vocab_gold + len(in_vocab), in_vocab_fn + len(in_vocab - found)
        flat = set().union(*stated_must_haves(text), set())
        must_ok += flat == parse_skills(row['skills_mandatory'])
        years = row['min_years_experience'].strip()
        exp_ok += years.isdigit() and experience_evidence(job)[0] == int(years)
    n = len(rows)
    ratio = lambda a, b: a / b if b else None
    return {'rows': n, 'precision': ratio(tp, tp + fp), 'recall': ratio(tp, tp + fn),
            'recall_in_dictionary': ratio(in_vocab_gold - in_vocab_fn, in_vocab_gold),
            'must_have_accuracy': ratio(must_ok, n), 'experience_accuracy': ratio(exp_ok, n),
            'counts': {'true_positive': tp, 'false_positive': fp, 'false_negative': fn}}

def pct(value):
    return 'n/a' if value is None else f'{value:.1%}'

def render(result, total):
    if not result['rows']:
        return ('# Hand-labelled accuracy\n\nStatus: pending. No fully labelled rows yet '
                f'({total} listings drawn, labels not filled).\n\nNo accuracy figure is claimed until a person '
                'fills evaluation/labels_template.csv and runs scripts/score_labels.py.\n')
    c = result['counts']
    return (f"# Hand-labelled accuracy\n\nListings scored: {result['rows']} of {total} drawn.\n\n"
            f"| Measure | Result |\n|---|---|\n| Skill precision | {pct(result['precision'])} |\n"
            f"| Skill recall (all labelled skills) | {pct(result['recall'])} |\n"
            f"| Skill recall (skills the dictionary contains) | {pct(result['recall_in_dictionary'])} |\n"
            f"| Stated must-haves exactly right | {pct(result['must_have_accuracy'])} |\n"
            f"| Minimum experience exactly right | {pct(result['experience_accuracy'])} |\n\n"
            f"Counts: {c['true_positive']} true positive, {c['false_positive']} false positive, "
            f"{c['false_negative']} false negative skill mentions. Small sample; treat as indicative.\n")

def main(path=None, output=OUTPUT):
    with open(path or ROOT / 'evaluation/labels_template.csv', newline='') as handle:
        rows = list(csv.DictReader(handle))
    text = render(score(rows), len(rows))
    Path(output).write_text(text)
    return text

if __name__ == '__main__':
    print(main(sys.argv[1] if len(sys.argv) > 1 else None))
