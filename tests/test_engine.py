import unittest
import tempfile
from io import BytesIO
from pathlib import Path
from datetime import date
from unittest.mock import patch
from pypdf import PdfWriter
from resume_pdf import extract_pdf_text

from engine import (DEFAULT_THRESHOLD, SerpClient, age_days, analyze_jobs, canonical_manual_skills,
                    coverage, course_videos, deduplicate, is_old, parse_duration, rank_skills, run,
                    has_role_fit_warning, select_core_skills, select_course_videos, two_skill_plan,
                    experience_required, experience_evidence, requirements_from_text, assess_robustness, hours_range,
                    listing_confidence, dictionary_coverage_warning, fresher_queries, fetch_jobs,
                    no_unlock_message, MOSTLY_READY_MESSAGE, optional_serpapi_key,
                    greedy_opportunity, exact_opportunity, opportunity_quality,
                    bootstrap_confidence, confidence_label, skill_distance,
                    listing_age_days, retrieval_date, stamp_response)
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

    def test_rest_api_requires_api_or_service_context(self):
        for sentence in ("Integrate REST API endpoints.", "Use REST APIs for backend calls.",
                         "Build RESTful APIs.", "Connect to REST services.", "Maintain RESTful services."):
            self.assertIn("REST API", extract_skills(sentence), sentence)
        for sentence in ("Work with the rest of the team.", "Rest assured, training is provided.",
                         "Take a rest after the sprint.", "A restful work environment.",
                         "Please rest before the interview."):
            self.assertNotIn("REST API", extract_skills(sentence), sentence)

    def test_coverage_and_unlock_known_answer(self):
        jobs = [job("A", "One", "SQL, Excel, Python, Power BI"),
                job("B", "Two", "SQL, Excel, Tableau, Power BI"),
                job("C", "Three", "SQL, Excel, Python, Tableau")]
        result = analyze_jobs(jobs, {"SQL", "Excel"}, threshold=0.75)
        self.assertEqual(coverage({"SQL", "Excel", "Python", "Power BI"}, {"SQL", "Excel"}), 0.5)
        self.assertEqual(result["ready"], 0)
        self.assertEqual(len(result["unlocked"]["Python"]), 2)
        self.assertEqual(len(result["unlocked"]["Power BI"]), 2)
        self.assertEqual(len(result["unlocked"]["Tableau"]), 2)

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

    def test_course_language_filters_titles_and_channels_before_estimating(self):
        videos = [{"title": "SQL full course Tamil", "length": "1:00:00"},
                  {"title": "SQL complete course", "channel": {"name": "Telugu Learning"}, "length": "2:00:00"},
                  {"title": "SQL full course Hindi", "length": "3:00:00"},
                  {"title": "SQL full course", "channel": {"name": "English Lessons"}, "length": "4:00:00"},
                  {"title": "SQL complete course English", "length": "6:00:00"}]
        hours, chosen, confidence = select_course_videos(videos, "SQL full course for beginners")
        self.assertEqual((hours, len(chosen), confidence), (5, 2, "standard"))
        self.assertEqual(select_course_videos(videos, "SQL tutorial in Hindi")[0], 4)
        for language in ("Tamil", "Telugu", "Kannada", "Malayalam", "Bengali", "Marathi", "Hindi",
                         "Gujarati", "Punjabi", "Urdu", "Spanish", "French", "हिंदी", "தமிழ்"):
            result = select_course_videos([{"title": f"SQL course {language}", "length": "1:00:00"}], "SQL course")
            self.assertIsNone(result[0], language)

    def test_language_filter_low_confidence_cannot_restore_excluded_courses(self):
        videos = [{"title": "API full course Tamil", "length": "2:00:00"},
                  {"title": "API full course Hindi", "length": "3:00:00"},
                  {"title": "API full course English", "length": "1:00:00"}]
        hours, chosen, confidence = select_course_videos(videos, "API full course")
        self.assertEqual((hours, len(chosen), confidence), (1, 1, "low"))
        self.assertEqual(select_course_videos(videos[:2], "API full course"), (None, [], "low"))

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

    def test_cached_posted_age_includes_elapsed_days(self):
        listing = {**job("A", "One", "SQL", "3 days ago"), "_retrieved_at": "2026-09-01 10:00:00 UTC"}
        self.assertEqual(listing_age_days(listing, date(2026, 9, 10)), 12)
        self.assertFalse(is_old(listing, date(2026, 9, 28)))
        self.assertTrue(is_old(listing, date(2026, 9, 29)))
        self.assertIsNone(listing_age_days({**listing, "detected_extensions": {"posted_at": "unknown"}}, date(2026, 10, 8)))
        self.assertIsNone(retrieval_date({"_retrieved_at": "invalid"}))
        self.assertEqual(stamp_response({}), {})
        old = {**listing, "_retrieved_at": "2020-01-01T00:00:00+00:00"}
        self.assertEqual(analyze_jobs([old], {"SQL"}, exclude_old=True)["eligible_count"], 0)

    def test_retrieval_time_is_persisted_and_preserved_on_cache_replay(self):
        response = {"search_metadata": {"created_at": "2026-09-01 10:00:00 UTC"},
                    "jobs_results": [job("A", "One", "SQL")]}
        with tempfile.TemporaryDirectory() as directory, patch("engine._request", return_value=response) as request:
            client = SerpClient(cache_dir=Path(directory))
            client.key = "unit-test-placeholder"
            first = fetch_jobs("Analyst", "Noida", pages=1, client=client)
            self.assertEqual(retrieval_date(first[0]), date(2026, 9, 1))
            self.assertEqual(request.call_count, 1)
            saved = __import__("json").loads(next(Path(directory).glob("search_*.json")).read_text())
            self.assertEqual(saved["_retrieved_at"], response["search_metadata"]["created_at"])
            with patch("engine._request", side_effect=AssertionError("network requested")):
                replay = fetch_jobs("Analyst", "Noida", pages=1, client=client)
            self.assertEqual(replay[0]["_retrieved_at"], first[0]["_retrieved_at"])
        self.assertIsNotNone(retrieval_date(stamp_response({}, fresh=True)))

    def test_fixture_replay_has_no_network(self):
        result = run("Data Analyst", "Noida", "Excel SQL Python", pages=2, offline=True, client=SerpClient(offline=True))
        self.assertGreaterEqual(len(result["jobs"]), 10)
        self.assertTrue(all(event["source"] in {"demo", "cache missing"} for event in result["replay"]))

    def test_data_driven_default(self):
        self.assertEqual(DEFAULT_THRESHOLD, .5)
        jobs = [job("Analyst", "A", "SQL, Excel, Python")]
        self.assertEqual(analyze_jobs(jobs, {"SQL"})["ready"], 0)
        self.assertEqual(analyze_jobs(jobs, {"SQL", "Excel"})["ready"], 1)

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
        self.assertEqual((mid["ready"], len(mid["experience_excluded"])), (1, 1))

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
        self.assertIn(frozenset({"Power BI", "Tableau"}), requirements_from_text("Power BI/Tableau"))
        self.assertIn(frozenset({"React", "Angular"}), requirements_from_text("React or Angular"))
        self.assertIn(frozenset({"SQL", "Python"}), requirements_from_text("SQL or Python"))
        self.assertEqual(coverage(requirements_from_text("SQL/Python"), {"Python"}), 1)
        self.assertEqual(coverage(requirements_from_text("Power BI/Tableau, SQL"), {"Tableau", "SQL"}), 1)
        jobs = [job("Analyst", "A", "SQL, Excel, Power BI or Tableau"),
                job("Analyst", "B", "SQL, Excel, Power BI")]
        analysis = analyze_jobs(jobs, {"SQL", "Excel", "Tableau"}, threshold=1)
        self.assertEqual(analysis["ready"], 1)
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
        self.assertEqual(stable["label"], "Consistent across checked settings")
        sensitive = assess_robustness(jobs, {"SQL"}, "Excel", {"Excel": 4.0, "Python": 1.0}, core_share=.25)
        self.assertEqual(sensitive["label"], "Changes with settings")
        self.assertTrue(any("Python" in change for change in sensitive["changes"]))

    def test_hours_variation_is_independent_seeded_and_affects_confidence(self):
        jobs = [job("A", "One", "SQL, Excel"), job("B", "Two", "SQL, Python")]
        first = assess_robustness(jobs, set(), "Excel", {"Excel": 2, "Python": 2}, samples=80, seed=7)
        second = assess_robustness(jobs, set(), "Excel", {"Python": 2, "Excel": 2}, samples=80, seed=7)
        self.assertEqual(first, second)
        self.assertEqual(first["samples"], 240)
        self.assertEqual(sum(first["wins"].values()), 240)
        self.assertGreater(first["wins"]["Excel"], 0)
        self.assertGreater(first["wins"]["Python"], 0)
        self.assertLess(first["top_share"], 1)
        self.assertEqual(confidence_label(.95, .7), "Likely")
        self.assertEqual(confidence_label(.95, .5), "Uncertain")
        self.assertEqual(confidence_label(.9, .9), "Strong")

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
        self.assertIn(frozenset({"SQL"}), analysis["jobs"][1]["required_skills"])
        self.assertIn(frozenset({"Power BI"}), analysis["jobs"][2]["required_skills"])

    def test_negation_scopes_apply_to_resumes_and_job_requirements(self):
        for phrase in ("no experience with", "not familiar with", "never used", "don't know",
                       "don’t know", "do not know"):
            text = f"I am {phrase} SQL or Python, but I use Excel."
            self.assertEqual(extract_skills(text), {"Excel"}, phrase)
            self.assertEqual(canonical_manual_skills(text), {"Excel"}, phrase)
            self.assertEqual(requirements_from_text(text), {frozenset({"Excel"})}, phrase)
        self.assertEqual(extract_skills("Never used React/Angular/Vue. JavaScript is required."), {"JavaScript"})
        self.assertEqual(extract_skills("No experience with SQL; proficient in Python."), {"Python"})
        self.assertEqual(extract_skills("Not only SQL but also Python."), {"SQL", "Python"})
        self.assertEqual(extract_skills("SQL is not required. Excel is required."), {"Excel"})
        self.assertEqual(canonical_manual_skills("No experience with SQL, Python, Excel"), set())
        self.assertEqual(canonical_manual_skills("R, basic Python"), {"R", "Python"})
        self.assertEqual(canonical_manual_skills("No experience with R, Go, C"), set())

    def test_only_listing_alternatives_are_interchangeable(self):
        self.assertEqual(coverage(requirements_from_text("React is mandatory."), {"Angular"}), 0)
        self.assertEqual(coverage(requirements_from_text("AWS is required."), {"Azure"}), 0)
        self.assertEqual(requirements_from_text("React/Angular/Vue"), {frozenset({"React", "Angular", "Vue.js"})})
        self.assertEqual(requirements_from_text("Any cloud such as AWS or Azure"), {frozenset({"AWS", "Azure"})})
        self.assertEqual(requirements_from_text("SQL or Python. SQL is required."),
                         {frozenset({"SQL", "Python"}), frozenset({"SQL"})})
        for text in ("Frameworks (React, Angular, or Vue)", "Experience with React, Vue or Angular"):
            self.assertEqual(requirements_from_text(text), {frozenset({"React", "Angular", "Vue.js"})}, text)
        self.assertEqual(requirements_from_text("SQL, Excel or Power BI, Python"),
                         {frozenset({"SQL"}), frozenset({"Excel", "Power BI"}), frozenset({"Python"})})
        self.assertEqual(requirements_from_text("React, Angular and Vue"),
                         {frozenset({"React"}), frozenset({"Angular"}), frozenset({"Vue.js"})})
        independent = analyze_jobs([job("A", "One", "React"), job("B", "Two", "Angular")], set(), threshold=1)
        self.assertEqual(set(independent["pair"][:2]), {"React", "Angular"})
        self.assertEqual(independent["display_members"]["React"], frozenset({"React"}))

    def test_description_experience_overrides_title_and_bands_use_minimum(self):
        for description, minimum in [("1-3 years", 1), ("3+ years", 3), ("Freshers welcome", 0),
                                     ("0-1 years", 0), ("entry level", 0)]:
            self.assertEqual(experience_evidence(job("Senior Manager", "A", description))[0], minimum)
        for description in ("Not an entry level role", "No freshers welcome"):
            self.assertEqual(experience_evidence(job("Senior Analyst", "A", description))[0], 3)
        jobs = [job("A", "One", "Experience: 1-3 years. SQL"),
                job("B", "Two", "Experience: 3+ years. SQL"),
                job("C", "Three", "Experience: 7+ years. SQL")]
        self.assertEqual(analyze_jobs(jobs, {"SQL"}, experience_level="1-3 years")["ready"], 1)
        self.assertEqual(analyze_jobs(jobs, {"SQL"}, experience_level="3+ years")["ready"], 2)

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
            self.assertEqual(result["ranked"][0]["skill"], "Data Cleaning")
            self.assertIsNotNone(result["ranked"][0]["hours"])
            self.assertEqual(result["robustness"]["label"], confidence_label(
                result["bootstrap"]["top_share"], result["robustness"]["top_share"]))
            self.assertTrue(all(event["source"] in {"demo", "cache missing"} for event in result["replay"]))

    def test_batch_d_courses_are_bundled_for_demo_mode(self):
        with tempfile.TemporaryDirectory() as directory, patch("engine._request", side_effect=AssertionError("network requested")):
            client = SerpClient(use_fixtures=True, cache_only=True, cache_dir=Path(directory))
            for skill in ("Data Cleaning", "Data Visualization", "REST API", "Responsive Design"):
                hours, videos, confidence = course_videos(skill, client)
                self.assertIsNotNone(hours, skill)
                self.assertGreaterEqual(len(videos), 2, skill)
                self.assertEqual(confidence, "standard", skill)
            self.assertTrue(all(event["source"] == "demo" for event in client.replay))

    def test_missing_key_detection(self):
        with tempfile.TemporaryDirectory() as directory, patch("engine.ROOT", Path(directory)), \
             patch.dict("os.environ", {"SERPAPI_KEY": ""}):
            self.assertIsNone(optional_serpapi_key())

    def test_greedy_vs_exact_known_budget(self):
        jobs = ([job(f"SQL {i}", f"SqlCo{i}", "SQL") for i in range(3)] +
                [job(f"Python {i}", f"PyCo{i}", "Python") for i in range(4)] +
                [job(f"Excel {i}", f"ExcelCo{i}", "Excel") for i in range(4)])
        analysis = analyze_jobs(jobs, set(), threshold=1)
        hours = {"SQL": 1.0, "Python": 2.0, "Excel": 2.0}
        greedy = greedy_opportunity(analysis, hours, budget=2)
        optimum = exact_opportunity(analysis, hours, budget=2)
        self.assertEqual(([step["skill"] for step in greedy], greedy[-1]["total_jobs"]), (["SQL"], 3))
        self.assertEqual(optimum["jobs_gained"], 4)
        self.assertEqual(opportunity_quality(analysis, hours, budgets=(2,))[0]["ratio"], .75)

    def test_opportunity_respects_alternatives_and_experience(self):
        jobs = [job("Analyst", "One", "Power BI/Tableau, SQL"),
                job("Senior Analyst", "Two", "Power BI/Tableau, SQL")]
        analysis = analyze_jobs(jobs, {"SQL"}, threshold=1, experience_level="Fresher")
        steps = greedy_opportunity(analysis, {"Power BI": 2, "Tableau": 1})
        self.assertEqual(analysis["eligible_count"], 1)
        self.assertEqual([(step["skill"], step["jobs_gained"]) for step in steps], [("Power BI", 1)])
        self.assertEqual(exact_opportunity(analysis, {"Power BI": 2}, budget=2)["jobs_gained"], 1)

    def test_bootstrap_is_seeded_and_cached(self):
        jobs = ([job(f"SQL {i}", f"SqlCo{i}", "SQL") for i in range(3)] +
                [job(f"Python {i}", f"PyCo{i}", "Python") for i in range(4)])
        analysis = analyze_jobs(jobs, set(), threshold=1)
        hours = {"SQL": 1.0, "Python": 2.0}
        first = bootstrap_confidence(analysis, hours, "SQL", samples=50, seed=123)
        second = bootstrap_confidence(analysis, hours, "SQL", samples=50, seed=123)
        self.assertEqual(first, second)
        self.assertEqual(sum(first["wins"].values()), 50)
        self.assertIn(first["label"], {"Strong", "Likely", "Uncertain"})

    def test_bootstrap_confidence_label_boundaries(self):
        self.assertEqual(confidence_label(.85), "Strong")
        self.assertEqual(confidence_label(.849), "Likely")
        self.assertEqual(confidence_label(.60), "Likely")
        self.assertEqual(confidence_label(.599), "Uncertain")

    def test_ui_ux_counts_for_matching_but_is_not_recommended(self):
        self.assertIn("UI/UX", GENERIC)
        jobs = [job("Designer", "A", "UI/UX, Figma"), job("Designer", "B", "UI/UX, Figma")]
        analysis = analyze_jobs(jobs, set(), threshold=1)
        self.assertIn("UI/UX", analysis["core_skills"])
        self.assertNotIn("UI/UX", analysis["candidates"])
        self.assertNotIn("UI/UX", [skill for skill in analysis["option_members"] if skill in analysis["candidates"]])

    def test_skill_distance_known_counts_and_experience_filter(self):
        jobs = [job("A", "One", "SQL"), job("B", "Two", "SQL, Python"),
                job("C", "Three", "SQL, Python, Excel"),
                job("D", "Four", "SQL, Python, Excel, Figma"),
                job("Senior E", "Five", "SQL, Python, Excel, Figma")]
        analysis = analyze_jobs(jobs, {"SQL"}, threshold=1, experience_level="Fresher")
        distances = skill_distance(analysis)
        self.assertEqual(distances["counts"], {"0": 1, "1": 1, "2": 1, "3+": 1, "Unknown": 0})
        self.assertEqual([job["title"] for job in distances["one_away"]["Python"]], ["B"])
        self.assertEqual(len(analysis["experience_excluded"]), 1)


if __name__ == "__main__":
    unittest.main()
