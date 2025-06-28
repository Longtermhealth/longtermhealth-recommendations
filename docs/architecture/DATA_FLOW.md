# Data Flow Architecture

## Overview
This document describes how data flows through the recommendation engine from user input to final action plan.

## Complete Data Flow

```
1. Typeform Survey
       ↓
2. Webhook POST /webhook
       ↓
3. Extract Responses
       ↓
4. Health Assessment (7 pillars)
       ↓
5. Filter Service
       ↓
6. Scheduler Algorithm
       ↓
7. API Integrations
       ↓
8. User Receives Plan
```

## Detailed Flow

### 1. Typeform Survey Submission
User completes health assessment survey with questions about:
- Personal information (age, gender, height, weight)
- Health habits across 7 pillars
- Time availability
- Equipment access
- Medical conditions

### 2. Webhook Reception
```python
POST /webhook
{
  "event_id": "...",
  "form_response": {
    "answers": [...],
    "hidden": {
      "userid": "123"
    }
  }
}
```

### 3. Response Processing
The system extracts and maps answers to internal data structure:
- Numeric values converted to scales
- Text choices mapped to enums
- Calculations performed (e.g., BMI)

### 4. Health Score Calculation
For each pillar:
1. Extract relevant answers
2. Apply weighted scoring algorithm
3. Normalize to 0-80 scale
4. Assign rating (OPTIMAL/AUSBAUFÄHIG/AKTIONSBEDARF)
5. Generate interpretation text

### 5. Filter Service Processing
1. **Load routine database** from JSON files
2. **Apply exclusions** based on:
   - Equipment requirements
   - Medical contraindications
   - User preferences
3. **Score inclusions** based on:
   - Matching preferences
   - Appropriate difficulty
   - Time constraints
4. **Select packages** based on:
   - Health scores
   - Time availability
   - Special conditions

### 6. Scheduler Algorithm
1. **Initialize 4-week calendar**
2. **Select movement workouts** based on daily time:
   - 20 min: Basic only
   - 40-50 min: Full program
   - 90 min: Complete with all components
3. **Add daily routines** (nutrition, gratitude)
4. **Schedule challenges**:
   - Daily (max 3/week)
   - Weekly (1/week)
   - Monthly (1/month)
5. **Calculate durations** including breaks
6. **Generate final JSON structure**

### 7. External API Integration

#### Strapi CMS
```
POST /api/action-plans
POST /api/health-scores
```
Stores complete action plan and health scores for retrieval by mobile app.

#### Internal Health Score API
```
POST /account/{id}/health-score
```
Notifies internal systems of new health assessment.

#### ClickUp
```
POST /list/{id}/task
```
Creates task with:
- Health score visualization
- User responses
- Action plan details

#### Azure Blob Storage
Stores action plan JSON for long-term retrieval.

### 8. User Access
User receives action plan through:
- Mobile application (via Strapi)
- Email notification
- ClickUp task assignment

## Data Formats

### Input: Typeform Response
```json
{
  "form_response": {
    "answers": [
      {
        "field": {"ref": "flexibility"},
        "choice": {"label": "3"}
      }
    ]
  }
}
```

### Intermediate: Health Scores
```json
{
  "accountId": 123,
  "totalScore": 54.5,
  "pillarScores": [
    {
      "pillar": "MOVEMENT",
      "score": 65.0,
      "rating": "OPTIMAL"
    }
  ]
}
```

### Output: Action Plan
```json
{
  "account": {
    "accountId": 123
  },
  "schedule": {
    "days": [
      {
        "date": "2024-01-01",
        "routines": [
          {
            "routineId": 1001,
            "duration": 30,
            "timeSlot": "MORNING"
          }
        ]
      }
    ]
  }
}
```

## Error Handling

Each stage includes error handling:
1. **Webhook validation** - Verify payload structure
2. **Score calculation** - Handle missing answers
3. **Filtering** - Default to basic routines if no matches
4. **Scheduling** - Ensure minimum viable plan
5. **API calls** - Retry with backoff

## Performance Considerations

- Routine database cached in memory
- Parallel API calls where possible
- Async processing for non-critical paths
- Early termination for invalid inputs

## Monitoring Points

Key metrics tracked:
- Webhook processing time
- Health score distribution
- Filter effectiveness (routines selected/total)
- Scheduler success rate
- API call latency
- Error rates by stage