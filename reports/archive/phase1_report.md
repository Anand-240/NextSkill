# NextSkill Phase 1 report

Run at 2026-10-07T19:41:19.010089+00:00 UTC.

Matcher precision on 20 fixed random matches: 80% before (16/20), 100% after (16/16 retained). See [audit](../matcher_audit.md) for the sentences and flags.

## Credits

Account API this_month_usage: 222 → 228 (6 credited searches).
Phase 1 search requests attempted: 6 of 6 maximum. Free account checks before and after.

## Saved-data demo

Threshold: 0.4. Historical validation fixtures; missing course fixtures show unavailable hours.

Role/city: Data Analyst, Noida
Ready: 1 of 16 usable jobs; 3 ignored (<3 skills); 1 likely duplicates removed.
User skills: Excel, Python, SQL.
| Rank | Skill | Jobs unlocked | Learning hours | Jobs/hour |
|---:|---|---:|---:|---:|
| 1 | Power BI | 4 | 0.51 | 7.82 |
| 2 | Data Visualization | 3 | unavailable | unavailable |
| 3 | Tableau | 3 | unavailable | unavailable |
| 4 | Data Analysis | 2 | unavailable | unavailable |
| 5 | Data Cleaning | 2 | unavailable | unavailable |

Search replay:
- fixture: google_jobs — Data Analyst — Noida, India
- fixture: google_jobs — Data Analyst — Noida, India
- fixture: youtube — Power BI full course for beginners
- fixture missing: youtube — Data Visualization full course for beginners
- fixture missing: youtube — Tableau full course for beginners
- fixture missing: youtube — Data Analysis full course for beginners
- fixture missing: youtube — Data Cleaning full course for beginners

## Live demo

Threshold: 0.4; one new Google Jobs page so five YouTube queries fit the six-call cap.

Role/city: Business Analyst, Hyderabad
Ready: 0 of 5 usable jobs; 5 ignored (<3 skills); 0 likely duplicates removed.
User skills: Excel, Power BI, SQL.
| Rank | Skill | Jobs unlocked | Learning hours | Jobs/hour |
|---:|---|---:|---:|---:|
| 1 | Compliance | 1 | 1.03 | 0.97 |
| 2 | CRM | 1 | 1.08 | 0.92 |
| 3 | Tableau | 2 | 6.00 | 0.33 |
| 4 | Agile | 1 | 3.42 | 0.29 |
| 5 | Data Analysis | 1 | 7.19 | 0.14 |

Search replay:
- cache: google_jobs — Business Analyst — Hyderabad, India
- live: youtube — Tableau full course for beginners
- live: youtube — Agile full course for beginners
- live: youtube — CRM full course for beginners
- live: youtube — Compliance full course for beginners
- live: youtube — Data Analysis full course for beginners

## App verification

Seven offline unit tests passed. Streamlit rendered both the saved-data and live-data runs end to end. Screenshots: [saved-data](../../screenshots/fixture.png), [live-data](../../screenshots/live.png).

Learning hours are the median duration of up to three eligible free course videos per skill; videos under 20 minutes are excluded. These estimates do not guarantee job readiness or hiring.

API field references: [Google Jobs](https://serpapi.com/google-jobs-api), [YouTube search](https://serpapi.com/youtube-search-api), [YouTube video results](https://serpapi.com/youtube-video-results), [Account](https://serpapi.com/account-api).
