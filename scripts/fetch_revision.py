"""Fetch missing revision-video responses: the skills saved personas already have (phase C, cap 15), then the
most common skills a user might pick (phase K, final batch, cap 8)."""
from engine import canonical_manual_skills
from job_prep import is_cached, revision_params
from personas import saved_pairs
from scripts.build_data import BuildClient, publish_usage, record_account

def needed():
    skills = sorted({s for pair in saved_pairs() for s in canonical_manual_skills(pair['resume'])})
    return [s for s in skills if not is_cached(revision_params(s), True)]

COMMON = ['SQL', 'Tally', 'GST', 'React', 'Tableau', 'Google Ads', 'SEO', 'Django']


def needed_common():
    return [s for s in COMMON if not is_cached(revision_params(s), True)]


if __name__ == '__main__' and 'common' in __import__('sys').argv[1:]:
    todo = needed_common()
    print('missing common revision responses:', todo, flush=True)
    if todo:
        record_account('K before')
        for skill in todo:
            BuildClient('K', 'revision').search(revision_params(skill))
        record_account('K after')
        publish_usage()
elif __name__ == '__main__':
    todo = needed()
    print('missing revision responses:', todo, flush=True)
    if todo:
        record_account('C5 before')
        for skill in todo:
            BuildClient('C', 'revision').search(revision_params(skill))
        record_account('C5 after')
        publish_usage()
