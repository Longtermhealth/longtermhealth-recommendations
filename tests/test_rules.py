# rule_based_system/tests/test_rules.py


import unittest
from rule_based_system.rules.rule_evaluation import apply_rules, evaluate_rule

class TestRuleEvaluation(unittest.TestCase):

    def setUp(self):
        self.rules = {
            '1': ["responses['age'] > 18", "responses['exercise'] == 'regular'"],
            '2': ["responses['age'] <= 18", "responses['exercise'] == 'none'"],
            '3': ["responses['stress'] < 5", "responses['nutrition'] == 'balanced'"]
        }
        self.responses_valid = {
            'age': 25,
            'exercise': 'regular',
            'stress': 3,
            'nutrition': 'balanced'
        }
        self.responses_invalid = {
            'age': 17,
            'exercise': 'regular',
            'stress': 6,
            'nutrition': 'junk'
        }

    def test_evaluate_rule_valid(self):
        self.assertTrue(evaluate_rule("responses['age'] > 18", self.responses_valid))
        self.assertTrue(evaluate_rule("responses['exercise'] == 'regular'", self.responses_valid))
        self.assertTrue(evaluate_rule("responses['stress'] < 5", self.responses_valid))
        self.assertTrue(evaluate_rule("responses['nutrition'] == 'balanced'", self.responses_valid))

    def test_evaluate_rule_invalid(self):
        self.assertFalse(evaluate_rule("responses['age'] <= 18", self.responses_valid))
        self.assertFalse(evaluate_rule("responses['exercise'] == 'none'", self.responses_valid))
        self.assertFalse(evaluate_rule("responses['stress'] > 5", self.responses_valid))
        self.assertFalse(evaluate_rule("responses['nutrition'] == 'junk'", self.responses_valid))

    def test_apply_rules_valid(self):
        self.assertTrue(apply_rules(['1'], self.responses_valid, self.rules))
        self.assertTrue(apply_rules(['3'], self.responses_valid, self.rules))

    def test_apply_rules_invalid(self):
        self.assertFalse(apply_rules(['2'], self.responses_valid, self.rules))
        self.assertFalse(apply_rules(['1'], self.responses_invalid, self.rules))
        self.assertFalse(apply_rules(['3'], self.responses_invalid, self.rules))

    def test_apply_rules_mixed(self):
        self.assertTrue(apply_rules(['1', '3'], self.responses_valid, self.rules))
        self.assertFalse(apply_rules(['1', '2'], self.responses_valid, self.rules))
        self.assertFalse(apply_rules(['2', '3'], self.responses_valid, self.rules))

if __name__ == '__main__':
    unittest.main()
