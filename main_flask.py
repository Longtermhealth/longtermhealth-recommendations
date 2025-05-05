# rule_based_system/main_flask.py
import time
import math
import json
import uuid
import os
from flask import Flask, jsonify, request
from config import Config
from utils.strapi_api import strapi_get_action_plan, strapi_post_action_plan, strapi_get_old_action_plan, strapi_get_health_scores
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

k = 0.025


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


def recalc_action_plan(payload, host):
    unique_id  = payload.get("actionPlanUniqueId")
    account_id = payload.get("accountId")
    app.logger.debug("recalc_action_plan: unique_id=%s account_id=%s", unique_id, account_id)
    print('unique_id',unique_id)
    print('account_id', account_id)
    print('host', host)
    if not unique_id:
        app.logger.error("Missing actionPlanUniqueId in payload")
        return {"error": "missing-action-plan-id"}
    if account_id is None:
        app.logger.error("Missing accountId in payload")
        return {"error": "missing-account-id"}

    try:
        old_plan = strapi_get_old_action_plan(unique_id, host)
    except Exception as e:
        app.logger.exception("Error fetching action plan %s: %s", unique_id, e)
        return {"error": "strapi-fetch-failed"}

    if not old_plan:
        app.logger.error("No action plan found for uniqueId: %s", unique_id)
        return {"error": "not-found"}

    routines = old_plan.get("routines", [])
    if not isinstance(routines, list):
        app.logger.error("Expected 'routines' list but got %s", type(routines))
        routines = []

    app.logger.info("Found %d routines in action plan %s", len(routines), unique_id)

    matching = print_matching_routine_details(
        new_data=payload,
        old_action_plan=old_plan
    )
    app.logger.info("Computed matching routines: %s", matching)

    strapi_matches = list_strapi_matches_with_original(matching)
    app.logger.info("Enriched Strapi matches: %s", strapi_matches)

    return {
        "actionPlanUniqueId": unique_id,
        "matches": strapi_matches
    }


def renew_action_plan(payload, host):
    unique_id  = payload.get("actionPlanUniqueId")
    account_id = payload.get("accountId")
    app.logger.debug("renew_action_plan: unique_id=%s account_id=%s", unique_id, account_id)

    if not unique_id:
        app.logger.error("Missing actionPlanUniqueId in payload")
        return {"error": "missing-action-plan-id"}

    try:
        old_plan = strapi_get_old_action_plan(unique_id, host)
    except Exception as e:
        app.logger.exception("Error fetching action plan %s: %s", unique_id, e)
        return {"error": "strapi-fetch-failed"}

    if not old_plan:
        app.logger.error("No action plan found for uniqueId: %s", unique_id)
        return {"error": "not-found"}

    new_plan = json.loads(json.dumps(old_plan))
    prev_id  = old_plan.get("actionPlanUniqueId")
    new_id   = str(uuid.uuid4())
    new_plan["attributes"]["previousActionPlanUniqueId"] = prev_id
    new_plan["attributes"]["actionPlanUniqueId"]         = new_id
    app.logger.info("Cloned plan %s → %s", prev_id, new_id)

    latest_changes = {}
    for ev in payload.get("changeLog", []):
        if (
            ev.get("eventEnum") == "ROUTINE_SCHEDULE_CHANGE"
            and ev.get("changeTarget") == "ROUTINE"
            and ev.get("eventDetails", {}).get("scheduleCategory") == "WEEKLY_ROUTINE"
        ):
            rid        = int(ev.get("targetId", 0))
            event_date = ev.get("eventDate")
            for ch in ev.get("changes", []):
                if ch.get("changedProperty") == "SCHEDULE_DAYS":
                    try:
                        days = json.loads(ch.get("newValue", "[]"))
                    except (TypeError, json.JSONDecodeError):
                        days = [int(c) for c in str(ch.get("newValue", "")) if c.isdigit()]
                    prev = latest_changes.get(rid)
                    if not prev or event_date > prev["eventDate"]:
                        latest_changes[rid] = {"scheduleDays": days, "eventDate": event_date}

    for routine in new_plan.get("routines", []):
        rid = routine.get("routineId") or routine.get("routineUniqueId")
        if rid in latest_changes:
            old_days = routine.get("scheduleDays", [])
            new_days = latest_changes[rid]["scheduleDays"]
            routine["scheduleDays"] = new_days
            app.logger.info("Routine %s scheduleDays: %s → %s", rid, old_days, new_days)
    print('old plan: ', old_plan)
    print('new plan: ', new_plan)
    if host == "lthrecommendation-dev-g2g0hmcqdtbpg8dw.germanywestcentral-01.azurewebsites.net":
        app_env = "development"
    else:
        app_env = "production"

    strapi_post_action_plan(new_plan, account_id, app_env)
    return new_plan


