"""Job-information gap: how many listings Google Jobs shows for the same query in different cities.

Equal queries only: the plain role name, no fresher or junior variants, up to three result pages,
following next_page_token and stopping when there is none. The numbers describe what is visible through
Google Jobs in this snapshot, never the number of jobs in a city. Every query filled all three pages, so the
page cap sets the total; the informative number is how many of those listings are located in the named city
(its name appears in the listing's location text; suburbs under other names, such as Pimpri-Chinchwad, do not count).

    python -m scripts.job_gap            rebuild reports/job_gap.json from saved responses (offline)
    python -m scripts.job_gap --plan     list the requests that are not saved yet (offline)
    python -m scripts.job_gap --fetch    collect the missing responses within the phase J cap"""
import json
import sys
from collections import Counter
from engine import ROOT, SerpClient, _check_error, normalize, retrieval_date

ROLES = ["Data Analyst", "Accountant"]
CITIES = ["Bengaluru", "Pune", "Jaipur", "Indore", "Dehradun"]
MAX_PAGES = 3
OUTPUT = ROOT / "reports/job_gap.json"


def query(role: str, city: str, token: str | None = None) -> dict:
    return {"engine": "google_jobs", "location": f"{city}, India", "gl": "in", "hl": "en", "q": role,
            **({"next_page_token": token} if token else {})}


def traverse(client, role: str, city: str) -> dict:
    """Follow the result pages for one equal query. A page missing from the saved data ends the walk."""
    pages, jobs, token, status = [], [], None, "ok"
    for number in range(1, MAX_PAGES + 1):
        data = client.search(query(role, city, token), page=number)
        if not data:
            status = "page not saved"
            break
        _check_error(data)
        batch = data.get("jobs_results") or []
        pages.append({"listings": len(batch), "retrieved": (retrieval_date(data) or "").isoformat() if retrieval_date(data) else None})
        jobs.extend(batch)
        token = (data.get("serpapi_pagination") or {}).get("next_page_token")
        if not token:
            break
    places = [str(job.get("location") or "").split(",")[0].strip() for job in jobs]
    in_city = sum(city.casefold() in str(job.get("location") or "").casefold() for job in jobs)
    remote = sum(place.casefold() == "anywhere" for place in places)
    elsewhere = Counter(place for place, job in zip(places, jobs)
                        if place and place.casefold() != "anywhere" and city.casefold() not in str(job.get("location") or "").casefold())
    return {"role": role, "city": city, "pages_fetched": len(pages), "more_pages_after": bool(token),
            "listings": len(jobs), "in_city": in_city, "remote": remote,
            "other_places": [f"{place} ({count})" for place, count in sorted(elsewhere.items(), key=lambda row: (-row[1], row[0]))[:3]],
            "distinct_employers": len({normalize(str(job.get("company_name") or "")) for job in jobs} - {""}),
            "snapshot_dates": sorted({page["retrieved"] for page in pages if page["retrieved"]}), "status": status}


def build() -> dict:
    client = SerpClient(use_fixtures=True, cache_only=True)
    rows = [traverse(client, role, city) for role in ROLES for city in CITIES]
    return {"note": "Equal-query snapshot: plain role name, base query only, up to 3 pages. Counts are listings visible "
                    "through Google Jobs, not the number of jobs in a city. Generated offline by scripts/job_gap.py.",
            "rows": rows}


def missing() -> list[str]:
    client = SerpClient(use_fixtures=True, cache_only=True)
    found = []
    for role in ROLES:
        for city in CITIES:
            result = traverse(client, role, city)
            if result["status"] != "ok":
                found.append(f"{role} / {city}: stops after {result['pages_fetched']} saved page(s)"
                             + (", more pages exist" if result["more_pages_after"] or result["status"] != "ok" else ""))
    return found


def fetch() -> None:
    from scripts.build_data import BuildClient, publish_usage, record_account
    record_account("J before")
    for role in ROLES:
        for city in CITIES:
            client = BuildClient("J", "gap")
            try:
                result = traverse(client, role, city)
            except RuntimeError as exc:
                print("STOPPED", role, city, exc, flush=True)
                publish_usage()
                raise
            publish_usage()
            print(role, city, result["listings"], "listings", result["pages_fetched"], "pages", flush=True)
    record_account("J after")


if __name__ == "__main__":
    if "--fetch" in sys.argv:
        fetch()
    elif "--plan" in sys.argv:
        print("\n".join(missing()) or "nothing missing")
    else:
        OUTPUT.write_text(json.dumps(build(), indent=2, ensure_ascii=False) + "\n")
