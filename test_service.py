import requests
import time

url = "https://lthrecommendation-usertest-dev-h4cxg6cmfbfbgwc3.germanywestcentral-01.azurewebsites.net"

print("Testing service endpoints...")

endpoints = ["/", "/health", "/survey"]

for endpoint in endpoints:
    try:
        response = requests.get(f"{url}{endpoint}", timeout=10)
        print(f"{endpoint}: Status {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.text[:200]}...")
    except Exception as e:
        print(f"{endpoint}: Error - {e}")

print("\nTesting POST to /survey...")
test_data = {
    "form_response": {
        "form_id": "test",
        "submitted_at": "2025-06-21T12:00:00Z",
        "hidden": {
            "email": "test@example.com",
            "name": "Test",
            "surname": "User"
        }
    }
}

try:
    response = requests.post(f"{url}/survey", json=test_data, timeout=10)
    print(f"POST /survey: Status {response.status_code}")
    print(f"  Response: {response.text[:200]}...")
except Exception as e:
    print(f"POST /survey: Error - {e}")