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
        f"Confidence is Strong in {labels['Strong']}, Likely in {labels['Likely']} and Uncertain in {labels['Uncertain']} markets; "
        f"{limited} markets are flagged as limited data. The example profile matched between "
        f"{low[0]:.0%} ({low[1]['role']}, {low[1]['city']}) and {high[0]:.0%} ({high[1]['role']}, {high[1]['city']}) of scored listings.",
    ]


def flag_text(row: dict) -> str:
    names = [label for key, label in (("limited_data", "limited data"), ("dictionary_warning", "outside strongest areas"))
             if row["flags"].get(key)]
    return ", ".join(names) or "none"


def map_table(rows: dict, only_cities: set[str] | None = None) -> str:
    """Markdown table of saved markets."""
    text = ("| Role / city | Eligible | Scored | Matches | Must-haves met among matches | Fastest win | Biggest unlock | Confidence | Flags |\n"
            "|---|---:|---:|---:|---:|---|---|---|---|\n")
    for row in rows.values():
        if only_cities and row["city"] not in only_cities:
            continue
        text += (f"| {row['role']} / {row['city']} | {row['eligible']} | {row['scored']} | {row['matches']} | "
                 f"{row['must_haves_met']} | {row['fastest_win'] or 'Unavailable'} | {row['biggest_unlock'] or 'Unavailable'} | "
                 f"{row['confidence']} | {flag_text(row)} |\n")
    return text
