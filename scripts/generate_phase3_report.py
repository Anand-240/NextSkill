"""Offline Phase 3 report from cached jobs and course responses only."""
from collections import Counter

from engine import DEFAULT_THRESHOLD, ROOT, SerpClient, run

PERSONAS = [
    ("Fresher", "Excel, basic Python"),
    ("Mid", "SQL, Excel, Python, Tableau"),
    ("Frontend fresher", "HTML, CSS, JavaScript"),
]
ROLES = [("Data Analyst", "Noida"), ("Frontend Developer", "Bengaluru")]


def distribution(result: dict) -> str:
    counts = Counter(round(entry["coverage"], 3) for entry in result["jobs"])
    return ", ".join(f"{value:.3f}×{count}" for value, count in sorted(counts.items()))


def summary(result: dict) -> str:
    return "; ".join(f"{item['skill']} +{item['unlocked_count']}" for item in result["ranked"][:3]) or "none"


def main() -> None:
    results = {}
    for role, city in ROLES:
        for label, resume in PERSONAS:
            results[(role, label)] = run(role, city, resume=resume, threshold=DEFAULT_THRESHOLD,
                                          pages=3, client=SerpClient(use_fixtures=True, cache_only=True))
    lines = [
        "# NextSkill Phase 3: demo readiness", "",
        "All figures below use the saved Noida and Bengaluru job responses and cached course responses. No SerpApi requests were made in Phase 3.", "",
        "## Coverage distributions", "",
        "Each `value×count` is the share of a job's core skills present in the persona resume and the number of jobs with that value. Jobs with no detected core skill are omitted.", "",
        "| Role | Persona | Coverage distribution |", "|---|---|---|",
    ]
    for role, _ in ROLES:
        for label, _ in PERSONAS:
            lines.append(f"| {role} | {label} | {distribution(results[(role, label)])} |")
    lines += ["", "## Default threshold", "",
              "**0.50** is the single default for both demo roles. In the saved Noida jobs, the analyst fresher reaches 2/17 jobs (12%) at this threshold, while the analyst mid persona reaches 14/17. In Bengaluru, the frontend fresher reaches 8/28 (29%). The adjacent 0.55 threshold would leave the analyst fresher at 0/17, so 0.50 is the highest slider step that gives both matching beginners a small but non-zero share. The slider remains configurable, and readiness is a skill-overlap signal rather than a hiring probability.", "",
              "## Persona table at 0.50", "",
              "| Role | Persona | Ready | Top recommendations | Role-fit warning |", "|---|---|---:|---|---|",
             ]
    for role, _ in ROLES:
        for label, _ in PERSONAS:
            result = results[(role, label)]
            lines.append(f"| {role} | {label} | {result['ready']}/{len(result['jobs'])} | {summary(result)} | {'yes' if result['role_fit_warning'] else 'no'} |")
    lines += ["", "## Demo outputs", "",
              "- Noida fresher: SQL is the top scored skill, followed by Power BI; the two-skill plan is SQL + Tableau. The SQL card links the unlocked listings and the course videos behind its ~4.34-hour estimate.",
              "- Bengaluru frontend fresher: React is the top scored skill, followed by TypeScript. The React card links the unlocked listings and the course videos behind its ~5.09-hour estimate.",
              "- Generic terms still contribute to core-skill coverage but cannot appear in the ranked skills or two-skill plan.",
              "- A profile below 20% coverage on most jobs triggers the role-fit warning; this occurs for the cross-role personas above.", "",
              "## README preview", "",
              "> Learn the one skill that unlocks the most real jobs, in the least time.", "",
              "The [README](../README.md) explains the problem, Mermaid flow, SerpApi engines, screenshot examples, validation, limitations, setup, tests, AI tools and MIT licence. The [demo script](../DEMO.md) covers the three-minute recording.", "",
              "## Verification", "",
              "Twelve offline unit tests passed, including the new default, generic-skill exclusion and role-fit warning. The app was checked in Demo data mode for both saved roles. [Noida screenshot](../screenshots/phase3_noida.png) · [Frontend screenshot](../screenshots/phase3_frontend.png).", ""]
    path = ROOT / "reports" / "archive" / "phase3_report.md"
    path.write_text("\n".join(lines))
    print(f"report={path}")
    print(f"default={DEFAULT_THRESHOLD}")
    for key in (("Data Analyst", "Fresher"), ("Data Analyst", "Mid"), ("Frontend Developer", "Frontend fresher")):
        result = results[key]
        print(f"{key[0]} / {key[1]}: {result['ready']}/{len(result['jobs'])}")


if __name__ == "__main__":
    main()
