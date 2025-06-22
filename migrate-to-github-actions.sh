#!/bin/bash

echo "🚀 Migrating User Test Service deployment to GitHub Actions"
echo "=========================================================="

# Check if Azure CLI is logged in
echo "🔐 Checking Azure CLI login status..."
if ! az account show &> /dev/null; then
    echo "❌ Not logged into Azure CLI. Please run: az login"
    exit 1
fi

echo "✅ Azure CLI is authenticated"

# Verify container registry access
echo "🐳 Verifying container registry access..."
if az acr login --name lthrecommendations; then
    echo "✅ Successfully logged into container registry"
else
    echo "❌ Failed to login to container registry"
    exit 1
fi

# Check if the slot exists and is configured for containers
echo "🔍 Checking usertest-dev slot configuration..."
SLOT_CONFIG=$(az webapp config container show \
    --name lthrecommendation \
    --slot usertest-dev \
    --resource-group rg-sponsorship 2>/dev/null)

if [ $? -ne 0 ]; then
    echo "⚠️  Slot 'usertest-dev' not found or not configured for containers"
    echo "📝 Creating container configuration for the slot..."
    
    # Set the slot to use container deployment
    az webapp config container set \
        --name lthrecommendation \
        --slot usertest-dev \
        --resource-group rg-sponsorship \
        --docker-registry-server-url "https://lthrecommendations.azurecr.io" \
        --docker-custom-image-name "lthrecommendations.azurecr.io/lthusertest:latest"
else
    echo "✅ Slot is already configured for container deployment"
fi

# Ensure the slot has the correct port configuration
echo "🔧 Configuring container port settings..."
az webapp config appsettings set \
    --name lthrecommendation \
    --slot usertest-dev \
    --resource-group rg-sponsorship \
    --settings WEBSITES_PORT=5001 USER_TEST_SERVICE_PORT=5001 \
    --output none

echo "✅ Port configuration updated"

# Test GitHub Actions secrets
echo ""
echo "📋 GitHub Actions Prerequisites:"
echo "================================"
echo "Ensure these secrets are set in your GitHub repository:"
echo "  - AZURE_CREDENTIALS (Service Principal JSON)"
echo "  - USER_TEST_CLICKUP_API_KEY"
echo "  - USER_TEST_CLICKUP_LIST_ID"
echo "  - USER_TEST_KEY_FEEDBACK_FIELD_ID"
echo "  - USER_TEST_EMAIL_FIELD_ID"
echo "  - USER_TEST_TYPEFORM_API_TOKEN"
echo ""
echo "To create AZURE_CREDENTIALS if needed:"
echo "az ad sp create-for-rbac --name \"github-actions-user-test\" \\"
echo "  --role contributor \\"
echo "  --scopes /subscriptions/{subscription-id}/resourceGroups/rg-sponsorship \\"
echo "  --sdk-auth"
echo ""
echo "✅ Migration preparation complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Commit the updated GitHub Actions workflow"
echo "2. Push to development branch to trigger deployment"
echo "3. Monitor the Actions tab in GitHub for deployment progress"
echo ""
echo "📝 To disable Azure Pipelines for user-test service:"
echo "   - Comment out the user-test job in azure-pipelines.yml"
echo "   - Or add a condition to skip it when using GitHub Actions"