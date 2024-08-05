# rule_based_system/utils/data_loader.py

import json
import os

def load_routines(filepath=None):
    """
    Load routines data from a JSON file.

    Parameters:
        filepath (str): The path to the routines JSON file.

    Returns:
        list: A list of routines.
    """
    if filepath is None:
        filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/routines.json'))
    with open(filepath, 'r') as file:
        routines = json.load(file)
    return routines

def load_rules(filepath=None):
    """
    Load rules data from a JSON file.

    Parameters:
        filepath (str): The path to the rules JSON file.

    Returns:
        dict: A dictionary of rules.
    """
    if filepath is None:
        filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/rules_same.json'))
    with open(filepath, 'r') as file:
        rules = json.load(file)
    return rules

if __name__ == "__main__":
    routines = load_routines()
    rules = load_rules()
    print("Routines:", routines)
    print("Rules:", rules)
