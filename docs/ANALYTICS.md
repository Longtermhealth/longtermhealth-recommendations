# Analytics Module Documentation

## Overview

The analytics module provides comprehensive analysis of user completion data, generating insights, trends, and recommendations to improve user engagement and health outcomes.

## Architecture

The analytics module consists of four main components:

### 1. Event Processor (`event_processor.py`)
- Processes raw completion event data from webhooks
- Extracts and structures analytics data
- Calculates summary statistics

### 2. Metrics Calculator (`metrics_calculator.py`)
- Calculates detailed metrics from processed events
- Computes engagement scores, completion rates, and consistency scores
- Maintains historical metrics cache

### 3. Trend Analyzer (`trend_analyzer.py`)
- Analyzes historical data to identify trends
- Predicts future performance
- Identifies risks and opportunities

### 4. Insights Engine (`insights_engine.py`)
- Generates human-readable insights
- Creates prioritized recommendations
- Identifies achievements and alerts

## Key Features

### Real-time Analytics
- Process completion events as they arrive
- Calculate metrics instantly
- Generate actionable insights

### Comprehensive Metrics
- **Engagement Score**: Overall user engagement (0-100)
- **Completion Score**: Success rate per pillar (0-100)
- **Consistency Score**: Measure of routine consistency
- **Habit Formation Index**: Likelihood of habit formation

### Trend Analysis
- Weekly and monthly trend detection
- Performance predictions
- Momentum analysis
- Risk identification

### Intelligent Insights
- Executive summaries
- Pillar-specific insights
- Behavioral pattern recognition
- Personalized recommendations

## API Endpoints

### Process Event
```
POST /api/analytics/process-event
```
Process a completion event and generate analytics.

**Request Body:**
```json
{
    "accountId": 5,
    "actionPlanUniqueId": "uuid",
    "pillarCompletionStats": [...],
    "changeLog": [...]
}
```

### Get Analytics Summary
```
GET /api/analytics/summary/{account_id}?days=7
```
Get analytics summary for an account over specified days.

### Get Pillar Analytics
```
GET /api/analytics/pillar/{account_id}/{pillar}
```
Get detailed analytics for a specific pillar.

### Get Latest Insights
```
GET /api/analytics/insights/{account_id}
```
Get latest insights and recommendations.

## Usage Example

```python
from src.analytics import AnalyticsService

# Initialize service
analytics_service = AnalyticsService()

# Process an event
result = analytics_service.process_event(event_data)

# Get summary
summary = analytics_service.get_analytics_summary(account_id=5, days=7)
```

## Metrics Explained

### Engagement Score
- Measures overall user participation
- Factors: active routines, completion rates, consistency
- Range: 0-100 (higher is better)

### Completion Score
- Success rate for routines within a pillar
- Weighted by engagement and actual completions
- Range: 0-100

### Consistency Score
- Measures variation in completion patterns
- Lower variance = higher consistency
- Important for habit formation

### Habit Formation Index
- Predicts likelihood of routine becoming a habit
- Based on consistency and frequency
- Range: 0-100

## Insights Categories

### Achievements
- High engagement (80%+)
- Consistency masters (90%+)
- Rising stars (strong improvement)
- Perfect routines

### Alerts
- Abandoned pillars
- Rapid decline in engagement
- Routine overload
- Low performance warnings

### Recommendations
- High priority: Risk mitigation
- Medium priority: Opportunities
- Low priority: Optimizations

## Integration

The analytics module integrates with:
- Webhook processing for real-time events
- Health score calculations
- Action plan recommendations
- User dashboards

## Performance Considerations

- Events are processed asynchronously
- Metrics are cached for performance
- Historical data limited to prevent memory issues
- Batch processing available for bulk analysis