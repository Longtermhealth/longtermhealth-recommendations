import json
from src.analytics import AnalyticsService

# Load test payload
with open('/Users/janoschgrellner/PycharmProjects/lth-rec/tests/fixtures/event_payload_sample.json', 'r') as f:
    payload = json.load(f)

# Process analytics
service = AnalyticsService()
result = service.process_event(payload)