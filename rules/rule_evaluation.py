# rule_based_system/rule_evaluation.py

from .rules import rules

def apply_rules(rule_ids, responses, rules):
    """
    Apply a set of rules to the given responses.

    :param rule_ids: A list of rule IDs to apply
    :param responses: A dictionary of responses to be evaluated against the rules
    :param rules: A dictionary of rules where the key is the rule ID and the value is a list of conditions
    :return: True if all rules are satisfied, False otherwise
    """
    for rule_id in rule_ids:
        conditions = rules.get(str(rule_id), [])
        for condition in conditions:
            if condition and not evaluate_rule(condition, responses):
                print(f"Rule {rule_id} condition {condition} not satisfied.")
                return False
    return True

def evaluate_rule(rule, responses):
    """
    Evaluate a single rule against the given responses.

    :param rule: The rule condition to evaluate
    :param responses: A dictionary of responses to be used in the evaluation
    :return: True if the rule is satisfied, False otherwise
    """
    try:
        result = eval(rule)
        return result
    except Exception as e:
        #print(f"Error evaluating rule {rule}: {e}")
        return False
