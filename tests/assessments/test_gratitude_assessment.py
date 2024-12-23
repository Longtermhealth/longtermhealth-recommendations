# rule_based_system/tests/test_gratitude_assessment_unittest.py

import unittest
from rule_based_system.assessments.gratitude_assessment import GratitudeAssessment

class TestGratitudeAssessment(unittest.TestCase):

    def test_valid_input(self):
        answers = {
            'Ich habe so viel im Leben, wofür ich dankbar sein kann.': '5',
            'Wenn ich alles auflisten müsste, wofür ich dankbar bin, wäre es eine sehr lange Liste.': '5',
            'Wenn ich die Welt betrachte, sehe ich nicht viel, wofür ich dankbar sein könnte.': '1',
            'Ich bin vielen verschiedenen Menschen dankbar.': '5',
            'Je älter ich werde, desto mehr schätze ich die Menschen, Ereignisse und Situationen, die Teil meiner Lebensgeschichte waren.': '5',
            'Es können lange Zeiträume vergehen, bevor ich etwas oder jemandem dankbar bin.': '1'
        }
        # Calculation:
        # Initial: [5,5,1,5,5,1]
        # Reverse index 2: 1 -> 6-1=5
        # Reverse index 5: 1 -> 6-1=5
        # Now: [5,5,5,5,5,5] sum=30
        # min_score=5, max_score=30
        # normalized=((30-5)/(30-5))*100=((25/25)*100)=100
        assessment = GratitudeAssessment(answers)
        score = assessment.calculate_gratitude_score()
        self.assertAlmostEqual(score, 100.0, places=1)

    def test_missing_key(self):
        answers = {
            # Missing last key
            'Ich habe so viel im Leben, wofür ich dankbar sein kann.': '5',
            'Wenn ich alles auflisten müsste, wofür ich dankbar bin, wäre es eine sehr lange Liste.': '5',
            'Wenn ich die Welt betrachte, sehe ich nicht viel, wofür ich dankbar sein könnte.': '1',
            'Ich bin vielen verschiedenen Menschen dankbar.': '5',
            'Je älter ich werde, desto mehr schätze ich die Menschen, Ereignisse und Situationen, die Teil meiner Lebensgeschichte waren.': '5'
        }
        with self.assertRaises(ValueError) as context:
            GratitudeAssessment(answers=answers)
        self.assertIn("Missing required key", str(context.exception))

    def test_non_integer_value(self):
        answers = {
            'Ich habe so viel im Leben, wofür ich dankbar sein kann.': '5',
            'Wenn ich alles auflisten müsste, wofür ich dankbar bin, wäre es eine sehr lange Liste.': 'NotAnInt',
            'Wenn ich die Welt betrachte, sehe ich nicht viel, wofür ich dankbar sein könnte.': '3',
            'Ich bin vielen verschiedenen Menschen dankbar.': '4',
            'Je älter ich werde, desto mehr schätze ich die Menschen, Ereignisse und Situationen, die Teil meiner Lebensgeschichte waren.': '2',
            'Es können lange Zeiträume vergehen, bevor ich etwas oder jemandem dankbar bin.': '1'
        }
        with self.assertRaises(ValueError) as context:
            GratitudeAssessment(answers=answers)
        self.assertIn("must be an integer", str(context.exception))

    def test_all_zero(self):
        # If all are zero:
        # [0,0,0,0,0,0]
        # normalized_score=0
        answers = {
            'Ich habe so viel im Leben, wofür ich dankbar sein kann.': '0',
            'Wenn ich alles auflisten müsste, wofür ich dankbar bin, wäre es eine sehr lange Liste.': '0',
            'Wenn ich die Welt betrachte, sehe ich nicht viel, wofür ich dankbar sein könnte.': '0',
            'Ich bin vielen verschiedenen Menschen dankbar.': '0',
            'Je älter ich werde, desto mehr schätze ich die Menschen, Ereignisse und Situationen, die Teil meiner Lebensgeschichte waren.': '0',
            'Es können lange Zeiträume vergehen, bevor ich etwas oder jemandem dankbar bin.': '0'
        }
        assessment = GratitudeAssessment(answers)
        score = assessment.calculate_gratitude_score()
        self.assertEqual(score, 0)

    def test_mixed_values(self):
        # Let's pick some values:
        # [2,4,5,1,3,4]
        # reverse index 2 (5-> 6-5=1)
        # reverse index 5 (4-> 6-4=2)
        # final: [2,4,1,1,3,2] sum=13
        # normalized=((13-5)/25)*100 = (8/25)*100=32.0
        answers = {
            'Ich habe so viel im Leben, wofür ich dankbar sein kann.': '2',
            'Wenn ich alles auflisten müsste, wofür ich dankbar bin, wäre es eine sehr lange Liste.': '4',
            'Wenn ich die Welt betrachte, sehe ich nicht viel, wofür ich dankbar sein könnte.': '5',
            'Ich bin vielen verschiedenen Menschen dankbar.': '1',
            'Je älter ich werde, desto mehr schätze ich die Menschen, Ereignisse und Situationen, die Teil meiner Lebensgeschichte waren.': '3',
            'Es können lange Zeiträume vergehen, bevor ich etwas oder jemandem dankbar bin.': '4'
        }
        assessment = GratitudeAssessment(answers)
        score = assessment.calculate_gratitude_score()
        self.assertAlmostEqual(score, 32.0, places=1)

    def test_medium_values(self):
        # [3,3,3,3,3,3]
        # reverse index 2 (3->6-3=3)
        # reverse index 5 (3->6-3=3)
        # final: still [3,3,3,3,3,3] sum=18
        # normalized=((18-5)/25)*100=(13/25)*100=52.0
        answers = {
            'Ich habe so viel im Leben, wofür ich dankbar sein kann.': '3',
            'Wenn ich alles auflisten müsste, wofür ich dankbar bin, wäre es eine sehr lange Liste.': '3',
            'Wenn ich die Welt betrachte, sehe ich nicht viel, wofür ich dankbar sein könnte.': '3',
            'Ich bin vielen verschiedenen Menschen dankbar.': '3',
            'Je älter ich werde, desto mehr schätze ich die Menschen, Ereignisse und Situationen, die Teil meiner Lebensgeschichte waren.': '3',
            'Es können lange Zeiträume vergehen, bevor ich etwas oder jemandem dankbar bin.': '3'
        }
        assessment = GratitudeAssessment(answers)
        score = assessment.calculate_gratitude_score()
        self.assertAlmostEqual(score, 52.0, places=1)


if __name__ == '__main__':
    unittest.main()
