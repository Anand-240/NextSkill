"""Fetch missing revision-video responses for the skills saved personas already have (phase C, cap 15)."""
from engine import canonical_manual_skills
from job_prep import is_cached, revision_params
from personas import saved_pairs
from scripts.build_data import BuildClient, publish_usage, record_account

def needed():
    skills = sorted({s for pair in saved_pairs() for s in canonical_manual_skills(pair['resume'])})
    return [s for s in skills if not is_cached(revision_params(s), True)]

if __name__ == '__main__':
    todo = needed()
    print('missing revision responses:', todo, flush=True)
    if todo:
        record_account('C5 before')
        for skill in todo:
            BuildClient('C', 'revision').search(revision_params(skill))
        record_account('C5 after')
        publish_usage()
