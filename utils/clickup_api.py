# rule_based_system/utils/clickup_api.py

import requests
import json
from config import Config

def create_clickup_task(lastname, scores, answers, total_score, routines, task_name_suffix):
    url = f"https://api.clickup.com/api/v2/list/{Config.CLICKUP_LIST_ID}/task"
    headers = {
        "Authorization": Config.CLICKUP_API_KEY,
        "Content-Type": "application/json"
    }
    answers_str = "\n".join([f"{key}: {value}" for key, value in answers.items()])
    routines_str = "\n".join(routines)

    custom_fields = [
        {
            "id": Config.SCORES_FIELD_ID,
            "value": (f"Exercise: {round(scores['Movement&Exercise'], 2)}, Nutrition: {round(scores['HealthfulNutrition'], 2)}, "
                      f"Sleep: {round(scores['RestorativeSleep'], 2)}, Social Connections: {round(scores['SocialEngagement'], 2)}, "
                      f"Stress Management: {round(scores['StressManagement'], 2)}, Gratitude: {round(scores['Gratitude&Reflection'], 2)}, "
                      f"Cognition: {round(scores['Cognition'], 2)}, Total Score: {round(total_score, 2)}")
        },
        {
            "id": Config.ANSWERS_FIELD_ID,
            "value": answers_str
        },
        {
            "id": Config.ROUTINES_FIELD_ID,
            "value": routines_str
        }
    ]

    payload = {
        "name": f"Health Assessment for {lastname} {task_name_suffix}",
        "custom_fields": custom_fields
    }

    print(f"Payload for creating ClickUp task: {json.dumps(payload, indent=2)}")

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Failed to create ClickUp task: {response.content}")
        raise Exception("Failed to create ClickUp task")
    task = response.json()
    return task['id']

def upload_file_to_clickup(task_id, file_path):
    url = f"https://api.clickup.com/api/v2/task/{task_id}/attachment"
    headers = {
        "Authorization": Config.CLICKUP_API_KEY
    }
    files = {
        'attachment': open(file_path, 'rb')
    }
    response = requests.post(url, headers=headers, files=files)
    if response.status_code != 200:
        print(f"Failed to upload file to ClickUp: {response.content}")
        raise Exception("Failed to upload file to ClickUp")
    print("Successfully uploaded file to ClickUp")
