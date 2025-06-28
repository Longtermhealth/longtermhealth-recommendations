# API Reference

## Flask Application Endpoints

### Health Check
**GET /**
- Returns service health status
- Response: `{"status": "healthy", "service": "lth-recommendation"}`

### Event Processing
**POST /event**
- Processes action plan events
- Request body:
```json
{
  "eventEnum": "RECALCULATE_ACTION_PLAN" | "RENEW_ACTION_PLAN",
  // Additional event data
}
```

### Webhook Processing
**POST /webhook**
- Main Typeform webhook endpoint
- Headers:
  - `X-Webhook-Followup: true` (for follow-up webhooks)
- Triggers action plan generation

### Analytics Endpoints

**POST /analytics/process**
- Process webhook data for analytics insights

**GET /analytics/user/{user_id}**
- Get user analytics history
- Query params: `days` (default: 30)

**GET /analytics/user/{user_id}/aggregate**
- Get aggregated analytics
- Query params: `period` (week/month/quarter)

**GET /analytics/insights/{user_id}**
- Get latest insights for user

**POST /api/analytics/event**
- Process completion event
- Request body:
```json
{
  "accountId": 123,
  "actionPlanUniqueId": "uuid",
  "pillarCompletionStats": {...}
}
```

**GET /api/analytics/summary/{account_id}**
- Get analytics summary
- Query params: `days` (default: 7)

## External API Integrations

### Strapi CMS

#### Base URLs
- Development: `http://4.182.8.101:7004/api`
- Staging: `http://4.182.8.101:8004/api`

#### Authentication
```
Authorization: Bearer {STRAPI_API_KEY}
```

#### Endpoints Used

**GET /action-plans**
- Filter by actionPlanUniqueId or accountId
- Used to retrieve existing action plans

**POST /action-plans**
- Create new action plan
- Request includes full action plan JSON

**GET /health-scores**
- Filter by accountId
- Retrieve health score history

**POST /health-scores**
- Store health scores
- Includes pillar scores and interpretations

**GET /routines**
- Paginated routine retrieval
- Includes full routine details with populate=*

### Internal Health Score API

#### Base URLs
- Development: `https://bluesphere.dev.longtermhealth.de`
- Staging: `https://bluesphere.staging.longtermhealth.de`

#### Authentication
```
INTERNAL_API_KEY: {key}
```

#### Endpoint
**POST /account/{accountId}/health-score**
- Same payload as Strapi health scores
- Used for internal system integration

### ClickUp API

#### Base URL
`https://api.clickup.com/api/v2`

#### Authentication
```
Authorization: {CLICKUP_API_KEY}
```

#### Endpoints Used

**POST /list/{list_id}/task**
- Create health assessment tasks
- Includes custom fields for:
  - Health scores (SCORES_FIELD_ID)
  - Visualization plot (PLOT_FIELD_ID)
  - User answers (ANSWERS_FIELD_ID)
  - Selected routines (ROUTINES_FIELD_ID)
  - Action plan (ACTIONPLAN_FIELD_ID)

**POST /task/{task_id}/attachment**
- Upload files to tasks
- Used for plot images

**POST /task/{task_id}/field/{field_id}**
- Update custom fields
- Used to add data after task creation

## Environment Variables

### API Keys
- `STRAPI_API_KEY` - Staging Strapi authentication
- `STRAPI_API_KEY_DEV` - Development Strapi authentication
- `INTERNAL_API_KEY_DEV` - Internal API (dev)
- `INTERNAL_API_KEY_STAGING` - Internal API (staging)
- `CLICKUP_API_KEY` - ClickUp authentication

### ClickUp Configuration
- `CLICKUP_LIST_ID` - Target list for tasks
- `SCORES_FIELD_ID` - Custom field for health scores
- `PLOT_FIELD_ID` - Custom field for visualizations
- `ANSWERS_FIELD_ID` - Custom field for user responses
- `ROUTINES_FIELD_ID` - Custom field for routines
- `ACTIONPLAN_FIELD_ID` - Custom field for action plan

## Error Handling

All endpoints return appropriate HTTP status codes:
- 200: Success
- 400: Bad request
- 401: Unauthorized
- 404: Not found
- 500: Internal server error

Error responses include message details when applicable.