def compute_routine_completion(routine):
    stats = routine.get("completionStatistics", [])
    if not stats:
        return {"scheduled": 0, "completed": 0, "percentage": None}
    actual_rates = [int(stat.get("completionRate", 0)) for stat in stats]
    scheduled = len(actual_rates)
    completed = sum(actual_rates)
    unique_rates = set(actual_rates)
    if len(unique_rates) == 1:
        expected_total = unique_rates.pop() * scheduled
    else:
        expected_total = 0
        for stat in stats:
            unit = stat.get("completionRatePeriodUnit")
            try:
                seq = int(stat.get("periodSequenceNo", 0))
            except (ValueError, TypeError):
                seq = 0
            if unit == "WEEK":
                expected_total += min(seq, 4)
            elif unit == "MONTH":
                expected_total += 4
            else:
                expected_total += int(stat.get("completionRate", 0))
    percentage = (completed / expected_total * 100) if expected_total > 0 else 0
    return {"scheduled": scheduled, "completed": completed, "percentage": percentage}


def get_insights(payload):
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
        insights[pillar_name] = {"numRoutines": len(routines), "routines": routine_details}
    return insights

def process_event_data(event_data):
    """
    Process the entire event data by:
      1. Extracting eventPayload (which may be a dict or a JSON‐encoded string).
      2. Parsing it if necessary.
      3. Computing routine insights.

    Returns:
        tuple: (insights_dict, payload_dict) or (None, None) on JSON parse error.
    """
    raw_payload = event_data.get("eventPayload")

    if isinstance(raw_payload, str):
        try:
            payload = json.loads(raw_payload)
        except json.JSONDecodeError as e:
            app.logger.error(f"Invalid JSON in eventPayload: {raw_payload!r} – {e}")
            return None, None
    elif isinstance(raw_payload, dict):
        payload = raw_payload
    else:
        app.logger.error(f"Unexpected type for eventPayload: {type(raw_payload).__name__}")
        return None, None

    insights = get_insights(payload)
    return insights, payload


def compute_scheduled_by_pillar(payload):
    print("DEBUG: compute_scheduled_by_pillar called with payload keys:", list(payload.keys()))
    scheduled_by_pillar = {}
    if "pillarCompletionStats" in payload:
        print("DEBUG: detected webhook payload")
        for pillar in payload["pillarCompletionStats"]:
            pillar_enum = pillar.get("pillarEnum")
            routines = pillar.get("routineCompletionStats", [])
            print(f"DEBUG: adding {len(routines)} routines under pillar {pillar_enum}")
            scheduled_by_pillar[pillar_enum] = routines
        print("DEBUG: scheduled_by_pillar (webhook) =", scheduled_by_pillar)
        return scheduled_by_pillar
    data = payload.get("data", [])
    print("DEBUG: detected Strapi payload, data length =", len(data))
    if isinstance(data, list) and data:
        attributes = data[0].get("attributes", {})
        routines_list = attributes.get("routines", [])
        print("DEBUG: routines_list length =", len(routines_list))
    else:
        routines_list = []
        print("DEBUG: no routines_list found")
    for r in routines_list:
        pillar_enum = r.get("pillar", {}).get("pillarEnum")
        scheduled_by_pillar.setdefault(pillar_enum, []).append(r)
        #print(f"DEBUG: appended routine {r.get('routineUniqueId')} to pillar {pillar_enum}")
    #print("DEBUG: scheduled_by_pillar (Strapi) =", scheduled_by_pillar)
    return scheduled_by_pillar



def extract_pretty_completions(pretty_payload):
    """
    Extract completed counts from the pretty_payload and sum them by pillar.
    For each pillar, iterate over all routines, filter for MONTH statistics,
    and sum their completionRate values.

    Returns:
      dict: Mapping pillarEnum -> { "completed": total completions }
    """
    completions_by_pillar = {}
    for pillar_entry in pretty_payload.get("pillarCompletionStats", []):
        pillar = pillar_entry.get("pillarEnum", "UNKNOWN")
        if pillar not in completions_by_pillar:
            completions_by_pillar[pillar] = {"completed": 0}
        for routine in pillar_entry.get("routineCompletionStats", []):
            month_stats = [stat for stat in routine.get("completionStatistics", [])
                           if stat.get("completionRatePeriodUnit") == "MONTH"]
            if month_stats:
                # Get the latest month entry based on periodSequenceNo
                latest_stat = max(month_stats, key=lambda s: s.get("periodSequenceNo", 0))
                completion = latest_stat.get("completionRate", 0)
            else:
                completion = 0
            completions_by_pillar[pillar]["completed"] += completion
    return completions_by_pillar

