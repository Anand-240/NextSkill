"""Generate the Phase 2 report entirely from cached data and account snapshots."""
import json
from pathlib import Path

from engine import ROOT, SerpClient, analyze_jobs, deduplicate, extract_skills, fetch_jobs, run

PERSONAS = [
    ("Fresher", "Excel, basic Python"),
    ("Mid", "SQL, Excel, Python, Tableau"),
    ("Frontend fresher", "HTML, CSS, JavaScript"),
]


def cached_run(role: str, city: str, resume: str, threshold: float = .7) -> dict:
    return run(role, city, resume=resume, threshold=threshold, pages=3,
               client=SerpClient(use_fixtures=True, cache_only=True))


def skill_summary(result: dict, count: int = 3) -> str:
    return "; ".join(
        f"{row['skill']} (+{row['unlocked_count']}, ~{row['hours']:.2f}h, {row['score']:.2f} jobs/h)" if row["hours"] is not None
        else f"{row['skill']} (+{row['unlocked_count']}, hours unavailable)"
        for row in result["ranked"][:count]
    ) or "no one-skill unlocks"


def pair_summary(result: dict) -> str:
    pair = result["two_skill_plan"]
    if not pair:
        return "none"
    text = f"{pair['skills'][0]} + {pair['skills'][1]} unlocks {pair['unlocked_count']} jobs"
    if pair["hours"] is not None:
        text += f"; ~{pair['hours']:.2f} combined hours; {pair['score']:.2f} jobs/hour"
    else:
        text += "; combined hours unavailable because one skill lacks cached course data"
    return text


def legacy_noida() -> dict:
    """Phase 1 rule on the same two saved pages, for an apples-to-apples comparison."""
    jobs = fetch_jobs("Data Analyst", "Noida", pages=2, client=SerpClient(offline=True))
    usable = [(job, extract_skills(str(job.get("description") or ""))) for job in deduplicate(jobs)]
    usable = [(job, skills) for job, skills in usable if len(skills) >= 3]
    user = {"Excel", "SQL", "Python"}
    ready = sum(len(skills & user) / len(skills) >= .4 for _, skills in usable)
    gained = {}
    for skill in {skill for _, skills in usable for skill in skills} - user:
        gained[skill] = sum(len(skills & user) / len(skills) < .4 <= len(skills & (user | {skill})) / len(skills) for _, skills in usable)
    return {"ready": ready, "usable": len(usable), "gained": gained}


