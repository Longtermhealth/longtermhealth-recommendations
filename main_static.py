# rule_based_system/main_static.py
import os

from chart.chart_generation import generate_polar_chart
from chart.converter import create_final_image
from config import Config
from utils.blob_upload import upload_to_blob
from utils.typeform_api import get_responses, get_field_mapping, process_latest_response, get_last_name
from utils.clickup_api import create_clickup_task, upload_file_to_clickup
from utils.data_processing import integrate_answers
from assessments.health_assessment import HealthAssessment
import matplotlib.pyplot as plt
import numpy as np
from scheduling.scheduler import main as process_action_plan


CLICKUP_API_KEY = Config.CLICKUP_API_KEY
CLICKUP_LIST_ID = Config.CLICKUP_LIST_ID
SCORES_FIELD_ID = Config.SCORES_FIELD_ID
PLOT_FIELD_ID = Config.PLOT_FIELD_ID
ANSWERS_FIELD_ID = Config.ANSWERS_FIELD_ID
ROUTINES_FIELD_ID = Config.ROUTINES_FIELD_ID
ACTIONPLAN_FIELD_ID = Config.ACTIONPLAN_FIELD_ID
TYPEFORM_API_KEY = Config.TYPEFORM_API_KEY
FORM_ID = Config.FORM_ID






def main():

    final_action_plan = process_action_plan()
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

            """
            task_id = create_clickup_task(lastname, scores, answers, total_score, accountid)
            accountid_str = str(accountid) + "_1.png"
            generate_polar_chart(scores, accountid_str)
            total_score_str = str(round(total_score))
            create_final_image(total_score_str, accountid_str)
            upload_file_to_clickup(task_id, accountid_str)
            upload_to_blob(accountid_str)
            """


if __name__ == "__main__":
    main()
