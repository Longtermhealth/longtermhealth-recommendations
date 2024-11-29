# rule_based_system/main_flask.py
import traceback
from flask import Flask, request, jsonify
from config import Config
from utils.typeform_api import get_responses, get_field_mapping, process_latest_response, get_last_name
from utils.clickup_api import create_clickup_task, upload_file_to_clickup, update_clickup_custom_field
from utils.data_processing import integrate_answers
from utils.link_summary import fetch_url_content, generate_summary
from assessments.health_assessment import HealthAssessment
from scheduling.scheduler import main as process_action_plan

import matplotlib.pyplot as plt
import numpy as np
import os
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
    app.logger.info('Webhook received')
    final_action_plan = process_action_plan()
    field_mapping = get_field_mapping()
    responses = get_responses()

    if responses and field_mapping:
        answers = process_latest_response(responses, field_mapping)
        lastname = get_last_name(responses)
        if answers:
            integrated_data = integrate_answers(answers)
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

            categories = ['Exercise', 'Nutrition', 'Sleep', 'Social Connections', 'Stress Management', 'Gratitude',
                          'Cognition']

            scores = {
                "Movement&Exercise": exercise_score,
                "HealthfulNutrition": nutrition_score,
                "RestorativeSleep": sleep_score,
                "SocialEngagement": social_connections_score,
                "StressManagement": stress_management_score,
                "Gratitude&Reflection": gratitude_score,
                "Cognition": cognition_score
            }

            scores_values = [exercise_score, nutrition_score, sleep_score, social_connections_score,
                             stress_management_score, gratitude_score, cognition_score]

            num_vars = len(categories)
            angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
            scores_values += scores_values[:1]
            angles += angles[:1]

            fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
            ax.fill(angles, scores_values, color='blue', alpha=0.25)
            ax.plot(angles, scores_values, color='blue', linewidth=2)

            ax.set_yticks(np.arange(0, 101, 10))
            ax.set_yticklabels(['0', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100'])
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)

            plt.title(f'Health Scores for {lastname}')
            image_path = f"{lastname}_health_scores.png"
            plt.savefig(image_path)
            plt.show()
            task_id = create_clickup_task(lastname, scores, answers, total_score, final_action_plan, "")
            upload_file_to_clickup(task_id, image_path)
            action_plan_path = "./data/action_plan.json"
            upload_file_to_clickup(task_id, action_plan_path)
            plt.close()
            os.remove(image_path)
            app.logger.debug(f'action_plan {final_action_plan}')


    return jsonify({'status': 'success'}), 200





if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)