def create_health_scores_with_structure(account_id, health_scores):
    """
    Builds the final health-scores structure (with interpretation) to post to Strapi.
    """
    print('health_scores',health_scores)
    if not isinstance(health_scores, dict) or not health_scores:
        app.logger.error(
            "Empty or invalid health_scores for account %s; returning default structure",
            account_id
        )
        return {
            "data": {
                "totalScore": 0,
                "accountId": account_id,
                "pillarScores": []
            }
        }

    score_interpretation_dict = {
        "MOVEMENT": {
            "AKTIONSBEFARF": "Es ist Zeit, mehr Bewegung in deinen Alltag zu integrieren. Kleine Schritte können einen großen Unterschied für deine Gesundheit machen!",
            "AUSBAUFÄHIG": "Deine körperliche Aktivität ist gut! Mit ein wenig mehr Bewegung kannst du deine Fitness auf das nächste Level heben.",
            "OPTIMAL": "Fantastische Leistung! Deine regelmäßige Bewegung stärkt deine Gesundheit optimal. Weiter so!"
        },
        "NUTRITION": {
            "AKTIONSBEFARF": "Achte mehr auf eine ausgewogene Ernährung. Gesunde Essgewohnheiten geben dir Energie und Wohlbefinden.",
            "AUSBAUFÄHIG": "Deine Ernährung ist auf einem guten Weg! Mit kleinen Anpassungen kannst du deine Nährstoffzufuhr weiter optimieren.",
            "OPTIMAL": "Exzellente Ernährungsgewohnheiten! Du versorgst deinen Körper optimal mit wichtigen Nährstoffen. Weiter so!"
        },
        "SLEEP": {
            "AKTIONSBEFARF": "Verbessere deine Schlafgewohnheiten für mehr Energie und bessere Gesundheit. Guter Schlaf ist essenziell!",
            "AUSBAUFÄHIG": "Dein Schlaf ist gut! Ein paar Änderungen können dir helfen, noch erholsamer zu schlafen.",
            "OPTIMAL": "Ausgezeichneter Schlaf! Du sorgst für optimale Erholung und Vitalität. Weiter so!"
        },
        "SOCIAL_ENGAGEMENT": {
            "AKTIONSBEFARF": "Pflege deine sozialen Beziehungen. Verbindungen zu anderen sind wichtig für dein emotionales Wohlbefinden.",
            "AUSBAUFÄHIG": "Deine sozialen Beziehungen sind gut! Mit ein wenig mehr Engagement kannst du deine Verbindungen weiter vertiefen.",
            "OPTIMAL": "Starke und erfüllende soziale Beziehungen! Du pflegst wertvolle Verbindungen, die dein Leben bereichern. Weiter so!"
        },
        "STRESS": {
            "AKTIONSBEFARF": "Es ist wichtig, Wege zu finden, um deinen Stress besser zu bewältigen. Kleine Pausen und Entspannungstechniken können helfen.",
            "AUSBAUFÄHIG": "Dein Umgang mit Stress ist gut! Mit weiteren Strategien kannst du deine Stressresistenz weiter stärken.",
            "OPTIMAL": "Du meisterst Stress hervorragend! Deine effektiven Bewältigungsstrategien tragen zu deinem Wohlbefinden bei. Weiter so!"
        },
        "GRATITUDE": {
            "AKTIONSBEFARF": "Nimm dir Zeit, die positiven Dinge im Leben zu schätzen. Dankbarkeit kann dein Wohlbefinden erheblich steigern.",
            "AUSBAUFÄHIG": "Du zeigst bereits Dankbarkeit! Mit kleinen Ergänzungen kannst du deine positive Einstellung noch weiter ausbauen.",
            "OPTIMAL": "Eine wunderbare Haltung der Dankbarkeit! Deine positive Sicht bereichert dein Leben und das deiner Mitmenschen. Weiter so!"
        },
        "COGNITIVE_ENHANCEMENT": {
            "AKTIONSBEFARF": "Fordere deinen Geist regelmäßig heraus. Neue Lernmöglichkeiten können deine geistige Fitness verbessern.",
            "AUSBAUFÄHIG": "Deine kognitive Förderung ist gut! Mit zusätzlichen Aktivitäten kannst du deine geistige Leistungsfähigkeit weiter steigern.",
            "OPTIMAL": "Hervorragende geistige Fitness! Du hältst deinen Verstand aktiv und stark. Weiter so!"
        }
    }

    def get_score_details(pillar, score):
        if score < 40:
            rating = "AKTIONSBEFARF"
        elif 40 <= score < 64:
            rating = "AUSBAUFÄHIG"
        else:
            rating = "OPTIMAL"
        return {
            "ratingEnum": rating,
            "displayName": rating.capitalize(),
            "scoreInterpretation": score_interpretation_dict.get(pillar, {}).get(rating, "No interpretation available.")
        }

    total_score = sum(health_scores.values()) / len(health_scores)
    pillars = []
    for pillar_enum, score in health_scores.items():
        details = get_score_details(pillar_enum, score)
        pillars.append({
            "pillar": {
                "pillarEnum": pillar_enum,
                "displayName": pillar_enum.replace("_", " ").capitalize()
            },
            "score": f"{score:.2f}",
            "scoreInterpretation": details["scoreInterpretation"],
            "rating": {
                "ratingEnum": details["ratingEnum"],
                "displayName": details["displayName"]
            }
        })
    return {
        "data": {
            "totalScore": int(total_score),
            "accountId": account_id,
            "pillarScores": pillars
        }
    }


