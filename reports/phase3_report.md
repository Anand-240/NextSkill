# NextSkill Phase 3: demo readiness

All figures below use the saved Noida and Bengaluru job responses and cached course responses. No SerpApi requests were made in Phase 3.

## Coverage distributions

Each `value×count` is the share of a job's core skills present in the persona resume and the number of jobs with that value. Jobs with no detected core skill are omitted.

| Role | Persona | Coverage distribution |
|---|---|---|
| Data Analyst | Fresher | 0.000×4, 0.143×1, 0.167×2, 0.200×1, 0.250×3, 0.333×3, 0.400×1, 0.500×2 |
| Data Analyst | Mid | 0.000×2, 0.429×1, 0.500×6, 0.600×2, 0.667×3, 0.750×2, 1.000×1 |
| Data Analyst | Frontend fresher | 0.000×17 |
| Frontend Developer | Fresher | 0.000×28 |
| Frontend Developer | Mid | 0.000×28 |
| Frontend Developer | Frontend fresher | 0.000×4, 0.125×1, 0.167×1, 0.250×3, 0.286×1, 0.300×1, 0.333×5, 0.375×2, 0.429×2, 0.500×5, 0.600×2, 0.750×1 |

## Default threshold

**0.50** is the single default for both demo roles. In the saved Noida jobs, the analyst fresher reaches 2/17 jobs (12%) at this threshold, while the analyst mid persona reaches 14/17. In Bengaluru, the frontend fresher reaches 8/28 (29%). The adjacent 0.55 threshold would leave the analyst fresher at 0/17, so 0.50 is the highest slider step that gives both matching beginners a small but non-zero share. The slider remains configurable, and readiness is a skill-overlap signal rather than a hiring probability.

## Persona table at 0.50

| Role | Persona | Ready | Top recommendations | Role-fit warning |
|---|---|---:|---|---|
| Data Analyst | Fresher | 2/17 | SQL +7; Power BI +5; Tableau +4 | no |
| Data Analyst | Mid | 14/17 | Power BI +1; Data Visualization +1 | no |
| Data Analyst | Frontend fresher | 0/17 | Tableau +1; Data Visualization +1; Excel +1 | yes |
| Frontend Developer | Fresher | 0/28 | React +2; UI/UX +1; Git +1 | yes |
| Frontend Developer | Mid | 0/28 | React +2; UI/UX +1; Git +1 | yes |
| Frontend Developer | Frontend fresher | 8/28 | React +10; TypeScript +4; UI/UX +7 | no |

## Demo outputs

- Noida fresher: SQL is the top scored skill, followed by Power BI; the two-skill plan is SQL + Tableau. The SQL card links the unlocked listings and the course videos behind its ~4.34-hour estimate.
- Bengaluru frontend fresher: React is the top scored skill, followed by TypeScript. The React card links the unlocked listings and the course videos behind its ~5.09-hour estimate.
- Generic terms still contribute to core-skill coverage but cannot appear in the ranked skills or two-skill plan.
- A profile below 20% coverage on most jobs triggers the role-fit warning; this occurs for the cross-role personas above.

## README preview

> Learn the one skill that unlocks the most real jobs, in the least time.

The [README](../README.md) explains the problem, Mermaid flow, SerpApi engines, screenshot examples, validation, limitations, setup, tests, AI tools and MIT licence. The [demo script](../DEMO.md) covers the three-minute recording.

## Verification

Twelve offline unit tests passed, including the new default, generic-skill exclusion and role-fit warning. The app was checked in Demo data mode for both saved roles. [Noida screenshot](../screenshots/phase3_noida.png) · [Frontend screenshot](../screenshots/phase3_frontend.png).
