import csv
import tempfile
import unittest
from pathlib import Path
from scripts import score_labels, summarise_user_test


def write(path, columns, rows):
    with open(path, 'w', newline='') as handle:
        writer = csv.DictWriter(handle, columns)
        writer.writeheader()
        writer.writerows(rows)


class EvaluationKitTests(unittest.TestCase):
    def test_label_scores_use_filled_rows_only(self):
        columns = ['listing_id', 'title', 'company', 'description_text', 'skills_required',
                   'skills_mandatory', 'min_years_experience']
        base = {'listing_id': 'x', 'title': 'Analyst', 'company': 'A'}
        rows = [{**base, 'description_text': 'SQL is required. Excel is a plus. 2+ years experience in analytics.',
                 'skills_required': 'SQL; Excel', 'skills_mandatory': 'SQL', 'min_years_experience': '2'},
                {**base, 'description_text': 'Work with Python.', 'skills_required': 'Python; Statistics',
                 'skills_mandatory': 'none', 'min_years_experience': '0'},
                {**base, 'description_text': 'Unlabelled SQL listing.', 'skills_required': '',
                 'skills_mandatory': '', 'min_years_experience': ''}]
        with tempfile.TemporaryDirectory() as directory:
            path, output = Path(directory) / 'labels.csv', Path(directory) / 'out.md'
            write(path, columns, rows)
            text = score_labels.main(path, output)
            self.assertEqual(output.read_text(), text)
        result = score_labels.score(rows)
        self.assertEqual(result['rows'], 2)
        self.assertEqual(result['counts']['false_negative'], 1)  # Statistics is not detected
        self.assertEqual(result['must_have_accuracy'], 1.0)
        self.assertEqual(result['experience_accuracy'], 1.0)
        self.assertIn('Listings scored: 2 of 3', text)

    def test_labels_in_progress_when_nothing_is_filled(self):
        text = score_labels.render(score_labels.score([]), 20)
        self.assertIn('in progress', text)
        self.assertNotIn('%', text)

    def test_user_test_counts_real_rows_and_gates_quotes(self):
        columns = ['participant_id', 'role', 'city', 'unaided_choice', 'nextskill_choice', 'changed_choice',
                   'trust_1_to_5', 'confusing_points', 'would_recommend', 'quote', 'quote_permission']
        rows = [{'participant_id': 'P1', 'changed_choice': 'yes', 'trust_1_to_5': '4', 'would_recommend': 'yes',
                 'quote': 'Helpful', 'quote_permission': 'yes', 'confusing_points': 'the chart'},
                {'participant_id': 'P2', 'changed_choice': 'no', 'trust_1_to_5': '2', 'would_recommend': 'no',
                 'quote': 'Private remark', 'quote_permission': 'no', 'confusing_points': ''},
                {'participant_id': '', 'trust_1_to_5': '', 'quote': 'ignored', 'quote_permission': 'yes'}]
        text = summarise_user_test.summarise(rows)
        self.assertIn('Participants: 2', text)
        self.assertIn('Changed their choice after seeing NextSkill: 1 of 2', text)
        self.assertIn('Average trust (1 to 5): 3.0', text)
        self.assertIn('Helpful', text)
        self.assertNotIn('Private remark', text)
        self.assertNotIn('ignored', text)
        self.assertIn('Informal check: 3 friends (students and freshers)', summarise_user_test.summarise([]))
        self.assertIn('4.33 out of 5', summarise_user_test.summarise([]))
        self.assertIn('4, 4 and 5', summarise_user_test.summarise([]))

    def test_label_template_has_no_labels_and_no_contact_data(self):
        from scripts.build_data import EMAIL, PHONE
        root = Path(__file__).resolve().parents[1]
        with open(root / 'evaluation/labels_template.csv', newline='') as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 20)
        self.assertEqual(len({r['listing_id'] for r in rows}), 20)
        for row in rows:
            self.assertFalse(row['skills_required'] or row['skills_mandatory'] or row['min_years_experience'])
            self.assertFalse(EMAIL.search(row['description_text']))
            self.assertFalse(PHONE.search(row['description_text']))


if __name__ == '__main__':
    unittest.main()