def calculate_first_month_update_from_pretty_final(account_id, action_plan, pretty_payload, initial_health_scores):
    print(f"calculate_first_month_update_from_pretty_final start for account {account_id}")
    if action_plan is None:
        print(f"ERROR: no action_plan for account {account_id}")
        return {}
    if isinstance(action_plan, str):
        try:
            action_plan_payload = json.loads(action_plan)
            print(f"Parsed action_plan string for account {account_id}")
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse action_plan JSON for account {account_id}: {e}")
            return {}
    elif isinstance(action_plan, dict):
        action_plan_payload = action_plan
        print(f"Using action_plan dict for account {account_id}")
    else:
        print(f"ERROR: Unexpected type for action_plan for account {account_id}: {type(action_plan)}")
        return {}
    scheduled_by_pillar = compute_scheduled_by_pillar(action_plan_payload)
    #print(f"scheduled_by_pillar for account {account_id}: {scheduled_by_pillar}")
    completions_by_pillar = extract_pretty_completions(pretty_payload)
    print(f"completions_by_pillar for account {account_id}: {completions_by_pillar}")
    final_scores = {}
    final_deltas = {}
    for pillar, info in scheduled_by_pillar.items():
        if isinstance(info, dict) and "scheduled" in info:
            scheduled_total = info["scheduled"]
        elif isinstance(info, list):
            scheduled_total = len(info)
        else:
            scheduled_total = 0
        completed_count = completions_by_pillar.get(pillar, {}).get("completed", 0)
        not_completed_count = scheduled_total - completed_count
        init_score = initial_health_scores.get(pillar, 50)
        dampening = (100 - init_score) / 90.0
        delta_completed = 10 * dampening * (1 - math.exp(-k * completed_count))
        delta_not = 10 * dampening * (1 - math.exp(-k * not_completed_count))
        final_delta = delta_completed - (delta_not / 3.0)
        new_score = init_score + final_delta
        new_score = min(max(new_score, 0), 100)
        final_scores[pillar] = new_score
        final_deltas[pillar] = final_delta
        print(f"{pillar}: scheduled={scheduled_total}, completed={completed_count}, not_completed={not_completed_count}")
        print(f"  delta_completed={delta_completed:.4f}, delta_not_component={-delta_not/3.0:.4f}, final_delta={final_delta:.4f}")
        print(f"  init_score={init_score}, new_score={new_score:.4f}")
    base_structure = create_health_scores_with_structure(account_id, final_scores)
    for entry in base_structure["data"]["pillarScores"]:
        p = entry["pillar"]["pillarEnum"]
        entry["delta"] = round(final_deltas.get(p, 0), 2)
    print(f"calculate_first_month_update_from_pretty_final end for account {account_id}")
    return base_structure



@app.route('/event', methods=['POST'])
def event():
    host = request.host
    app.logger.info("Received webhook on host: %s", host)

    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400

    insights, payload = process_event_data(data)
    if payload is None:
        return jsonify({"error": "Invalid eventPayload JSON"}), 400

    # log a pretty-printed payload for debugging
    pretty_payload = json.dumps(payload, indent=4)
    print('pretty_payload', pretty_payload)

    # now payload is a dict, so .get() works
    action_plan_id = payload.get('actionPlanUniqueId', 0)
    account_id     = payload.get('accountId', 0)

    initial_health_scores = strapi_get_health_scores(account_id, host)
    action_plan           = strapi_get_old_action_plan(action_plan_id, host)

    final_scores = calculate_first_month_update_from_pretty_final(
        account_id=account_id,
        action_plan=action_plan,
        pretty_payload=payload,
        initial_health_scores=initial_health_scores
    )
    print("Final Health Scores per Pillar:", final_scores)

    event_type = data.get('eventEnum')
    if not event_type:
        return jsonify({"error": "Missing eventEnum in payload"}), 400

    if event_type == 'RECALCULATE_ACTION_PLAN':
        result = renew_action_plan(payload, host)
        print('RECALCULATE_ACTION_PLAN')
    elif event_type == 'RENEW_ACTION_PLAN':
        print('RENEW_ACTION_PLAN')
        result = renew_action_plan(payload, host)
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
