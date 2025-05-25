"""Test the analytics fix"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analytics import AnalyticsService

# Load test payload
payload_path = Path(__file__).parent / "fixtures" / "event_payload_sample.json"
with open(payload_path, 'r') as f:
    payload = json.load(f)

# Process analytics
service = AnalyticsService()
try:
    result = service.process_event(payload)
    print("✅ Analytics processing successful!")
    print(f"Account ID: {result['account_id']}")
    print(f"Engagement Score: {result['metrics']['current']['engagement_score']:.1f}%")
    print(f"Total Alerts: {len(result['alerts'])}")
    print(f"Total Recommendations: {len(result['recommendations'])}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()