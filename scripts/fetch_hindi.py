"""Fetch Hindi course and revision results for the most common persona skills (phase D, cap 30)."""
from hindi import course_params
from job_prep import is_cached, revision_params
from scripts.build_data import BuildClient, publish_usage, record_account

SKILLS = ["Excel", "SQL", "Python", "JavaScript"]

if __name__ == "__main__":
    todo = [("course", course_params(s)) for s in SKILLS if not is_cached(course_params(s), True)]
    todo += [("revision", revision_params(s, True)) for s in SKILLS if not is_cached(revision_params(s, True), True)]
    print("missing Hindi responses:", [p["search_query"] for _, p in todo], flush=True)
    if todo:
        record_account("D hindi before")
        for category, params in todo:
            BuildClient("D", category).search(params)
        record_account("D hindi after")
        publish_usage()
