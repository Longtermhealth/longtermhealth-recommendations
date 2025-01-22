import json
import logging
from typing import Dict, Any, List

from assessments.health_assessment import HealthAssessment
from rules.rule_service import evaluate_rule
from utils.data_processing import integrate_answers
from utils.strapi_api import strapi_get_all_routines
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
    return load_json_data('../data/strapi_all_routines.json')


def new_load_rules() -> Dict[str, Any]:
    """Load new rules from a JSON file."""
    return load_json_data('../data/rules.json')

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
                        if routine.get('attributes', {}).get('rule_status') == 'excluded':
                            continue

                        routine_id = routine['id']
                        routine_pillar = routine['attributes']['pillar']['pillarEnum']

                        if routine_pillar == pillar_name:
                            routine_field_value = check_dynamic_field(routine['attributes'], action_field)

                            if (isinstance(routine_field_value, list) and action_value in routine_field_value) \
                               or routine_field_value == action_value:
                                routine_scores[routine_id] += weight
                                explanation = (
                                    f"matched the rule '{rule.get('name', 'Unnamed Rule')}' with score {weight} "
                                    f"due to {action_field}: {action_value}"
                                )
                                routine_explanations[routine_id].append(explanation)
                                included_rules.add((rule.get('name', 'Unnamed Rule'), f"{action_field}: {action_value}"))

                                routine['rule_status'] = 'included'
                                routine['score_rules'] = routine_scores[routine_id]
                                combined_explanations = " | ".join(routine_explanations[routine_id])
                                routine["score_rules_explanation"] = (
                                    f"Routine '{routine['attributes'].get('name', 'Unnamed Routine')}' recommended under pillar '{pillar_name}' "
                                    f"with cumulative score {routine_scores[routine_id]} because it {combined_explanations}"
                                )

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
        "Wie oft in der Woche treibst du eine Cardio-Sportart?": None,
        "Wie schätzt du deine Kraft ein?": None
    },
    "NUTRITION": {
        "Welcher Ernährungsstil trifft bei dir am ehesten zu?": None,
        "Wie viel zuckerhaltige Produkte nimmst du zu dir?": None,
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
        "Bist du sozial engagiert?": None,
        "Fühlst du dich einsam?": None
    },
    "STRESS": {
        "Leidest du aktuell unter Stress?": None,
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
        "Nimmst du dir im Alltag Zeit, noch neue Dinge/Fähigkeiten zu erlernen?": None,
    },
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
              'Wie viel Zeit möchtest du am Tag ungefähr in deine Gesundheit investieren?', '')

    basics_keys = [
        ('Was ist deine Körpergröße (in cm)?', None),
        ('Wie viel wiegst du (in kg)?', None),
        ('Geburtsjahr', None),
        ('Rauchst du?', None)
    ]
    for key, default in basics_keys:
        set_value(input_static_template['basics'], key, answers, default)

    movement_keys = [
        ('Wie schätzt du deine Beweglichkeit ein?', None),
        ('Wie aktiv bist du im Alltag?', None),
        ('Wie oft in der Woche treibst du eine Cardio-Sportart?', None),
        ('Wie schätzt du deine Kraft ein?', None)
    ]
    for key, default in movement_keys:
        set_value(input_static_template['MOVEMENT'], key, answers, default)

    nutrition_keys = [
        ('Welcher Ernährungsstil trifft bei dir am ehesten zu?', None),
        ('Wie viel zuckerhaltige Produkte nimmst du zu dir?', None),
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
        ('Bist du sozial engagiert?', None),
        ('Fühlst du dich einsam?', None)
    ]
    for key, default in social_engagement_keys:
        set_value(input_static_template['SOCIAL_ENGAGEMENT'], key, answers, default)

    stress_keys = [
        ('Leidest du aktuell unter Stress?', None),
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
        ('Nimmst du dir im Alltag Zeit, noch neue Dinge/Fähigkeiten zu erlernen?', None)
    ]
    for key, default in cognitive_enhancement_keys:
        set_value(input_static_template['COGNITIVE_ENHANCEMENT'], key, answers, default)


    scores_keys = [
        'MOVEMENT', 'NUTRITION', 'SLEEP', 'SOCIAL_ENGAGEMENT', 'STRESS', 'GRATITUDE', 'COGNITIVE_ENHANCEMENT', 'Total Score'
    ]
    for key in scores_keys:
        set_value(input_static_template['SCORES'], key, scores)

    output_json = json.dumps(input_static_template, ensure_ascii=False, indent=2)
    print(output_json)
    return output_json

