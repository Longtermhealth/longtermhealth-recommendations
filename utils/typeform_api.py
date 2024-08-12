# rule_based_system/utils/typeform_api.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

TYPEFORM_API_KEY = os.getenv("TYPEFORM_API_KEY")
FORM_ID = os.getenv("FORM_ID")

responses_url = f'https://api.typeform.com/forms/{FORM_ID}/responses'
form_url = f'https://api.typeform.com/forms/{FORM_ID}'

headers = {
    'Authorization': f'Bearer {TYPEFORM_API_KEY}',
    'Content-Type': 'application/json'
}

def get_responses():
    response = requests.get(responses_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve responses. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def get_field_mapping():
    response = requests.get(form_url, headers=headers)
    if response.status_code == 200:
        form_data = response.json()
        field_mapping = {field['id']: field['title'] for field in form_data['fields']}
        return field_mapping
    else:
        print(f"Failed to retrieve form. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def process_latest_response(responses, field_mapping):
    if not responses or 'items' not in responses or not responses['items']:
        print("No responses found.")
        return None

    latest_response = responses['items'][1]
    print("Latest response", latest_response)

    special_field_labels = {
        '7RNIAzXy1eCa': 'Vorname',
        'ANmNYBscN0R5': 'Nachname',
        'TMp57UpKHkMM': 'Frühstück',
        'mAtyQU2ScE16': 'Mittagessen',
        'cRdUJhgqJfMx': 'Abendessen'
    }

    answers = {}
    for answer in latest_response['answers']:
        field_id = answer['field']['id']
        field_label = special_field_labels.get(field_id, field_mapping.get(field_id, f"Unknown Field ({field_id})"))

        answer_type = answer['type']
        value = None

        if answer_type == 'choice':
            value = answer.get('choice', {}).get('label', 'No label')
        elif answer_type == 'choices':
            value = ", ".join(answer.get('choices', {}).get('labels', []))
        elif answer_type == 'boolean':
            value = answer.get('boolean', 'No boolean value')
        elif answer_type == 'number':
            value = answer.get('number', 'No number value')
        elif answer_type == 'text':
            value = answer.get('text', 'No text value')
        else:
            value = 'Unknown Type'

        answers[field_label] = value

    print('answers', answers)
    return answers


def get_last_name(responses):
    if not responses or 'items' not in responses or not responses['items']:
        return "Unknown"

    first_name = None
    last_name = None
    latest_response = responses['items'][1]
    for answer in latest_response['answers']:
        field_id = answer['field']['id']
        if field_id == 'ANmNYBscN0R5':
            last_name = answer['text']
        elif field_id == '7RNIAzXy1eCa':
            first_name = answer['text']

    full_name = f"{first_name} {last_name}" if first_name and last_name else None
    return full_name
