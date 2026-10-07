import unittest
import tempfile
from io import BytesIO
from pathlib import Path
from unittest.mock import patch
from pypdf import PdfWriter
from resume_pdf import extract_pdf_text

from engine import (DEFAULT_THRESHOLD, SerpClient, age_days, analyze_jobs, canonical_manual_skills,
                    coverage, deduplicate, is_old, parse_duration, rank_skills, run,
                    has_role_fit_warning, select_core_skills, select_course_videos, two_skill_plan,
                    experience_required, experience_evidence, requirements_from_text, assess_robustness, hours_range,
                    listing_confidence, dictionary_coverage_warning, fresher_queries, fetch_jobs,
                    no_unlock_message, MOSTLY_READY_MESSAGE, optional_serpapi_key)
from skills import GENERIC
from skills import extract_skills


def job(title, company, description, posted="2 days ago"):
    return {"title": title, "company_name": company, "description": description,
            "detected_extensions": {"posted_at": posted}, "via": "source A"}


class EngineTests(unittest.TestCase):
    def test_matcher_aliases_and_short_names(self):
        self.assertEqual(extract_skills("MS Excel, PowerBI and SQL"), {"Excel", "Power BI", "SQL"})
        self.assertFalse({"Go", "R", "C"} & extract_skills("Go to a car in R city for a C grade"))
        self.assertEqual(canonical_manual_skills("R, Go, C"), {"R", "Go", "C"})
        self.assertNotIn("Digital Marketing", extract_skills("You don’t need to be a digital marketing expert."))

    def test_coverage_and_unlock_known_answer(self):
        jobs = [job("A", "One", "SQL, Excel, Python, Power BI"),
                job("B", "Two", "SQL, Excel, Tableau, Power BI"),
                job("C", "Three", "SQL, Excel, Python, Tableau")]
        result = analyze_jobs(jobs, {"SQL", "Excel"}, threshold=0.75)
        self.assertEqual(coverage({"SQL", "Excel", "Python", "Power BI"}, {"SQL", "Excel"}), 0.5)
        self.assertEqual(result["ready"], 0)
        self.assertEqual(len(result["unlocked"]["Python"]), 2)
        self.assertEqual(len(result["unlocked"]["Power BI"]), 3)
        self.assertNotIn("Tableau", result["unlocked"])

    def test_core_skills_and_rank_by_unlock(self):
        jobs = [job("A", "One", "SQL, Excel, Python"), job("B", "Two", "SQL, Excel, Python"), job("Sparse", "Three", "SQL only")]
        result = analyze_jobs(jobs, {"SQL", "Excel"}, 0.7)
        self.assertEqual(result["ignored"], 0)
        self.assertEqual(result["candidates"], ["Python"])
        self.assertEqual(len(result["unlocked"]["Python"]), 2)
        five = [job(str(i), str(i), "SQL and Excel") for i in range(4)] + [job("last", "last", "SQL and Figma")]
        self.assertEqual(select_core_skills(five), {"SQL", "Excel"})
        self.assertIn("Figma", select_core_skills(five, .2))

    def test_duration(self):
        self.assertAlmostEqual(parse_duration("1:30:00"), 1.5)
        self.assertAlmostEqual(parse_duration("30:00"), 0.5)
        for value in ("LIVE", "1:65", "1:00:80", "", None):
            self.assertIsNone(parse_duration(value))

    def test_course_filter_and_low_confidence_fallback(self):
        videos = [
            {"title": "SQL Full Course for Beginners", "length": "2:00:00", "channel": {"name": "A"}},
            {"title": "SQL Complete Course", "length": "3:00:00", "channel": {"name": "B"}},
            {"title": "SQL in 10 minutes", "length": "10:00", "channel": {"name": "C"}},
        ]
        hours, selected, confidence = select_course_videos(videos, "SQL full course for beginners")
        self.assertEqual((hours, len(selected), confidence), (2.5, 2, "standard"))
        fallback = [videos[0], {"title": "SQL tutorial", "length": "45:00"}, videos[2]]
        hours, selected, confidence = select_course_videos(fallback, "SQL full course for beginners")
        self.assertEqual((hours, len(selected), confidence), (1.375, 2, "low"))

    def test_two_skill_plan_and_limited_data(self):
        jobs = [job("A", "One", "SQL, Excel, Python"), job("B", "Two", "SQL, Excel, Python"),
                job("C", "Three", "SQL, Tableau, Java")]
        result = analyze_jobs(jobs, {"SQL"}, threshold=1.0)
        plan = two_skill_plan(result, {"Excel": 2.0, "Python": 3.0})
        self.assertTrue(result["limited_data"])
        self.assertEqual(set(plan["skills"]), {"Excel", "Python"})
        self.assertEqual((plan["unlocked_count"], plan["hours"], plan["score"]), (2, 5.0, .4))
        twelve = [job(f"Role {i}", f"Company {i}", "SQL, Excel, Python") for i in range(12)]
        self.assertFalse(analyze_jobs(twelve, {"SQL"})["limited_data"])

    def test_ranking_score_and_unlock_tiebreak(self):
        jobs = [job("A", "One", "SQL, Excel, Python")]
        analysis = {"candidates": ["Python", "Power BI", "Tableau"],
                    "unlocked": {"Python": jobs * 2, "Power BI": jobs, "Tableau": jobs * 2},
                    "skill_counts": {"Python": 2, "Power BI": 1, "Tableau": 2}}
        estimates = {"Python": (2.0, [], "standard"), "Power BI": (1.0, [], "standard"), "Tableau": (2.0, [], "standard")}
        with patch("engine.course_videos", side_effect=lambda skill, *_: estimates[skill]):
            ranked = rank_skills(analysis, SerpClient(offline=True))
        self.assertEqual([row["skill"] for row in ranked], ["Python", "Tableau", "Power BI"])
        self.assertEqual([row["score"] for row in ranked], [1.0, 1.0, 1.0])

    def test_freshness_and_dedup(self):
        self.assertTrue(is_old(job("A", "One", "SQL, Excel, Python", "2 months ago")))
        self.assertFalse(is_old(job("B", "Two", "SQL, Excel, Python", "30 days ago")))
        self.assertIsNone(age_days("unknown"))
        a = job("Senior Data Analyst", "Acme", "SQL, Excel, Python")
        b = {**a, "title": "Senior Data Analyst", "via": "source B"}
        self.assertEqual(len(deduplicate([a, b])), 1)
        self.assertEqual(len(analyze_jobs([a, job("Old", "Other", "SQL, Excel, Python", "6 weeks ago")], set(), exclude_old=True)["jobs"]), 1)

    def test_fixture_replay_has_no_network(self):
        result = run("Data Analyst", "Noida", "Excel SQL Python", pages=2, offline=True, client=SerpClient(offline=True))
        self.assertGreaterEqual(len(result["jobs"]), 10)
        self.assertTrue(all(event["source"] in {"demo", "cache missing"} for event in result["replay"]))

    def test_data_driven_default(self):
        self.assertEqual(DEFAULT_THRESHOLD, .5)
        analyst_jobs = __import__("engine").fetch_jobs("Data Analyst", "Noida", client=SerpClient(use_fixtures=True, cache_only=True))
        frontend_jobs = __import__("engine").fetch_jobs("Frontend Developer", "Bengaluru", client=SerpClient(use_fixtures=True, cache_only=True))
        self.assertEqual(analyze_jobs(analyst_jobs, {"Excel", "Python"})["ready"], 2)
        self.assertEqual(analyze_jobs(analyst_jobs, {"SQL", "Excel", "Python", "Tableau"})["ready"], 15)
        self.assertEqual(analyze_jobs(frontend_jobs, {"HTML", "CSS", "JavaScript"})["ready"], 10)

    def test_generic_terms_count_but_never_recommend(self):
        jobs = [job("A", "One", "SQL and Data Analysis"), job("B", "Two", "SQL and Data Analysis"),
                job("C", "Three", "SQL and Excel")]
        analysis = analyze_jobs(jobs, {"SQL"}, threshold=1)
        self.assertIn("Data Analysis", GENERIC)
        self.assertIn("Data Analysis", analysis["core_skills"])
        self.assertEqual(len(analysis["unlocked"]["Data Analysis"]), 2)
        self.assertNotIn("Data Analysis", analysis["candidates"])
        self.assertTrue(all(skill not in GENERIC for skill in analysis["candidates"]))
        if analysis["pair"]:
            self.assertTrue(all(skill not in GENERIC for skill in analysis["pair"][:2]))

    def test_role_fit_warning_is_most_jobs_below_twenty_percent(self):
        self.assertTrue(has_role_fit_warning({"jobs": [{"coverage": .1}, {"coverage": 0}, {"coverage": .2}]}))
        self.assertFalse(has_role_fit_warning({"jobs": [{"coverage": .1}, {"coverage": .2}, {"coverage": .3}]}))
        self.assertFalse(has_role_fit_warning({"jobs": []}))

    def test_experience_requirement_and_exclusion(self):
        cases = [("Analyst", "2+ years of SQL", 2), ("Analyst", "3-5 years in Python", 3),
                 ("Analyst", "minimum 4 yrs", 4), ("Intern", "fresher", 0),
                 ("Intern", "0-1 year", 0), ("Senior Analyst", "SQL", 3),
                 ("Lead Developer", "SQL", 5), ("Manager", "SQL", 5),
                 ("Principal Engineer", "SQL", 8)]
        for title, description, minimum in cases:
            with self.subTest(title=title, description=description):
                self.assertEqual(experience_required(job(title, "A", description))[0], minimum)
        jobs = [job("Analyst", "A", "SQL, Excel, Python. Fresher"),
                job("Senior Analyst", "B", "SQL, Excel, Python. 3-5 years")]
        fresher = analyze_jobs(jobs, {"SQL", "Excel", "Python"}, experience_level="Fresher")
        self.assertEqual((fresher["ready"], len(fresher["experience_excluded"])), (1, 1))
        self.assertEqual(len(fresher["jobs"]), 1)
        self.assertFalse(any(excluded["job"] in unlocked for excluded in fresher["experience_excluded"]
                             for unlocked in fresher["unlocked"].values()))
        mid = analyze_jobs(jobs, {"SQL", "Excel", "Python"}, experience_level="1-3 years")
        self.assertEqual((mid["ready"], len(mid["experience_excluded"])), (2, 0))

    def test_experience_parser_rejects_incidental_years(self):
        false_cases = ["A company with 20 years of experience", "Report to a Senior Manager",
                       "Includes a 5 years warranty", "Our firm has 7 years of experience",
                       "Experience: 25 Years"]
        for text in false_cases:
            with self.subTest(text=text):
                self.assertEqual(experience_evidence(job("Developer", "A", text))[0], 0)
        self.assertEqual(experience_evidence(job("Developer", "A", "What you bring: 3 5 years of professional development experience"))[0], 3)
        self.assertEqual(experience_evidence(job("Developer", "A", "Overall 4.5+ years of frontend experience"))[0], 5)

    def test_skill_alternatives_and_explicit_or(self):
        self.assertIn(frozenset({"Power BI", "Tableau", "Looker"}), requirements_from_text("Power BI/Tableau"))
        self.assertIn(frozenset({"React", "Angular", "Vue.js"}), requirements_from_text("React or Angular"))
        self.assertIn(frozenset({"SQL", "Python"}), requirements_from_text("SQL or Python"))
        self.assertEqual(coverage(requirements_from_text("SQL/Python"), {"Python"}), 1)
        self.assertEqual(coverage(requirements_from_text("Power BI/Tableau, SQL"), {"Tableau", "SQL"}), 1)
        jobs = [job("Analyst", "A", "SQL, Excel, Power BI or Tableau"),
                job("Analyst", "B", "SQL, Excel, Power BI")]
        analysis = analyze_jobs(jobs, {"SQL", "Excel", "Tableau"}, threshold=1)
        self.assertEqual(analysis["ready"], 2)
        analysis = analyze_jobs(jobs, {"SQL", "Excel"}, threshold=1)
        self.assertIn("Power BI", analysis["candidates"])
        self.assertNotIn("Tableau", analysis["candidates"])
        if analysis["pair"]:
            a, b, _ = analysis["pair"]
            self.assertFalse(analysis["option_members"][a] & analysis["option_members"][b])

    def test_robustness_and_hours_range(self):
        self.assertEqual(hours_range(3.68), "~2–5 hours")
        jobs = [job("A", "One", "SQL, Excel and Figma"), job("B", "Two", "SQL, Python and Figma")]
        stable = assess_robustness(jobs, {"SQL"}, "Excel", {"Excel": 1.0}, core_share=.25)
        self.assertEqual(stable["label"], "Stable pick")
        sensitive = assess_robustness(jobs, {"SQL"}, "Excel", {"Excel": 4.0, "Python": 1.0}, core_share=.25)
        self.assertEqual(sensitive["label"], "Sensitive pick")
        self.assertTrue(any("Python" in change for change in sensitive["changes"]))

    def test_listing_confidence_boundaries(self):
        self.assertEqual([listing_confidence(n) for n in (0, 11, 12, 24, 25)],
                         ["Low", "Low", "Medium", "Medium", "High"])

    def test_dictionary_coverage_warning(self):
        sparse = [job("A", "One", "SQL"), job("B", "Two", "Excel"), job("C", "Three", "No named skills")]
        warning, median = dictionary_coverage_warning(sparse)
        self.assertTrue(warning)
        self.assertEqual(median, 1)
        rich = [job("A", "One", "SQL, Excel, Python")]
        self.assertFalse(dictionary_coverage_warning(rich)[0])

    def test_pdf_resume_extraction_and_scanned_fallback(self):
        writer = PdfWriter()
        writer.add_blank_page(width=300, height=300)
        output = BytesIO()
        writer.write(output)
        self.assertEqual(extract_pdf_text(output.getvalue()), "")
        with patch("resume_pdf.PdfReader") as reader:
            reader.return_value.pages = [type("Page", (), {"extract_text": lambda self: "SQL, Excel"})()]
            self.assertEqual(extract_skills(extract_pdf_text(b"pdf")), {"SQL", "Excel"})
        with patch("resume_pdf.PdfReader", side_effect=ValueError("bad PDF")):
            with self.assertRaisesRegex(ValueError, "paste your resume text"):
                extract_pdf_text(b"not a PDF")

    def test_readme_validation_link_stays_inside_project(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "reports" / "validation_check.md").is_file())
        self.assertIn("reports/validation_check.md", (root / "README.md").read_text())

    def test_fresher_variants_merge_deduplicate_and_keep_origins(self):
        self.assertEqual([q for q, _ in fresher_queries("Data Analyst", "Fresher")],
                         ["Data Analyst", "Data Analyst fresher", "Junior Data Analyst"])
        self.assertEqual(len(fresher_queries("Data Analyst", "1-3 years")), 1)
        self.assertEqual(fresher_queries("Marketing Intern", "Fresher")[-1],
                         ("Marketing Intern intern", "Intern variant"))
        client = SerpClient(cache_only=True)
        first = job("Data Analyst", "Acme", "SQL, Excel, Python")
        second = job("Junior Data Analyst", "Other", "SQL, Excel, Python")
        def fake_search(params, page=1):
            client.replay.append({"query": dict(params), "source": "cache"})
            results = {"Data Analyst": [first], "Data Analyst fresher": [first],
                       "Junior Data Analyst": [second]}.get(params["q"], [])
            return {"jobs_results": results}
        with patch.object(client, "search", side_effect=fake_search):
            found = fetch_jobs("Data Analyst", "Noida", client=client, experience_level="Fresher")
        self.assertEqual(len(found), 2)
        self.assertEqual(found.raw_count, 3)
        self.assertEqual(found[0]["_search_queries"], ["Data Analyst", "Data Analyst fresher"])
        self.assertEqual(found[1]["_search_queries"], ["Junior Data Analyst"])
        self.assertEqual([row["variant"] for row in client.replay],
                         ["Base role", "Fresher variant", "Junior variant"])

    def test_explicit_or_does_not_turn_sql_into_a_global_bi_group(self):
        jobs = [job("A", "One", "SQL or Power BI, Excel"),
                job("B", "Two", "SQL, Excel, Python"),
                job("C", "Three", "Power BI, Excel, Python")]
        analysis = analyze_jobs(jobs, {"Excel"}, threshold=1)
        self.assertEqual(analysis["display_members"].get("SQL"), frozenset({"SQL"}))
        if analysis["pair"]:
            self.assertFalse(any(analysis["pair"][0] in group and analysis["pair"][1] in group
                                 for group in __import__("engine").SUBSTITUTE_GROUPS))

    def test_mostly_ready_no_unlock_message(self):
        analysis = {"jobs": [{}, {}, {}], "ready": 2, "candidates": []}
        self.assertEqual(no_unlock_message(analysis), MOSTLY_READY_MESSAGE)
        analysis["ready"] = 0
        self.assertNotEqual(no_unlock_message(analysis), MOSTLY_READY_MESSAGE)

    def test_bundled_demo_runs_without_key_or_cache(self):
        with tempfile.TemporaryDirectory() as directory, patch("engine.optional_serpapi_key", return_value=None), \
             patch("engine._request", side_effect=AssertionError("network requested")):
            client = SerpClient(use_fixtures=True, cache_only=True, cache_dir=Path(directory))
            result = run("Data Analyst", "Noida", "Excel, basic Python", client=client,
                         experience_level="Fresher")
            self.assertEqual(result["eligible_count"], 20)
            self.assertEqual(result["ranked"][0]["skill"], "SQL")
            self.assertIsNotNone(result["ranked"][0]["hours"])
            self.assertTrue(all(event["source"] in {"demo", "cache missing"} for event in result["replay"]))

    def test_missing_key_detection(self):
        with tempfile.TemporaryDirectory() as directory, patch("engine.ROOT", Path(directory)), \
             patch.dict("os.environ", {"SERPAPI_KEY": ""}):
            self.assertIsNone(optional_serpapi_key())


if __name__ == "__main__":
    unittest.main()
