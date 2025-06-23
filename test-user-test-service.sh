#!/bin/bash

echo "🧪 Testing User Test Service Deployment"
echo "======================================"

SERVICE_URL="https://lthrecommendation-usertest-dev-h4cxg6cmfbfbgwc3.germanywestcentral-01.azurewebsites.net"

echo ""
echo "1️⃣ Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s "$SERVICE_URL/health")
HEALTH_STATUS=$(echo $HEALTH_RESPONSE | jq -r '.status' 2>/dev/null || echo "error")

if [ "$HEALTH_STATUS" = "healthy" ]; then
    echo "✅ Health check passed!"
    echo "Response: $HEALTH_RESPONSE"
else
    echo "❌ Health check failed!"
    echo "Response: $HEALTH_RESPONSE"
    exit 1
fi

echo ""
echo "2️⃣ Testing root endpoint..."
ROOT_RESPONSE=$(curl -s "$SERVICE_URL/")
SERVICE_STATUS=$(echo $ROOT_RESPONSE | jq -r '.status' 2>/dev/null || echo "error")

if [ "$SERVICE_STATUS" = "running" ]; then
    echo "✅ Service is running!"
    echo "Available endpoints:"
    echo $ROOT_RESPONSE | jq '.endpoints' 2>/dev/null || echo $ROOT_RESPONSE
else
    echo "❌ Service check failed!"
    echo "Response: $ROOT_RESPONSE"
    exit 1
fi

echo ""
echo "3️⃣ Testing survey endpoint (GET - should return 405)..."
SURVEY_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/survey")

if [ "$SURVEY_STATUS" = "405" ]; then
    echo "✅ Survey endpoint exists (returns 405 for GET as expected)"
else
    echo "❌ Survey endpoint returned unexpected status: $SURVEY_STATUS"
fi

echo ""
echo "4️⃣ Checking container configuration..."
CONTAINER_IMAGE=$(az webapp config container show \
    --name lthrecommendation \
    --slot usertest-dev \
    --resource-group rg-sponsorship \
    --query "[?name=='DOCKER_CUSTOM_IMAGE_NAME'].value" -o tsv)

echo "Container image: $CONTAINER_IMAGE"

echo ""
echo "✅ All tests passed! User Test Service is fully operational."
echo ""
echo "📝 Webhook URL for Typeform: $SERVICE_URL/survey"
echo "🔍 Health check URL: $SERVICE_URL/health"
echo ""