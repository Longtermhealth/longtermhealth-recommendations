# Routine Data Model

## Overview
Routines are the core building blocks of action plans. Each routine represents a health-related activity that users can perform.

## Routine Structure

### Core Attributes
```json
{
  "id": 123,
  "attributes": {
    "routineId": 1001,
    "displayName": "Morgenyoga",
    "description": "Eine sanfte Yoga-Routine...",
    "pillar": {
      "pillarEnum": "MOVEMENT",
      "displayName": "Bewegung"
    },
    "duration": 30,
    "frequency": "DAILY",
    "timeOfDay": "MORNING|AFTERNOON|EVENING|ANY",
    "imageUrl_1x1": "https://...",
    "imageUrl_16x9": "https://..."
  }
}
```

### Movement-Specific Attributes
```json
{
  "movementType": "mobility|cardio|strength",
  "equipmentNeeded": [
    {
      "equipmentEnum": "NONE|YOGAMATTE|HANTELN|KETTLEBELL|..."
    }
  ],
  "locations": [
    {
      "locationEnum": "INDOOR|OUTDOOR"
    }
  ]
}
```

### Scheduling Attributes
```json
{
  "scheduleDays": [1, 2, 3, 4, 5, 6, 7],
  "scheduleWeeks": [1, 2, 3, 4],
  "scheduleCategory": "DAILY_ROUTINE|WEEKLY_ROUTINE|DAILY_CHALLENGE|WEEKLY_CHALLENGE|MONTHLY_CHALLENGE",
  "displayForOrder": "1,2,3,4,5",
  "order": 3
}
```

### Tags and Categorization
```json
{
  "tags": {
    "tag": "BASICS|MOVEMENT_BASICS|5_MINUTE_CARDIO|...",
    "movement_order": 1-10,
    "sets": 3,
    "isPairExercise": true,
    "pairId": "exercise_pair_123"
  },
  "contraindications": [
    "PREGNANCY",
    "BACK_PAIN",
    "KNEE_PROBLEMS"
  ]
}
```

### Super Routine Attributes
```json
{
  "isSuperRoutine": true,
  "subRoutines": [1444, 1445, 1446],
  "parentRoutineId": 998,
  "durationCalculated": 45,
  "goal": {
    "amount": 1,
    "unit": {
      "amountUnitEnum": "ROUTINE|MINUTES",
      "displayName": "Routine"
    }
  }
}
```

### Filter Service Additions
```json
{
  "rule_status": "excluded|included|no_rule_applied",
  "score_rules": 0-100,
  "score_rules_explanation": "Excluded due to equipment requirement",
  "computed_order": 1-5
}
```

## Routine Types

### 1. Regular Routines
Standard activities with fixed duration and frequency.

### 2. Super Routines
Container routines that include multiple sub-routines:
- Sleep Superroutine (Abendritual)
- Movement Superroutines (Full Body, Upper Body, Lower Body, Core)
- Nutrition Superroutine (Bewusste Ernährung)
- Gratitude Superroutine

### 3. Challenges
Special routines designed to push users:
- **Daily Challenges**: Quick daily activities
- **Weekly Challenges**: More complex weekly goals
- **Monthly Challenges**: Long-term habit formation

### 4. Paired Exercises
Movement exercises that come in left/right pairs:
- Identified by `isPairExercise: true`
- Share the same `pairId`
- Must be scheduled together

## Pillar Enum Values
- `MOVEMENT`
- `NUTRITION`
- `SLEEP`
- `SOCIAL_ENGAGEMENT`
- `STRESS`
- `GRATITUDE`
- `COGNITIVE_ENHANCEMENT`
- `BASICS`
- `SCORES`

## Equipment Enum Values
- `NONE` - No equipment needed
- `YOGAMATTE` - Yoga mat
- `HANTELN` - Dumbbells
- `KETTLEBELL` - Kettlebell
- `WIDERSTANDSBAND` - Resistance band
- `GYMNASTIKBALL` - Exercise ball
- `FOAM_ROLLER` - Foam roller
- `SPRINGSEIL` - Jump rope

## Time of Day Values
- `MORNING` - 06:00-12:00
- `AFTERNOON` - 12:00-18:00
- `EVENING` - 18:00-23:00
- `ANY` - Any time

## Display Order Logic
The `displayForOrder` field contains comma-separated values indicating which user order levels can see this routine:
- Order 1: Beginner
- Order 2: Basic
- Order 3: Intermediate
- Order 4: Advanced
- Order 5: Expert

Example: `"1,2,3"` means the routine is visible for beginners through intermediate users.