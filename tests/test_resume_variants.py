import unittest

from skills import extract_skills

# Realistic resume lines and the skills a careful reader would record.
CASES = [
    ("Skills: HTML5, CSS3, JavaScript (ES6), React.js", {"HTML", "CSS", "JavaScript", "React"}),
    ("Python Developer", {"Python"}),
    ("Data Analyst (SQL, Excel, Power BI)", {"SQL", "Excel", "Power BI"}),
    ("Technical Skills: C, C++, Java, Python", {"C", "C++", "Java", "Python"}),
    ("Languages: Java | Python | JavaScript", {"Java", "Python", "JavaScript"}),
    ("Tools: MS Excel, PowerBI, Tableau, Jira", {"Excel", "Power BI", "Tableau", "Jira"}),
    ("MERN Stack Developer", {"MongoDB", "Express.js", "React", "Node.js"}),
    ("Built a MERN stack e-commerce site", {"MongoDB", "Express.js", "React", "Node.js"}),
    ("Frontend: React, Redux, Tailwind CSS", {"React", "CSS"}),
    ("Backend: Node, Express, MongoDB", {"Node.js", "Express.js", "MongoDB"}),
    ("Databases: MySQL, PostgreSQL, Mongo", {"MySQL", "PostgreSQL", "MongoDB"}),
    ("Cloud: AWS (EC2, S3), basic Azure", {"AWS", "Azure"}),
    ("Version control: Git & GitHub", {"Git"}),
    ("Certified in Google Analytics 4 and Google Ads", {"GA4", "Google Analytics", "Google Ads"}),
    ("No experience with Java", set()),
    ("Excel (advanced), SQL (intermediate), no Tableau", {"Excel", "SQL"}),
    ("Currently learning Power BI and DAX", set()),
    ("Learning: Docker", set()),
    ("Tableau: no; Excel: yes", {"Excel"}),
    ("Familiar with React; not Angular", {"React"}),
    ("Machine Learning with Python and scikit-learn", {"Machine Learning", "Python", "Scikit-learn"}),
    ("Deep Learning (TensorFlow, PyTorch)", {"Deep Learning", "TensorFlow", "PyTorch"}),
    ("Data Science Intern using Pandas and NumPy", {"Pandas", "NumPy"}),
    ("B.Tech in Computer Science, 2026", set()),
    ("Proficient in C# and .NET", {"C#"}),
    ("Go (Golang) microservices", {"Go", "Microservices"}),
    ("R programming for statistics", {"R", "Statistics"}),
    ("Tally ERP 9, GST filing, TDS returns", {"Tally", "ERP", "GST", "TDS"}),
    ("SEO, SEM and social media marketing", {"SEO", "SEM", "Social Media Marketing"}),
    ("Figma, Adobe XD and Photoshop", {"Figma", "Adobe XD", "Adobe Photoshop"}),
    ("UI/UX Designer", {"UI/UX"}),
    ("REST APIs with FastAPI", {"REST API", "FastAPI"}),
    ("Typescript, Next.js", {"TypeScript", "Next.js"}),
    ("Knowledge of Data Structures and Algorithms (DSA)", {"Data Structures", "Algorithms"}),
    ("CI/CD with Jenkins and Docker", {"CI/CD", "Jenkins", "Docker"}),
    ("Worked with Spring Boot and Java 17", {"Spring Boot", "Java"}),
    ("Python 3.x, Django", {"Python", "Django"}),
    ("JS, TS", {"JavaScript", "TypeScript"}),
    ("Node.js (Express), MongoDB", {"Node.js", "Express.js", "MongoDB"}),
    ("Not familiar with Kubernetes, but used Docker", {"Docker"}),
    ("Hands-on with Selenium and Postman for API testing", {"Selenium", "Postman", "API Testing"}),
    ("Excel, but never used Power Query", {"Excel"}),
    ("HTML/CSS", {"HTML", "CSS"}),
    ("Accounting, Bookkeeping, QuickBooks", {"Accounting", "Bookkeeping", "QuickBooks"}),
    ("SQL - basic, Python - intermediate", {"SQL", "Python"}),
    ("Grade: C", set()),
    ("Section C, Python", {"Python"}),
]


class ResumeVariantTests(unittest.TestCase):
    def test_realistic_resume_lines(self):
        self.assertGreaterEqual(len(CASES), 30)
        for line, expected in CASES:
            with self.subTest(line=line):
                self.assertEqual(extract_skills(line, resume=True), expected)


if __name__ == "__main__":
    unittest.main()
