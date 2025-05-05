import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

STAGING_BASE_URL = "http://4.182.8.101:8004/api"
DEV_BASE_URL = "http://4.182.8.101:7004/api"

STAGING_API_KEY = os.getenv("STRAPI_API_KEY")
DEV_API_KEY = os.getenv("STRAPI_API_KEY_DEV")

STAGING_HEADERS = {
    "Authorization": f"Bearer {STAGING_API_KEY}",
    "Content-Type": "application/json"
}
DEV_HEADERS = {
    "Authorization": f"Bearer {DEV_API_KEY}",
    "Content-Type": "application/json"
}

STAGING_ACTION_PLAN_ENDPOINT = f"{STAGING_BASE_URL}/action-plans"
STAGING_ROUTINES_ENDPOINT = f"{STAGING_BASE_URL}/routines"
STAGING_HEALTH_SCORES_ENDPOINT = f"{STAGING_BASE_URL}/health-scores"

DEV_ACTION_PLAN_ENDPOINT = f"{DEV_BASE_URL}/action-plans"
DEV_ROUTINES_ENDPOINT = f"{DEV_BASE_URL}/routines"
DEV_HEALTH_SCORES_ENDPOINT = f"{DEV_BASE_URL}/health-scores"

def strapi_get_action_plan(actionPlanId, host):
    if host.endswith("lthrecommendation-dev-g2g0hmcqdtbpg8dw.germanywestcentral-01.azurewebsites.net"):
        app_env = "development"
        base_url = DEV_ACTION_PLAN_ENDPOINT
        headers  = DEV_HEADERS
    else:
        app_env = "production"
        base_url = STAGING_ACTION_PLAN_ENDPOINT
        headers  = STAGING_HEADERS
    params = {"filters[actionPlanUniqueId][$eq]": actionPlanId}
    print(f"[DEBUG][strapi_get_action_plan] env={app_env}")
    print(f"[DEBUG][strapi_get_action_plan] URL       = {base_url}")
    print(f"[DEBUG][strapi_get_action_plan] headers   = {headers}")
    print(f"[DEBUG][strapi_get_action_plan] params    = {params}")
    try:
        response = requests.get(base_url, headers=headers, params=params)
    except Exception as e:
        print(f"[ERROR][strapi_get_action_plan] request exception: {e}")
        return None
    print(f"[DEBUG][strapi_get_action_plan] response.url         = {response.url}")
    print(f"[DEBUG][strapi_get_action_plan] status_code          = {response.status_code}")
    raw = response.text
    snippet = (raw[:500] + "...") if len(raw) > 500 else raw
    print(f"[DEBUG][strapi_get_action_plan] response.text (first 500 chars):\n{snippet}")
    try:
        response.raise_for_status()
    except Exception as e:
        print(f"[ERROR][strapi_get_action_plan] HTTP error: {e}")
        return None
    try:
        result = response.json()
    except json.JSONDecodeError as e:
        print(f"[ERROR][strapi_get_action_plan] JSON decode error: {e}")
        return None
    print(f"[DEBUG][strapi_get_action_plan] parsed JSON keys: {list(result.keys())}")
    data = result.get("data")
    if isinstance(data, list):
        print(f"[DEBUG][strapi_get_action_plan] data is list, length = {len(data)}")
    else:
        print(f"[DEBUG][strapi_get_action_plan] data is not list ({type(data)}) → returning None")
        return None
    if len(data) == 0:
        print("[DEBUG][strapi_get_action_plan] No matching action plan found.")
        return None
    record = data[0]
    attrs  = record.get("attributes")
    if attrs is not None:
        print(f"[DEBUG][strapi_get_action_plan] returning attributes: {json.dumps(attrs, indent=2)}")
        return attrs
    else:
        print(f"[DEBUG][strapi_get_action_plan] no attributes key, returning full record: {json.dumps(record, indent=2)}")
        return record

