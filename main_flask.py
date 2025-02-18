# rule_based_system/main_flask.py
import time
import json
import os
from flask import Flask, jsonify, request
from config import Config
from utils.strapi_api import strapi_get_action_plan
from utils.typeform_api import get_responses, get_field_mapping, process_latest_response, get_last_name, \
    trigger_followup
from utils.clickup_api import create_clickup_task
from utils.data_processing import integrate_answers
from assessments.health_assessment import HealthAssessment
from scheduling.scheduler import main as process_action_plan
import logging

CLICKUP_API_KEY = Config.CLICKUP_API_KEY
CLICKUP_LIST_ID = Config.CLICKUP_LIST_ID
SCORES_FIELD_ID = Config.SCORES_FIELD_ID
PLOT_FIELD_ID = Config.PLOT_FIELD_ID
ANSWERS_FIELD_ID = Config.ANSWERS_FIELD_ID
ROUTINES_FIELD_ID = Config.ROUTINES_FIELD_ID
TYPEFORM_API_KEY = Config.TYPEFORM_API_KEY
FORM_ID = Config.FORM_ID

LINK_SUMMARY_TITLE_FIELD_ID = Config.LINK_SUMMARY_TITLE_FIELD_ID
LINK_SUMMARY_SUMMARY_FIELD_ID = Config.LINK_SUMMARY_SUMMARY_FIELD_ID
LINK_SUMMARY_OPENAI_API_KEY = Config.LINK_SUMMARY_OPENAI_API_KEY

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)


def print_matching_routine_details(new_data, old_action_plan):
    """
    Extracts routines from the new data that are also found in the old action plan,
    then prints and returns a list of dictionaries with each routine's id, name,
    and completion statistics.

    Parameters:
        new_data (dict): The incoming payload that includes 'pillarCompletionStats'
                         with routine details.
        old_action_plan (dict)

    Returns:
        list: A list of dictionaries. Each dictionary contains:
              - "id": The routineId.
              - "name": The routine's displayName.
              - "statistics": The list of completion statistics (if any).
    """
    old_routine_ids = set()
    try:
        old_routines = old_action_plan["data"]["attributes"]["routines"]
        for routine in old_routines:
            rid = routine.get('routineId')
            if rid is not None:
                old_routine_ids.add(rid)
    except (KeyError, TypeError) as e:
        print("Error extracting routine IDs from old action plan:", e)
        return []

    matching_routines = []

    pillar_stats_list = new_data.get('pillarCompletionStats', [])
    for pillar in pillar_stats_list:
        routine_stats_list = pillar.get('routineCompletionStats', [])
        for routine in routine_stats_list:
            rid = routine.get('routineId')
            if rid in old_routine_ids:
                routine_details = {
                    "id": rid,
                    "name": routine.get('displayName'),
                    "statistics": routine.get('completionStatistics', [])
                }
                matching_routines.append(routine_details)

    print("Matching routines (found in both new data and old action plan):")
    for routine in matching_routines:
        print("ID: {id}, Name: {name}, Statistics: {statistics}".format(**routine))

    return matching_routines
def list_strapi_matches(matching_routines, strapi_routines_file="./data/strapi_all_routines.json"):
    """
    For each routine in `matching_routines`, search in the provided Strapi routines file
    for an entry with a matching `cleanedName` attribute. For every match found, print
    and collect its id, name, and order.

    Parameters:
        matching_routines (list): A list of dictionaries representing routines.
                                  Each dictionary is expected to have a "cleanedName" key.
        strapi_routines_file (str): Path to the JSON file containing all Strapi routines.

    Returns:
        list: A list of dictionaries. Each dictionary represents a matched routine with keys:
              "id", "name", and "order".
    """
    if not os.path.exists(strapi_routines_file):
        print("Strapi routines file not found:", strapi_routines_file)
        return []

    try:
        with open(strapi_routines_file, "r", encoding="utf-8") as f:
            strapi_routines = json.load(f)
    except json.JSONDecodeError as e:
        print("Error decoding JSON from", strapi_routines_file, ":", e)
        return []

    search_cleaned_names = set()
    for routine in matching_routines:
        cleaned = routine.get("cleanedName")
        if cleaned:
            search_cleaned_names.add(cleaned)
        else:
            display = routine.get("name") or routine.get("displayName")
            if display:
                search_cleaned_names.add(display)

    matches = []
    for entry in strapi_routines:
        attributes = entry.get("attributes", {})
        strapi_cleaned_name = attributes.get("cleanedName")
        if strapi_cleaned_name in search_cleaned_names:
            match = {
                "id": entry.get("id"),
                "name": attributes.get("name"),
                "order": attributes.get("order")
            }
            matches.append(match)
            print("Found match - ID: {id}, Name: {name}, Order: {order}".format(**match))

    return matches

