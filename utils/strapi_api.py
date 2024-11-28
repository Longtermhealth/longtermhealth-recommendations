#utils/strapi_api.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = "http://4.182.8.101:8004/api/action-plans"
STRAPI_API_KEY = os.getenv("STRAPI_API_KEY")

def strapi_post_action_plan(action_plan, account_id):
    headers = {
        "Authorization": f"Bearer {STRAPI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = action_plan
    response = requests.post(url, headers=headers, json=data)

    print(f"Response for account {account_id}: {response.status_code}")
    try:
        response_data = response.json()
        print(response_data)
    except requests.exceptions.JSONDecodeError:
        print(f"Response for account {account_id} is not JSON, raw content:", response.text)