def get_order(score: float) -> int:
    if score < 0:
        raise ValueError("Score cannot be negative.")
    elif score <= 20:
        return 1
    elif score <= 40:
        return 2
    elif score <= 60:
        return 3
    elif score <= 80:
        return 4
    else:
        return 5

def set_fasten_order(answer: str) -> int:
    answer_to_order = {
        "Nein": 1,
        "16:8 (täglich 16 Stunden fasten)": 4,
        "14:10 (täglich 14 Stunden fasten)": 3,
        "12:12 (täglich 12 Stunden fasten)": 2,
        "5:2 (an 2 Tagen der Woche nur Einnahme von 500 (Frauen) bzw. 600 (Männer) Kalorien.)": 4,
        "Eat Stop Eat (1-2 x pro Woche für 24 Stunden fasten)": 3,
        "Alternierendes Fasten (jeden zweiten Tag fasten oder stark reduzierte Kalorienaufnahme)": 5,
        "Spontanes Auslassen einer Mahlzeit (regelmäßiges Auslassen einzelner Mahlzeiten)": 3,
        "Sonstiges": None
    }
    return answer_to_order.get(answer, None)


def parse_package_key(pkg_key):
    """
    Returns the full package key as packageName.

    :param pkg_key: The package key string (e.g., "Sport, 1, kurz").
    :return: The full packageKey as packageName.
    """
    package_name = pkg_key.strip() if pkg_key else pkg_key
    return package_name

def load_packages(file_path):
    try:
        with open(file_path, "r", encoding='utf-8') as file:
            data = json.load(file)
            logger.debug(f"Loaded packages data from '{file_path}'.")
            return data
    except Exception as e:
        logger.error(f"Failed to load {file_path}: {e}")
        return {}

def find_package_with_fallback(packages_data, pillar, subcategory, order=None):
    """
    Find a package based on pillar, subcategory, and order.
    If no exact match is found, fallback to the closest lower order.
    :param packages_data: Loaded JSON data.
    :param pillar: The pillar name (e.g., "MOVEMENT").
    :param subcategory: The subcategory name (e.g., "MOVEMENT BASICS").
    :param order: The package order (e.g., 1).
    :return: packageName and the package dictionary, or (None, None).
    """
    try:
        logger.debug(
            f"Searching for Pillar: '{pillar}', Subcategory: '{subcategory}', Order: '{order}'")
        subcategories = packages_data.get("packages", {}).get("pillars", {}).get(pillar, {})
        if not subcategories:
            available_subcats = list(packages_data.get("packages", {}).get("pillars", {}).get(pillar, {}).keys())
            logger.debug(
                f"No subcategories found for pillar '{pillar}'. Available subcategories: {available_subcats}")
            return (None, None)
        subcat = subcategories.get(subcategory, {})
        if not subcat:
            available_subcats = list(subcategories.keys())
            logger.debug(
                f"No subcategory '{subcategory}' found under pillar '{pillar}'. Available subcategories: {available_subcats}")
            return (None, None)

        packages = []
        for pkg_key, pkg in subcat.items():
            try:
                pkg_order = int(pkg.get("packageOrder"))
            except (TypeError, ValueError):
                logger.warning(
                    f"Invalid packageOrder '{pkg.get('packageOrder')}' for package '{pkg_key}'. Skipping.")
                continue
            packages.append((pkg_order, pkg_key, pkg))
        if not packages:
            logger.debug(f"No valid packages found under pillar '{pillar}' and subcategory '{subcategory}'.")
            return (None, None)

        packages.sort(key=lambda x: x[0])

        for pkg_order, pkg_key, pkg in packages:
            if order and pkg_order == order:
                package_name = parse_package_key(pkg_key)
                logger.debug(
                    f"Exact match found: '{pkg_key}' with Order='{pkg_order}'")
                return (package_name, pkg)

        available_orders = sorted([pkg_order for pkg_order, _, _ in packages])
        fallback_order = None
        for o in reversed(available_orders):
            if order and o <= order:
                fallback_order = o
                break

        if fallback_order:
            for pkg_order, pkg_key, pkg in packages:
                if pkg_order == fallback_order:
                    package_name = parse_package_key(pkg_key)
                    logger.debug(
                        f"Fallback match found: '{pkg_key}' with Order='{pkg_order}'")
                    return (package_name, pkg)

        logger.debug(
            f"No package found with Order <= {order} for Pillar '{pillar}' and Subcategory '{subcategory}'.")
    except Exception as e:
        logger.error(f"Error finding package in {pillar} - {subcategory}: {e}")
    return (None, None)


