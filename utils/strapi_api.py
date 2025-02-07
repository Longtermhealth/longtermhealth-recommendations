# utils/strapi_api.py
import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

# Define the base URL and API key (optionally, set STRAPI_BASE_URL in your .env file)
STRAPI_BASE_URL = os.getenv("STRAPI_BASE_URL", "http://4.182.8.101:8004/api")
STRAPI_API_KEY = os.getenv("STRAPI_API_KEY")

# Common headers for all requests
HEADERS = {
    "Authorization": f"Bearer {STRAPI_API_KEY}",
    "Content-Type": "application/json"
}

# Define endpoints for various resources
ACTION_PLAN_ENDPOINT = f"{STRAPI_BASE_URL}/action-plans"
ROUTINES_ENDPOINT = f"{STRAPI_BASE_URL}/routines"
HEALTH_SCORES_ENDPOINT = f"{STRAPI_BASE_URL}/health-scores"


def strapi_get_action_plan(account_id):
    """Fetch the action plan for a given account."""
    url = f"{ACTION_PLAN_ENDPOINT}?accountId={account_id}"
    print(f"Account ID: {account_id}")
    print("URL:", url)
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()  # Raise an exception for HTTP errors
        old_action_plan = response.json()
        print("Received old action plan:", old_action_plan)
        return old_action_plan
    except Exception as e:
        print(f"Error while fetching the action plan for account {account_id}: {e}")
        return None


def strapi_post_action_plan(action_plan, account_id):
    """Post an updated action plan for a given account."""
    url = ACTION_PLAN_ENDPOINT
    print("=== Outgoing Request Details (Post Action Plan) ===")
    print(f"Account ID: {account_id}")
    print("URL:", url)
    print("Payload:", action_plan)
    print("================================")
    try:
        response = requests.post(url, headers=HEADERS, json=action_plan)
    except Exception as e:
        print(f"Error while making the POST request for account {account_id}: {e}")
        return

    print("=== Response Received ===")
    print(f"Response for account {account_id}: {response.status_code}")
    try:
        response_data = response.json()
        print("JSON Response:", response_data)
    except ValueError as json_error:
        print(f"JSON decoding failed for account {account_id}: {json_error}")
        print("Raw response content:", response.text)
    print("================================")


def strapi_get_all_routines():
    """Fetch all routines from the Strapi API."""
    page = 1
    page_size = 100
    all_routines = []

    while True:
        url = (
            f"{ROUTINES_ENDPOINT}"
            f"?pagination[page]={page}"
            f"&pagination[pageSize]={page_size}"
            f"&populate[variations][populate]=*"
            f"&populate[pillar][populate]=*"
            f"&populate[amountUnit][populate]=*"
            f"&populate[locations][populate]=*"
            f"&populate[educationArticle][populate]=*"
            f"&populate[tags][populate]=*"
            f"&populate[routineType][populate]=*"
            f"&populate[benefits][populate]=*"
            f"&populate[adaptibility][populate]=*"
            f"&populate[equipmentNeeded][populate]=*"
            f"&populate[contraindications][populate]=*"
            f"&populate[subRoutines][populate]=*"
            f"&populate[resources][populate]=*"
            f"&populate[routineClass][populate]=*"
        )
        response = requests.get(url, headers=HEADERS)
        print(f"Fetching page {page}: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                routines = data.get('data', [])
                all_routines.extend(routines)

                # If fewer routines than the page size are returned, we've reached the last page.
                if len(routines) < page_size:
                    break
                page += 1
            except json.JSONDecodeError as e:
                print("Response content is not valid JSON:", e)
                print("Raw content:", response.text)
                break
        else:
            print(f"Error fetching page {page}: {response.text}")
            break

    return all_routines


def strapi_post_health_scores(healthscores_with_tags):
    """Post health scores with tags to the Strapi API."""
    url = HEALTH_SCORES_ENDPOINT
    response = requests.post(url, headers=HEADERS, json=healthscores_with_tags)
    print("=== Response Post Health Scores ===")
    print("Response:", response.status_code)
    try:
        response_data = response.json()
        print("JSON Response:", response_data)
    except ValueError:
        print("Response is not JSON, raw content:", response.text)
