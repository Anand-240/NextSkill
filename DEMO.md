# NextSkill demo script (2 minutes 45 seconds)

**Before recording**

- Run the app **locally** with `streamlit run app.py`, with your key in `.env`. The hosted app has no key and cannot do the live step.
- Leave **Demo data** on. The Bengaluru frontend fresher result (HTML, CSS, JavaScript) appears automatically. Keep **Fresher**, threshold **0.50** and core share **0.25**.
- Live step cost: 1 job search, plus one YouTube search for each top skill without a cached course. SQL, Tableau, Data Cleaning and Data Visualization courses are already cached and cost nothing. Expect about 1 to 3 credits, never more than 6. Check that your SerpApi dashboard shows enough credits, and do not rehearse the live step.
- If SerpApi is slow, pause the recording while the live search loads. Check that the exported video is 2:45 or shorter.

| Time | On screen | Narration |
|---|---|---|
| 0:00-0:20 | Hero, then the Bengaluru headline and snapshot date. | "Freshers see a wall of skills in job listings and don't know what to learn first. This Bengaluru frontend fresher knows HTML, CSS and JavaScript. Of 19 local listings NextSkill could score, the profile matches 5." |
| 0:20-1:00 | The **Fastest win** and **Biggest unlock** cards. Open the REST API card: expand **7 jobs this skill could unlock**, then point at the course videos. | "REST API is the fastest win: 7 more listings for about 3 hours of free courses. React is the biggest unlock: 10 more listings, but about 5 hours. A short course can win per hour, so the app shows both. These are the real listings behind the 7, and these free full courses set the hour estimate." |
| 1:00-1:25 | Scroll to **Opportunity curve**, then open **Greedy plan vs exact budgets**. | "The curve adds the best next skill per hour: REST API, Responsive Design, then React, reaching 19 listings in about 11 hours. We check this plan against an exact search. With a 10-hour budget, greedy adds 12 matches, but React plus Responsive Design adds 14, and the app shows that." |
| 1:25-1:45 | Change **Demo role** to **Data Analyst, Noida** and press **Find my next skill**. Point at the **Uncertain** label. | "Not every answer is clear. For this Noida analyst fresher, Data Cleaning is the fastest win, with 2 more listings in about one and a half hours. SQL unlocks 5. Data Cleaning wins only 49 percent of resamples, so the app labels it Uncertain." |
| 1:45-2:20 | Turn on **Live search**. Enter **Data Analyst**, **Hyderabad**, experience **1-3 years**, job pages **1**. Press **Find my next skill**, then open **Search replay** and show the credit message. | "Now a live search: Data Analyst in Hyderabad, one to three years of experience, one page. SerpApi fetches current Google Jobs listings and YouTube course lengths. Search Replay marks the job search as a live SerpApi request and reused course searches as local cache, and the message shows the credits used." |
| 2:20-2:45 | Scroll to **How this is calculated**, then back to the top cards. | "Matches mean skill coverage, not a hiring prediction. Course length is not time to mastery, and confidence measures stability, not accuracy. NextSkill turns a wall of job requirements into one clear next step, with the evidence to check it." |

Reference screenshots: [Bengaluru](screenshots/final_frontend.png), [Bengaluru plan](screenshots/final_frontend_plan.png), [Noida](screenshots/final_noida.png), [Search Replay](screenshots/final_replay.png). All demo figures come from [the final report](reports/final_report.md).
