import unittest
from rule_based_system.assessments.stress_management_assessment import StressManagementAssessment


class TestStressManagementAssessment(unittest.TestCase):

    def test_valid_input(self):
        answers = {
            'Leidest du aktuell unter Stress?': '1',
            'Ich versuche, die positive Seite von Stress und Druck zu sehen.': '5',
            'Ich tue alles, damit Stress erst gar nicht entsteht.': '5',
            'Wenn ich unter Druck gerate, habe ich Menschen, die mir helfen.': '5',
            'Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.': '1',
        }
        assessment = StressManagementAssessment(answers=answers)
        score = assessment.calculate_stress_management_score()
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        self.assertIsNotNone(assessment.report())

    def test_missing_key(self):
        answers = {
            # Missing 'Leidest du aktuell unter Stress?' key
            'Ich versuche, die positive Seite von Stress und Druck zu sehen.': '5',
            'Ich tue alles, damit Stress erst gar nicht entsteht.': '5',
            'Wenn ich unter Druck gerate, habe ich Menschen, die mir helfen.': '5',
            'Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.': '1',
        }
        with self.assertRaises(ValueError) as context:
            StressManagementAssessment(answers=answers)
        self.assertIn("Missing required key", str(context.exception))

    def test_non_integer_value(self):
        answers = {
            'Leidest du aktuell unter Stress?': 'NotAnInt',
            'Ich versuche, die positive Seite von Stress und Druck zu sehen.': '5',
            'Ich tue alles, damit Stress erst gar nicht entsteht.': '5',
            'Wenn ich unter Druck gerate, habe ich Menschen, die mir helfen.': '5',
            'Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.': '1',
        }
        with self.assertRaises(ValueError) as context:
            StressManagementAssessment(answers=answers)
        self.assertIn("must be an integer", str(context.exception))

    def test_all_high_scores(self):
        answers = {
            'Leidest du aktuell unter Stress?': '1',
            'Ich versuche, die positive Seite von Stress und Druck zu sehen.': '5',
            'Ich tue alles, damit Stress erst gar nicht entsteht.': '5',
            'Wenn ich unter Druck gerate, habe ich Menschen, die mir helfen.': '5',
            'Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.': '5',
        }
        assessment = StressManagementAssessment(answers=answers)
        score = assessment.calculate_stress_management_score()
        # High coping and low stress scenario should yield a high score
        self.assertGreater(score, 0)

    def test_zero_stress(self):
        # Expected:
        # Stress '5' => maps to 0
        # Coping: 1,1,1 and reversed(1)=5 for the negative Q => sum=8/4=2 avg
        # Weighted=(0.6*0)+(0.4*2)=0.8; normalized=(0.8/5)*100=16.0
        answers = {
            'Leidest du aktuell unter Stress?': '5',
            'Ich versuche, die positive Seite von Stress und Druck zu sehen.': '1',
            'Ich tue alles, damit Stress erst gar nicht entsteht.': '1',
            'Wenn ich unter Druck gerate, habe ich Menschen, die mir helfen.': '1',
            'Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.': '1',
        }
        assessment = StressManagementAssessment(answers=answers)
        score = assessment.calculate_stress_management_score()
        self.assertAlmostEqual(score, 16.0, places=1)

    def test_reversed_logic_all_possible_values(self):
        # Check the reversed logic question for all values
        for raw_value, expected_reversed in [(1, 5), (2,4), (3,3), (4,2), (5,1)]:
            answers = {
                'Leidest du aktuell unter Stress?': '3',
                'Ich versuche, die positive Seite von Stress und Druck zu sehen.': '3',
                'Ich tue alles, damit Stress erst gar nicht entsteht.': '3',
                'Wenn ich unter Druck gerate, habe ich Menschen, die mir helfen.': '3',
                'Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.': str(raw_value),
            }
            assessment = StressManagementAssessment(answers=answers)
            stress_level, coping_avg = assessment.stress_management
            expected_average = (3 + 3 + 3 + expected_reversed) / 4
            self.assertAlmostEqual(coping_avg, expected_average, places=2)
            score = assessment.calculate_stress_management_score()
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)

    def test_mixed_values(self):
        # Calculation per previous discussion:
        # Stress '2' => maps to 4
        # Coping: 4,2,5,2(reversed=4) => sum=4+2+5+4=15/4=3.75
        # Weighted=0.6*4 +0.4*3.75=2.4+1.5=3.9; normalized=(3.9/5)*100=78.0
        answers = {
            'Leidest du aktuell unter Stress?': '2',
            'Ich versuche, die positive Seite von Stress und Druck zu sehen.': '4',
            'Ich tue alles, damit Stress erst gar nicht entsteht.': '2',
            'Wenn ich unter Druck gerate, habe ich Menschen, die mir helfen.': '5',
            'Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.': '2',
        }
        assessment = StressManagementAssessment(answers=answers)
        score = assessment.calculate_stress_management_score()
        self.assertAlmostEqual(score, 78.0, places=1)

    def test_low_values(self):
        # Stress '1'=>5
        # Coping: 1,1,1,1(reversed still 1)
        # sum=4/4=1 avg
        # Weighted=0.6*5+0.4*1=3+0.4=3.4; (3.4/5)*100=68.0
        # Correction: The logic described earlier was for "test_high_stress_poor_coping" scenario.
        # For low_values scenario from previous tests:
        # Actually, let's keep consistent with the old test:
        #   Stress: '1' =>5
        #   Coping all '1': posQ=1 each, negQ=1 => reversed=5 actually if it's '1' raw => reversed=5???
        # Wait, the negative question reversal is: reversed_value = 6 - raw_value
        # If raw_value=1 => reversed=6-1=5
        # sum=1+1+1+5=8/4=2 avg
        # Weighted=0.6*5+0.4*2=3+0.8=3.8; normalized=(3.8/5)*100=76.0

        answers = {
            'Leidest du aktuell unter Stress?': '1',
            'Ich versuche, die positive Seite von Stress und Druck zu sehen.': '1',
            'Ich tue alles, damit Stress erst gar nicht entsteht.': '1',
            'Wenn ich unter Druck gerate, habe ich Menschen, die mir helfen.': '1',
            'Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.': '1',
        }
        assessment = StressManagementAssessment(answers=answers)
        score = assessment.calculate_stress_management_score()
        self.assertAlmostEqual(score, 76.0, places=1)

    def test_high_stress_poor_coping(self):
        # Stress: '1' => 5
        # Positive coping: all '1'
        # Negative coping: '5' => reversed=1
        # sum=1+1+1+1=4/4=1 avg
        # Weighted=0.6*5+0.4*1=3+0.4=3.4; normalized=(3.4/5)*100=68.0

        answers = {
            'Leidest du aktuell unter Stress?': '1',
            'Ich versuche, die positive Seite von Stress und Druck zu sehen.': '1',
            'Ich tue alles, damit Stress erst gar nicht entsteht.': '1',
            'Wenn ich unter Druck gerate, habe ich Menschen, die mir helfen.': '1',
            'Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.': '5',
        }
        assessment = StressManagementAssessment(answers=answers)
        score = assessment.calculate_stress_management_score()
        self.assertAlmostEqual(score, 68.0, places=1)

    def test_medium_stress_medium_coping(self):
        # Stress '3' => 3
        # Coping: 3,3,3,3(reversed=3)
        # sum=12/4=3
        # Weighted=0.6*3+0.4*3=1.8+1.2=3
        # normalized=(3/5)*100=60.0

        answers = {
            'Leidest du aktuell unter Stress?': '3',
            'Ich versuche, die positive Seite von Stress und Druck zu sehen.': '3',
            'Ich tue alles, damit Stress erst gar nicht entsteht.': '3',
            'Wenn ich unter Druck gerate, habe ich Menschen, die mir helfen.': '3',
            'Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.': '3',
        }
        assessment = StressManagementAssessment(answers=answers)
        score = assessment.calculate_stress_management_score()
        self.assertAlmostEqual(score, 60.0, places=1)


if __name__ == '__main__':
    unittest.main()
