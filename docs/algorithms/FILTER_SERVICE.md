# Filter Service Documentation

## Overview
The filter service is responsible for processing user health assessment data and filtering the routine database to provide personalized recommendations.

## Main Entry Point
```python
def main(typeform_data, host)
```
Processes Typeform responses and returns filtered routines with health scores.

## Filtering Pipeline

### 1. Data Extraction
Extracts user responses from Typeform payload:
- Personal data (age, gender, BMI)
- Health preferences
- Equipment availability
- Time commitments
- Medical conditions

### 2. Health Score Calculation
Calculates scores for each health pillar:
- **Movement**: Based on flexibility, activity, cardio frequency, strength
- **Nutrition**: Based on BMI, sugar intake, hydration, alcohol, food quality
- **Sleep**: Based on quality, duration, daytime fatigue
- **Stress**: Based on stress levels and coping mechanisms
- **Social Engagement**: Based on social connections and activities
- **Cognitive Enhancement**: Based on mental activities
- **Gratitude**: Based on gratitude practices

### 3. Order Calculation
Maps scores to difficulty levels (1-5):

#### Standard Mapping
- Score ≤ 16 → Order 1 (Beginner)
- Score ≤ 32 → Order 2 (Basic)
- Score ≤ 48 → Order 3 (Intermediate)
- Score ≤ 64 → Order 4 (Advanced)
- Score > 64 → Order 5 (Expert)

#### Special Cases
- **Movement**: Uses specific assessment answers
- **Stress**: Based on meditation experience
- **Nutrition**: Includes fasting order based on practice

### 4. Filtering Process

#### Phase 1: Equipment Exclusion
```python
exclude_movement_routines_by_equipment(routines, user_data)
```
- Excludes movement routines requiring equipment user doesn't have
- Only applies to MOVEMENT pillar routines

#### Phase 2: Global Exclusions
```python
apply_global_exclusions(routines, rules['exclusion_rules'], user_data)
```
Applies exclusion rules based on:
- Medical conditions (pregnancy, injuries)
- User preferences
- Contraindications

#### Phase 3: Inclusion Scoring
```python
filter_inclusions(routines, rules['inclusion_rules'], user_data)
```
Scores routines based on positive matches:
- Assigns weights to routines matching user preferences
- Higher scores = better matches

#### Phase 4: Display Order Filtering
```python
filter_routines_by_display_order(routines, allowed_display_orders)
```
- Filters based on computed order vs routine's displayForOrder
- Ensures appropriate difficulty level

## Rule Engine

### Rule Structure
```json
{
  "exclusion_rules": [{
    "name": "Exclude pregnancy contraindicated",
    "pillar": "MOVEMENT",
    "conditions": {
      "logic": "and",
      "rules": [{
        "field": "gender",
        "operator": "==",
        "value": "Weiblich"
      }, {
        "field": "pregnant",
        "operator": "==",
        "value": "Ja"
      }]
    },
    "action": {
      "field": "contraindications",
      "value": "PREGNANCY"
    }
  }],
  "inclusion_rules": {
    "MOVEMENT": [{
      "name": "Prefer outdoor activities",
      "conditions": {
        "logic": "or",
        "rules": [{
          "field": "outdoor_preference",
          "operator": "includes",
          "value": "Draußen"
        }]
      },
      "actions": [{
        "field": "locations.locationEnum",
        "value": "OUTDOOR",
        "weight": 2
      }]
    }]
  }
}
```

### Condition Operators
- `>`, `>=`, `<`, `<=` - Numeric comparisons
- `==`, `!=` - Equality checks
- `includes` - Array/string contains

### Evaluation Logic
- `AND` logic: All conditions must be true
- `OR` logic: At least one condition must be true
- Nested conditions supported

## Package Selection

### Movement Packages by Time
- **20 minutes**: MOVEMENT BASICS only
- **40 minutes**: Full program with strength training
- **50 minutes**: Extended program
- **90 minutes**: Complete program with all components

### Special Package Logic
- **Sleep**: Always includes SLEEPING ROOM, optionally SLEEP PROBLEM
- **Nutrition**: May include fasting packages based on user practice
- **Others**: Standard BASICS packages

## Output Format

### Filtered Routines
```json
{
  "id": 123,
  "attributes": {
    "rule_status": "included",
    "score_rules": 5,
    "score_rules_explanation": "Matched 2 inclusion rules",
    "computed_order": 3
  }
}
```

### Health Scores
```json
{
  "data": {
    "accountId": 123,
    "totalScore": 54.5,
    "pillarScores": [{
      "pillar": {
        "pillarEnum": "MOVEMENT",
        "displayName": "Bewegung"
      },
      "score": "65.0",
      "scoreInterpretation": "Gut! Deine Bewegung...",
      "rating": {
        "ratingEnum": "OPTIMAL",
        "displayName": "Optimal"
      }
    }]
  }
}
```

## Key Functions

### `evaluate_conditions(conditions, user_data)`
Recursively evaluates rule conditions with AND/OR logic.

### `check_dynamic_field(field_path, data)`
Retrieves nested field values using dot notation (e.g., "tags.tag").

### `add_default_fields(routines)`
Ensures all routines have required filter fields with defaults.

### `compute_order_for_routine(routine, orders)`
Calculates appropriate order based on routine type and user orders.