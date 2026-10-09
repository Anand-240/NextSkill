"""Summarise real user-test rows from evaluation/user_test_template.csv into reports/user_test.md.

Only rows with a participant id and a trust score count. Quotes appear only with quote_permission = yes."""
import csv
import sys
from pathlib import Path
from engine import ROOT

OUTPUT = ROOT / 'reports/user_test.md'

def real(rows):
    return [r for r in rows if (r.get('participant_id') or '').strip() and (r.get('trust_1_to_5') or '').strip().isdigit()]

def yes(value):
    return (value or '').strip().casefold() in {'yes', 'y', 'true', '1'}

def summarise(rows):
    rows = real(rows)
    n = len(rows)
    if not n:
        return ('# User test\n\nStatus: in progress. No participant rows have been recorded, so no result, '
                'quote or satisfaction figure is claimed.\n')
    changed = sum(yes(r['changed_choice']) for r in rows)
    trust = [int(r['trust_1_to_5']) for r in rows]
    recommend = sum(yes(r['would_recommend']) for r in rows)
    points = [r['confusing_points'].strip() for r in rows if r['confusing_points'].strip()]
    quotes = [r['quote'].strip() for r in rows if yes(r['quote_permission']) and r['quote'].strip()]
    lines = [f'# User test\n\nParticipants: {n}. Real sessions only; small sample, not a statistical result.\n',
             f'- Changed their choice after seeing NextSkill: {changed} of {n}',
             f'- Average trust (1 to 5): {sum(trust) / n:.1f}',
             f'- Would recommend: {recommend} of {n}']
    if points:
        lines += ['\nConfusing points reported:'] + [f'- {p}' for p in points]
    if quotes:
        lines += ['\nQuotes shared with permission:'] + [f'- "{q}"' for q in quotes]
    return '\n'.join(lines) + '\n'

def main(path=None, output=OUTPUT):
    with open(path or ROOT / 'evaluation/user_test_template.csv', newline='') as handle:
        text = summarise(list(csv.DictReader(handle)))
    Path(output).write_text(text)
    return text

if __name__ == '__main__':
    print(main(sys.argv[1] if len(sys.argv) > 1 else None))
