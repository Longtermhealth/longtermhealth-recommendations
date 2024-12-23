# rule_based_system/tests/test_nutrition_assessment_unittest.py

import unittest
from rule_based_system.assessments.nutrition_assessment import NutritionAssessment

class TestNutritionAssessment(unittest.TestCase):

    def test_valid_input(self):
        # Provide a valid input scenario
        answers = {
            'Praktizierst du Intervallfasten und auf welche Art??': '16:8 (täglich 14-16 Stunden fasten)',
            'Wie viele Gläser Flüssigkeit (200ml) nimmst du ca. täglich zu dir?': '10-12',
            'Wie viel Alkohol trinkst du in der Woche?': 'Gar keinen',
            'Wie viel zuckerhaltige Produkte nimmst du zu dir?': '1',
            'Wie häufig nimmst du Fertiggerichte zu dir?': '1',
            'Wie viel Vollkorn nimmst du zu dir?': '5'
        }
        assessment = NutritionAssessment(answers=answers)
        score = assessment.calculate_nutrition_score()
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_missing_key(self):
        # Missing one required key
        answers = {
            'Praktizierst du Intervallfasten und auf welche Art??': '16:8 (täglich 14-16 Stunden fasten)',
            'Wie viele Gläser Flüssigkeit (200ml) nimmst du ca. täglich zu dir?': '10-12',
            'Wie viel Alkohol trinkst du in der Woche?': 'Gar keinen',
            'Wie viel zuckerhaltige Produkte nimmst du zu dir?': '1',
            'Wie häufig nimmst du Fertiggerichte zu dir?': '1'
            # Missing 'Wie viel Vollkorn nimmst du zu dir?' key
        }
        with self.assertRaises(ValueError) as context:
            NutritionAssessment(answers=answers)
        self.assertIn("Missing required key", str(context.exception))

    def test_non_integer_value(self):
        # Non-integer where integer is expected
        answers = {
            'Praktizierst du Intervallfasten und auf welche Art??': '16:8 (täglich 14-16 Stunden fasten)',
            'Wie viele Gläser Flüssigkeit (200ml) nimmst du ca. täglich zu dir?': '10-12',
            'Wie viel Alkohol trinkst du in der Woche?': 'Gar keinen',
            'Wie viel zuckerhaltige Produkte nimmst du zu dir?': 'NotAnInt',
            'Wie häufig nimmst du Fertiggerichte zu dir?': '1',
            'Wie viel Vollkorn nimmst du zu dir?': '5'
        }
        with self.assertRaises(ValueError) as context:
            NutritionAssessment(answers=answers)
        self.assertIn("must be an integer", str(context.exception))

    def test_low_values(self):
        # Minimal values for sugar and processed (5 or 6 reversed logic)
        # If sugar=5 => after reversal = 6-5=1
        # If processed=5 => after reversal=6-5=1
        # whole_grain=1 (no reversal)
        answers = {
            'Praktizierst du Intervallfasten und auf welche Art??': 'Spontanes Auslassen einer Mahlzeit (regelmäßiges Auslassen einzelner Mahlzeiten)',
            'Wie viele Gläser Flüssigkeit (200ml) nimmst du ca. täglich zu dir?': '0-3',
            'Wie viel Alkohol trinkst du in der Woche?': '10-12',
            'Wie viel zuckerhaltige Produkte nimmst du zu dir?': '5',
            'Wie häufig nimmst du Fertiggerichte zu dir?': '5',
            'Wie viel Vollkorn nimmst du zu dir?': '1'
        }
        assessment = NutritionAssessment(answers)
        score = assessment.calculate_nutrition_score()
        # Just check that it's within a reasonable range
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_all_high_values(self):
        # sugar=1 => reversed=6-1=5
        # processed=1 => reversed=6-1=5
        # whole_grain=5
        # This yields a high nutri_score
        answers = {
            'Praktizierst du Intervallfasten und auf welche Art??': '16:8 (täglich 14-16 Stunden fasten)',
            'Wie viele Gläser Flüssigkeit (200ml) nimmst du ca. täglich zu dir?': '10-12',
            'Wie viel Alkohol trinkst du in der Woche?': 'Gar keinen',
            'Wie viel zuckerhaltige Produkte nimmst du zu dir?': '1',
            'Wie häufig nimmst du Fertiggerichte zu dir?': '1',
            'Wie viel Vollkorn nimmst du zu dir?': '5'
        }
        assessment = NutritionAssessment(answers)
        score = assessment.calculate_nutrition_score()
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_mixed_values(self):
        # Mixed scenario:
        answers = {
            'Praktizierst du Intervallfasten und auf welche Art??': '5:2 (an 2 Tagen der Woche nur Einnahme von 500 bzw. 600 Kalorien)',
            'Wie viele Gläser Flüssigkeit (200ml) nimmst du ca. täglich zu dir?': '4-6',
            'Wie viel Alkohol trinkst du in der Woche?': '4-6',
            'Wie viel zuckerhaltige Produkte nimmst du zu dir?': '3',  # reversed=6-3=3
            'Wie häufig nimmst du Fertiggerichte zu dir?': '2',        # reversed=6-2=4
            'Wie viel Vollkorn nimmst du zu dir?': '2'
        }
        assessment = NutritionAssessment(answers)
        score = assessment.calculate_nutrition_score()
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)


if __name__ == '__main__':
    unittest.main()
