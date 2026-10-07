# Matcher precision audit

20 seeded random (skill, job) matches from validation job descriptions. Human review flags mentions that do not state a skill requirement.

| # | Skill | Job | Sentence | False before? | Kept after? |
|---:|---|---|---|---|---|
| 1 | Python | IT Analyst Applications (Python Developer - Automation & AI) (Bengaluru) | - Robust knowledge of Python frameworks such as Flask, FastAPI, or Django. | no | yes |
| 2 | Graphic Design | IT Analyst Applications (Python Developer - Automation & AI) (Bengaluru) | Implementation: Knowledge of how to run applications for organizations; ability to implement application software within an organization and help end-users perform specific tasks (ex: accounting or graphic design). | yes | no |
| 3 | Digital Marketing | Digital Marketing Internship in Pune, Pimpri-Chinchwad, Wakad | We are looking for a creative, enthusiastic, and motivated Digital Marketing Intern to join our team and gain hands-on experience in digital marketing, content creation, and social media marketing. | no | yes |
| 4 | Excel | Sales and Marketing Internship | Proficiency in Microsoft Office Suite (Word, Excel, PowerPoint). | no | yes |
| 5 | Python | Python Developer Trainee | Stay updated with emerging technologies and best practices in Python development. | no | yes |
| 6 | Digital Marketing | Client Servicing Intern – Digital Marketing | You don’t need to be a digital marketing expert. | yes | no |
| 7 | Data Visualization | Data Analyst | Data Visualization and Reporting: | no | yes |
| 8 | Python | Senior Python Developer – Game Engine Scalability Product Engineering · Bengaluru · | Expertise in Python libraries to fully leverage Python’s capabilities. | no | yes |
| 9 | Google Ads | Social Media Marketing Intern | Responsibilities: Contribute to live marketing projects at upGrad; Build, test and document solutions using SEO, Google Ads, Meta Ads, Social Media; Collaborate with cross-functional teams and present your work; Apply feedback to ship production-quality output. | no | yes |
| 10 | Compliance | Senior Financial Data Analyst | This role combines deep financial data domain expertise with analytical and technical capabilities to support business decision-making, operational excellence, and regulatory compliance. | no | yes |
| 11 | SQL | Data Analyst Internship | The ideal candidate should have strong knowledge of Excel, MS Office, SQL, and data visualization, as well as experience with tools like Tableau, PowerBI, or Maven. | no | yes |
| 12 | Digital Marketing | Digital Marketing Internship in Pune, Pimpri-Chinchwad, Wakad | Stay updated with digital marketing trends, tools, and best practices. | no | yes |
| 13 | Python | Python Developer \| Jobs In India | Candidates should have strong hands-on Python programming skills along with knowledge of data structures, OOP and problem-solving. | no | yes |
| 14 | Kubernetes | Senior Back-End Developer - Python Developer | Kubernetes or similar container orchestration, beyond Docker.Public cloud, AWS preferred.Event-driven architecture (Kafka, CDC/streaming).Big-data / analytics warehouses (Snowflake, Redshift).Java/Kotlin (Spring Boot) - you'll integrate closely with our JVM platform.#LI-MK1 | no | yes |
| 15 | Digital Marketing | Digital Marketing Internship in Pune, Pimpri-Chinchwad, Wakad | If you are passionate about digital marketing, have a creative mindset, and want to gain real-world experience while working with a growing CRM & AI company, we’d love to hear from you. | no | yes |
| 16 | Digital Marketing | Digital Marketing Intern | This is a hands-on internship where you will get practical exposure to SEO, Google Ads, social media marketing, content marketing, Google Analytics, and other digital marketing activities while working on real client projects. | no | yes |
| 17 | Digital Marketing | Content Creator & Digital Marketing Intern (Anchor Role) | Content Creator & Digital Marketing Intern | yes | no |
| 18 | Tableau | Data & Analytics Analyst | Good knowledge of Excel, SQL, Power BI/Tableau and analytical skills is required. | no | yes |
| 19 | Compliance | Data Analyst (Supply Chain and Inventory Management) | Track purchase orders, open orders, lead times, and vendor compliance metrics. | yes | no |
| 20 | Databricks | Senior Data Analyst I | Databricks, Python, Pandas, PySpark, Apache Spark, Snowflake, JIRA, Tableau, Power BI Minimum of 5 years of work experience in business intelligence, data engineering, analytics, data analysis, or related discipline Strong SQL skills, including experience working with large and complex datasets. | no | yes |

Precision before: 80.0% (16/20).
Precision after: 100.0% on retained sampled matches.

Context filters remove bare role headings, explicit ‘don't need’ statements, illustrative examples, and vendor compliance metrics. This is a small, hand-reviewed sample; it does not establish recall.
