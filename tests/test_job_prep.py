import json
import unittest
from pathlib import Path
from unittest.mock import patch

import job_prep
from engine import SerpClient, analyze_jobs, course_videos, run
from job_prep import (build_plan, default_prep_index, prep_candidates, revision_videos,
                      select_revision_videos, time_range)

ROOT = Path(__file__).resolve().parents[1]


def job(title, company, description):
    return {"title": title, "company_name": company, "description": description,
            "detected_extensions": {"posted_at": "2 days ago"}, "via": "source A"}


def video(title, length, channel="Channel"):
    return {"title": title, "length": length, "channel": {"name": channel}, "link": "https://example.test/v"}


def no_course(skill):
    return None, [], "low"


def no_revision(skill):
    return [], "not_saved"


class FakeClient:
    def __init__(self, data):
        self.data = data

    def search(self, params, page=1):
        return self.data


def demo_result(role, city, resume):
    with patch("engine._request", side_effect=AssertionError("network requested")):
        return run(role, city, resume, "", .5, False, False, 3, False,
                   SerpClient(use_fixtures=True, cache_only=True, ledger_name="demo_ledger.json", call_cap=6),
                   .25, experience_level="Fresher")


class RevisionVideoTests(unittest.TestCase):
    def test_duration_title_and_topic_filters(self):
        results = [video("SQL revision", "4:59"), video("SQL crash course", "25:01"),
                   video("SQL tutorial for beginners", "10:00"), video("Python crash course", "10:00"),
                   video("SQL exam revision strategy", "10:00"), video("SQL one shot revision", "5:00"),
                   video("SQL interview questions", "25:00"), video("SQL in 10 minutes", "12:00")]
        chosen = select_revision_videos(results, "SQL")
        self.assertEqual([item["title"] for item in chosen], ["SQL one shot revision", "SQL interview questions"])
        self.assertEqual([round(item["minutes"]) for item in chosen], [5, 25])
        self.assertEqual(select_revision_videos(results[2:5], "SQL"), [])

    def test_language_filter_uses_title_and_channel(self):
        results = [video("SQL revision in Tamil", "10:00"), video("SQL quick revision", "10:00", "Telugu Tech"),
                   video("SQL crash course", "10:00")]
        self.assertEqual([item["title"] for item in select_revision_videos(results, "SQL")], ["SQL crash course"])
        self.assertEqual(len(select_revision_videos(results, "SQL", {"english", "tamil"})), 2)

    def test_no_result_fallbacks_never_fill_gaps(self):
        self.assertEqual(revision_videos("SQL", FakeClient({})), ([], "not_saved"))
        unrelated = {"video_results": [video("Excel crash course", "10:00"), video("SQL full course", "3:00:00")]}
        self.assertEqual(revision_videos("SQL", FakeClient(unrelated)), ([], "none"))


