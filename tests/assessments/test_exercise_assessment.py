# rule_based_system/tests/test_exercise_assessment_unittest.py

import unittest
from rule_based_system.assessments.exercise_assessment import ExerciseAssessment

class TestExerciseAssessment(unittest.TestCase):

    def test_valid_input(self):
        # Given all answers as '3':
        # flexibility=3, activity=3, sports_per_week=3, strength=3
        # score = (0.1*3)+(0.4*3)+(0.3*3)+(0.2*3)
        # =0.3+1.2+0.9+0.6=3.0
        # normalized=(3/5)*100=60.0
        answers = {
            'Wie schätzt du deine Beweglichkeit ein?': '3',
            'Wie aktiv bist du im Alltag?': '3',
            'Wie oft in der Woche treibst du eine Cardio-Sportart?': '3',
            'Wie schätzt du deine Kraft ein?': '3'
        }
        assessment = ExerciseAssessment(answers=answers)
        score = assessment.calculate_exercise_score()
        self.assertIsInstance(score, float)
        self.assertAlmostEqual(score, 60.0, places=1)

    def test_missing_key(self):
        # Missing 'Wie schätzt du deine Kraft ein?'
        answers = {
            'Wie schätzt du deine Beweglichkeit ein?': '5',
            'Wie aktiv bist du im Alltag?': '5',
            'Wie oft in der Woche treibst du eine Cardio-Sportart?': '5',
            # Missing strength key
        }
        with self.assertRaises(ValueError) as context:
            ExerciseAssessment(answers=answers)
        self.assertIn("Missing required key", str(context.exception))

    def test_non_integer_value(self):
        answers = {
            'Wie schätzt du deine Beweglichkeit ein?': 'five',
            'Wie aktiv bist du im Alltag?': '3',
            'Wie oft in der Woche treibst du eine Cardio-Sportart?': '3',
            'Wie schätzt du deine Kraft ein?': '3'
        }
        with self.assertRaises(ValueError) as context:
            ExerciseAssessment(answers=answers)
        self.assertIn("must be an integer", str(context.exception))

    def test_all_high_values(self):
        # All 5:
        # (0.1*5)+(0.4*5)+(0.3*5)+(0.2*5)=0.5+2.0+1.5+1.0=5.0
        # normalized=(5/5)*100=100.0
        answers = {
            'Wie schätzt du deine Beweglichkeit ein?': '5',
            'Wie aktiv bist du im Alltag?': '5',
            'Wie oft in der Woche treibst du eine Cardio-Sportart?': '5',
            'Wie schätzt du deine Kraft ein?': '5'
        }
        assessment = ExerciseAssessment(answers=answers)
        score = assessment.calculate_exercise_score()
        self.assertAlmostEqual(score, 100.0, places=1)

    def test_all_low_values(self):
        # All 1:
        # (0.1*1)+(0.4*1)+(0.3*1)+(0.2*1)=0.1+0.4+0.3+0.2=1.0
        # normalized=(1/5)*100=20.0
        answers = {
            'Wie schätzt du deine Beweglichkeit ein?': '1',
            'Wie aktiv bist du im Alltag?': '1',
            'Wie oft in der Woche treibst du eine Cardio-Sportart?': '1',
            'Wie schätzt du deine Kraft ein?': '1'
        }
        assessment = ExerciseAssessment(answers=answers)
        score = assessment.calculate_exercise_score()
        self.assertAlmostEqual(score, 20.0, places=1)

    def test_mixed_values(self):
        # flexibility=2, activity=5, sports=4, strength=3
        # score=(0.1*2)+(0.4*4)+(0.3*5)+(0.2*3)
        # =0.2+(1.6)+(1.5)+(0.6)=3.9
        # normalized=(3.9/5)*100=78.0
        answers = {
            'Wie schätzt du deine Beweglichkeit ein?': '2',
            'Wie aktiv bist du im Alltag?': '5',
            'Wie oft in der Woche treibst du eine Cardio-Sportart?': '4',
            'Wie schätzt du deine Kraft ein?': '3'
        }
        assessment = ExerciseAssessment(answers=answers)
        score = assessment.calculate_exercise_score()
        self.assertAlmostEqual(score, 78.0, places=1)

    def test_medium_values(self):
        # flexibility=4, activity=4, sports=4, strength=4
        # score=(0.1*4)+(0.4*4)+(0.3*4)+(0.2*4)
        # =0.4+1.6+1.2+0.8=4.0
        # normalized=(4/5)*100=80.0
        answers = {
            'Wie schätzt du deine Beweglichkeit ein?': '4',
            'Wie aktiv bist du im Alltag?': '4',
            'Wie oft in der Woche treibst du eine Cardio-Sportart?': '4',
            'Wie schätzt du deine Kraft ein?': '4'
        }
        assessment = ExerciseAssessment(answers=answers)
        score = assessment.calculate_exercise_score()
        self.assertAlmostEqual(score, 80.0, places=1)


if __name__ == '__main__':
    unittest.main()
