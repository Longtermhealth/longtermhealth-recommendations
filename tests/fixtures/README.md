# Test Fixtures for Analytics

This directory contains JSON payloads for offline testing of the analytics functionality.

## Files

### event_payload_sample.json
- Full payload from actual production logs
- Account ID: 5
- Contains data for all 7 pillars
- 63 total routines
- Includes completion statistics and change log
- Use this for comprehensive testing

### event_payload_minimal.json
- Simplified payload for quick testing
- Account ID: 999
- Contains basic data for each pillar
- 6 routines total
- Use this for debugging and unit tests

### analytics_output.json
- Generated output from running analytics on test payload
- Created by test_analytics_offline.py
- Contains full analytics results

## Usage

### Python Testing
```python
import json
from src.analytics import AnalyticsService

# Load test payload
with open('tests/fixtures/event_payload_sample.json', 'r') as f:
    payload = json.load(f)

# Process analytics
service = AnalyticsService()
result = service.process_event(payload)
```

### API Testing with curl
```bash
# Test with full payload
curl -X POST http://localhost:5000/api/analytics/process-event \
  -H "Content-Type: application/json" \
  -d @tests/fixtures/event_payload_sample.json

# Test with minimal payload
curl -X POST http://localhost:5000/api/analytics/process-event \
  -H "Content-Type: application/json" \
  -d @tests/fixtures/event_payload_minimal.json
```

### Running Offline Tests
```bash
# From project root
python tests/test_analytics_offline.py
```

## Payload Structure

The event payload contains:
- `accountId`: User account identifier
- `actionPlanUniqueId`: Unique ID for the action plan
- `startDate`: When the action plan started
- `periodInDays`: Duration of the plan
- `pillarCompletionStats`: Array of pillar data
  - `pillarEnum`: Pillar name (MOVEMENT, NUTRITION, etc.)
  - `routineCompletionStats`: Array of routines
    - `routineUniqueId`: Unique routine ID
    - `displayName`: Human-readable name
    - `scheduleCategory`: DAILY_ROUTINE, WEEKLY_ROUTINE, etc.
    - `completionStatistics`: Array of completion data
      - `completionRate`: Number of completions
      - `completionRatePeriodUnit`: WEEK or MONTH
      - `periodSequenceNo`: Which week/month
      - `completionUnit`: MINUTES, ROUTINE, SECONDS, etc.
- `changeLog`: Array of changes to routines

## Modifying Test Data

To create your own test scenarios:

1. Copy one of the existing files
2. Modify the completion rates to test different scenarios:
   - High engagement: Set completionRate to 5-7
   - Low engagement: Set completionRate to 0-1
   - No data: Empty completionStatistics array
3. Test edge cases:
   - All routines with no completion data
   - Single pillar with high engagement
   - Gradually improving completion rates