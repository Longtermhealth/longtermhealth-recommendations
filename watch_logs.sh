#!/bin/bash

echo "=== Watching Flask Application Logs ==="
echo "The app is running on port 5003"
echo "Your ngrok URL: https://b2c4-2001-fb1-74-b186-88dc-88b0-4f95-5f4e.ngrok-free.app"
echo ""
echo "To see logs in real-time:"
echo "1. Check flask_app.log file: tail -f flask_app.log"
echo "2. Or watch the terminal where you started the app"
echo ""
echo "Testing endpoints now..."
echo ""

# Test health endpoint
echo "Testing health endpoint..."
curl -s "https://b2c4-2001-fb1-74-b186-88dc-88b0-4f95-5f4e.ngrok-free.app/" \
  -H "ngrok-skip-browser-warning: true" | jq '.' || echo "Error parsing response"

echo ""
echo "To test other endpoints, use these commands:"
echo ""
echo "# Test event endpoint (RECALCULATE_ACTION_PLAN):"
echo 'curl -X POST "https://b2c4-2001-fb1-74-b186-88dc-88b0-4f95-5f4e.ngrok-free.app/event" \'
echo '  -H "Content-Type: application/json" \'
echo '  -H "ngrok-skip-browser-warning: true" \'
echo '  -d '"'"'{"eventEnum":"RECALCULATE_ACTION_PLAN","eventPayload":{"actionPlanUniqueId":"test-123","accountId":12345}}'"'"''