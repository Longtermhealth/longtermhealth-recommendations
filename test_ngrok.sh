#!/bin/bash

# Your ngrok URL
NGROK_URL="https://b2c4-2001-fb1-74-b186-88dc-88b0-4f95-5f4e.ngrok-free.app"

echo "=== Testing LTH Recommendation Service via ngrok ==="
echo "URL: $NGROK_URL"
echo ""

# Test 1: Health Check
echo "1. Testing Health Check endpoint..."
curl -s "$NGROK_URL/" | jq '.' || echo "Failed to parse JSON"
echo ""

# Test 2: Event - RECALCULATE_ACTION_PLAN
echo "2. Testing Event endpoint - RECALCULATE_ACTION_PLAN..."
curl -s -X POST "$NGROK_URL/event" \
  -H "Content-Type: application/json" \
  -H "ngrok-skip-browser-warning: true" \
  -d '{
    "eventEnum": "RECALCULATE_ACTION_PLAN",
    "eventPayload": {
      "actionPlanUniqueId": "test-plan-123",
      "accountId": 12345,
      "pillarCompletionStats": [
        {
          "pillarEnum": "MOVEMENT",
          "routineCompletionStats": [
            {
              "routineId": 1,
              "routineUniqueId": "routine-1",
              "displayName": "Morning Walk",
              "completionStatistics": []
            }
          ]
        }
      ]
    }
  }' | jq '.' || echo "Failed to parse JSON"
echo ""

# Test 3: Check logs
echo "3. To see real-time logs, run:"
echo "   tail -f flask.log"
echo ""
echo "Or if running in terminal directly, logs will appear there"