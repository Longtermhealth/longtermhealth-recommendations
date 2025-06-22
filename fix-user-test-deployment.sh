#!/bin/bash

# Script to fix User Test Service deployment on Azure
# This script updates the startup command to use the startup.sh script

set -e

echo "🔧 Fixing User Test Service Deployment..."
echo ""

# Azure configuration
RESOURCE_GROUP="rg-sponsorship"
APP_NAME="lthrecommendation"
SLOT_NAME="usertest-dev"

# Step 1: Update the startup command to use startup.sh
echo "1️⃣ Updating startup command..."
az webapp config set \
  --name "$APP_NAME" \
  --slot "$SLOT_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --startup-file "/home/site/wwwroot/startup.sh"

echo "✅ Startup command updated"
echo ""

# Step 2: Ensure gunicorn is in requirements.txt
echo "2️⃣ Checking if gunicorn is in requirements.txt..."
if ! grep -q "gunicorn" user-test-service/requirements.txt; then
    echo "Adding gunicorn to requirements.txt..."
    echo "gunicorn==20.1.0" >> user-test-service/requirements.txt
    echo "✅ Added gunicorn to requirements.txt"
else
    echo "✅ gunicorn already in requirements.txt"
fi
echo ""

# Step 3: Make startup.sh executable
echo "3️⃣ Making startup.sh executable..."
chmod +x user-test-service/startup.sh
echo "✅ startup.sh is now executable"
echo ""

# Step 4: Commit and push changes
echo "4️⃣ Committing changes..."
git add user-test-service/startup.sh user-test-service/requirements.txt scripts/set-azure-app-settings.sh
git commit -m "[user-test] Fix Python import issues with proper PYTHONPATH configuration

- Updated startup.sh to set PYTHONPATH correctly
- Made startup.sh executable
- Updated Azure deployment script to use startup.sh
- Ensured gunicorn is in requirements.txt

This fixes the 503 errors by ensuring Python can find the app modules."

echo "✅ Changes committed"
echo ""

# Step 5: Push to trigger deployment
echo "5️⃣ Pushing to trigger deployment..."
git push origin development

echo ""
echo "✅ Fix deployed! The Azure Pipeline will now rebuild and deploy the service."
echo ""
echo "📝 Next steps:"
echo "1. Wait for the Azure Pipeline to complete (~5-10 minutes)"
echo "2. Monitor the deployment at: https://dev.azure.com/lthtransformation/lth-recommendation"
echo "3. Test the service at: https://lthrecommendation-usertest-dev.azurewebsites.net/health"
echo ""
echo "🔍 To monitor logs after deployment:"
echo "az webapp log tail --name $APP_NAME --slot $SLOT_NAME --resource-group $RESOURCE_GROUP"