# rule_based_system/main_flask.py
import time
from flask import Flask, jsonify, request
from config import Config
from utils.strapi_api import strapi_get_action_plan
from utils.typeform_api import get_responses, get_field_mapping, process_latest_response, get_last_name
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


def main():
    field_mapping = get_field_mapping()
    responses = get_responses()

@app.route('/')
def hello():
    return "Hello, Flask is working!"

@app.route('/webhook-recalculate-action-plan', methods=['POST'])
def recalc_action_plan():
    data = request.get_json()

    action_plan_id = data.get('actionPlanId')
    start_date = data.get('startDate')
    period_in_days = data.get('periodInDays')

    app.logger.info("Action Plan ID: %s", action_plan_id)
    app.logger.info("Start Date: %s", start_date)
    app.logger.info("Period in Days: %s", period_in_days)

    # Fetch the old action plan using the actionPlanId
    old_action_plan = strapi_get_action_plan(action_plan_id)
    if old_action_plan:
        app.logger.info("Old action plan retrieved: %s")
    else:
        app.logger.error("No old action plan found for actionPlanId: %s", action_plan_id)

    # Process the pillar statistics from the incoming data.
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

                # Try either property name in case one is missing
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

    total_target = 0
    for pillar in pillar_stats_list:
        for routine in pillar.get('routineCompletionStats', []):
            for stat in routine.get('completionStatistics', []):
                target_value = stat.get('completionTargetTotal', stat.get('completionTarget'))
                if target_value is not None:
                    try:
                        total_target += float(target_value)
                    except ValueError as e:
                        app.logger.error("Error converting target value: %s", e)

    #app.logger.info("Total target value: %s", total_target)

    # Assuming old_action_plan is the dictionary returned by strapi_get_action_plan(action_plan_id)
    if old_action_plan and 'data' in old_action_plan:
        account_id = None
        total_daily_time = None
        # Iterate over the list in case some entries have None values
        for plan in old_action_plan['data']:
            attributes = plan.get('attributes', {})
            account_id_candidate = attributes.get('accountId')
            total_daily_time_candidate = attributes.get('totalDailyTimeInMins')
            # Choose the record if at least one of the values is present
            if account_id_candidate is not None or total_daily_time_candidate is not None:
                account_id = account_id_candidate
                total_daily_time = total_daily_time_candidate
                break

        app.logger.info("Account ID from old action plan: %s", account_id)
        app.logger.info("Total Daily Time (in mins) from old action plan: %s", total_daily_time)
    else:
        app.logger.error("Old action plan is not in the expected format.")


    final_action_plan = {
        "actionPlanId": action_plan_id,
        "calculatedTotalTarget": total_target,
    }

    return jsonify({'action_plan': final_action_plan}), 200


@app.route('/webhook', methods=['POST'])
def webhook():
    field_mapping = get_field_mapping()
    responses = get_responses()
    if responses and field_mapping:
        answers = process_latest_response(responses, field_mapping)
        lastname = get_last_name(responses)
        if answers:
            accountid = answers.get('accountid', 'Unknown Account ID')
            print('accountid', accountid)
            print('lastname',lastname)

    start_time = time.perf_counter()
    app.logger.info('Webhook received')
    app.logger.info('Start processing action plan')
    final_action_plan = process_action_plan()
    app.logger.info('Action plan processed and posted')
    end_time = time.perf_counter()
    elapsed = end_time - start_time
    app.logger.info(f"Total time from webhook reception to posting action plan: {elapsed:.2f} seconds")
    """
    field_mapping = get_field_mapping()
    responses = get_responses()

    if responses and field_mapping:
        answers = process_latest_response(responses, field_mapping)
        lastname = get_last_name(responses)
        if answers:
            integrated_data = integrate_answers(answers)
            accountid = answers.get('accountid', 'Unknown Account ID')
            print(accountid)
    
            assessment = HealthAssessment(
                integrated_data['exercise'],
                integrated_data['nutrition'],
                integrated_data['sleep'],
                integrated_data['social_connections'],
                integrated_data['stress_management'],
                integrated_data['gratitude'],
                integrated_data['cognition'],
            )

            exercise_score = float(assessment.exercise_assessment.report())
            nutrition_score = float(assessment.nutrition_assessment.report())
            sleep_score = float(assessment.sleep_assessment.report())
            social_connections_score = float(assessment.social_connections_assessment.report())
            stress_management_score = float(assessment.stress_management_assessment.report())
            gratitude_score = float(assessment.gratitude_assessment.report())
            cognition_score = float(assessment.cognition_assessment.report())
            total_score = float(assessment.calculate_total_score())

            #print(f"Exercise Score: {exercise_score}")
            #print(f"Nutrition Score: {nutrition_score}")
            #print(f"Sleep Score: {sleep_score}")
            #print(f"Social Connections Score: {social_connections_score}")
            #print(f"Stress Management Score: {stress_management_score}")
            #print(f"Gratitude and Reflection Score: {gratitude_score}")
            #print(f"Cognitive Enhancement Score: {cognition_score}")
            #print(f"Total Score: {assessment.calculate_total_score()}")

            scores = {
                "NUTRITION": nutrition_score,
                "MOVEMENT": exercise_score,
                "GRATITUDE": gratitude_score,
                "SLEEP": sleep_score,
                "SOCIAL_ENGAGEMENT": social_connections_score,
                "STRESS": stress_management_score,
                "COGNITIVE_ENHANCEMENT": cognition_score
            }

            create_clickup_task(lastname, scores, answers, total_score, accountid)
        """


    return jsonify({'status': 'success'}), 200





if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)