def strapi_get_health_scores(accountId, host):
    if host.endswith("lthrecommendation-dev-g2g0hmcqdtbpg8dw.germanywestcentral-01.azurewebsites.net"):
        app_env = "development"
        base_url = DEV_HEALTH_SCORES_ENDPOINT
        headers  = DEV_HEADERS
    else:
        app_env = "production"
        base_url = STAGING_HEALTH_SCORES_ENDPOINT
        headers  = STAGING_HEADERS
    params = {"filters[accountId][$eq]": accountId}
    print(f"[DEBUG][strapi_get_health_scores] env={app_env}")
    print(f"[DEBUG][strapi_get_health_scores] URL     = {base_url}")
    print(f"[DEBUG][strapi_get_health_scores] headers = {headers}")
    print(f"[DEBUG][strapi_get_health_scores] params  = {params}")
    try:
        response = requests.get(base_url, headers=headers, params=params)
    except Exception as e:
        print(f"[ERROR][strapi_get_health_scores] request exception: {e}")
        return None
    print(f"[DEBUG][strapi_get_health_scores] response.url    = {response.url}")
    print(f"[DEBUG][strapi_get_health_scores] status_code     = {response.status_code}")
    raw = response.text
    snippet = (raw[:500] + "...") if len(raw) > 500 else raw
    print(f"[DEBUG][strapi_get_health_scores] response.text (first 500 chars):\n{snippet}")
    try:
        response.raise_for_status()
    except Exception as e:
        print(f"[ERROR][strapi_get_health_scores] HTTP error: {e}")
        return None
    try:
        result = response.json()
    except json.JSONDecodeError as e:
        print(f"[ERROR][strapi_get_health_scores] JSON decode error: {e}")
        return None
    print(f"[DEBUG][strapi_get_health_scores] parsed JSON keys: {list(result.keys())}")
    return result


def strapi_get_all_routines():
    page = 1
    page_size = 100
    all_routines = []
    while True:
        url = (
            f"{STAGING_ROUTINES_ENDPOINT}"
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
        response = requests.get(url, headers=STAGING_HEADERS)
        print(f"Fetching page {page}: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                routines = data.get('data', [])
                all_routines.extend(routines)
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


def strapi_get_all_routines_development():
    page = 1
    page_size = 100
    all_routines = []
    while True:
        url = (
            f"{DEV_ROUTINES_ENDPOINT}"
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
        response = requests.get(url, headers=DEV_HEADERS)
        print(f"Fetching page {page}: {response.status_code}")
        print(f"Fetching DEV_ROUTINES_ENDPOINT {DEV_ROUTINES_ENDPOINT}: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                routines = data.get('data', [])
                all_routines.extend(routines)
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


def strapi_post_action_plan(action_plan, account_id, environment):
    if environment == 'development':
        environments = [
            ("dev", DEV_ACTION_PLAN_ENDPOINT, DEV_HEADERS)
        ]
    else:
            environments = [
            ("staging", STAGING_ACTION_PLAN_ENDPOINT, STAGING_HEADERS),
        ]
    for env, endpoint, headers in environments:
        print(f"=== Outgoing Request Details (Post Action Plan) for {env} ===")
        print(f"Account ID: {account_id}")
        print("URL:", endpoint)
        print("================================")
        try:
            response = requests.post(endpoint, headers=headers, json=action_plan)
        except Exception as e:
            print(f"Error while making the POST request for account {account_id} to {env}: {e}")
            continue
        print(f"=== Response Received from {env} ===")
        print(f"Response for account {account_id}: {response.status_code}")
        try:
            response_data = response.json()
            #print("JSON Response:", response_data)
        except ValueError as json_error:
            print(f"JSON decoding failed for account {account_id} on {env}: {json_error}")
            print("Raw response content:", response.text)
        print("================================")

def strapi_post_health_scores(healthscores_with_tags, environment):
    if environment == 'development':
        environments = [
            ("dev", DEV_HEALTH_SCORES_ENDPOINT, DEV_HEADERS)
        ]
    else:
            environments = [
            ("staging", STAGING_HEALTH_SCORES_ENDPOINT, STAGING_HEADERS),
        ]
    for env, endpoint, headers in environments:
        print(f"=== Outgoing Request Details (Post Health Scores) for {env} ===")
        print("URL:", endpoint)
        try:
            response = requests.post(endpoint, headers=headers, json=healthscores_with_tags)
        except Exception as e:
            print(f"Error while making the POST request to {env}: {e}")
            continue
        print(f"=== Response Received from {env} ===")
        print("Response:", response.status_code)
        try:
            response_data = response.json()
            #print("JSON Response:", response_data)
        except ValueError:
            print("Response is not JSON, raw content:", response.text)
        print("================================")

