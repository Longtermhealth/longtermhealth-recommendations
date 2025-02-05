# rule_based_system/main_flask.py
import time
from flask import Flask, jsonify
from config import Config
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

@app.route('/webhook', methods=['POST'])
def webhook():
    start_time = time.perf_counter()
    app.logger.info('Webhook received')
    final_action_plan = process_action_plan()
    app.logger.info('Action plan processed and posted')
    end_time = time.perf_counter()
    elapsed = end_time - start_time
    app.logger.info(f"Total time from webhook reception to posting action plan: {elapsed:.2f} seconds")

    field_mapping = get_field_mapping()
    responses = get_responses()

    if responses and field_mapping:
        answers = process_latest_response(responses, field_mapping)
        lastname = get_last_name(responses)
        if answers:
            integrated_data = integrate_answers(answers)
            accountid = answers.get('accountid', 'Unknown Account ID')

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

            print(f"Exercise Score: {exercise_score}")
            print(f"Nutrition Score: {nutrition_score}")
            print(f"Sleep Score: {sleep_score}")
            print(f"Social Connections Score: {social_connections_score}")
            print(f"Stress Management Score: {stress_management_score}")
            print(f"Gratitude and Reflection Score: {gratitude_score}")
            print(f"Cognitive Enhancement Score: {cognition_score}")
            print(f"Total Score: {assessment.calculate_total_score()}")

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



    return jsonify({'status': 'success'}), 200





if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)