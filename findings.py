"""Headline findings computed from reports/final_results.json. Pure functions, shared by the site and the documents."""
from __future__ import annotations


def key_findings(results: dict) -> list[str]:
    rows = list(results["pairs"].values())
    cities = {row["city"] for row in rows}
    scored = sum(row["scored"] for row in rows)
    differ = sum(1 for row in rows if row["fastest_win"] and row["fastest_win"] != row["biggest_unlock"])
    with_picks = sum(1 for row in rows if row["fastest_win"])
    labels = {name: sum(row["confidence"] == name for row in rows) for name in ("Strong", "Likely", "Uncertain")}
    limited = sum(bool(row["flags"]["limited_data"]) for row in rows)
    share = [(row["matches"] / row["scored"], row) for row in rows if row["scored"]]
    low, high = min(share, key=lambda x: x[0]), max(share, key=lambda x: x[0])
    return [
        f"{len(rows)} saved markets across {len(cities)} cities, {scored} scored listings in total. Each answer is "
        "counted from the listings saved for that market, not from a national dataset.",
        f"The fastest win differs from the biggest unlock in {differ} of the {with_picks} markets with a measured pick, "
        "so a short course can beat a big skill per hour.",
        f"Pick stability is Strong in {labels['Strong']}, Likely in {labels['Likely']} and Uncertain in {labels['Uncertain']} markets; "
        f"{limited} markets are flagged as limited data. The example profile matched between "
        f"{low[0]:.0%} ({low[1]['role']}, {low[1]['city']}) and {high[0]:.0%} ({high[1]['role']}, {high[1]['city']}) of scored listings.",
    ]


def flag_text(row: dict) -> str:
    names = [label for key, label in (("limited_data", "limited data"), ("dictionary_warning", "few skills detected"))
             if row["flags"].get(key)]
    return ", ".join(names) or "none"


def map_table(rows: dict, only_cities: set[str] | None = None) -> str:
    """Markdown table of saved markets."""
    text = ("| Role / city | Eligible | Scored | Matches | Must-haves met among matches | Fastest win | Biggest unlock | Pick stability | Flags |\n"
            "|---|---:|---:|---:|---:|---|---|---|---|\n")
    for row in rows.values():
        if only_cities and row["city"] not in only_cities:
            continue
        text += (f"| {row['role']} / {row['city']} | {row['eligible']} | {row['scored']} | {row['matches']} | "
                 f"{row['must_haves_met']} | {row['fastest_win'] or 'Unavailable'} | {row['biggest_unlock'] or 'Unavailable'} | "
                 f"{row['confidence']} | {flag_text(row)} |\n")
    return text


def gap_rows(gap: dict) -> list[dict]:
    return gap["rows"]


def gap_sentence(gap: dict) -> str:
    """The job-information gap in one honest sentence, computed from reports/job_gap.json."""
    rows = gap_rows(gap)
    totals = [row["listings"] for row in rows]
    low = min(rows, key=lambda row: (row["in_city"] / row["listings"], row["role"], row["city"]))
    high = max(rows, key=lambda row: (row["in_city"] / row["listings"], row["role"], row["city"]))
    others = ", ".join(low["other_places"][:2])
    return (f"Asked the same plain question in {len({row['city'] for row in rows})} cities, Google Jobs returned between {min(totals)} and "
            f"{max(totals)} listings every time (the three-page limit), but only {low['in_city']} of {low['listings']} "
            f"{low['role']} listings for {low['city']} were located there (the rest were in {others} and elsewhere), against "
            f"{high['in_city']} of {high['listings']} for {high['role']} in {high['city']}. A fresher outside the biggest hubs "
            "can see far less local evidence than the list length suggests.")


def gap_table(gap: dict) -> str:
    text = ("| Role | City | Visible listings | Located in the city | Distinct employers | Pages | Snapshot |\n"
            "|---|---|---:|---:|---:|---:|---|\n")
    for row in gap_rows(gap):
        text += (f"| {row['role']} | {row['city']} | {row['listings']} | {row['in_city']} | {row['distinct_employers']} | "
                 f"{row['pages_fetched']} | {', '.join(row['snapshot_dates'])} |\n")
    return text
