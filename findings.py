"""Headline findings computed from reports/final_results.json. Pure functions, shared by the site and the documents."""
from __future__ import annotations

import re

from engine import hours_text


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
    places = natural_list([re.sub(r"\s*\(\d+\)$", "", place) for place in low["other_places"][:3]])
    return (f"Asked the same plain question for {len({row['role'] for row in rows})} roles in {len({row['city'] for row in rows})} cities, "
            f"Google Jobs returned between {min(totals)} and {max(totals)} listings every time (the three-page limit). "
            f"How many were located in the named city varied a lot: only {low['in_city']} of {low['listings']} for "
            f"{low['role']} in {low['city']} (most of the rest were in {places}), against {high['in_city']} of "
            f"{high['listings']} for {high['role']} in {high['city']}. A fresher outside the biggest hubs can see far less "
            "local evidence than the length of the list suggests.")


def gap_table(gap: dict) -> str:
    text = ("| Role | City | Visible listings | Located in the city | Distinct employers | Pages | Snapshot |\n"
            "|---|---|---:|---:|---:|---:|---|\n")
    for row in gap_rows(gap):
        text += (f"| {row['role']} | {row['city']} | {row['listings']} | {row['in_city']} | {row['distinct_employers']} | "
                 f"{row['pages_fetched']} | {', '.join(row['snapshot_dates'])} |\n")
    return text


def _hours(value: float | None) -> str:
    return "hours unknown" if value is None else f"{value:.1f} h"


def baseline_rows(results: dict) -> list[dict]:
    """Markets with a headline pick, compared with the frequency-only baseline."""
    rows = []
    for pair in results["pairs"].values():
        base = pair.get("baseline")
        if base and base["headline_skill"]:
            rows.append({"market": f"{pair['role']} / {pair['city']}", **base})
    return rows


def _reading(row: dict) -> str:
    more, same = row["headline_unlocked"] > row["unlocked"], row["headline_unlocked"] == row["unlocked"]
    hours, base_hours = row["headline_hours"], row["hours"]
    if base_hours is None or hours is None:
        shorter = None
    else:
        shorter = hours < base_hours
    if (more or same) and shorter:
        return "headline unlocks " + ("more" if more else "as many") + " listings in less course time"
    if more:
        return "headline unlocks more listings"
    if shorter:
        return "headline unlocks fewer listings in less course time"
    return "headline unlocks fewer listings"


def baseline_summary(results: dict) -> dict:
    rows = baseline_rows(results)
    agree = sum(row["agrees"] for row in rows)
    differ = [row for row in rows if not row["agrees"]]
    return {"markets": len(rows), "agree": agree, "differ": differ,
            "at_least_as_many": sum(row["headline_unlocked"] >= row["unlocked"] for row in differ),
            "faster": sum(row["headline_hours"] is not None and row["hours"] is not None and row["headline_hours"] < row["hours"]
                          for row in differ)}


def baseline_text(results: dict) -> str:
    summary = baseline_summary(results)
    differ = summary["differ"]
    lines = [f"A simple alternative is to recommend the missing core skill that the most scored listings ask for, with no course "
             f"hours. The two methods agree in {summary['agree']} of {summary['markets']} markets that have a headline pick. In the "
             f"other {len(differ)}, the headline pick unlocks at least as many extra listings as the frequency-only pick in "
             f"{summary['at_least_as_many']} and needs less course time in {summary['faster']}. So including course hours does "
             "change the answer, but it trades off listings against hours, and it rests on video lengths that are only a "
             "proxy for study time.\n",
             "| Market | Most asked skill (extra listings, course time) | Headline pick (extra listings, course time) | Reading |",
             "|---|---|---|---|"]
    for row in differ:
        lines.append(f"| {row['market']} | {row['skill']} (+{row['unlocked']}, {_hours(row['hours'])}) | "
                     f"{row['headline_skill']} (+{row['headline_unlocked']}, {_hours(row['headline_hours'])}) | {_reading(row)} |")
    return "\n".join(lines) + "\n"


STABILITY_ORDER = {"Strong": 0, "Likely": 1, "Uncertain": 2}


def example_key(results: dict) -> str:
    """The market with the best pick-stability label and, among equals, the most scored listings."""
    rows = [(key, row) for key, row in results["pairs"].items() if row.get("headline_skill")]
    return min(rows, key=lambda item: (STABILITY_ORDER[item[1]["confidence"]], -item[1]["scored"], item[0]))[0]


def natural_list(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def example_text(results: dict, resume: str) -> str:
    """One worked example, written once and used by the README, the demo script and the Home page."""
    row = results["pairs"][example_key(results)]
    head = next(item for item in row["ranked"] if item["skill"] == row["headline_skill"])
    skills = natural_list([part.strip() for part in resume.split(",") if part.strip()])
    article = "an" if row["role"][0] in "AEIOU" else "a"
    courses = "course" if head["hours"] and head["hours"] < 1.5 else "courses"
    return (f"Priya is a sample profile, not a real person. She knows {skills} and wants {article} {row['role']} job in "
            f"{row['city']}. In **{row['scored']}** scored local listings pulled through SerpApi, her profile meets the core skills "
            f"of **{row['matches']}**. **{head['display_skill']}** would add **{head['unlocked']}** more, for {hours_text(head['hours'])} "
            f"of free {courses}. Pick stability: {row['confidence']}, based on {row['stability_listings']} listings. "
            "Every listing and course behind that estimate is linked.")


def compact_table(results: dict) -> str:
    text = ("| Market | Scored listings | Headline pick | Pick stability | Flags |\n"
            "|---|---:|---|---|---|\n")
    for row in results["pairs"].values():
        pick = row["headline_skill"] or "none"
        text += f"| {row['role']} / {row['city']} | {row['scored']} | {pick} | {row['confidence']} | {flag_text(row)} |\n"
    return text
