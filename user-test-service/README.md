# User Test Service

This service handles Typeform webhook integration with ClickUp for user test feedback management.

## Features

- Receives Typeform webhook data
- Formats responses into human-readable feedback
- Updates ClickUp tasks with feedback
- Creates new tasks or subtasks based on user identification

## Setup

1. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example ../.env
   ```

2. Required environment variables:
   - `CLICKUP_API_KEY`: Your ClickUp API key
   - `CLICKUP_LIST_ID`: The ClickUp list ID where tasks are managed
   - `KEY_FEEDBACK_FIELD_ID`: Custom field ID for feedback in ClickUp
   - `EMAIL_FIELD_ID`: Custom field ID for email in ClickUp
   - `TYPEFORM_API_TOKEN`: Your Typeform API token

## Running Locally

### With Docker Compose (Recommended)
From the project root:
```bash
docker-compose up user-test-service
```

### Standalone
```bash
cd user-test-service
pip install -r requirements.txt
python src/app.py
```

## Webhook URL

Once deployed, the webhook URL will be:
- Development: `https://lthrecommendation-dev.azurewebsites.net/user-test/survey`
- Production: `https://lthrecommendation.azurewebsites.net/user-test/survey`

Configure this URL in your Typeform webhook settings.

## API Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `POST /survey` - Typeform webhook endpoint
- `POST /webhook/typeform` - Alternative webhook endpoint

## Deployment

The service is deployed using Azure Pipelines. To deploy only the user test service:

```bash
git commit -m "[user-test] Your changes here"
```

To deploy all services:
```bash
git commit -m "[deploy-all] Your changes here"
```