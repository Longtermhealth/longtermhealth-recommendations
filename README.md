# LongTermHealth Recommendation Engine

A personalized health recommendation system that generates action plans and tracks health scores based on user data.

## Overview

The Recommendation Engine analyzes user health data from Typeform surveys and generates personalized action plans with scheduled routines across different health pillars (Movement, Nutrition, Sleep, Stress, Social Engagement, Cognitive Enhancement, and Gratitude).

## Architecture

```
   src/                    # Source code
      app.py             # Flask application entry point
      config.py          # Configuration management
      scheduling/        # Action plan generation
      services/          # Business logic services
      utils/             # Utility functions
   docker/                # Docker configurations
   data/                  # Static data files
   tests/                 # Test suite
   config/                # Configuration files
```

## Key Components

### 1. Flask Application (`src/app.py`)
- Main entry point for the web service
- Handles webhook endpoints for Typeform data
- Processes health questionnaire responses

### 2. Scheduler (`src/scheduling/scheduler.py`)
- Core algorithm for generating personalized action plans
- Schedules routines based on user preferences and health scores
- Manages weekly and daily routine distribution

### 3. Action Plan Service (`src/services/action_plan/`)
- Processes and structures action plans
- Handles routine selection and customization
- Manages super routines and sub-routines

### 4. Strapi Integration (`src/utils/strapi_api.py`)
- Posts action plans to Strapi CMS
- Posts health scores to Strapi
- Posts health scores to internal API endpoints

## Environment Variables

Required environment variables (store in `.env` file):

```bash
# ClickUp Integration
CLICKUP_API_KEY=your_clickup_api_key
CLICKUP_LIST_ID=your_list_id
SCORES_FIELD_ID=field_id
PLOT_FIELD_ID=field_id
ANSWERS_FIELD_ID=field_id
ROUTINES_FIELD_ID=field_id
ACTIONPLAN_FIELD_ID=field_id

# Typeform Integration
TYPEFORM_API_KEY=your_typeform_api_key
FORM_ID=your_form_id

# Strapi API Keys
STRAPI_API_KEY=your_staging_api_key
STRAPI_API_KEY_DEV=your_dev_api_key

# Internal API Keys
INTERNAL_API_KEY_DEV=your_internal_dev_key
INTERNAL_API_KEY_STAGING=your_internal_staging_key

# Azure Storage
AZURE_BLOB_CONNECTION_STRING=your_connection_string

# OpenAI (for link summaries)
LINK_SUMMARY_OPENAI_API_KEY=your_openai_key
```

## Local Development

### Prerequisites
- Python 3.9+
- Docker and Docker Compose
- Azure CLI (for deployment)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Longtermhealth/longtermhealth-recommendations.git
cd longtermhealth-recommendations
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file with required environment variables

5. Run locally:
```bash
python -m src.app
```

### Docker Development

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

2. The service will be available at `http://localhost:5003`

## API Endpoints

### POST `/`
Main webhook endpoint for Typeform data processing.

**Request Body:**
- Typeform webhook payload containing user responses

**Response:**
- 200: Successfully processed
- 400: Bad request
- 500: Internal server error

### GET `/health`
Health check endpoint.

## Deployment

### GitHub Actions
Automated deployment via `.github/workflows/main_lthrecommendation.yml`:
- Builds Docker image
- Pushes to Azure Container Registry
- Deploys to Azure App Service

### Azure Pipeline
Alternative deployment via `azure-pipelines.yml`:
- Supports both production and development deployments
- Handles container registry authentication
- Manages deployment slots

### Deployment Environments
- **Production**: Deployed from `main` branch
- **Development**: Deployed from `development` branch

## Testing

Run tests with pytest:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=src
```

## Data Flow

1. **User completes Typeform survey** � Webhook triggered
2. **Flask app receives data** � Processes responses
3. **Health scores calculated** � Based on survey answers
4. **Action plan generated** � Personalized routines scheduled
5. **Data posted to Strapi** � Action plans and health scores stored
6. **Internal API notified** � Health scores sent to internal system
7. **ClickUp task created** � Tracking and visualization

## Configuration Files

- `requirements.txt` - Python dependencies
- `setup.py` - Package configuration
- `pytest.ini` - Test configuration
- `docker/Dockerfile` - Production Docker image
- `docker/Dockerfile.dev` - Development Docker image
- `docker/docker-compose.yml` - Local development setup

## Troubleshooting

### Common Issues

1. **401 Unauthorized errors**
   - Check if API keys are expired
   - Verify environment variables are set correctly

2. **Action plan generation fails**
   - Check data files in `/data` directory
   - Verify Typeform response format

3. **Docker build issues**
   - Ensure all environment variables are passed in build args
   - Check Dockerfile path references

## Contributing

1. Create feature branch from `development`
2. Make changes and test thoroughly
3. Create pull request to `development`
4. After review, merge to `main` for production deployment

## License

Proprietary - LongTermHealth GmbH