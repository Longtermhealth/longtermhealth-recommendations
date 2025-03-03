# rule_based_system/main_flask.py
import time
import json
import os
from flask import Flask, jsonify, request
from config import Config
from utils.strapi_api import strapi_get_action_plan
from utils.typeform_api import (
    get_responses, get_field_mapping, process_latest_response, get_last_name, trigger_followup
)
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
        old_action_plan (dict): The existing action plan retrieved from Strapi.

    Returns:
        list: A list of dictionaries. Each dictionary contains:
              - "id": The routineId.
              - "name": The routine's displayName.
              - "statistics": The list of completion statistics (if any).
    """
    old_routine_ids = set()
    try:
        old_routines = old_action_plan.get("routines", [])
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


@app.route('/')
def hello():
    return "Hello, Flask is working!"


def recalc_action_plan(data, host):
    action_plan_id = data.get('actionPlanId')
    start_date = data.get('startDate')
    period_in_days = data.get('periodInDays')

    app.logger.info("Action Plan ID: %s", action_plan_id)
    app.logger.info("Start Date: %s", start_date)
    app.logger.info("Period in Days: %s", period_in_days)

    old_action_plan = strapi_get_action_plan(action_plan_id, host)
    if old_action_plan:
        app.logger.info("Old action plan retrieved.")
        routines = old_action_plan.get('routines', [])
        if not isinstance(routines, list):
            app.logger.error("Expected 'routines' to be a list but got: %s", type(routines))
            routines = []
        app.logger.info("Found %d routines in old action plan.", len(routines))
        for routine in routines:
            routine_id = routine.get('routineId')
            display_name = routine.get('displayName')
            app.logger.info("Routine ID: %s, Display Name: %s", routine_id, display_name)


        matching_routines = print_matching_routine_details(data, old_action_plan)
        app.logger.info("Matching routine details: %s", matching_routines)
        strapi_matches = list_strapi_matches_with_original(matching_routines)
        matches = list_strapi_matches(matching_routines)
        app.logger.info("Strapi matches: %s", strapi_matches)
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

    return final_action_plan


def compute_routine_completion(routine):
    """
    For a given routine, compute:
      - scheduled: Number of scheduled instances (entries in completionStatistics).
      - completed: Sum of completionRate values (as a proxy for completion count).
      - percentage: (completed / (scheduled * max_rate)) * 100.
    If there are no statistics, returns scheduled 0 and percentage as None.
    """
    stats = routine.get("completionStatistics", [])
    if not stats:
        return {
            "scheduled": 0,
            "completed": 0,
            "percentage": None
        }

    rates = [int(stat.get("completionRate", 0)) for stat in stats]
    scheduled = len(rates)
    completed = sum(rates)
    max_rate = max(rates) if rates else 0
    max_possible = scheduled * max_rate
    percentage = (completed / max_possible * 100) if max_possible > 0 else 0
    return {
        "scheduled": scheduled,
        "completed": completed,
        "percentage": percentage
    }


def get_insights(payload):
    """
    Process the payload (the inner JSON in eventPayload) and for each routine
    in every pillar, calculate:
      - Scheduled count
      - Completed total (sum of completionRate values)
      - Completion percentage (as computed by compute_routine_completion)
    """
    insights = {}

    for pillar in payload.get("pillarCompletionStats", []):
        pillar_name = pillar.get("pillarEnum")
        routines = pillar.get("routineCompletionStats", [])
        routine_details = []

        for routine in routines:
            completion_stats = compute_routine_completion(routine)

            rates = [int(stat.get("completionRate", 0)) for stat in routine.get("completionStatistics", [])]
            avg_rate = sum(rates) / len(rates) if rates else None

            detail = {
                "routineId": routine.get("routineId"),
                "displayName": routine.get("displayName"),
                "scheduled": completion_stats["scheduled"],
                "completed": completion_stats["completed"],
                "completionPercentage": completion_stats["percentage"],
                "averageCompletionRate": avg_rate,
                "numStatistics": len(routine.get("completionStatistics", []))
            }
            routine_details.append(detail)

        insights[pillar_name] = {
            "numRoutines": len(routines),
            "routines": routine_details
        }

    return insights


def process_event_data(event_data):
    """
    Process the entire event data by:
      1. Parsing the outer event.
      2. Parsing the JSON string in 'eventPayload'.
      3. Extracting routine insights.
    """
    payload_str = event_data.get("eventPayload", "")
    try:
        payload = json.loads(payload_str)
    except json.JSONDecodeError as e:
        print("Error parsing eventPayload:", e)
        return None

    insights = get_insights(payload)
    return insights, payload_str


@app.route('/event', methods=['POST'])
def event():
    host = request.host
    app.logger.info("Received webhook on host: %s", host)
    data = request.get_json()
    #print("data", json.dumps(data, indent=3))
    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400

    insights, payload = process_event_data(data)
    pretty_payload = json.dumps(payload, indent=4)
    print('pretty_payload', pretty_payload)
    if insights is not None:
        print("insights", json.dumps(insights, indent=4))

    event_type = data.get('eventEnum')
    if not event_type:
        return jsonify({"error": "Missing eventEnum in payload"}), 400

    if event_type == 'RECALCULATE_ACTION_PLAN':
        result = recalc_action_plan(data, host)
        print('RECALCULATE_ACTION_PLAN')
    elif event_type == 'RENEWAL_ACTION_PLAN':
        result = webhook()
        print('RENEWAL_ACTION_PLAN')
        recalc_action_plan(data, host)
    else:
        result = {"error": f"Unhandled event type: {event_type}"}

    return jsonify(result), 200


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
    app.logger.info('Action plan processed and posted: %s', final_action_plan)
    end_time = time.perf_counter()
    elapsed = end_time - start_time
    app.logger.info(f"Total time from webhook reception to posting action plan: {elapsed:.2f} seconds")
    time.sleep(5)
    trigger_followup(host)

    return jsonify({'status': 'success'}), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
