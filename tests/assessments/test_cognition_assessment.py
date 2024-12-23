# rule_based_system/tests/test_cognition_assessment_unittest.py

import unittest
from rule_based_system.assessments.cognition_assessment import CognitionAssessment

class TestCognitionAssessment(unittest.TestCase):

    def test_valid_input(self):
        answers = {
            'Wie würdest du deine Vergesslichkeit einstufen?': '3',
            'Wie gut ist dein Konzentrationsvermögen?': '4',
            'Nimmst du dir im Alltag Zeit, noch neue Dinge/Fähigkeiten zu erlernen?': '2'
        }
        # forgetfulness=6-3=3, concentration=4, learning=2
        # total=3+4+2=9; score=(9/15)*100=60.0
        assessment = CognitionAssessment(answers=answers)
        score = assessment.calculate_cognition_score()
        self.assertIsInstance(score, float)
        self.assertAlmostEqual(score, 60.0, places=1)
        self.assertIsNotNone(assessment.report())

    def test_missing_key(self):
        # Missing one required key
        answers = {
            'Wie würdest du deine Vergesslichkeit einstufen?': '3',
            'Wie gut ist dein Konzentrationsvermögen?': '4',
            # Missing 'Nimmst du dir im Alltag Zeit...'
        }
        with self.assertRaises(ValueError) as context:
            CognitionAssessment(answers=answers)
        self.assertIn("Missing required key", str(context.exception))

    def test_non_integer_value(self):
        answers = {
            'Wie würdest du deine Vergesslichkeit einstufen?': 'NotAnInt',
            'Wie gut ist dein Konzentrationsvermögen?': '4',
            'Nimmst du dir im Alltag Zeit, noch neue Dinge/Fähigkeiten zu erlernen?': '2'
        }
        with self.assertRaises(ValueError) as context:
            CognitionAssessment(answers=answers)
        self.assertIn("must be an integer", str(context.exception))

    def test_high_values(self):
        # All answers '5':
        # forgetfulness=6-5=1, concentration=5, learning=5
        # total=1+5+5=11; score=(11/15)*100 ≈ 73.33
        answers = {
            'Wie würdest du deine Vergesslichkeit einstufen?': '5',
            'Wie gut ist dein Konzentrationsvermögen?': '5',
            'Nimmst du dir im Alltag Zeit, noch neue Dinge/Fähigkeiten zu erlernen?': '5'
        }
        assessment = CognitionAssessment(answers)
        score = assessment.calculate_cognition_score()
        self.assertAlmostEqual(score, (11/15)*100, places=2)

    def test_low_values(self):
        # All answers '1':
        # forgetfulness=6-1=5, concentration=1, learning=1
        # total=5+1+1=7; score=(7/15)*100 ≈ 46.67
        answers = {
            'Wie würdest du deine Vergesslichkeit einstufen?': '1',
            'Wie gut ist dein Konzentrationsvermögen?': '1',
            'Nimmst du dir im Alltag Zeit, noch neue Dinge/Fähigkeiten zu erlernen?': '1'
        }
        assessment = CognitionAssessment(answers)
        score = assessment.calculate_cognition_score()
        self.assertAlmostEqual(score, (7/15)*100, places=2)

    def test_mixed_values(self):
        # forgetfulness=4 => raw=2 (6-2=4)
        # concentration=3
        # learning=5
        # total=4+3+5=12; score=(12/15)*100=80.0
        answers = {
            'Wie würdest du deine Vergesslichkeit einstufen?': '2',
            'Wie gut ist dein Konzentrationsvermögen?': '3',
            'Nimmst du dir im Alltag Zeit, noch neue Dinge/Fähigkeiten zu erlernen?': '5'
        }
        assessment = CognitionAssessment(answers)
        score = assessment.calculate_cognition_score()
        self.assertAlmostEqual(score, 80.0, places=1)

    def test_medium_values(self):
        # forgetfulness=6-3=3
        # concentration=3
        # learning=3
        # total=3+3+3=9; score= (9/15)*100=60.0
        answers = {
            'Wie würdest du deine Vergesslichkeit einstufen?': '3',
            'Wie gut ist dein Konzentrationsvermögen?': '3',
            'Nimmst du dir im Alltag Zeit, noch neue Dinge/Fähigkeiten zu erlernen?': '3'
        }
        assessment = CognitionAssessment(answers)
        score = assessment.calculate_cognition_score()
        self.assertAlmostEqual(score, 60.0, places=1)


if __name__ == '__main__':
    unittest.main()