def list_strapi_matches_with_original(matching_routines, strapi_routines_file="./data/strapi_all_routines.json"):
    """
    For each routine in `matching_routines`, search the Strapi routines file for an entry
    with a matching `cleanedName` attribute. For every match found, print and collect its id,
    name, order, and the original routine object.

    Parameters:
        matching_routines (list): A list of dictionaries representing routines.
                                  Each dictionary is expected to have a "cleanedName" key.
        strapi_routines_file (str): Path to the JSON file containing all Strapi routines.

    Returns:
        list: A list of dictionaries. Each dictionary represents a matched routine with keys:
              "id", "name", "order", and "original" (the full JSON object from Strapi).
    """
    if not os.path.exists(strapi_routines_file):
        print("Strapi routines file not found:", strapi_routines_file)
        return []

    try:
        with open(strapi_routines_file, "r", encoding="utf-8") as f:
            strapi_routines = json.load(f)
    except json.JSONDecodeError as e:
        print("Error decoding JSON from", strapi_routines_file, ":", e)
        return []

    search_cleaned_names = set()
    for routine in matching_routines:
        cleaned = routine.get("cleanedName")
        if cleaned:
            search_cleaned_names.add(cleaned)
        else:
            display = routine.get("name") or routine.get("displayName")
            if display:
                search_cleaned_names.add(display)

    matches = []
    for entry in strapi_routines:
        attributes = entry.get("attributes", {})
        strapi_cleaned_name = attributes.get("cleanedName")
        if strapi_cleaned_name in search_cleaned_names:
            match = {
                "id": entry.get("id"),
                "name": attributes.get("name"),
                "order": attributes.get("order"),
                "original": entry
            }
            matches.append(match)
            print("Found match - ID: {id}, Name: {name}, Order: {order}".format(**match))

    return matches



def main():
    field_mapping = get_field_mapping()
    responses = get_responses()

@app.route('/')
def hello():
    return "Hello, Flask is working!"

@app.route('/webhook-recalculate-action-plan', methods=['POST'])
def recalc_action_plan():
    host = request.host
    print(f"Received webhook on host: {host}")
    data = request.get_json()

    action_plan_id = data.get('actionPlanId')
    start_date = data.get('startDate')
    period_in_days = data.get('periodInDays')

    app.logger.info("Action Plan ID: %s", action_plan_id)
    app.logger.info("Start Date: %s", start_date)
    app.logger.info("Period in Days: %s", period_in_days)

    # Retrieve the old action plan from your backend.
    old_action_plan = strapi_get_action_plan(action_plan_id, host)
    if old_action_plan:
        app.logger.info("Old action plan retrieved.")
        #print(old_action_plan)

        matching_routines = print_matching_routine_details(data, old_action_plan)
        app.logger.info("Matching routine details: %s", matching_routines)
        strapi_matches = list_strapi_matches_with_original(matching_routines)
        matches = list_strapi_matches(matching_routines)
        print(strapi_matches)
    else:
        app.logger.error("No old action plan found for actionPlanId: %s", action_plan_id)

    pillar_stats_list = data.get('pillarCompletionStats', [])
    for pillar in pillar_stats_list:
        pillar_enum = pillar.get('pillarEnum')
        app.logger.info("Pillar Enum: %s", pillar_enum)

        routine_stats_list = pillar.get('routineCompletionStats', [])
        for routine in routine_stats_list:
            routine_id = routine.get('routineId')
            display_name = routine.get('displayName')
            app.logger.info("Routine ID: %s, Display Name: %s", routine_id, display_name)

            completion_stats = routine.get('completionStatistics', [])
            for stat in completion_stats:
                completion_rate = stat.get('completionRate')
                rate_period_unit = stat.get('completionRatePeriodUnit')
                period_sequence_no = stat.get('periodSequenceNo')
                completion_unit = stat.get('completionUnit')

                completion_target = stat.get('completionTargetTotal', stat.get('completionTarget'))
                completed_value = stat.get('completedValueTotal', stat.get('completedValue'))

                app.logger.info(
                    "Stat - Completion Rate: %s, Period Unit: %s, Sequence: %s, Unit: %s, Target: %s, Completed: %s",
                    completion_rate, rate_period_unit, period_sequence_no, completion_unit,
                    completion_target, completed_value
                )

                try:
                    completion_rate_float = float(completion_rate)
                    period_sequence_no_int = int(period_sequence_no)
                except (ValueError, TypeError) as e:
                    app.logger.error("Error converting values: %s", e)

    final_action_plan = {
        "actionPlanId": action_plan_id
    }

    return jsonify({'action_plan': final_action_plan}), 200


@app.route('/webhook', methods=['POST'])
def webhook():
    host = request.host
    print(f"Received webhook on host: {host}")
    time.sleep(3)
    if request.headers.get("X-Webhook-Followup") == "true":
        app.logger.info("Follow-up webhook already received: %s")
        process_action_plan(host)
        return jsonify({"status": "follow-up processed"}), 200
    else:
        app.logger.info('Original webhook received: %s')

    start_time = time.perf_counter()
    app.logger.info('Start processing action plan')
    final_action_plan = process_action_plan(host)
    app.logger.info('Action plan processed and posted: %s')
    end_time = time.perf_counter()
    elapsed = end_time - start_time
    app.logger.info(f"Total time from webhook reception to posting action plan: {elapsed:.2f} seconds")
    time.sleep(5)
    trigger_followup(host)

    return jsonify({'status': 'success'}), 200





if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)