class ShortestRouteAndNotesTests(unittest.TestCase):
    def setUp(self):
        self.jobs = [job("Frontend Developer (React JS + Node JS)", "Target", "Strong HTML. Required: React and Responsive Design and REST API."),
                     job("Dev", "One", "HTML, React"), job("Dev", "Two", "HTML, REST API"), job("Dev", "Three", "HTML, Responsive Design, React")]
        self.analysis = analyze_jobs(self.jobs, {"HTML"}, threshold=.5)
        self.index = next(i for i, row in enumerate(self.analysis["jobs"]) if row["job"]["company_name"] == "Target")

    def lookup(self, table):
        return lambda skill: table.get(skill, (None, [], "low"))

    def test_standard_confidence_routes_win_over_a_shorter_low_confidence_one(self):
        table = {"Responsive Design": (0.8, [], "low"), "REST API": (2.5, [], "standard"), "React": (5.0, [], "standard")}
        plan = build_plan(self.analysis, self.index, self.lookup(table), no_revision)
        self.assertEqual(plan["shortest_route"]["skills"], ["REST API"])
        self.assertEqual(plan["shortest_route"]["low_confidence"], [])

    def test_low_confidence_route_is_used_only_when_nothing_else_reaches_the_threshold(self):
        table = {"Responsive Design": (0.8, [], "low"), "REST API": (2.5, [], "low")}
        plan = build_plan(self.analysis, self.index, self.lookup(table), no_revision)
        route = plan["shortest_route"]
        self.assertEqual(route["skills"], ["Responsive Design"])
        self.assertEqual(route["low_confidence"], ["Responsive Design"])
        self.assertIn("low course confidence", route["status"])

    def test_title_naming_a_tool_outside_the_plan_is_noted(self):
        table = {"React": (5.0, [], "standard"), "REST API": (2.5, [], "standard"), "Responsive Design": (1.5, [], "standard")}
        plan = build_plan(self.analysis, self.index, self.lookup(table), no_revision)
        self.assertTrue(any("React" in note and "shortest route does not include" in note for note in plan["title_notes"]), plan["title_notes"])
        self.assertTrue(any("Node.js" in note and "does not include" in note for note in plan["title_notes"]), plan["title_notes"])

    def test_revise_and_learn_steps_are_numbered_separately(self):
        table = {"React": (5.0, [], "standard"), "REST API": (2.5, [], "standard"), "Responsive Design": (1.5, [], "standard")}
        plan = build_plan(self.analysis, self.index, self.lookup(table), no_revision)
        for action in ("revise", "learn"):
            numbers = [item["order"] for item in plan["items"] if item["action"] == action]
            self.assertEqual(numbers, list(range(1, len(numbers) + 1)))


