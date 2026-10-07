# NextSkill Batch B — fresher data and experience filter

## Experience filter spot-check (cached jobs; 0 calls)

Fifteen listings that the Batch A parser put in “Needs more experience” were reviewed. The phrase column quotes the title or description that triggered the old exclusion. “False” means the quoted text is not reliable evidence of the candidate's minimum experience; it does not prove a fresher qualifies for that job.

| # | Demo role | Listing | Exact trigger phrase | Review |
|---:|---|---|---|---|
| 1 | Analyst | Senior Data Analyst — UnitedHealth Group | `4+ years` | Valid: “of experience in data analytics” follows. |
| 2 | Analyst | Sr. Data Analyst — Team Pumpkin | `Sr` | Valid title seniority; description also says `Experience: 3–4 Years`. |
| 3 | Analyst | Senior Data Analyst I — Softcrayons IT Education | `5 - 6 Years` | Valid experience field. |
| 4 | Analyst | Lead Data Analyst (OAC) (Noida) — Important Group | `06-08 years` | Valid: “Total Experience Expected” precedes it. |
| 5 | Analyst | Marketing Data Analyst — The House of Abhinandan Lodha | `2 to 5 years` | Valid: “of hands-on experience” follows. |
| 6 | Analyst | Data & Analytics Analyst — Softcrayons IT Education | `1 - 2 Years` | Valid experience field. |
| 7 | Analyst | Senior Financial Data Analyst — SimCorp | `5+ years` | Valid: “of experience in financial data analysis” follows. |
| 8 | Frontend | Angular Frontend Developer — Parangat Technologies | `4-9 years` | Valid job requirement. |
| 9 | Frontend | Hiring Drupal Frontend Developer (Bengaluru) — Specbee | `3+ years` | Valid: “of experience in Drupal development” follows. |
| 10 | Frontend | Frontend Developer (ReactJS) — Lenskart | `3 to 6 years` | Valid ideal experience. |
| 11 | Frontend | Senior Frontend Developer — Two95 International Inc. | `Senior` | Valid title seniority; description also says `9+yrs`. |
| 12 | Frontend | Frontend Developer - React.js/AngularJS — xTag Services | `Experience :  4+ Years` | Valid experience field. |
| 13 | Frontend | Senior Frontend Developer At Flipkart Internet Pvt Ltd — FrontendGeek | `Senior` | Valid title seniority. |
| 14 | Frontend | Frontend Developer – SDE3 — Volks Consulting | `Overall 4.5+ years` | Valid candidate experience. |
| 15 | Frontend | Frontend Developer React.js, TypeScript & Shopify (Gurugram) — Aumraa | `Experience: 25 Years` | **False/ambiguous:** implausible individual minimum, likely a lost range hyphen. No independent minimum appears in the title. |

**Trigger-evidence precision on this sampled set:** before **14/15 (93.3%)**; after **14/14 retained (100%)**. The malformed `25 Years` text might have meant a 2–5 year range; the listing itself is still ambiguous. The new parser drops implausible values over 15 years, reads numeric years only in candidate requirement context, ignores company history and warranty wording, and does not infer seniority from “report to a Senior Manager.” It also handles a scraped `3 5 years` range as a 3-year minimum. This small audit does not measure recall or actual hiring eligibility.

On the original cached pages, set-aside counts are **Noida 9 → 9** and **Bengaluru 17 → 17**. The removed Aumraa trigger is offset by another valid frontend requirement the old parser missed. After merging the new fresher searches, set-aside counts become **Noida 14** and **Bengaluru 22**.

## Fresher searches and results

The product searches the base role's requested pages, then one first page each for `<role> fresher` and `Junior <role>` when the selected experience level is Fresher. Intern roles also add `<role> intern`. Duplicate company/title listings are merged, and their search origins are preserved in Search Replay.

| Demo | New query | First-page listings | Location |
|---|---|---:|---|
| Data Analyst | `Data Analyst fresher` | 10 | Noida, India |
| Data Analyst | `Junior Data Analyst` | 10 | Noida, India |
| Frontend Developer | `Frontend Developer fresher` | 10 | Bengaluru, India |
| Frontend Developer | `Junior Frontend Developer` | 9 | Bengaluru, India |

Noida returned enough results, so Delhi fallback was unnecessary. All four responses are cached. The current cached base-plus-variant merges have **34** unique Noida listings and **45** unique Bengaluru listings before experience filtering.

| Fresher persona | Eligible listings | Jobs with core requirements | Ready | Needs more experience | Top scored skill | Jobs unlocked | Sample confidence | Robustness |
|---|---:|---:|---:|---:|---|---:|---|---|
| Excel, basic Python → Data Analyst, Noida | 20 | 17 | 1/17 | 14 | SQL | +8 | Medium | Power BI leads at threshold 0.6 |
| HTML, CSS, JavaScript → Frontend Developer, Bengaluru | 23 | 19 | 7/19 | 22 | React (or Angular / Vue.js) | +8 | Medium | Pick unchanged across checked settings |

Both demos now exceed the 12-listing target, so the top scored card gets a 🥇 badge. These are saved snapshots; “ready” means core-skill coverage reaches the selected threshold, not that hiring is likely.

The analyst mid persona still has **11/13** usable jobs within reach on the base Noida pages and no one-skill unlock. The app now says: “You already match most jobs here. Your best next step is applying, or exploring a more senior role.”

## Credits and verification

The free Account API reported `this_month_usage` **238 → 242** and credits remaining **12 → 8**. The Batch B ledger records **4 real search attempts** out of its six-call cap. Eight credits remain untouched for the demo. There were no new YouTube searches.

The [Google Jobs API](https://serpapi.com/google-jobs-api) documentation was checked for `q`, `location`, `gl`, `hl`, `next_page_token`, `jobs_results`, and pagination. All offline tests passed (**23 tests**). The updated cached demo screenshots are [Noida](../screenshots/batch_b_noida.png), [Bengaluru](../screenshots/batch_b_frontend.png), and [Search Replay](../screenshots/batch_b_replay.png).