def main():

    field_mapping = get_field_mapping()
    responses = get_responses()

    if not (responses and field_mapping):
        logger.error("No responses or field mapping available.")
        return "No responses or field mapping available.", 400

    answers = process_latest_response(responses, field_mapping)
    gender = answers.get('Biologisches Geschlecht:', None)
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
        "NUTRITION": float(assessment.nutrition_assessment.report()),
        "MOVEMENT": float(assessment.exercise_assessment.report()),
        "GRATITUDE": float(assessment.gratitude_assessment.report()),
        "SLEEP": float(assessment.sleep_assessment.report()),
        "SOCIAL_ENGAGEMENT": float(assessment.social_connections_assessment.report()),
        "STRESS": float(assessment.stress_management_assessment.report()),
        "COGNITIVE_ENHANCEMENT": float(assessment.cognition_assessment.report()),
    }
    total_score = float(assessment.calculate_total_score())
    scores["Total Score"] = total_score

    output_json = map_answers(answers, scores)
    user_data = json.loads(output_json)

    account_id = answers.get('accountid', None)
    daily_time = answers.get(
        'Wie viel Zeit möchtest du am Tag ungefähr in deine Gesundheit investieren?',0
    )
    if daily_time == '15-30 Minuten':
        daily_time = 30
    elif daily_time == '30-45 Minuten':
        daily_time = 45
    elif daily_time == '45-60 Minuten':
        daily_time = 60
    elif daily_time == '> 60 Minuten':
        daily_time = 90


    print('daily_time',daily_time)
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
    routines = strapi_get_all_routines()

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

    print("\nExcluded Rules and Actions:")
    for rule_name, action in excluded_rules:
        print(f"Rule: {rule_name}, Action: {action}")

    print("\nIncluded Rules and Actions:")
    for rule_name, action in included_rules:
        print(f"Rule: {rule_name}, Action: {action}")

    print('Health Scores: ', scores)


    packages_file_path = "../data/packages.json"
    packages_data = load_packages(packages_file_path)

    fasten_answer = answers.get('Praktizierst du Intervallfasten und auf welche Art?', None)
    fasten_answer = answers.get('Praktizierst du Intervallfasten und auf welche Art?', None)
    if fasten_answer and bmi >= 18:
        fasten_order = set_fasten_order(fasten_answer)
        logger.debug(f"Fasting order determined: {fasten_order}")
    else:
        fasten_order = 0
        logger.debug("Fasting not applicable based on BMI or answer.")

    score_order_list = []
    for pillar, score in scores.items():
        try:
            order = get_order(score)
            logger.debug(f"Pillar '{pillar}': Score={score}, Order={order}")
        except ValueError as e:
            logger.error(f"Error determining order for {pillar}: {e}")
            order = None
        score_order_list.append({
            "pillar": pillar,
            "score": score,
            "order": order
        })

    fasten_order = 1

    if fasten_order and fasten_order > 0:
        package_name, fasting_package = find_package_with_fallback(
            packages_data,
            pillar="NUTRITION",
            subcategory="FASTING BASICS",
            order=fasten_order
        )
        if fasting_package:
            score_order_list.append({
                "pillar": "NUTRITION",
                "score": None,
                "order": fasten_order,
                "fasting_package": package_name
            })
        else:
            logger.warning(f"No fasting package found for order {fasten_order} in 'NUTRITION > FASTING BASICS'.")

    print("Pillar Scores with Orders:")
    print(json.dumps(score_order_list, ensure_ascii=False, indent=2))

    selected_packages = []
    for entry in score_order_list:
        if entry["order"] is not None:
            pillar = entry["pillar"].upper()
            order = entry["order"]
            package = None
            package_name = None
            subcategory = None

            if pillar == "MOVEMENT":
                subcategory = "MOVEMENT BASICS SHORT"
                package_name, package = find_package_with_fallback(
                    packages_data,
                    pillar="MOVEMENT",
                    subcategory=subcategory,
                    order=order
                )
            elif pillar == "NUTRITION":
                if "fasting_package" in entry:
                    subcategory = "FASTING BASICS"
                    package_name = entry["fasting_package"]
                    _, fasting_package = find_package_with_fallback(
                        packages_data,
                        pillar="NUTRITION",
                        subcategory=subcategory,
                        order=entry["order"]
                    )
                    if fasting_package:
                        package = fasting_package
                    else:
                        package = {"packageName": package_name}
                else:
                    subcategory = "NUTRITION BASICS"
                    package_name, package = find_package_with_fallback(
                        packages_data,
                        pillar="NUTRITION",
                        subcategory=subcategory,
                        order=order
                    )
            elif pillar == "SLEEP":
                subcategory = "SLEEP BASICS"
                package_name, package = find_package_with_fallback(
                    packages_data,
                    pillar="SLEEP",
                    subcategory=subcategory,
                    order=order
                )
            elif pillar == "STRESS":
                subcategory = "STRESS BASICS"
                package_name, package = find_package_with_fallback(
                    packages_data,
                    pillar="STRESS",
                    subcategory=subcategory,
                    order=order
                )
            elif pillar == "GRATITUDE":
                subcategory = "GRATITUDE BASICS"
                package_name, package = find_package_with_fallback(
                    packages_data,
                    pillar="GRATITUDE",
                    subcategory=subcategory,
                    order=order
                )
            elif pillar == "SOCIAL_ENGAGEMENT":
                subcategory = "SOCIAL ENGAGEMENT BASICS"
                package_name, package = find_package_with_fallback(
                    packages_data,
                    pillar="SOCIAL_ENGAGEMENT",
                    subcategory=subcategory,
                    order=order
                )
            elif pillar == "COGNITIVE_ENHANCEMENT":
                subcategory = "COGNITIVE ENHANCEMENT BASICS"
                package_name, package = find_package_with_fallback(
                    packages_data,
                    pillar="COGNITIVE_ENHANCEMENT",
                    subcategory=subcategory,
                    order=order
                )
            else:
                logger.warning(f"Pillar '{pillar}' is not handled in the selection logic.")
                subcategory = "Unknown Subcategory"
                package = {
                    "packageName": "No package available",
                    "pillar": entry["pillar"]
                }
                package_name = "No package available"

            if package:
                selected_packages.append({
                    "pillar": entry["pillar"],
                    "packageName": package_name,
                    "packageTag": subcategory, 
                    "selected_package": package
                })
            else:
                logger.warning(f"No package selected for Pillar: '{entry['pillar']}' with Order: {order}")

    print("\nSelected Packages:")
    print(json.dumps(selected_packages, ensure_ascii=False, indent=2))

    return account_id, daily_time, routines_with_defaults, scores, user_data, answers, gender, selected_packages





if __name__ == '__main__':
    main()
