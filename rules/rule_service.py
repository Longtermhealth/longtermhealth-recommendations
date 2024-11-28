#rules/rule_service.py

from typing import Dict, Any, List


def evaluate_rule(rule: Dict[str, Any], user_data: Dict[str, Any]) -> bool:
    field = rule['condition']['field']
    operator = rule['condition']['operator']
    value = rule['condition']['value']

    user_value = user_data.get(field)

    if user_value is None:
        return False

    if operator == '==':
        return user_value == value
    elif operator == '>':
        return user_value > value
    elif operator == '<':
        return user_value < value
    elif operator == '>=':
        return user_value >= value
    elif operator == '<=':
        return user_value <= value
    else:
        raise ValueError(f"Unknown operator: {operator}")



def apply_rules(rules: Dict[str, Any], user_data: Dict[str, Any], routines: Dict[str, Dict[str, Any]]) -> List[str]:
    matched_routines = []

    for rule in rules['rules']:
        print(f"Evaluating rule: {rule['name']}")
        if evaluate_rule(rule, user_data):
            print(f"Rule matched: {rule['name']}")
            condition_field = rule['condition']['field']
            condition_value = rule['condition']['value']
            action_field = rule['action']['field']
            action_value = rule['action']['value']

            for routine_name, routine_details in routines.items():
                print(f"Checking routine: {routine_name}")
                if (
                    routine_details.get(condition_field) == condition_value and
                    routine_details.get(action_field) == action_value
                ):
                    print(f"Routine matched: {routine_name}")
                    if routine_name not in matched_routines:
                        matched_routines.append(routine_name)

            print(f"Matched routines after applying rule {rule['name']}: {matched_routines}")
        else:
            print(f"Rule did not match: {rule['name']}")

    return matched_routines



