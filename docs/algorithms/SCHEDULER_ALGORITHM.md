# Scheduler Algorithm Documentation

## Overview
The scheduler creates 4-week personalized action plans based on user health scores and time availability.

## Super Routines

### Sleep Super Routines
- **Abendritual** (ID: 998) - Evening routine for weeks 2-4
- **Schlafzimmer vorbereiten** (ID: 964) - Bedroom preparation for week 1
- **Schlafqualität steigern** (ID: 963) - Sleep quality improvement for weeks 2-4

### Movement Super Routines
- **Fullbody Workout** (ID: 997) - Complete body workout
- **Unterkörper-Krafttraining** (ID: 996) - Lower body strength training
- **Core-Krafttraining** (ID: 994) - Core strength training
- **Oberkörper-Krafttraining** (ID: 995) - Upper body strength training
- **5 Minute Cardio 1-7** (IDs: 988-980) - Seven different 5-minute cardio workouts

### Nutrition Super Routines
- **Bewusste Ernährung** (ID: 999) - Conscious eating habits
- **Anti-Entzündungs-Paket** (ID: 986) - Anti-inflammation package

### Gratitude Super Routine
- **Gratitude Ritual** (ID: 990) - Daily gratitude practice

## Algorithm Flow

### 1. Initialization
- Load routines from JSON data files
- Filter out excluded routines
- Sort by score_rules for prioritization

### 2. Time-Based Workout Selection
The algorithm selects workouts based on daily available time:

#### 20 Minutes Daily
- Movement Basics: 7 tags
- 5 Minute Cardio: All 7 variants

#### 40-50 Minutes Daily
- Movement Basics: 5 tags
- Full Body Workout: 10 tags
- Upper/Lower Body: 3 tags each
- 5 Minute Cardio: All 7 variants

#### 90 Minutes Daily
- Movement Basics: 5 tags
- Full Body Workout: 15 tags
- Upper/Lower Body: 5 tags each
- Core Training: 10 tags
- 5 Minute Cardio: All 7 variants

### 3. Challenge Scheduling

#### Daily Challenges
- Maximum 3 per week
- Scheduled on days 1, 4, and 7
- Based on lowest health score pillars

#### Weekly Challenges
- 1 per week for each pillar
- Distributed across 4 weeks
- Considers health score priorities

#### Monthly Challenges
- 1 challenge for the entire month
- Higher complexity routines

### 4. Special Rules

#### Cognitive Enhancement & Social Engagement
- If COGNITIVE_ENHANCEMENT score < 40: Schedule daily challenges
- If SOCIAL_ENGAGEMENT score < 40: Schedule daily challenges
- Otherwise: Schedule as weekly challenges

#### Movement Ordering
Specific order for movement routines:
1. Warm-up
2. Main exercises
3. Cool-down

#### Left/Right Pairing
Exercise pairs (e.g., "Ausfallschritte links" and "Ausfallschritte rechts") are kept together.

### 5. Duration Calculations

Super routine durations include:
- Sum of all child routine durations
- Break time: 20 seconds per set
- Calculated as: `total_minutes + (break_seconds / 60)`

## Key Functions

### `main(host)`
Entry point that orchestrates the entire scheduling process.

### `select_routines(routines, tag_count, package_tag, movement_order)`
Selects routines based on:
- Tag count limits
- Package categorization
- Movement order requirements
- Left/right exercise pairing

### `add_individual_routine_entry(routine, day_number, week_number)`
Adds routine to action plan with:
- Variation checking (prevents duplicates)
- Proper scheduling metadata
- Image URL handling

### `schedule_all_daily_challenges()`
Distributes daily challenges across the week based on health scores.

### `update_parent_durationCalculated_and_goal()`
Updates super routine durations based on child routines.

## Configuration Constants

```python
# Time slots
DAILY_TIME_OPTIONS = [20, 40, 50, 90]  # minutes

# Schedule period
PERIOD_DAYS = 28  # 4 weeks

# Break times
BREAK_SECONDS_PER_SET = 20

# Maximum challenges
MAX_DAILY_CHALLENGES_PER_WEEK = 3
MAX_WEEKLY_CHALLENGES = 1

# Schedule categories
CATEGORIES = [
    "DAILY_ROUTINE",
    "WEEKLY_ROUTINE", 
    "DAILY_CHALLENGE",
    "WEEKLY_CHALLENGE",
    "MONTHLY_CHALLENGE"
]
```

## Health Pillars
- MOVEMENT
- SLEEP
- NUTRITION
- STRESS
- SOCIAL_ENGAGEMENT
- COGNITIVE_ENHANCEMENT
- GRATITUDE

## Output Format
The scheduler produces a JSON action plan containing:
- User account information
- 4-week schedule with daily routines
- Routine metadata (images, descriptions, durations)
- Challenge assignments
- Total time commitments