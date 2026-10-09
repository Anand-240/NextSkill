"""Draw the hand-labelling sample: 20 eligible listings from markets collected after the matcher rules were frozen.

The matcher rules were written while reading the Bengaluru and Noida demos and the validation fixtures.
This sample only uses the six later markets, with a fixed seed, so nobody has tuned the rules on it."""
import csv
import hashlib
import random
from unittest.mock import patch
from engine import ROOT, SerpClient, run
from personas import saved_pairs

SEED = 20261009
EXCLUDED_PAIRS = {'frontend-developer-bengaluru', 'data-analyst-noida'}
COLUMNS = ['listing_id', 'title', 'company', 'description_text',
           'skills_required', 'skills_mandatory', 'min_years_experience']

def listing_id(job):
    key = '|'.join(str(job.get(k) or '') for k in ('title', 'company_name', 'description'))
    return 'L' + hashlib.sha1(key.encode()).hexdigest()[:10]

def pool():
    seen, rows = set(), []
    for pair in saved_pairs():
        if pair['id'] in EXCLUDED_PAIRS:
            continue
        with patch('engine._request', side_effect=AssertionError('Offline build forbids requests')):
            result = run(pair['role'], pair['city'], resume=pair['resume'], pages=pair['pages'],
                         client=SerpClient(use_fixtures=True, cache_only=True), experience_level='Fresher')
        for job in result['eligible_jobs']:
            ident = listing_id(job)
            if ident not in seen:
                seen.add(ident)
                rows.append(job)
    return sorted(rows, key=listing_id)

def build(count=20):
    jobs = pool()
    chosen = random.Random(SEED).sample(jobs, min(count, len(jobs)))
    return len(jobs), [{'listing_id': listing_id(job), 'title': job.get('title') or '',
                        'company': job.get('company_name') or '', 'description_text': job.get('description') or '',
                        'skills_required': '', 'skills_mandatory': '', 'min_years_experience': ''}
                       for job in chosen]

if __name__ == '__main__':
    size, rows = build()
    with open(ROOT / 'evaluation/labels_template.csv', 'w', newline='') as handle:
        writer = csv.DictWriter(handle, COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f'{len(rows)} listings drawn from a pool of {size}')