class JobPrepPlanTests(unittest.TestCase):
    def setUp(self):
        self.jobs = [job("Analyst", "Target", "Strong SQL is required. Excel reporting. Power BI dashboards. Power BI reports."),
                     job("Analyst", "One", "Excel, Power BI"), job("Analyst", "Two", "Excel, Tableau"),
                     job("Analyst", "Three", "Excel, SQL")]
        self.analysis = analyze_jobs(self.jobs, {"Excel"}, threshold=.5)
        self.index = next(i for i, row in enumerate(self.analysis["jobs"]) if row["job"]["company_name"] == "Target")

    def test_order_uses_job_importance_then_market_share(self):
        plan = build_plan(self.analysis, self.index, no_course, no_revision)
        rows = [(item["skill"], item["importance"], item["market"], item["market_total"]) for item in plan["items"]]
        self.assertEqual(rows, [("SQL", 3, 2, 4), ("Power BI", 2, 2, 4), ("Excel", 1, 4, 4)])
        self.assertTrue(plan["items"][0]["emphasised"])
        flat = analyze_jobs([job("Analyst", "Target", "SQL, Excel, Power BI"), *self.jobs[1:]], {"Excel"}, threshold=.5)
        target = next(i for i, row in enumerate(flat["jobs"]) if row["job"]["company_name"] == "Target")
        order = [item["skill"] for item in build_plan(flat, target, no_course, no_revision)["items"]]
        self.assertEqual(order, ["Excel", "Power BI", "SQL"])

    def test_readiness_before_and_after_and_other_unlocks(self):
        plan = build_plan(self.analysis, self.index, lambda skill: (2.0, [], "standard"), no_revision)
        self.assertEqual((plan["covered_now"], plan["covered_after"], plan["core_total"]), (1, 3, 3))
        self.assertEqual(plan["unlock_skills"], ["Power BI", "SQL"])
        for item in plan["items"]:
            if item["action"] == "learn":
                unlocked = self.analysis["unlocked"].get(item["skill"], [])
                expected = len([found for found in unlocked if found is not self.analysis["jobs"][self.index]["job"]])
                self.assertEqual(item["other_unlocks"], expected, item["skill"])
        self.assertEqual([item["skill"] for item in plan["items"] if item["action"] == "revise"], ["Excel"])
        self.assertEqual(plan["learning_hours"], 4.0)
        self.assertEqual(time_range(plan), "about 3 to 5 hours")
        self.assertEqual(time_range({"revision_minutes": 59, "learning_hours": 0.0}), "about 1 hour")
        self.assertEqual(time_range({"revision_minutes": 12, "learning_hours": 0.0}), "about 10 minutes")
        self.assertEqual(time_range({"revision_minutes": 20, "learning_hours": 0.5}), "about 40 minutes to 1 hour")
        self.assertEqual(time_range({"revision_minutes": 0, "learning_hours": 0.0}), "No measured time")

    def test_evidence_is_an_exact_line_from_the_listing(self):
        plan = build_plan(self.analysis, self.index, no_course, no_revision)
        description = self.jobs[0]["description"]
        for item in plan["items"]:
            self.assertIn(item["evidence"].strip("…"), description)
            self.assertIn(item["skill"].lower(), item["evidence"].lower())
        self.assertEqual(plan["items"][0]["evidence"], "Strong SQL is required.")

    def test_alternatives_report_the_satisfied_option_or_a_pick(self):
        jobs = [job("Dev", "Target", "React or Angular. CSS and HTML."), job("Dev", "One", "React, CSS"),
                job("Dev", "Two", "React, HTML"), job("Dev", "Three", "Angular, CSS")]
        for user, status, skill in (({"Angular", "CSS"}, "satisfied", "Angular"), ({"CSS"}, "pick", "React")):
            analysis = analyze_jobs(jobs, user, threshold=.5)
            index = next(i for i, row in enumerate(analysis["jobs"]) if row["job"]["company_name"] == "Target")
            plan = build_plan(analysis, index, no_course, no_revision)
            self.assertEqual([(alt["status"], alt["skill"]) for alt in plan["alternatives"]], [(status, skill)])
            learn = {item["skill"] for item in plan["items"] if item["action"] == "learn"}
            self.assertNotIn("Angular" if status == "pick" else "React", learn)
        self.assertIn("Pick React: asked by 3 of 4 eligible listings", plan["alternatives"][0]["text"])

    def test_missing_revision_videos_are_reported(self):
        plan = build_plan(self.analysis, self.index, no_course,
                          lambda skill: ([], "none") if skill == "Excel" else ([], "not_saved"))
        self.assertEqual(plan["missing_revision"], ["Excel"])
        self.assertEqual(plan["revision_minutes"], 0)
        self.assertEqual(plan["hours_unknown"], ["Power BI", "SQL"])


class SmallFixTests(unittest.TestCase):
    def test_evidence_spacing_never_splits_skill_names(self):
        from job_prep import readable
        self.assertEqual(readable("Web DevelopmentProficiency in HTML, CSS, JavaScript and frameworksAbility to work"),
                         "Web Development Proficiency in HTML, CSS, JavaScript and frameworks Ability to work")
        self.assertEqual(readable("(e.g., React, or Vue).Ensure high"), "(e.g., React, or Vue). Ensure high")
        for text in ("JavaScript, TypeScript and PostgreSQL on GitHub", "Node.js and Vue.js with MongoDB", "U.S. based"):
            self.assertEqual(readable(text), text)

    def test_job_list_labels_exclude_broad_skills(self):
        jobs = [job("Designer", "Target", "Figma, UI/UX, Canva"), job("Designer", "One", "Figma, UI/UX"),
                job("Designer", "Two", "Canva, UI/UX")]
        analysis = analyze_jobs(jobs, {"Figma"}, threshold=.6)
        rows = {row["job"]["company_name"]: row for row in prep_candidates(analysis)}
        self.assertEqual(rows["Target"]["unlock_skills"], ["Canva"])
        self.assertEqual((rows["One"]["unlock_skills"], rows["One"]["broad_only"]), ([], ["UI/UX"]))


class DemoJobPrepTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = demo_result("Frontend Developer", "Bengaluru", "HTML, CSS, JavaScript")

    def test_existing_demo_results_are_unchanged(self):
        recorded = json.loads((ROOT / "reports" / "final_results.json").read_text())["after"]
        for city, role, resume in (("Bengaluru", "Frontend Developer", "HTML, CSS, JavaScript"),
                                   ("Noida", "Data Analyst", "Excel, basic Python")):
            result = self.result if city == "Bengaluru" else demo_result(role, city, resume)
            saved = recorded[city]
            self.assertEqual((result["ready"], len(result["jobs"]), result["eligible_count"]),
                             (saved["matches"], saved["scored"], saved["eligible"]))
            self.assertEqual([(row["skill"], row["unlocked_count"], round(row["hours"], 2) if row["hours"] else None)
                              for row in result["ranked"]],
                             [(row["skill"], row["unlocked"], row["hours"]) for row in saved["ranked"]])
            self.assertEqual(result["bootstrap"]["shares"], saved["bootstrap"]["shares"])
            self.assertEqual(round(result["robustness"]["top_share"], 4), saved["hour_variation"]["top_share"])
            self.assertEqual([(step["skill"], step["total_jobs"]) for step in result["opportunity"]["steps"]],
                             [(step["skill"], step["total"]) for step in saved["curve"]])
            self.assertEqual(result["distance"]["counts"], saved["distance"])

    def test_default_demo_job_plan(self):
        index = default_prep_index(self.result)
        self.assertIsNotNone(index)
        statuses = {row["index"]: row["status"] for row in prep_candidates(self.result)}
        self.assertEqual(statuses[index], "one_away")
        cached = SerpClient(use_fixtures=True, cache_only=True)
        with patch("engine._request", side_effect=AssertionError("network requested")):
            plan = build_plan(self.result, index, lambda skill: course_videos(skill, cached),
                              lambda skill: revision_videos(skill, cached))
        self.assertEqual((plan["job"]["company_name"], plan["job"]["title"]), ("Team Geek Solutions", "Frontend Developer (Fresher)"))
        self.assertEqual((plan["covered_now"], plan["core_total"], plan["covered_after"]), (3, 7, 7))
        self.assertEqual(plan["unlock_skills"], ["REST API", "React", "Responsive Design"])
        items = {item["skill"]: item for item in plan["items"]}
        self.assertEqual((items["JavaScript"]["market"], items["JavaScript"]["market_total"]), (17, 23))
        self.assertEqual(items["JavaScript"]["revision_status"], "found")
        self.assertEqual(items["CSS"]["revision_status"], "found")
        self.assertEqual(items["HTML"]["revision_status"], "found")
        self.assertEqual(items["REST API"]["other_unlocks"], 7)
        self.assertTrue(items["UI/UX"]["broad"])

    def test_every_saved_pair_opens_a_prep_plan(self):
        from personas import saved_pairs
        learn_only = []
        for pair in saved_pairs():
            with patch("engine._request", side_effect=AssertionError("network requested")):
                client = SerpClient(use_fixtures=True, cache_only=True)
                result = run(pair["role"], pair["city"], resume=pair["resume"], pages=pair["pages"],
                             client=client, experience_level="Fresher")
                index = default_prep_index(result)
                self.assertIsNotNone(index, pair["id"])
                plan = build_plan(result, index, lambda skill: course_videos(skill, client),
                                  lambda skill: revision_videos(skill, client))
            self.assertEqual(plan["missing_revision"], [], pair["id"])
            if {item["action"] for item in plan["items"]} != {"revise", "learn"}:
                learn_only.append(pair["id"])
        # These two markets have no listing that asks for a skill the example profile holds.
        self.assertEqual(sorted(learn_only), ["data-analyst-indore", "digital-marketing-executive-pune"])

if __name__ == "__main__":
    unittest.main()
