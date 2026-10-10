# Current saved results

Generated from final_results.json; historical reports are in archive/.

- 15 saved markets across 10 cities, 163 scored listings in total. Each answer is counted from the listings saved for that market, not from a national dataset.
- The fastest win differs from the biggest unlock in 5 of the 14 markets with a measured pick, so a short course can beat a big skill per hour.
- Pick stability is Strong in 0, Likely in 3 and Uncertain in 12 markets; 8 markets are flagged as limited data. The example profile matched between 0% (Data Analyst, Indore) and 55% (Frontend Developer, Hyderabad) of scored listings.

| Role / city | Eligible | Scored | Matches | Must-haves met among matches | Fastest win | Biggest unlock | Pick stability | Flags |
|---|---:|---:|---:|---:|---|---|---|---|
| Frontend Developer / Bengaluru | 23 | 19 | 9 | 1 | REST API | React | Likely | none |
| Data Analyst / Noida | 20 | 17 | 1 | 0 | SQL | SQL | Uncertain | none |
| Data Analyst / Hyderabad | 16 | 14 | 3 | 1 | Data Cleaning | SQL | Uncertain | none |
| Data Analyst / Pune | 14 | 11 | 2 | 0 | Power BI | Statistics | Uncertain | none |
| Data Analyst / Jaipur | 17 | 14 | 4 | 0 | Power BI | Power BI | Uncertain | none |
| Data Analyst / Indore | 5 | 4 | 0 | 0 | Unavailable | Unavailable | Uncertain | limited data |
| Accountant / Jaipur | 14 | 12 | 3 | 0 | Bookkeeping | Bookkeeping | Likely | none |
| Digital Marketing Executive / Dehradun | 5 | 5 | 1 | 0 | SEO | Google Ads | Uncertain | limited data |
| Python Developer / Bengaluru | 11 | 11 | 4 | 0 | REST API | REST API | Uncertain | limited data |
| Python Developer / Kochi | 7 | 7 | 0 | 0 | PostgreSQL | PostgreSQL | Uncertain | limited data |
| Accountant / Mumbai | 15 | 15 | 5 | 0 | Tally | Tally | Likely | none |
| Accountant / Indore | 9 | 9 | 2 | 1 | TDS | TDS | Uncertain | limited data |
| Digital Marketing Executive / Pune | 7 | 5 | 0 | 0 | Email Marketing | Market Research | Uncertain | limited data, few skills detected |
| Digital Marketing Executive / Chennai | 11 | 9 | 1 | 0 | SEO | SEO | Uncertain | limited data, few skills detected |
| Frontend Developer / Hyderabad | 11 | 11 | 6 | 2 | REST API | REST API | Uncertain | limited data |

## Job-information gap

Asked the same plain question for 2 roles in 5 cities, Google Jobs returned between 26 and 30 listings every time (the three-page limit). How many were located in the named city varied a lot: only 3 of 28 for Accountant in Dehradun (the most common other places were New Delhi, Gurugram and Noida), against 27 of 28 for Data Analyst in Jaipur. A fresher outside the biggest hubs can see far less local evidence than the length of the list suggests.

| Role | City | Visible listings | Located in the city | Distinct employers | Pages | Snapshot |
|---|---|---:|---:|---:|---:|---|
| Data Analyst | Bengaluru | 26 | 22 | 25 | 3 | 2026-10-09 |
| Data Analyst | Pune | 29 | 6 | 28 | 3 | 2026-10-09 |
| Data Analyst | Jaipur | 28 | 27 | 26 | 3 | 2026-10-09 |
| Data Analyst | Indore | 28 | 23 | 27 | 3 | 2026-10-09 |
| Data Analyst | Dehradun | 29 | 21 | 29 | 3 | 2026-10-09 |
| Accountant | Bengaluru | 29 | 26 | 28 | 3 | 2026-10-09 |
| Accountant | Pune | 28 | 8 | 27 | 3 | 2026-10-09 |
| Accountant | Jaipur | 30 | 9 | 29 | 3 | 2026-10-09 |
| Accountant | Indore | 29 | 17 | 29 | 3 | 2026-10-09 |
| Accountant | Dehradun | 28 | 3 | 27 | 3 | 2026-10-09 |

## Does jobs-per-hour change the answer?

A simple alternative is to recommend the missing core skill that the most scored listings ask for, with no course hours. The two methods agree in 4 of 14 markets that have a headline pick. In the other 10, the headline pick unlocks at least as many extra listings as the frequency-only pick in 5 and needs less course time in 7. So including course hours does change the answer, but it trades off listings against hours, and it rests on video lengths that are only a proxy for study time.

| Market | Most asked skill (extra listings, course time) | Headline pick (extra listings, course time) | Reading |
|---|---|---|---|
| Frontend Developer / Bengaluru | React (+10, about 5 hours) | REST API (+8, about 3 hours) | headline unlocks fewer listings in less course time |
| Data Analyst / Hyderabad | SQL (+7, about 4 hours) | Data Cleaning (+4, about 2 hours) | headline unlocks fewer listings in less course time |
| Data Analyst / Pune | Statistics (+4, about 8 hours) | Power BI (+3, about 4 hours) | headline unlocks fewer listings in less course time |
| Data Analyst / Jaipur | SQL (+4, about 4 hours) | Power BI (+4, about 4 hours) | headline unlocks as many listings in about the same course time |
| Digital Marketing Executive / Dehradun | Google Ads (+3, about 5 hours) | SEO (+2, about 2 hours) | headline unlocks fewer listings in less course time |
| Python Developer / Bengaluru | Django (+1, about 3 hours) | REST API (+1, about 3 hours) | headline unlocks as many listings in about the same course time |
| Python Developer / Kochi | HTML (+2, about 5 hours) | PostgreSQL (+3, about 4 hours) | headline unlocks more listings in less course time |
| Accountant / Indore | GST (+2, about 5 hours) | TDS (+2, about 2 hours) | headline unlocks as many listings in less course time |
| Digital Marketing Executive / Pune | Market Research (+2, about 1 hour) | Email Marketing (+1, about 2 hours) | headline unlocks fewer listings |
| Frontend Developer / Hyderabad | Git (+3, about 4 hours) | REST API (+3, about 3 hours) | headline unlocks as many listings in less course time |
