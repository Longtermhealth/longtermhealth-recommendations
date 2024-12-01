#utils/strapi_api.py
import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

url = "http://4.182.8.101:8004/api/action-plans"
STRAPI_API_KEY = os.getenv("STRAPI_API_KEY")
headers = {
    "Authorization": f"Bearer {STRAPI_API_KEY}",
    "Content-Type": "application/json"
}

def strapi_post_action_plan(action_plan, account_id):

    data = action_plan
    response = requests.post(url, headers=headers, json=data)

    print(f"Response for account {account_id}: {response.status_code}")
    try:
        response_data = response.json()
        print(response_data)
    except requests.exceptions.JSONDecodeError:
        print(f"Response for account {account_id} is not JSON, raw content:", response.text)




def strapi_api_azure_get_all_routines():

    base_url = "http://4.182.8.101:8004/api/routines"
    page = 1
    page_size = 100
    all_recommendations = []

    while True:
        url = f"{base_url}?pagination[page]={page}&pagination[pageSize]={page_size}&populate[variations][populate]=*&populate[pillar][populate]=*&populate[amountUnit][populate]=*&populate[locations][populate]=*&populate[educationArticle][populate]=*&populate[tags][populate]=*&populate[routineType][populate]=*&populate[benefits][populate]=*&populate[adaptibility][populate]=*&populate[equipmentNeeded][populate]=*&populate[contraindications][populate]=*&populate[subRoutines][populate]=*&populate[resources][populate]=*"

        response = requests.get(url, headers=headers)

        print(f"Fetching page {page}: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                recommendations = data.get('data', [])
                all_recommendations.extend(recommendations)

                if len(recommendations) < page_size:
                    break
                page += 1
            except json.JSONDecodeError as e:
                print("Response content is not valid JSON:", e)
                print("Raw content:", response.text)
                break
        else:
            print(f"Error fetching page {page}: {response.text}")
            break

    result_json = json.dumps(all_recommendations, ensure_ascii=False, indent=4)
    file_path = './data/strapi_all_routines.json'

    try:
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json_file.write(result_json)
        print(f"Data saved to {file_path}")
    except IOError as e:
        print(f"Error writing to file: {e}")

