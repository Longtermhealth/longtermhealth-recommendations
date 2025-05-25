# rule_based_system/utils/clickup_api.py

import requests
import json
from src.config import Config

def create_clickup_task(lastname, scores, answers, total_score, task_name_suffix):
    url = f"https://api.clickup.com/api/v2/list/{Config.CLICKUP_LIST_ID}/task"
    headers = {
        "Authorization": Config.CLICKUP_API_KEY,
        "Content-Type": "application/json"
    }
    answers_str = "\n".join([f"{key}: {value}" for key, value in answers.items()])
    print('scores',scores)

    custom_fields = [
        {
            "id": Config.SCORES_FIELD_ID,
            "value": (f"Exercise: {round(scores['MOVEMENT'], 2)}, Nutrition: {round(scores['NUTRITION'], 2)}, "
                      f"Sleep: {round(scores['SLEEP'], 2)}, Social Connections: {round(scores['SOCIAL_ENGAGEMENT'], 2)}, "
                      f"Stress Management: {round(scores['STRESS'], 2)}, Gratitude: {round(scores['GRATITUDE'], 2)}, "
                      f"Cognition: {round(scores['COGNITIVE_ENHANCEMENT'], 2)}, Total Score: {round(total_score, 2)}")
        },
        {
            "id": Config.ANSWERS_FIELD_ID,
            "value": answers_str
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


def update_clickup_custom_field(task_id, field_id, value):
    url = f"https://api.clickup.com/api/v2/task/{task_id}/field/{field_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": Config.CLICKUP_API_KEY
    }
    payload = {"value": value}

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"Successfully updated ClickUp task {task_id} with {field_id}")
    else:
        print(f"Failed to update ClickUp task {task_id}. Response: {response.content}")
        raise Exception(f"Failed to update task {task_id}")
