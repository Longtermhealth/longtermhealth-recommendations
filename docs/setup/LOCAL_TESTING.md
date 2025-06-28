# Local Testing Guide

## Prerequisites
- Python 3.9+
- Docker and Docker Compose (optional)
- Environment variables configured

## Option 1: Run with Python directly

### 1. Set up virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set environment variables
Create a `.env` file in the project root:
```bash
# Flask settings
export FLASK_ENV=development
export FLASK_DEBUG=1

# API Keys (get these from your team/config)
export CLICKUP_API_KEY=your_clickup_api_key
export CLICKUP_LIST_ID=your_list_id
export TYPEFORM_API_KEY=your_typeform_api_key
export FORM_ID=your_form_id
export STRAPI_API_KEY=your_strapi_api_key
export STRAPI_API_KEY_DEV=your_strapi_dev_api_key
export STRAPI_BASE_URL=https://api.longtermhealth.de/api

# Field IDs
export SCORES_FIELD_ID=your_scores_field_id
export PLOT_FIELD_ID=your_plot_field_id
export ANSWERS_FIELD_ID=your_answers_field_id
export ROUTINES_FIELD_ID=your_routines_field_id
export ACTIONPLAN_FIELD_ID=your_actionplan_field_id

# Optional
export LINK_SUMMARY_OPENAI_API_KEY=your_openai_key
export AZURE_BLOB_CONNECTION_STRING=your_azure_connection
```

Then load the environment:
```bash
source .env  # On Windows: use set instead of export in .env file
```

### 3. Run the application
```bash
# From project root
python -m src.app
```

The app should start on http://localhost:5003

## Option 2: Run with Docker

### 1. Build and run with docker-compose
```bash
# Build the image
docker-compose build

# Run the container
docker-compose up
```

### 2. With environment variables
```bash
# Create .env file with all variables above, then:
docker-compose --env-file .env up
```

## Testing the Endpoints

### 1. Health Check
```bash
curl http://localhost:5003/
```
Expected response:
```json
{"status": "healthy", "service": "lth-recommendation"}
```

### 2. Event Endpoint - RECALCULATE_ACTION_PLAN
```bash
curl -X POST http://localhost:5003/event \
  -H "Content-Type: application/json" \
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
  }'
```

### 3. Event Endpoint - RENEW_ACTION_PLAN
```bash
curl -X POST http://localhost:5003/event \
  -H "Content-Type: application/json" \
  -d '{
    "eventEnum": "RENEW_ACTION_PLAN",
    "eventPayload": {
      "actionPlanUniqueId": "test-plan-123",
      "accountId": 12345,
      "changeLog": [
        {
          "eventEnum": "ROUTINE_SCHEDULE_CHANGE",
          "changeTarget": "ROUTINE",
          "targetId": "1",
          "eventDate": "2024-01-15",
          "eventDetails": {
            "scheduleCategory": "WEEKLY_ROUTINE"
          },
          "changes": [
            {
              "changedProperty": "SCHEDULE_DAYS",
              "newValue": "[1,3,5]"
            }
          ]
        }
      ]
    }
  }'
```

### 4. Webhook Endpoint
```bash
curl -X POST http://localhost:5003/webhook \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Debugging Tips

### 1. Check logs
```bash
# If running with Python
# Logs will appear in terminal

# If running with Docker
docker-compose logs -f
```

### 2. Common Issues

**Port already in use:**
```bash
# Check what's using port 5003
lsof -i :5003

# Kill the process or change port in app.py
```

**Import errors:**
```bash
# Make sure PYTHONPATH includes project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Missing environment variables:**
```bash
# Check which are set
env | grep STRAPI
env | grep CLICKUP
env | grep TYPEFORM
```

### 3. Test with minimal setup
If you don't have all API keys, you can still test the health endpoint:
```bash
# Just run with minimal env
export FLASK_ENV=development
python -m src.app
```

## Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_app.py
```

## Development Mode Features
When `FLASK_ENV=development`:
- Auto-reload on code changes
- Detailed error pages
- Debug logging enabled

## Production Considerations
For production-like testing:
```bash
export FLASK_ENV=production
gunicorn --bind 0.0.0.0:5003 --workers 3 src.app:app
```