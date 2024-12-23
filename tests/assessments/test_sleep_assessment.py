# rule_based_system/tests/test_sleep_assessment_unittest.py

import unittest
from rule_based_system.assessments.sleep_assessment import SleepAssessment

class TestSleepAssessment(unittest.TestCase):

    def test_valid_input(self):
        answers = {
            'Wie ist deine Schlafqualität?': 'Sehr gut',
            'Welche Schlafprobleme hast du?': [],
            'Wie viele Stunden schläfst du im Durchschnitt pro Nacht?': '7-9',
            'Fühlst du dich tagsüber müde?': '1',
            'Wie viel Zeit verbringst du morgens draußen?': '> 20 min',
            'Wie viel Zeit verbringst du abends draußen?': '> 20 min'
        }
        assessment = SleepAssessment(answers)
        score = assessment.calculate_sleep_score()
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        self.assertIsNotNone(assessment.report())

    def test_missing_key(self):
        answers = {
            # Missing 'Wie ist deine Schlafqualität?'
            'Welche Schlafprobleme hast du?': [],
            'Wie viele Stunden schläfst du im Durchschnitt pro Nacht?': '7-9',
            'Fühlst du dich tagsüber müde?': '1',
            'Wie viel Zeit verbringst du morgens draußen?': '> 20 min',
            'Wie viel Zeit verbringst du abends draußen?': '> 20 min'
        }
        with self.assertRaises(ValueError) as context:
            SleepAssessment(answers)
        self.assertIn("Missing required key", str(context.exception))

    def test_invalid_sleep_quality(self):
        answers = {
            'Wie ist deine Schlafqualität?': 'sehr gut',  # invalid, should be "Sehr gut"
            'Welche Schlafprobleme hast du?': [],
            'Wie viele Stunden schläfst du im Durchschnitt pro Nacht?': '7-9',
            'Fühlst du dich tagsüber müde?': '1',
            'Wie viel Zeit verbringst du morgens draußen?': '> 20 min',
            'Wie viel Zeit verbringst du abends draußen?': '> 20 min'
        }
        with self.assertRaises(ValueError) as context:
            SleepAssessment(answers)
        self.assertIn("Invalid sleep quality", str(context.exception))

    def test_non_integer_tiredness(self):
        answers = {
            'Wie ist deine Schlafqualität?': 'Gut',
            'Welche Schlafprobleme hast du?': [],
            'Wie viele Stunden schläfst du im Durchschnitt pro Nacht?': '4-6',
            'Fühlst du dich tagsüber müde?': 'NotAnInt',
            'Wie viel Zeit verbringst du morgens draußen?': '5-10 min',
            'Wie viel Zeit verbringst du abends draußen?': '5-10 min'
        }
        with self.assertRaises(ValueError) as context:
            SleepAssessment(answers)
        self.assertIn("must be an integer", str(context.exception))

    def test_invalid_sleep_hours(self):
        answers = {
            'Wie ist deine Schlafqualität?': 'Gut',
            'Welche Schlafprobleme hast du?': ['Einschlafprobleme'],
            'Wie viele Stunden schläfst du im Durchschnitt pro Nacht?': '8-10', # not in mapping
            'Fühlst du dich tagsüber müde?': '2',
            'Wie viel Zeit verbringst du morgens draußen?': '5-10 min',
            'Wie viel Zeit verbringst du abends draußen?': '5-10 min'
        }
        with self.assertRaises(ValueError) as context:
            SleepAssessment(answers)
        self.assertIn("Invalid sleep hours", str(context.exception))

    def test_invalid_morning_time(self):
        answers = {
            'Wie ist deine Schlafqualität?': 'Mittel',
            'Welche Schlafprobleme hast du?': [],
            'Wie viele Stunden schläfst du im Durchschnitt pro Nacht?': '7-9',
            'Fühlst du dich tagsüber müde?': '3',
            'Wie viel Zeit verbringst du morgens draußen?': 'mehr als 60 min', # not in mapping
            'Wie viel Zeit verbringst du abends draußen?': '5-10 min'
        }
        with self.assertRaises(ValueError) as context:
            SleepAssessment(answers)
        self.assertIn("Invalid morning outside time", str(context.exception))

    def test_invalid_evening_time(self):
        answers = {
            'Wie ist deine Schlafqualität?': 'Mittel',
            'Welche Schlafprobleme hast du?': [],
            'Wie viele Stunden schläfst du im Durchschnitt pro Nacht?': '7-9',
            'Fühlst du dich tagsüber müde?': '3',
            'Wie viel Zeit verbringst du morgens draußen?': '5-10 min',
            'Wie viel Zeit verbringst du abends draußen?': 'mehr als 60 min' # not in mapping
        }
        with self.assertRaises(ValueError) as context:
            SleepAssessment(answers)
        self.assertIn("Invalid evening outside time", str(context.exception))

    def test_problems_with_poor_quality(self):
        # poor quality: 'Ich habe leichte Schlafprobleme'
        # Suppose they have 'Einschlafprobleme' and 'Durchschlafprobleme'
        # This should reduce sleep_problems_value from 5 by 2 (1 each)
        answers = {
            'Wie ist deine Schlafqualität?': 'Ich habe leichte Schlafprobleme',
            'Welche Schlafprobleme hast du?': ['Einschlafprobleme', 'Durchschlafprobleme'],
            'Wie viele Stunden schläfst du im Durchschnitt pro Nacht?': '4-6',
            'Fühlst du dich tagsüber müde?': '2',
            'Wie viel Zeit verbringst du morgens draußen?': '5-10 min',
            'Wie viel Zeit verbringst du abends draußen?': '5-10 min'
        }
        assessment = SleepAssessment(answers)
        score = assessment.calculate_sleep_score()
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

if __name__ == '__main__':
    unittest.main()
