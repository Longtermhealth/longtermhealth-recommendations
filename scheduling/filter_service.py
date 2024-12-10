import json
import logging
from typing import Dict, Any, List

from assessments.health_assessment import HealthAssessment
from rules.rule_service import evaluate_rule
from utils.data_processing import integrate_answers
from utils.typeform_api import process_latest_response, get_field_mapping, get_responses

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

excluded_rules = set()
included_rules = set()
valid_pillars = [
    "MOVEMENT", "NUTRITION", "SLEEP", "SOCIAL_ENGAGEMENT",
    "STRESS", "GRATITUDE", "COGNITIVE_ENHANCEMENT", "BASICS", "SCORES"
]


def load_json_data(file_path: str) -> List[Dict[str, Any]]:
    """Load data from a JSON file and return it as a list of dictionaries."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"Error: The file {file_path} was not found.")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from the file {file_path}: {e}")
        return []


def new_load_routines() -> List[Dict[str, Any]]:
    """Load routines from the new JSON structure."""
    return load_json_data('./data/strapi_all_routines.json')


def new_load_rules() -> Dict[str, Any]:
    """Load new rules from a JSON file."""
    return load_json_data('./data/rules.json')

def calculate_bmi(weight: float, height: float) -> float:
    if height <= 0:
        raise ValueError("Height must be greater than zero")
    bmi = weight / (height ** 2)
    return round(bmi, 2)


def add_benefits_to_user_profile(user_profile, goals_benefits_map):
    for goal in user_profile.get("goals", []):
        benefits = goals_benefits_map.get(goal, [])
        for benefit in benefits:
            if benefit not in user_profile["benefits"]:
                user_profile["benefits"].append(benefit)


def save_routines_to_json(routines, file_path):
    try:
        with open(file_path, 'w') as f:
            json.dump(routines, f, indent=4)
        print(f"Routines successfully saved to {file_path}")
    except Exception as e:
        logger.error(f"An error occurred while saving routines: {e}")


def generate_recommendations(user_data, routines, rules):
    recommended_routines = {}
    user_profile = {"goals": [], "benefits": [], "category": []}
    seen_routines = set()

    for pillar, pillar_data in user_data.items():
        if pillar not in valid_pillars:
            continue
        filtered_routines = filter_inclusions(
            pillar_data, pillar,
            rules.get('rules', {}).get(pillar, []),
            routines, seen_routines, user_data
        )
        recommended_routines[pillar] = filtered_routines

        for rule in rules.get('rules', {}).get(pillar, []):
            if evaluate_rule(rule, pillar_data, user_data):
                actions = rule.get('actions') or [rule.get('action')]
                for action in actions:
                    action_field = action.get('field')
                    action_value = action.get('value')
                    if action_field == "Goal" and action_value not in user_profile["goals"]:
                        user_profile["goals"].append(action_value)
                    elif action_field.startswith("Benefit") and action_value not in user_profile["benefits"]:
                        user_profile["benefits"].append(action_value)

    add_benefits_to_user_profile(user_profile, load_goals_benefits())
    return recommended_routines, user_profile


def apply_global_exclusions(user_data, exclusion_rules, routines):
    global excluded_rules
    print("\nApplying global exclusions...")

    for rule in exclusion_rules:
        pillar_name = rule.get('pillar')
        pillar_data = user_data.get(pillar_name, {})
        conditions = rule.get('conditions')

        if not conditions:
            condition = rule.get('condition')
            if condition:
                conditions = {'rules': [condition], 'logic': 'and'}

        if conditions:
            logic = conditions.get('logic', 'and')
            rules = conditions.get('rules', [])
            if evaluate_conditions(rules, logic, pillar_data, user_data):
                actions = rule.get('action', [])
                if isinstance(actions, dict):
                    actions = [actions]

                for action in actions:
                    exclude_value = action.get('value')
                    field_to_check = action.get('field')

                    for routine in routines:
                        attributes = routine.get('attributes', {})


                        dynamic_field_value = check_dynamic_field(attributes, field_to_check)


                        if isinstance(dynamic_field_value, list):
                            if exclude_value in dynamic_field_value:
                                routine['rule_status'] = 'excluded'
                                routine['score_rules'] = 0
                                routine['score_rules_explanation'] = f"Excluded by rule '{rule.get('name', 'Unnamed Rule')}'"
                                excluded_rules.add(
                                    (rule.get('name', 'Unnamed Rule'), f"{field_to_check}: {exclude_value}"))
                        elif dynamic_field_value == exclude_value:
                            routine['rule_status'] = 'excluded'
                            routine['score_rules'] = 0
                            routine['score_rules_explanation'] = f"Excluded by rule '{rule.get('name', 'Unnamed Rule')}'"
                            excluded_rules.add((rule.get('name', 'Unnamed Rule'), f"{field_to_check}: {exclude_value}"))

    print("Exclusion processing complete.\n")
    return routines


def filter_inclusions(pillar_data, pillar_name, pillar_rules, routines, user_data, processed_routines):
    global included_rules
    routine_scores = {}
    routine_explanations = {}

    for routine in routines:
        if routine.get('attributes', {}).get('rule_status') == 'excluded':
            continue
        else:
            routine_id = routine['id']
            routine_scores[routine_id] = 0
            routine_explanations[routine_id] = []

    for rule in pillar_rules:
        conditions = rule.get('conditions')
        if not conditions:
            condition = rule.get('condition')
            if condition:
                conditions = {'rules': [condition], 'logic': 'and'}

        if conditions:
            logic = conditions.get('logic', 'and')
            rules = conditions.get('rules', [])

            if evaluate_conditions(rules, logic, pillar_data, user_data):
                actions = rule.get('actions') or [rule.get('action')]
                for action in actions:
                    action_value = action.get('value')
                    action_field = action.get('field')
                    weight = int(action.get('weight', 1))

                    for routine in routines:
                        routine_id = routine['id']
                        if routine_id in processed_routines:
                            continue
                        if routine.get('attributes', {}).get('rule_status') == 'excluded':
                            continue

                        routine_pillar = routine['attributes']['pillar']['pillar']

                        if routine_pillar == pillar_name:

                            routine_field_value = check_dynamic_field(routine['attributes'], action_field)

                            if isinstance(routine_field_value, list):
                                if action_value in routine_field_value:
                                    routine_scores[routine_id] += weight
                                    explanation = (
                                        f"matched the rule '{rule.get('name', 'Unnamed Rule')}' with score {weight} "
                                        f"due to {action_field}: {action_value}"
                                    )
                                    routine_explanations[routine_id].append(explanation)
                                    included_rules.add(
                                        (rule.get('name', 'Unnamed Rule'), f"{action_field}: {action_value}"))
                                    routine['rule_status'] = 'included'
                                    routine['score_rules'] = routine_scores[routine_id]
                                    routine["score_rules_explanation"] = (
                                        f"Routine '{routine['attributes'].get('name', 'Unnamed Routine')}' recommended under pillar '{pillar_name}' with "
                                        f"cumulative score {routine_scores[routine_id]} because it {explanation}"
                                    )
                                    processed_routines.add(routine_id)
                            elif routine_field_value == action_value:
                                routine_scores[routine_id] += weight
                                explanation = (
                                    f"matched the rule '{rule.get('name', 'Unnamed Rule')}' with score {weight} "
                                    f"due to {action_field}: {action_value}"
                                )
                                routine_explanations[routine_id].append(explanation)
                                included_rules.add((rule.get('name', 'Unnamed Rule'), f"{action_field}: {action_value}"))
                                routine['rule_status'] = 'included'
                                routine['score_rules'] = routine_scores[routine_id]
                                routine["score_rules_explanation"] = (
                                    f"Routine '{routine['attributes'].get('name', 'Unnamed Routine')}' recommended under pillar '{pillar_name}' with "
                                    f"cumulative score {routine_scores[routine_id]} because it {explanation}"
                                )
                                processed_routines.add(routine_id)

    return routines


def delete_filtered_routines(routines):
    filtered_routines = [routine for routine in routines if routine.get('rule_status') not in ['included', 'excluded']]
    return [routine for routine in routines if routine not in filtered_routines]


def ensure_default_fields(routines):
    """Ensure that all routines have default rule-related fields."""
    filtered_routines = [routine for routine in routines if routine.get('rule_status') not in ['included', 'excluded']]

    for routine in filtered_routines:
        attributes = routine.get('attributes', {})
        if 'rule_status' not in attributes:
            attributes['rule_status'] = 'no_rule_applied'
        if 'score_rules' not in attributes:
            attributes['score_rules'] = 1
        if 'score_rules_explanation' not in attributes:
            attributes['score_rules_explanation'] = "No inclusion rule applied"
    return routines


def evaluate_conditions(conditions, logic, pillar_data, user_data):
    if not conditions:
        return False

    results = []

    for condition in conditions:
        if isinstance(condition, str):
            continue
        elif isinstance(condition, dict):
            field = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')

            user_value = pillar_data.get(field, None)

            if user_value is None:
                for other_pillar, data in user_data.items():

                    if isinstance(data, dict):
                        user_value = data.get(field, None)
                        if user_value is not None:
                            break

            if user_value is not None:
                result = evaluate_condition(user_value, operator, value)
                results.append(result)
            else:
                results.append(False)

    if logic == 'and':
        overall_result = all(results)
    elif logic == 'or':
        overall_result = any(results)
    else:
        overall_result = False

    return overall_result


def evaluate_condition(user_value, operator, condition_value):
    if user_value is None:
        return False
    try:
        if operator == '>':
            return user_value > condition_value
        elif operator == '>=':
            return user_value >= condition_value
        elif operator == '<':
            return user_value < condition_value
        elif operator == '<=':
            return user_value <= condition_value
        elif operator == '==':
            return user_value == condition_value
        elif operator == '!=':
            return user_value != condition_value
        elif operator == 'includes':
            if isinstance(user_value, list):
                return condition_value in user_value
            else:
                return condition_value in str(user_value)
        else:
            return False
    except TypeError as e:
        return False


def check_dynamic_field(attributes, field):
    """Retrieve the value of a dynamic field (like tags.tag)."""
    if attributes is None:
        return None

    fields = field.split('.')

    for f in fields:
        if isinstance(attributes, list):
            attributes = [item.get(f) for item in attributes if isinstance(item, dict)]
        else:
            attributes = attributes.get(f)

        if attributes is None:
            return None

    return attributes


def evaluate_rule(rule, pillar_data, user_data):
    conditions = rule.get('conditions')
    if not conditions:
        condition = rule.get('condition')
        if condition:
            conditions = {'rules': [condition], 'logic': 'and'}
    if conditions:
        logic = conditions.get('logic', 'and')
        rules = conditions.get('rules', [])
        return evaluate_conditions(rules, logic, pillar_data, user_data)
    return False

input_static_template = {
    "accountid": None,
    "daily_time": None,
    "basics": {
        "Was ist deine Körpergröße (in cm)?": None,
        "Wie viel wiegst du (in kg)?": None,
        "Leidest Du unter einem oder mehreren der folgenden Symptome?": None,
        "Geburtsjahr": None,
        "Rauchst du?": None,
        "Hast oder hattest du schon einmal psychische Probleme?": None
    },
    "MOVEMENT": {
        "Wie schätzt du deine Beweglichkeit ein?": None,
        "Wie aktiv bist du im Alltag?": None,
        "Wie oft in der Woche treibst du Sport?": None,
        "Welchen Schwerpunkt haben die Sportarten, die du betreibst?": None
    },
    "NUTRITION": {
        "Welcher Ernährungsstil trifft bei dir am ehesten zu?": None,
        "Wie viel zuckerhaltige Produkte nimmst du zu dir?": None,
        "Wie viel Gemüse nimmst du pro Tag zu dir?": None,
        "Wie viel Obst nimmst du pro Tag zu dir?": None,
        "Wie häufig nimmst du Fertiggerichte zu dir?": None,
        "Wie viel Vollkorn nimmst du zu dir?": None,
        "Praktizierst du Intervallfasten und auf welche Art?": None,
        "Wie viele Gläser Flüssigkeit (200ml) nimmst du ca. täglich zu dir?": None,
        "Wie viel Alkohol trinkst du in der Woche?": None
    },
    "SLEEP": {
        "Wie ist deine Schlafqualität?": None,
        "Wie viele Stunden schläfst du im Durchschnitt pro Nacht?": None,
        "Fühlst du dich tagsüber müde?": None,
        "Wie viel Zeit verbringst du morgens draußen?": None,
        "Wie viel Zeit verbringst du abends draußen?": None,
        "Welche Schlafprobleme hast du?": None
    },
    "SOCIAL_ENGAGEMENT": {
        "Wie oft unternimmst du etwas mit anderen Menschen?": None,
        "Hast du gute Freunde?": None,
        "Bist du sozial engagiert?": None,
        "Fühlst du dich einsam?": None
    },
    "STRESS": {
        "Leidest du aktuell unter Stress?": None,
        "Welche der folgenden Stresssituationen trifft momentan auf dich zu?": None,
        "Welche der folgenden Stresssymptome hast du in den letzten 6 Monaten beobachtet?": None,
        "Ich versuche, die positive Seite von Stress und Druck zu sehen.": None,
        "Ich tue alles, damit Stress erst gar nicht entsteht.": None,
        "Wenn ich unter Druck gerate, habe ich Menschen, die mir helfen.": None,
        "Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.": None
    },
    "GRATITUDE": {
        "Ich habe so viel im Leben, wofür ich dankbar sein kann.": None,
        "Wenn ich alles auflisten müsste, wofür ich dankbar bin, wäre es eine sehr lange Liste.": None,
        "Wenn ich die Welt betrachte, sehe ich nicht viel, wofür ich dankbar sein könnte.": None,
        "Ich bin vielen verschiedenen Menschen dankbar.": None,
        "Je älter ich werde, desto mehr schätze ich die Menschen, Ereignisse und Situationen, die Teil meiner Lebensgeschichte waren.": None,
        "Es können lange Zeiträume vergehen, bevor ich etwas oder jemandem dankbar bin.": None
    },
    "COGNITIVE_ENHANCEMENT": {
        "Wie würdest du deine Vergesslichkeit einstufen?": None,
        "Wie gut ist dein Konzentrationsvermögen?": None,
        "Wie viel Zeit am Tag verbringst du im Büro/Ausbildung vor dem Bildschirm?": None,
        "Wie viel Zeit am Tag verbringst du in der Freizeit vor dem Bildschirm?": None,
        "Welche Zahl gehört unter die letzte Abbildung?": None,
        "Ergänze die Zahlenreihenfolge 3,6,18,21,?": None,
        "Welche Form kommt an die Stelle vom ?": None,
        "Quark : Milch / Brot : ?": None
    },
    "fasting_breakfast": None,
    "fasting_lunch": None,
    "fasting_dinner": None,
    "SCORES": {
        "MOVEMENT": None,
        "NUTRITION": None,
        "SLEEP": None,
        "SOCIAL_ENGAGEMENT": None,
        "STRESS": None,
        "GRATITUDE": None,
        "COGNITIVE_ENHANCEMENT": None,
        "Total Score": None
    }
}

def set_value(template, key, answers, default=None, log_missing=True):
    """
    Helper function to safely set values in the template from the answers.
    Logs a warning if the value is missing and log_missing is True.
    """
    key = key.strip()
    value = answers.get(key, default)
    if value is None and log_missing:
        print(f"Missing '{key}' in answers.")
    template[key] = value

def map_answers(answers, scores):
    """
    Populate the static template with answers and scores using helper functions.
    """
    set_value(input_static_template, 'accountid', answers)
    set_value(input_static_template, 'daily_time', answers,
              '*Vielen Dank!*\nWir erstellen nun deine erste individuelle Routine. Dazu müssen wir nur noch wissen, wie viel Zeit du täglich für deine langfristige Gesundheit investieren kannst.', 0)

    basics_keys = [
        ('Was ist deine Körpergröße (in cm)?', None),
        ('Wie viel wiegst du (in kg)?', None),
        ('Leidest Du unter einem oder mehreren der folgenden Symptome?', None),
        ('Geburtsjahr', None),
        ('Rauchst du?', None),
        ('Hast oder hattest du schon einmal psychische Probleme?', None)
    ]
    for key, default in basics_keys:
        set_value(input_static_template['basics'], key, answers, default)

    movement_keys = [
        ('Wie schätzt du deine Beweglichkeit ein?', None),
        ('Wie aktiv bist du im Alltag?', None),
        ('Wie oft in der Woche treibst du Sport?', None),
        ('Welchen Schwerpunkt haben die Sportarten, die du betreibst?', None)
    ]
    for key, default in movement_keys:
        set_value(input_static_template['MOVEMENT'], key, answers, default)

    nutrition_keys = [
        ('Welcher Ernährungsstil trifft bei dir am ehesten zu?', None),
        ('Wie viel zuckerhaltige Produkte nimmst du zu dir?', None),
        ('Wie viel Gemüse nimmst du pro Tag zu dir?', None),
        ('Wie viel Obst nimmst du pro Tag zu dir?', None),
        ('Wie häufig nimmst du Fertiggerichte zu dir?', None),
        ('Wie viel Vollkorn nimmst du zu dir?', None),
        ('Praktizierst du Intervallfasten und auf welche Art?', None),
        ('Wie viele Gläser Flüssigkeit (200ml) nimmst du ca. täglich zu dir?', None),
        ('Wie viel Alkohol trinkst du in der Woche?', None)
    ]
    for key, default in nutrition_keys:
        set_value(input_static_template['NUTRITION'], key, answers, default)

    sleep_keys = [
        ('Wie ist deine Schlafqualität?', None),
        ('Wie viele Stunden schläfst du im Durchschnitt pro Nacht?', None),
        ('Fühlst du dich tagsüber müde?', None),
        ('Wie viel Zeit verbringst du morgens draußen?', None),
        ('Wie viel Zeit verbringst du abends draußen?', None),
        ('Welche Schlafprobleme hast du?', None)
    ]
    for key, default in sleep_keys:
        set_value(input_static_template['SLEEP'], key, answers, default)

    social_engagement_keys = [
        ('Wie oft unternimmst du etwas mit anderen Menschen?', None),
        ('Hast du gute Freunde?', None),
        ('Bist du sozial engagiert?', None),
        ('Fühlst du dich einsam?', None)
    ]
    for key, default in social_engagement_keys:
        set_value(input_static_template['SOCIAL_ENGAGEMENT'], key, answers, default)

    stress_keys = [
        ('Leidest du aktuell unter Stress?', None),
        ('Welche der folgenden Stresssituationen trifft momentan auf dich zu?', None),
        ('Welche der folgenden Stresssymptome hast du in den letzten 6 Monaten beobachtet?', None),
        ('Ich versuche, die positive Seite von Stress und Druck zu sehen.', None),
        ('Ich tue alles, damit Stress erst gar nicht entsteht.', None),
        ('Wenn ich unter Druck gerate, habe ich Menschen, die mir helfen.', None),
        ('Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.', None)
    ]
    for key, default in stress_keys:
        set_value(input_static_template['STRESS'], key, answers, default)

    gratitude_keys = [
        ('Ich habe so viel im Leben, wofür ich dankbar sein kann.', None),
        ('Wenn ich alles auflisten müsste, wofür ich dankbar bin, wäre es eine sehr lange Liste.', None),
        ('Wenn ich die Welt betrachte, sehe ich nicht viel, wofür ich dankbar sein könnte.', None),
        ('Ich bin vielen verschiedenen Menschen dankbar.', None),
        ('Je älter ich werde, desto mehr schätze ich die Menschen, Ereignisse und Situationen, die Teil meiner Lebensgeschichte waren.', None),
        ('Es können lange Zeiträume vergehen, bevor ich etwas oder jemandem dankbar bin.', None)
    ]
    for key, default in gratitude_keys:
        set_value(input_static_template['GRATITUDE'], key, answers, default)

    cognitive_enhancement_keys = [
        ('Wie würdest du deine Vergesslichkeit einstufen?', None),
        ('Wie gut ist dein Konzentrationsvermögen?', None),
        ('Wie viel Zeit am Tag verbringst du im Büro/Ausbildung vor dem Bildschirm?', None),
        ('Wie viel Zeit am Tag verbringst du in der Freizeit vor dem Bildschirm?', None),
        ('Welche Zahl gehört unter die letzte Abbildung?', None),
        ('Ergänze die Zahlenreihenfolge 3,6,18,21,?', None),
        ('Welche Form kommt an die Stelle vom ?', None),
        ('Quark : Milch / Brot : ?', None)
    ]
    for key, default in cognitive_enhancement_keys:
        set_value(input_static_template['COGNITIVE_ENHANCEMENT'], key, answers, default)

    set_value(input_static_template, 'fasting_breakfast', answers)
    set_value(input_static_template, 'fasting_lunch', answers)
    set_value(input_static_template, 'fasting_dinner', answers)

    scores_keys = [
        'MOVEMENT', 'NUTRITION', 'SLEEP', 'SOCIAL_ENGAGEMENT', 'STRESS', 'GRATITUDE', 'COGNITIVE_ENHANCEMENT', 'Total Score'
    ]
    for key in scores_keys:
        set_value(input_static_template['SCORES'], key, scores)

    output_json = json.dumps(input_static_template, ensure_ascii=False, indent=2)
    print(output_json)
    return output_json


def main():

    field_mapping = get_field_mapping()
    responses = get_responses()

    if not (responses and field_mapping):
        logger.error("No responses or field mapping available.")
        return "No responses or field mapping available.", 400

    answers = process_latest_response(responses, field_mapping)
    if not answers:
        logger.error("No answers found in the latest response.")
        return "No answers found in the latest response.", 400

    integrated_data = integrate_answers(answers)

    assessment = HealthAssessment(
        integrated_data.get('exercise', 0),
        integrated_data.get('nutrition', 0),
        integrated_data.get('sleep', 0),
        integrated_data.get('social_connections', 0),
        integrated_data.get('stress_management', 0),
        integrated_data.get('gratitude', 0),
        integrated_data.get('cognition', 0),
    )

    scores = {
        "MOVEMENT": float(assessment.exercise_assessment.report()),
        "NUTRITION": float(assessment.nutrition_assessment.report()),
        "SLEEP": float(assessment.sleep_assessment.report()),
        "SOCIAL_ENGAGEMENT": float(assessment.social_connections_assessment.report()),
        "STRESS": float(assessment.stress_management_assessment.report()),
        "GRATITUDE": float(assessment.gratitude_assessment.report()),
        "COGNITIVE_ENHANCEMENT": float(assessment.cognition_assessment.report()),
    }
    total_score = float(assessment.calculate_total_score())
    scores["Total Score"] = total_score

    output_json = map_answers(answers, scores)
    user_data = json.loads(output_json)

    account_id = answers.get('accountid', None)
    daily_time = answers.get(
        '*Vielen Dank!*\nWir erstellen nun deine erste individuelle Routine. Dazu müssen wir nur noch wissen, wie viel Zeit du täglich für deine langfristige Gesundheit investieren kannst.',
        0
    )

    print('account_id',account_id)
    basics = user_data.get('basics', {})
    weight = basics.get('Wie viel wiegst du (in kg)?')
    height_cm = basics.get('Was ist deine Körpergröße (in cm)?')
    height_m = height_cm / 100 if isinstance(height_cm, (int, float)) else None
    if weight and height_m:
        try:
            bmi = calculate_bmi(weight, height_m)
            basics['bmi'] = bmi
        except ValueError as e:
            logger.error(f"Error calculating BMI: {e}")
            return
    else:
        logger.warning("Insufficient data to calculate BMI.")
    user_data['basics'] = basics

    rules = new_load_rules()
    routines = new_load_routines()

    processed_routines = set()

    routines_with_exclusions = apply_global_exclusions(user_data, rules.get('exclusion_rules', []), routines)

    for pillar, pillar_data in user_data.items():
        if pillar not in valid_pillars:
            continue
        pillar_rules = rules.get('inclusion_rules', {}).get(pillar, [])
        routines_with_exclusions = filter_inclusions(
            pillar_data, pillar, pillar_rules, routines_with_exclusions, user_data, processed_routines
        )

    routines_with_defaults = ensure_default_fields(routines_with_exclusions)

    output_file_path = './data/routines_with_scores.json'
    try:
        with open(output_file_path, 'w') as f:
            json.dump(routines_with_defaults, f, ensure_ascii=False, indent=4)
        print(f"Routines successfully saved to {output_file_path}")
    except Exception as e:
        logger.error(f"An error occurred while saving routines: {e}")

    print("\nExcluded Rules and Actions:")
    for rule_name, action in excluded_rules:
        print(f"Rule: {rule_name}, Action: {action}")

    print("\nIncluded Rules and Actions:")
    for rule_name, action in included_rules:
        print(f"Rule: {rule_name}, Action: {action}")

    print('Health Scores: ', scores)
    return account_id, daily_time, routines_with_defaults, scores


if __name__ == '__main__':
    main()
