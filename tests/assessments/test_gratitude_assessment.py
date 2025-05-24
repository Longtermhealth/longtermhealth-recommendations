# rule_based_system/tests/test_gratitude_assessment_unittest.py

import unittest
from assessments.gratitude_assessment import GratitudeAssessment

class TestGratitudeAssessment(unittest.TestCase):

    def test_valid_input(self):
        answers = {
            'Ich liebe mich so, wie ich bin.': '5',
            'Ich habe so viel im Leben, wofür ich dankbar sein kann.': '5',
            'Jeder Tag ist eine Chance, es besser zu machen.': '5',
            'Im Nachhinein bin ich für jede Niederlage dankbar, denn sie haben mich weitergebracht.': '5',
            'Ich bin vielen verschiedenen Menschen dankbar.': '5'
        }
        # Calculation:
        # Initial: [5,5,5,5,5]
        # No reversed scoring
        # sum=25
        # min_score=5, max_score=25
        # normalized=((25-5)/(25-5))*80=((20/20)*80)=80
        assessment = GratitudeAssessment(answers)
        score = assessment.calculate_gratitude_score()
        self.assertAlmostEqual(score, 80.0, places=1)

    def test_missing_key(self):
        answers = {
            # Missing last key
            'Ich liebe mich so, wie ich bin.': '5',
            'Ich habe so viel im Leben, wofür ich dankbar sein kann.': '5',
            'Jeder Tag ist eine Chance, es besser zu machen.': '5',
            'Im Nachhinein bin ich für jede Niederlage dankbar, denn sie haben mich weitergebracht.': '5'
        }
        with self.assertRaises(ValueError) as context:
            GratitudeAssessment(answers=answers)
        self.assertIn("Missing required key", str(context.exception))

    def test_non_integer_value(self):
        answers = {
            'Ich liebe mich so, wie ich bin.': '5',
            'Ich habe so viel im Leben, wofür ich dankbar sein kann.': 'NotAnInt',
            'Jeder Tag ist eine Chance, es besser zu machen.': '3',
            'Im Nachhinein bin ich für jede Niederlage dankbar, denn sie haben mich weitergebracht.': '4',
            'Ich bin vielen verschiedenen Menschen dankbar.': '2'
        }
        with self.assertRaises(ValueError) as context:
            GratitudeAssessment(answers=answers)
        self.assertIn("must be an integer", str(context.exception))

    def test_all_zero(self):
        # If all are zero:
        # [0,0,0,0,0]
        # normalized_score=0
        answers = {
            'Ich liebe mich so, wie ich bin.': '0',
            'Ich habe so viel im Leben, wofür ich dankbar sein kann.': '0',
            'Jeder Tag ist eine Chance, es besser zu machen.': '0',
            'Im Nachhinein bin ich für jede Niederlage dankbar, denn sie haben mich weitergebracht.': '0',
            'Ich bin vielen verschiedenen Menschen dankbar.': '0'
        }
        assessment = GratitudeAssessment(answers)
        score = assessment.calculate_gratitude_score()
        self.assertEqual(score, 0)

    def test_mixed_values(self):
        # Let's pick some values:
        # [2,4,1,3,2]
        # No reversed scoring
        # sum=12
        # normalized=((12-5)/(25-5))*80 = (7/20)*80=28.0
        answers = {
            'Ich liebe mich so, wie ich bin.': '2',
            'Ich habe so viel im Leben, wofür ich dankbar sein kann.': '4',
            'Jeder Tag ist eine Chance, es besser zu machen.': '1',
            'Im Nachhinein bin ich für jede Niederlage dankbar, denn sie haben mich weitergebracht.': '3',
            'Ich bin vielen verschiedenen Menschen dankbar.': '2'
        }
        assessment = GratitudeAssessment(answers)
        score = assessment.calculate_gratitude_score()
        self.assertAlmostEqual(score, 28.0, places=1)

    def test_medium_values(self):
        # [3,3,3,3,3]
        # No reversed scoring
        # sum=15
        # normalized=((15-5)/(25-5))*80=(10/20)*80=40.0
        answers = {
            'Ich liebe mich so, wie ich bin.': '3',
            'Ich habe so viel im Leben, wofür ich dankbar sein kann.': '3',
            'Jeder Tag ist eine Chance, es besser zu machen.': '3',
            'Im Nachhinein bin ich für jede Niederlage dankbar, denn sie haben mich weitergebracht.': '3',
            'Ich bin vielen verschiedenen Menschen dankbar.': '3'
        }
        assessment = GratitudeAssessment(answers)
        score = assessment.calculate_gratitude_score()
        self.assertAlmostEqual(score, 40.0, places=1)


if __name__ == '__main__':
    unittest.main()
