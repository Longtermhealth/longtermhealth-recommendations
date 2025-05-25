#!/bin/bash

# Test analytics endpoint with production data
echo "Testing analytics endpoint..."

# Use the event payload from the fixtures
PAYLOAD_FILE="tests/fixtures/event_payload_sample.json"

if [ ! -f "$PAYLOAD_FILE" ]; then
    echo "Error: Test payload file not found at $PAYLOAD_FILE"
    exit 1
fi

# Azure dev endpoint
ENDPOINT="http://lthrecommendation-dev-g2g0hmcqdtbpg8dw.germanywestcentral-01.azurewebsites.net/api/analytics/event"

echo "Sending analytics request to: $ENDPOINT"
echo "Using payload from: $PAYLOAD_FILE"

# Send request
response=$(curl -s -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -d @"$PAYLOAD_FILE")

# Pretty print response
echo -e "\nResponse:"
echo "$response" | python -m json.tool

# Test summary endpoint
echo -e "\n\nTesting summary endpoint for account 5..."
SUMMARY_ENDPOINT="http://lthrecommendation-dev-g2g0hmcqdtbpg8dw.germanywestcentral-01.azurewebsites.net/api/analytics/summary/5?days=7"

summary_response=$(curl -s "$SUMMARY_ENDPOINT")
echo -e "\nSummary Response:"
echo "$summary_response" | python -m json.tool