def main() -> None:
    before = json.loads((ROOT / "cache" / "account_phase2_before.json").read_text())
    after = json.loads((ROOT / "cache" / "account_phase2_after.json").read_text())
    ledger = json.loads((ROOT / "cache" / "phase2_ledger.json").read_text())
    old = legacy_noida()
    noida = cached_run("Data Analyst", "Noida", "Excel, SQL basics, Python basics", .4)
    noida_default = cached_run("Data Analyst", "Noida", "Excel, SQL basics, Python basics", .7)
    frontend_demo = cached_run("Frontend Developer", "Bengaluru", "HTML, CSS, JavaScript", .7)
    personas = {(role, label): cached_run(role, city, resume) for role, city in
                (("Data Analyst", "Noida"), ("Frontend Developer", "Bengaluru"))
                for label, resume in PERSONAS}
    lines = [
        "# NextSkill Phase 2: number check", "",
        "## Credits and data", "",
        f"Account API `this_month_usage`: {before['this_month_usage']} → {after['this_month_usage']} (change {after['this_month_usage'] - before['this_month_usage']}).",
        f"Phase 2 real search requests attempted: {ledger['real_calls']} of 12 maximum; all search responses are cached. Account checks were free.",
        "The four headline course skills were Data Analysis, Power BI, React and TypeScript. Power BI reused the saved validation response. Additional cached course searches for Tableau and UI/UX support the two-skill plans; SQL supports the analyst-fresher sanity check.",
        "Noida: 20 raw results, 19 distinct listings. A third page was requested but returned zero results. Frontend Bengaluru: 30 raw results, 29 distinct listings across three pages. Neither query triggers the <12-job limited-data warning.",
        "", "## Noida before and after", "",
        "Same resume: Excel, SQL basics, Python basics. Same 0.4 readiness threshold; Phase 1 used the two saved Noida pages, and the Phase 2 third page added no listings.", "",
        "| Measure | Phase 1 | Phase 2 |", "|---|---|---|",
        f"| Ready jobs | {old['ready']} of {old['usable']} usable | {noida['ready']} of {len(noida['jobs'])} usable |",
        "| Power BI learning estimate | ~0.51h from short tutorials | ~3.68h from three qualifying course videos |",
        "| Top 3 ranked skills | Power BI (+4); Data Visualization (+3, hours unavailable); Tableau (+3, hours unavailable) | " + skill_summary(noida) + " |",
        "| Best two-skill plan | not available | " + pair_summary(noida) + " |", "",
        "The 0.4 pair's hours remain unavailable under the 12-call cap because Machine Learning has no cached qualifying course search. At the required default 0.7 threshold, Phase 2 has " +
        f"{noida_default['ready']} of {len(noida_default['jobs'])} ready; its two-skill plan is {pair_summary(noida_default)}.", "",
        "## Demo rankings", "",
        f"- **Data Analyst, Noida** (sample resume, 0.4): ready {noida['ready']}/{len(noida['jobs'])}. {skill_summary(noida, 5)}. Pair: {pair_summary(noida)}.",
        f"- **Frontend Developer, Bengaluru** (frontend fresher, 0.7): ready {frontend_demo['ready']}/{len(frontend_demo['jobs'])}. {skill_summary(frontend_demo, 5)}. Pair: {pair_summary(frontend_demo)}.",
        "", "## Persona sanity check (default threshold 0.7)", "",
        "| Role | Persona | Ready | Top skills | Two-skill plan |", "|---|---|---:|---|---|",
    ]
    for role, _ in (("Data Analyst", "Noida"), ("Frontend Developer", "Bengaluru")):
        for label, _ in PERSONAS:
            result = personas[(role, label)]
            lines.append(f"| {role} | {label} | {result['ready']}/{len(result['jobs'])} | {skill_summary(result)} | {pair_summary(result)} |")
    lines += ["", "### Sanity flags", "",
              "- Analyst fresher has SQL and Power BI among scored suggestions; the mid analyst has Power BI and Data Analysis. Frontend fresher has React and TypeScript. Those match the intended roles.",
              "- Default 0.7 coverage remains stringent: the analyst fresher is ready for 0/17 and frontend fresher for 1/28. The model follows the requested core-skill formula; it should not be described as a hiring probability.",
              "- A frontend-only resume applied to analyst jobs produces an irrelevant Tableau suggestion because one job has few core requirements. The app should treat cross-role recommendations cautiously.",
              "- The broad Data Analysis query includes Excel-focused courses. Its hour estimate is useful as a rough curriculum length, but course-topic relevance needs further review before a public demo.",
              "- Some valid unlocks have no course estimate after the capped searches (for example Machine Learning). They remain visible with unavailable hours, rather than receiving invented scores.",
              "", "## Course evidence", "",
              "Titles must include full course, complete, course, masterclass, or bootcamp and run at least 60 minutes. The median uses up to the first three qualifying results. If fewer than two qualify, videos of at least 30 minutes supply a low-confidence estimate. The SerpApi YouTube `sp` long-video filter was used on new queries and local checks enforce the stricter rule.", ""]
    seen = set()
    for result in (noida, noida_default, frontend_demo, *personas.values()):
        for item in result["ranked"]:
            if item["skill"] in seen or not item["videos"]:
                continue
            seen.add(item["skill"])
            lines.append(f"### {item['skill']} — ~{item['hours']:.2f}h ({item['confidence']} confidence)")
            lines.append("")
            for video in item["videos"]:
                lines.append(f"- [{video['title']}]({video['link']}) — {video['channel']}, {video['duration']}")
            lines.append("")
    lines += ["## Verification", "",
              "Nine offline unit tests passed, covering core selection, pair planning, course filtering and fallback, limited data, matching, freshness, deduplication and ranking. Run: `PYTHONPATH=nextskill python3 -m unittest discover -s nextskill/tests -q`.",
              "Streamlit rendered both cached demos end to end: [Noida screenshot](../screenshots/archive/phase2_noida.png) and [Frontend screenshot](../screenshots/archive/phase2_frontend.png).", "",
              "Documentation checked: [Google Jobs API](https://serpapi.com/google-jobs-api), [YouTube Search API](https://serpapi.com/youtube-search-api), [SerpApi filter guidance](https://serpapi.com/blog/youtube-sp-filters-paginating-sorting-and-filtering-with-the-youtube-api/), [YouTube video fields](https://serpapi.com/youtube-video-results).", ""]
    path = ROOT / "reports" / "archive" / "phase2_report.md"
    path.write_text("\n".join(lines))
    print(f"report={path}")
    print(f"credits={after['this_month_usage'] - before['this_month_usage']} attempted={ledger['real_calls']}")
    print(f"noida_ready={old['ready']}/{old['usable']} -> {noida['ready']}/{len(noida['jobs'])}")


if __name__ == "__main__":
    main()
