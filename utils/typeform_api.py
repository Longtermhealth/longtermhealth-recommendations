import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

TYPEFORM_API_KEY = os.getenv("TYPEFORM_API_KEY")
FORM_ID = os.getenv("FORM_ID")
FORM_ID_DEV = "Js2csFWp"
RESPONSES_URL = f'https://api.typeform.com/forms/{FORM_ID}/responses'
RESPONSES_URL_DEV = f'https://api.typeform.com/forms/{FORM_ID_DEV}/responses'
FORM_URL = f'https://api.typeform.com/forms/{FORM_ID}'
FORM_URL_DEV = f'https://api.typeform.com/forms/{FORM_ID_DEV}'
WEBHOOK_URL = "https://lthrecommendation-hpdphma0ehf3bacn.germanywestcentral-01.azurewebsites.net/webhook"
WEBHOOK_URL_DEV = "https://lthrecommendation-dev-g2g0hmcqdtbpg8dw.germanywestcentral-01.azurewebsites.net/webhook"

headers = {
    'Authorization': f'Bearer {TYPEFORM_API_KEY}',
    'Content-Type': 'application/json'
}


def trigger_followup(app_env):
    """
    Trigger a follow-up call by sending a POST request to the same webhook URL,
    with a custom header so that the endpoint knows this is a follow-up request.
    """
    if app_env == "development":
        webhook_url = WEBHOOK_URL_DEV
    else:
        webhook_url = WEBHOOK_URL

    headers = {"X-Webhook-Followup": "true"}
    payload = {
        "message": "Follow-up trigger for latest Typeform response"
    }
    try:
        response = requests.post(webhook_url, json=payload, headers=headers)
        response.raise_for_status()
        print("Follow-up webhook triggered successfully. Response: %s")
    except Exception as e:
        print("Error triggering follow-up webhook: %s", e)


def get_responses(app_env):
    if app_env == "development":
        responses_url = RESPONSES_URL_DEV
    else:
        responses_url = RESPONSES_URL

    params = {
        'page_size': 1
    }
    response = requests.get(responses_url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve responses. Status code: {response.status_code}")
        return None

def get_field_mapping(app_env):
    if app_env == "development":
        form_url = FORM_URL_DEV
    else:
        form_url = FORM_URL

    response = requests.get(form_url, headers=headers)
    if response.status_code == 200:
        form_data = response.json()
        field_mapping = {field['id']: field['title'] for field in form_data['fields']}
        return field_mapping
    else:
        print(f"Failed to retrieve form. Status code: {response.status_code}")
        return None

def get_latest_response(responses):
    """
    Sorts the responses by the submitted_at timestamp (descending)
    and returns the most recent one.
    """
    if not responses or 'items' not in responses or not responses['items']:
        print("No responses found.")
        return None

    sorted_items = sorted(
        responses['items'],
        key=lambda x: x.get('submitted_at', ''),
        reverse=True
    )
    return sorted_items[0]

def process_latest_response(responses, field_mapping):
    latest_response = get_latest_response(responses)
    if not latest_response:
        return None
    #print("Latest response", latest_response)

    special_field_labels = {
        '7RNIAzXy1eCa': 'Vorname',
        'ANmNYBscN0R5': 'Nachname',
        'TMp57UpKHkMM': 'Frühstück',
        'mAtyQU2ScE16': 'Mittagessen',
        'cRdUJhgqJfMx': 'Abendessen'
    }

    answers = {}
    account_id = latest_response.get('hidden', {}).get('accountid', 'Unknown')
    answers['accountid'] = account_id

    for answer in latest_response.get('answers', []):
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

    return answers

def get_last_name(responses):
    latest_response = get_latest_response(responses)
    if not latest_response:
        return "Unknown"

    first_name = None
    last_name = None
    for answer in latest_response.get('answers', []):
        field_id = answer['field']['id']
        if field_id == 'ANmNYBscN0R5':
            last_name = answer.get('text', None)
        elif field_id == '7RNIAzXy1eCa':
            first_name = answer.get('text', None)

    full_name = f"{first_name} {last_name}" if first_name and last_name else None
    return full_name
