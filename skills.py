"""Conservative skill vocabulary for Indian tech, data, marketing, finance and design jobs."""

import re
from collections import defaultdict

# Canonical names are also searched, except for ambiguous short language names.
SKILLS = {
    "tech": "SQL|Excel|Power BI|Python|Tableau|Java|JavaScript|TypeScript|React|Node.js|AWS|Git|HTML|CSS|Angular|Vue.js|Next.js|Spring Boot|Django|Flask|FastAPI|PHP|C++|C#|Go|R|C|Kotlin|Swift|Android|React Native|MySQL|PostgreSQL|MongoDB|Redis|Docker|Kubernetes|Jenkins|Terraform|Linux|Bash|REST API|GraphQL|Microservices|CI/CD|DevOps|Azure|Google Cloud|Selenium|Playwright|Agile|Scrum|Jira|Postman|Kafka|Spark|Airflow|Databricks|Snowflake|BigQuery|Oracle Database|SQL Server|NoSQL|Data Structures|Algorithms|System Design|Cybersecurity|API Testing|Unit Testing|ETL|Data Warehousing|Machine Learning|Deep Learning|NLP|Computer Vision|TensorFlow|PyTorch|Scikit-learn|Pandas|NumPy".split("|"),
    "data": "Data Analysis|Data Visualization|Statistics|A/B Testing|Business Intelligence|Data Modeling|Data Cleaning|Data Engineering|Predictive Modeling|Regression|Time Series|Power Query|DAX|Looker|Google Analytics|GA4|Google Tag Manager|Mixpanel|Amplitude|dbt".split("|"),
    "marketing": "SEO|SEM|Google Ads|Meta Ads|Facebook Ads|Performance Marketing|Content Marketing|Email Marketing|Social Media Marketing|Marketing Automation|CRM|HubSpot|Salesforce|Mailchimp|WordPress|Copywriting|Keyword Research|Google Search Console|Campaign Management|Conversion Rate Optimization|CRO|Lead Generation|Brand Management|Market Research|Digital Marketing|Canva".split("|"),
    "finance": "Tally|GST|Accounting|Bookkeeping|Financial Modeling|Financial Analysis|Financial Reporting|Budgeting|Forecasting|Auditing|Taxation|Income Tax|TDS|SAP FICO|SAP|ERP|QuickBooks|Zoho Books|Accounts Payable|Accounts Receivable|Reconciliation|Payroll|IFRS|Valuation|Risk Management|Compliance|KYC|AML|Equity Research".split("|"),
    "design": "Figma|Adobe Photoshop|Adobe Illustrator|Adobe XD|UI Design|UX Design|UI/UX|Wireframing|Prototyping|User Research|Usability Testing|Design Systems|Graphic Design|Typography|Adobe InDesign|Adobe After Effects|Adobe Premiere Pro|Blender|AutoCAD|Responsive Design|Web Design|Product Design".split("|"),
}

ALIASES = {
    "Excel": ["MS Excel", "Microsoft Excel", "Advanced Excel"],
    "Power BI": ["PowerBI", "Power-BI", "Microsoft Power BI"],
    "JavaScript": ["JS"], "TypeScript": ["TS"],
    "Node.js": ["NodeJS", "Node JS"], "Next.js": ["NextJS", "Next JS"],
    "Vue.js": ["VueJS", "Vue JS"], "Express.js": ["ExpressJS", "Express JS"],
    "React": ["ReactJS", "React JS"],
    "AWS": ["Amazon Web Services"], "Google Cloud": ["GCP", "Google Cloud Platform"],
    "SQL Server": ["MS SQL Server", "Microsoft SQL Server", "MSSQL"],
    "PostgreSQL": ["Postgres"], "MongoDB": ["Mongo DB"],
    "CI/CD": ["CI CD", "continuous integration and continuous delivery"],
    "REST API": ["RESTful APIs", "RESTful API", "REST APIs"],
    "Scikit-learn": ["sklearn", "scikit learn"],
    "GA4": ["Google Analytics 4"],
    "Google Ads": ["Google AdWords", "AdWords"],
    "Meta Ads": ["Meta advertising"], "SEO": ["search engine optimization", "search engine optimisation"],
    "SEM": ["search engine marketing"], "CRM": ["customer relationship management"],
    "CRO": ["conversion rate optimisation"],
    "GST": ["goods and services tax"], "TDS": ["tax deducted at source"],
    "KYC": ["know your customer"], "AML": ["anti-money laundering"],
    "Figma": ["Figma design"], "Wireframing": ["wireframes", "wireframe"], "Adobe Photoshop": ["Photoshop"],
    "Adobe Illustrator": ["Illustrator"], "Adobe InDesign": ["InDesign"],
    "Adobe After Effects": ["After Effects"], "Adobe Premiere Pro": ["Premiere Pro"],
    "UI Design": ["user interface design"], "UX Design": ["user experience design"],
    "UI/UX": ["UX/UI", "UI UX", "UX UI"],
    "Go": ["Golang", "Go language", "Go programming", "Go developer"],
    "R": ["R language", "R programming", "RStudio", "R Studio"],
    "C": ["C language", "C programming", "C developer"],
}

AMBIGUOUS = {"R", "Go", "C"}
GENERIC = {"Data Analysis", "Business Intelligence", "Digital Marketing", "Graphic Design",
           "Compliance", "Machine Learning", "Communication", "Problem Solving",
           "Teamwork", "Analytical Skills"}
_patterns = defaultdict(list)
for names in SKILLS.values():
    for canonical in names:
        terms = ([] if canonical in AMBIGUOUS else [canonical]) + ALIASES.get(canonical, [])
        for term in terms:
            # Unicode-aware boundaries prevent matching inside names such as PowerBIA or MySQL2.
            _patterns[canonical].append(re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)", re.I))


def extract_skills(text: str) -> set[str]:
    """Return one canonical name per skill appearing in text."""
    found = set()
    for segment in re.split(r"(?<=[.!?])\s+|\n+|[•●▪]", text or ""):
        segment = segment.strip()
        if not segment:
            continue
        # A bare role heading is evidence about the vacancy, not a skill requirement.
        if len(segment) < 85 and re.search(r"\b(intern|internship|developer|analyst|designer)\s*$", segment, re.I) and not re.search(r"[:.;]", segment):
            continue
        for name, patterns in _patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(segment):
                    left = segment[max(0, match.start() - 75):match.start()].lower()
                    right = segment[match.end():match.end() + 25].lower()
                    if re.search(r"(?:don['’]t|do not|not)\s+need(?:\s+to\s+be\s+a)?\s*$", left):
                        continue
                    if name == "Graphic Design" and re.search(r"\b(?:e\.g\.|ex:)\s*[^.]{0,60}$", left):
                        continue
                    if name == "Compliance" and re.search(r"\bvendor\s*$", left):
                        continue
                    found.add(name)
                    break
    return found


def skill_count() -> int:
    return sum(map(len, SKILLS.values()))
