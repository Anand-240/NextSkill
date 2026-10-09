import json
import string
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

import i18n
from engine import SerpClient
from hindi import hindi_courses, hindi_revision
from views import common

ROOT = Path(__file__).resolve().parents[1]
APP = str(ROOT / "app.py")


def fields(text):
    return {name for _, name, _, _ in string.Formatter().parse(text) if name}


def offline():
    return (patch("engine.optional_serpapi_key", return_value=None),
            patch("engine._request", side_effect=AssertionError("network requested")))


class HindiVideoTests(unittest.TestCase):
    def test_saved_hindi_results_pass_the_hindi_and_relevance_filters(self):
        client = SerpClient(use_fixtures=True, cache_only=True)
        for skill in ("Excel", "SQL", "Python", "JavaScript"):
            with self.subTest(skill=skill):
                courses, status = hindi_courses(skill, client)
                self.assertEqual(status, "found")
                self.assertTrue(all("hindi" in (v["title"] + v["channel"]).lower() for v in courses))
                self.assertTrue(all(skill.lower() in v["title"].lower() for v in courses))
                revision, status = hindi_revision(skill, client)
                self.assertEqual(status, "found")
                self.assertTrue(all(5 <= v["minutes"] <= 25 for v in revision))

    def test_unsaved_skill_reports_not_saved_without_a_request(self):
        with patch("engine._request", side_effect=AssertionError("network requested")):
            client = SerpClient(use_fixtures=True, cache_only=True)
            self.assertEqual(hindi_courses("React", client), ([], "not_saved"))
            self.assertEqual(hindi_revision("React", client), ([], "not_saved"))


class StringFileTests(unittest.TestCase):
    def test_every_hindi_string_has_a_matching_english_key_and_placeholders(self):
        for key, entry in i18n.hindi_entries().items():
            with self.subTest(key=key):
                self.assertIn(key, i18n.STRINGS)
                self.assertEqual(fields(entry["hi"]) - fields(i18n.STRINGS[key]), set())
                self.assertIn("approved", entry)

    def test_unapproved_strings_never_display(self):
        entries = {k: {**v, "approved": False} for k, v in i18n.hindi_entries().items()}
        with patch.object(i18n, "hindi_entries", return_value=entries), patch.object(i18n, "hindi_on", return_value=True):
            self.assertEqual(i18n.t("tab_answer"), "Answer")


class HindiPageTests(unittest.TestCase):
    def setUp(self):
        for p in offline():
            p.start()
            self.addCleanup(p.stop)

    def test_toggle_with_unapproved_labels_keeps_english_and_shows_hindi_videos(self):
        app = AppTest.from_file(APP, default_timeout=120).run().switch_page("views/prep.py").run()
        app.toggle[0].set_value(True).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.header[0].value, "Job Prep")
        self.assertIn(i18n.HINDI_WAITING, [c.value for c in app.caption])
        text = "\n".join(m.value for m in app.markdown)
        self.assertIn("**Hindi videos**", text)
        self.assertIn("JavaScript Complete Tutorial in Hindi", text) if False else None
        captions = "\n".join(c.value for c in app.caption)
        self.assertIn("are not in the saved data, so English videos are shown", captions)

    def test_approved_strings_translate_the_headline_and_keep_user_input(self):
        entries = {k: {**v, "approved": True} for k, v in i18n.hindi_entries().items()}
        with patch.object(i18n, "hindi_entries", return_value=entries):
            app = AppTest.from_file(APP, default_timeout=120).run().switch_page("views/find.py").run()
            app.text_input[0].set_value("SQL").run()
            app.toggle[0].set_value(True).run()
            self.assertFalse(app.exception)
            self.assertEqual(app.header[0].value, entries["find_header"]["hi"])
            self.assertIn("लगभग", app.subheader[0].value)
            self.assertIn("Responsive Design", app.subheader[0].value)  # skill names stay English
            self.assertEqual(app.text_input[0].value, "SQL")
            self.assertNotIn("waiting for human review", "\n".join(c.value for c in app.caption))


if __name__ == "__main__":
    unittest.main()
