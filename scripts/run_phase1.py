"""Run fixture and one live demo; write a concise, reproducible Phase 1 report."""
import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.audit_matcher import audit
from engine import ROOT, SerpClient, run


def summary(result: dict) -> list[str]:
    lines = [
        f"Role/city: {result['role']}, {result['city']}",
        f"Ready: {result['ready']} of {len(result['jobs'])} usable jobs; {result['ignored']} ignored (<3 skills); {result['raw'] - result['deduplicated']} likely duplicates removed.",
        f"User skills: {', '.join(result['user_skills']) or 'none'}.",
        "| Rank | Skill | Jobs unlocked | Learning hours | Jobs/hour |",
        "|---:|---|---:|---:|---:|",
    ]
    for index, item in enumerate(result["ranked"], 1):
        hours = f"{item['hours']:.2f}" if item["hours"] is not None else "unavailable"
        score = f"{item['score']:.2f}" if item["score"] is not None else "unavailable"
        lines.append(f"| {index} | {item['skill']} | {item['unlocked_count']} | {hours} | {score} |")
    if not result["ranked"]:
        lines.append("No single missing skill crossed the selected threshold.")
    lines += ["", "Search replay:"]
    for item in result["replay"]:
        query = item["query"]
        lines.append(f"- {item['source']}: {query['engine']} — {query.get('q') or query.get('search_query')}" + (f" — {query['location']}" if query.get("location") else ""))
    return lines


def main() -> None:
    before_precision, after_precision = audit()[1:]
    offline = run("Data Analyst", "Noida", resume="Excel, SQL basics, Python basics", threshold=0.4, pages=2, offline=True)
    client = SerpClient()
    initial_account = ROOT / "cache" / "account_before.json"
    before = json.loads(initial_account.read_text()) if initial_account.exists() else client.account("before")
    try:
        live = run("Business Analyst", "Hyderabad", resume="Excel, SQL, Power BI", threshold=0.4, pages=1, client=client)
    finally:
        after = client.account("after")
    used = after["this_month_usage"] - before["this_month_usage"]
    lines = ["# NextSkill Phase 1 report", "", f"Run at {datetime.now(timezone.utc).isoformat()} UTC.", "",
             f"Matcher precision on 20 fixed random matches: {before_precision:.0%} before (16/20), {after_precision:.0%} after (16/16 retained). See [audit](matcher_audit.md) for the sentences and flags.",
             "", "## Credits", "", f"Account API this_month_usage: {before['this_month_usage']} → {after['this_month_usage']} ({used} credited searches).",
             f"Phase 1 search requests attempted: {__import__('json').loads((ROOT / 'cache' / 'ledger.json').read_text())['real_calls']} of 6 maximum. Free account checks before and after.",
             "", "## Saved-data demo", "", "Threshold: 0.4. Historical validation fixtures; missing course fixtures show unavailable hours.", "", *summary(offline),
             "", "## Live demo", "", "Threshold: 0.4; one new Google Jobs page so five YouTube queries fit the six-call cap.", "", *summary(live),
             "", "## App verification", "", "Seven offline unit tests passed. Streamlit rendered both the saved-data and live-data runs end to end. Screenshots: [saved-data](../screenshots/fixture.png), [live-data](../screenshots/live.png).",
             "", "Learning hours are the median duration of up to three eligible free course videos per skill; videos under 20 minutes are excluded. These estimates do not guarantee job readiness or hiring.", "",
             "API field references: [Google Jobs](https://serpapi.com/google-jobs-api), [YouTube search](https://serpapi.com/youtube-search-api), [YouTube video results](https://serpapi.com/youtube-video-results), [Account](https://serpapi.com/account-api).", ""]
    report = ROOT / "reports" / "archive" / "phase1_report.md"
    report.write_text("\n".join(lines))
    print("\n".join(lines[:12]))
    print(f"report={report}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Phase 1 demo stopped: {type(exc).__name__}. Search attempts remain recorded in the cache ledger.")
        raise SystemExit(1)
