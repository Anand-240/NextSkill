# Research for NextSkill

Checked 2026-10-09. Sources describe the problem and platform contracts; they do not
validate NextSkill's recommendations. All project outcomes require separate evidence.

## A1 - Requirements map

[Official rules](https://serpapi.github.io/serpapi-india-hackathon-2026/rules.html):

| Requirement | Evidence or remaining action |
|---|---|
| India resident, at least 18; one to five eligible contributors; organizer exclusions | Participant must confirm eligibility |
| Material SerpApi functionality | Jobs and YouTube determine outputs in engine.py |
| Public repository and setup instructions | GitHub repository and README |
| Local working screen recording under three minutes; accessible privately | DEMO.md is a script; human must record and publish |
| Authenticated website submission, completed by October 10, 23:59 IST | Human must submit; a draft does not qualify |
| Lead contact, occupation, experience; team details when applicable | Human enters privately in submission form |
| Select track, prior-project status, discovery source; accept rules and terms | Human form actions; Knowledge & Public Interest intended |
| Explain API use; disclose AI assistance | README; keep and update disclosure |
| Accessible, functional, honest entry; rights to all components | Tests and gates; participant remains responsible |
| No exposed secrets or private data, manipulation or infringement | Security scans; source attribution; honest evidence |

[Terms](https://serpapi.github.io/serpapi-india-hackathon-2026/terms.html): each participant
must accept and supply accurate eligibility information. Sanctions and anti-corruption
conditions apply. Up to three active entries are allowed. Third-party notices and rights
remain necessary; public materials cannot be confidential. Participants retain their
original work but grant the organizer an enduring license for judging, administration
and promotion, including names and demo excerpts. Human acceptance is required; this
repository cannot establish it. Award verification may require identity, tax and bank
information. Credits are subject to account terms, expiry and transfer restrictions.
Participants bear their costs and responsibilities; service availability is not promised.
Organizer discretion, changes, liability provisions and dispute-resolution terms apply.
Read the linked terms before submitting; this map does not replace them.

## A2 - API contracts and limits

| API and current documentation | Exact request contract | Response fields and limits |
|---|---|---|
| [Google Jobs](https://serpapi.com/google-jobs-api) | `engine=google_jobs`, `q=<role>`, `location=<city>, India`, `gl=in`, `hl=en`; subsequent requests use `next_page_token` | `jobs_results`: `job_id`, `title`, `company_name`, `description`, `location`, `share_link`, `detected_extensions.posted_at`, `extensions`; `serpapi_pagination.next_page_token`; up to ten results/page; `start` is discontinued |
| [YouTube search](https://serpapi.com/youtube-search-api) | `engine=youtube`, **`search_query`**, not `q`; `gl=in`, `hl=en`, `sp` for filter/pagination | `video_results`; `serpapi_pagination.next_page_token` becomes the next `sp`; this app reads only the first page |
| [Video fields](https://serpapi.com/youtube-video-results) | Returned by YouTube search | `title`, `link`, `channel.name`, `length` (M:SS or H:MM:SS); missing/live durations are unusable |
| [Google web search](https://serpapi.com/search-api) | `engine=google`, `q=<skill> course (site:nptel.ac.in OR site:swayam.gov.in)`, `gl=in`, `hl=en` | `organic_results`: `title`, `link`, `snippet`; validate returned hosts; search snippets alone do not establish course duration |
| [Account API](https://serpapi.com/account-api) | GET `/account.json` with the private `api_key`; never save its full response | `this_month_usage`, `total_searches_left`, `plan_searches_left`; account requests do not consume search quota |

The app passes raw `EgIYAg==` (long videos) and `EgIYAw==` (medium videos)
through `urlencode` exactly once. The docs document `sp` but do not promise a stable
catalogue of duration tokens. [SerpApi's example](https://serpapi.com/blog/making-youtube-mentions-tracker-in-python/)
uses the medium token. Keep response duration checks (courses >=30 minutes on fallback;
revision 5 to 25 minutes) even when a filter is sent. The latter is an acceptance
window, not a promise that YouTube's 4 to 20 minute filter returns 25-minute videos.

Current code correctly uses `search_query`, Jobs continuation tokens, `gl/hl`, a
75-second timeout, no retry, and treats "hasn't returned any results" as empty.
Required fixes: B1 measures all saved candidates; B3 makes Account failure nonfatal;
B4 validates course title relevance. No unsupported API parameter needs replacement.
App policy caps pages at three; this is not a SerpApi platform limit.

## A3 - Problem evidence

1. [ILO and IHD, India Employment Report 2024](https://www.ilo.org/publications/india-employment-report-2024-youth-employment-education-and-skills)
   examines youth employment, education and skills. It motivates investigating the
   education-to-work transition; it does not prove that a course recommendation
   causes employment. [Full report](https://www.ilo.org/sites/default/files/2024-08/India%20Employment%20-%20web_8%20April.pdf).
2. [World Bank, SIMO results (2023)](https://www.worldbank.org/en/results/2023/11/03/helping-india-build-skilled-inclusive-workforce)
   describes district-level, market-relevant training and inclusion. Its reported
   employment outcomes concern that program, not NextSkill. Local relevance and
   disadvantaged learners deserve evaluation here too.
3. [UNICEF, career guidance access (2021)](https://www.unicef.org/india/stories/experience-personalized-unique-career-journey)
   describes a free CBSE career portal, regional-language access, and support for
   teachers. It supports the need for accessible information, not a claim that free
   career guidance is absent. NextSkill should complement these services.
4. [UNICEF, economic opportunities for young people](https://www.unicef.org/india/economic-opportunities-young-people)
   identifies gaps in job awareness, information and employment support. Its YouthHub
   already combines jobs and skills, including languages and tier-2/tier-3 reach.
   This makes an unsupported "first" or "unique" claim inappropriate.

Product inference: an inspectable local listing-to-skill comparison may help applicants
choose a next step. We have not measured its benefit, and cannot attribute structural
unemployment to individual skill gaps. No credible price study was verified here;
we make no claim about an average monetary cost of career guidance.

## Implementation references for later pages

[Streamlit navigation](https://docs.streamlit.io/develop/api-reference/navigation/st.navigation)
runs from the entry point and executes the selected Page with `.run()`. The page
list may change on reruns, allowing a local-key-only live page.
[Multipage concepts](https://docs.streamlit.io/develop/concepts/multipage-apps/page-and-navigation)
explains the shared frame and page state.
[Cache data](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_data)
serializes cached outputs and returns copies; keep personal resume inputs out of
shared cache keys by extracting a canonical skill set first.
[File uploader](https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader)
returns uploaded bytes suitable for the existing pypdf extractor. Cap PDF size and
report parse/OCR limitations instead of exposing a traceback.
