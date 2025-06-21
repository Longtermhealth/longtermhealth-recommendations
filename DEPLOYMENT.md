# Azure Deployment Guide

This guide explains how to deploy the LTH Recommendation Service and User Test Service to Azure.

## Prerequisites

1. **Azure Service Principal**: Create one for GitHub Actions authentication
2. **GitHub Repository Secrets**: Configure all required secrets
3. **Azure Web App**: Already configured with deployment slots

## Creating Azure Service Principal

```bash
# Replace with your values
SUBSCRIPTION_ID="your-subscription-id"
RESOURCE_GROUP="lthrecommendation_group"
APP_NAME="lthrecommendation"

# Create service principal
az ad sp create-for-rbac \
  --name "github-actions-lth-rec" \
  --role contributor \
  --scopes /subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP} \
  --sdk-auth
```

Save the JSON output as the `AZURE_CREDENTIALS` secret in GitHub.

## GitHub Secrets Configuration

Go to: Settings → Secrets and variables → Actions

### Required Secrets

#### 1. Azure Authentication
- **AZURE_CREDENTIALS**: The JSON output from service principal creation

#### 2. Recommendation Service Secrets
- **CLICKUP_API_KEY**: Your ClickUp API key
- **CLICKUP_LIST_ID**: Your ClickUp list ID
- **SCORES_FIELD_ID**: Field ID for scores
- **PLOT_FIELD_ID**: Field ID for plots
- **ANSWERS_FIELD_ID**: Field ID for answers
- **ROUTINES_FIELD_ID**: Field ID for routines
- **ACTIONPLAN_FIELD_ID**: Field ID for action plans
- **TYPEFORM_API_KEY**: Your Typeform API key
- **STRAPI_API_KEY**: Production Strapi API key
- **STRAPI_API_KEY_DEV**: Development Strapi API key
- **FORM_ID**: Typeform form ID
- **LINK_SUMMARY_TITLE_FIELD_ID**: Field ID for link summaries
- **LINK_SUMMARY_SUMMARY_FIELD_ID**: Field ID for summaries
- **LINK_SUMMARY_OPENAI_API_KEY**: OpenAI API key
- **AZURE_BLOB_CONNECTION_STRING**: Azure Blob Storage connection string

#### 3. User Test Service Secrets
- **USER_TEST_CLICKUP_API_KEY**: ClickUp API key for user tests
- **USER_TEST_CLICKUP_LIST_ID**: ClickUp list ID for user tests
- **USER_TEST_KEY_FEEDBACK_FIELD_ID**: Field ID for feedback
- **USER_TEST_EMAIL_FIELD_ID**: Field ID for email
- **USER_TEST_TYPEFORM_API_TOKEN**: Typeform API token

## Deployment Methods

### 1. Automatic Deployment via Azure Pipelines (Current)

The existing Azure Pipelines configuration handles deployments automatically:

- **Main branch**: Deploys to production and dev slots
- **Development branch**: Deploys to dev slot only
- **[user-test] commits**: Deploys user test service
- **[deploy-all] commits**: Deploys all services

### 2. GitHub Actions Deployment (Alternative)

Two workflows are available for GitHub Actions deployment:

#### Deploy Recommendation Service
Triggered on push to main/development branches:
```yaml
.github/workflows/deploy-recommendation-service.yml
```

#### Deploy User Test Service
Triggered when user-test-service files change or manual dispatch:
```yaml
.github/workflows/deploy-user-test-service.yml
```

### Manual Deployment

```bash
# Deploy recommendation service
git push origin main  # or development

# Deploy only user test service
git commit -m "[user-test] Your changes"
git push origin development

# Deploy all services
git commit -m "[deploy-all] Your changes"
git push origin development
```

## Service URLs

### Recommendation Service
- **Production**: https://lthrecommendation.azurewebsites.net
- **Development**: https://lthrecommendation-dev.azurewebsites.net

### User Test Service
- **Development**: https://lthrecommendation-usertest-dev.azurewebsites.net
- **Webhook URL**: https://lthrecommendation-usertest-dev.azurewebsites.net/survey

## Typeform Webhook Configuration

1. Log in to Typeform
2. Go to your form settings
3. Navigate to Connect → Webhooks
4. Add new webhook with URL:
   ```
   https://lthrecommendation-usertest-dev.azurewebsites.net/survey
   ```
5. Enable "Include hidden fields"
6. Test the webhook

## Monitoring

### View Logs
```bash
# Recommendation service logs
az webapp log tail \
  --name lthrecommendation \
  --resource-group lthrecommendation_group

# User test service logs
az webapp log tail \
  --name lthrecommendation \
  --slot usertest-dev \
  --resource-group lthrecommendation_group
```

### Check Deployment Status
```bash
# List deployment slots
az webapp deployment slot list \
  --name lthrecommendation \
  --resource-group lthrecommendation_group \
  -o table

# Show slot configuration
az webapp show \
  --name lthrecommendation \
  --slot usertest-dev \
  --resource-group lthrecommendation_group
```

## Troubleshooting

### Common Issues

1. **Service doesn't start**
   - Check startup command configuration
   - Verify Python version compatibility
   - Review application logs

2. **Environment variables missing**
   - Ensure all secrets are set in GitHub/Azure DevOps
   - Check app settings in Azure Portal

3. **Webhook not receiving data**
   - Verify Typeform webhook configuration
   - Check service logs for incoming requests
   - Ensure hidden fields are included

### Useful Commands

```bash
# Restart a service
az webapp restart \
  --name lthrecommendation \
  --slot usertest-dev \
  --resource-group lthrecommendation_group

# Update app settings
az webapp config appsettings set \
  --name lthrecommendation \
  --slot usertest-dev \
  --resource-group lthrecommendation_group \
  --settings KEY=VALUE

# SSH into container (if enabled)
az webapp ssh \
  --name lthrecommendation \
  --slot usertest-dev \
  --resource-group lthrecommendation_group
```

## Security Notes

- Never commit sensitive data to the repository
- Use Azure Key Vault for production secrets (future enhancement)
- Regularly rotate API keys and tokens
- Monitor access logs for suspicious activity