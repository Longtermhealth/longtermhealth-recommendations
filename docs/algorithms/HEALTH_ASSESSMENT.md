# Health Assessment Documentation

## Overview
The health assessment system evaluates user health across 7 pillars based on Typeform survey responses, calculating scores that drive personalized action plan generation.

## Health Pillars

### 1. Movement (Bewegung)
Assesses physical activity and fitness levels.

**Key Questions:**
- "Wie schätzt du deine Beweglichkeit ein?" (Flexibility: 1-5)
- "Wie aktiv bist du im Alltag?" (Daily activity: 1-5)
- "Wie oft in der Woche treibst du eine Cardio-Sportart?" (Cardio frequency)
- "Wie schätzt du deine Kraft ein?" (Strength: 1-5)

**Scoring Weights:**
- Flexibility: 10%
- Cardio frequency: 40%
- Daily activity: 30%
- Strength: 20%

### 2. Nutrition (Ernährung)
Evaluates dietary habits and nutritional health.

**Key Metrics:**
- BMI calculation from height/weight
- Sugar consumption (1-5 scale)
- Hydration levels (glasses per day)
- Alcohol consumption
- Food quality indicators

**Special Considerations:**
- Fasting practices mapped to different orders
- BMI must be ≥ 18 for fasting recommendations

### 3. Sleep (Schlaf)
Measures sleep quality and habits.

**Assessment Factors:**
- Sleep quality (1-5)
- Sleep duration (hours)
- Daytime fatigue levels
- Morning/evening outdoor time
- Sleep environment factors

### 4. Stress
Evaluates stress levels and management strategies.

**Key Components:**
- Current stress level (1-5)
- Coping mechanisms effectiveness
- Meditation experience
- Unhealthy coping patterns (reverse scored)

**Meditation Mapping:**
- "Nein" → Order 1
- "Würde ich gern, aber ich weiß nicht wie" → Order 2
- "Habe ich schon mal" → Order 3
- "Mache ich schon" → Order 4

### 5. Social Engagement (Soziales)
Assesses social connections and activities.

**Evaluation Areas:**
- Quality of relationships
- Frequency of social interactions
- Social support systems
- Community involvement

### 6. Cognitive Enhancement (Kognition)
Measures mental stimulation and cognitive activities.

**Assessment Points:**
- Learning activities
- Mental challenges
- Creative pursuits
- Cognitive exercise frequency

### 7. Gratitude (Dankbarkeit)
Evaluates gratitude practices and positive mindset.

**Key Factors:**
- Gratitude journaling
- Appreciation practices
- Positive thinking patterns
- Mindfulness activities

## Score Calculation

### Individual Pillar Scores
Each pillar is scored on a 0-80 scale:
```python
# Example from Movement assessment
raw_score = (flexibility * 0.10 + 
             cardio * 0.40 + 
             activity * 0.30 + 
             strength * 0.20)
normalized_score = (raw_score / 5) * 80
```

### Total Health Score
```python
total_score = sum(all_pillar_scores) / len(pillars)
```

### Score Ratings
Scores are categorized into three levels:

| Rating | Score Range | German Term | Meaning |
|--------|------------|-------------|---------|
| OPTIMAL | ≥ 64 | Optimal | Excellent health in this area |
| AUSBAUFÄHIG | 40-63 | Ausbaufähig | Room for improvement |
| AKTIONSBEDARF | < 40 | Aktionsbedarf | Action required |

## Score Interpretations

Each rating has pillar-specific interpretations:

### Movement Examples
- **OPTIMAL**: "Fantastische Leistung! Deine regelmäßige Bewegung stärkt deine Gesundheit optimal. Weiter so!"
- **AUSBAUFÄHIG**: "Gut! Mit etwas mehr Bewegung kannst du deine Fitness weiter steigern."
- **AKTIONSBEDARF**: "Mehr Bewegung würde dir guttun. Starte mit kleinen Schritten für große Wirkung."

### Nutrition Examples
- **OPTIMAL**: "Hervorragend! Deine ausgewogene Ernährung ist die perfekte Grundlage für deine Gesundheit."
- **AUSBAUFÄHIG**: "Gut! Ein paar Anpassungen können deine Ernährung noch gesünder machen."
- **AKTIONSBEDARF**: "Achte mehr auf eine ausgewogene Ernährung. Gesunde Essgewohnheiten geben dir Energie."

## Dynamic Score Updates

Scores can be updated based on routine completion:

```python
def update_score(init_score, completed_count, not_completed_count):
    K_FACTOR = 0.2  # Sensitivity factor
    
    # Dampening prevents extreme score changes
    dampening = (100 - init_score) / 90.0
    
    # Calculate positive impact from completions
    delta_completed = 10 * dampening * (1 - math.exp(-K_FACTOR * completed_count))
    
    # Calculate negative impact from non-completions (reduced by factor of 3)
    delta_not = 10 * dampening * (1 - math.exp(-K_FACTOR * not_completed_count))
    
    # Final score adjustment
    final_delta = delta_completed - (delta_not / 3.0)
    new_score = init_score + final_delta
    
    return max(0, min(80, new_score))  # Clamp to 0-80 range
```

## Integration with Action Plans

Health scores drive action plan generation:

1. **Package Selection**: Low scores trigger specific intervention packages
2. **Routine Difficulty**: Orders (1-5) based on score thresholds
3. **Challenge Frequency**: Lower scores may trigger daily vs. weekly challenges
4. **Priority Scheduling**: Lower-scoring pillars get priority in scheduling

## Special Logic

### Movement Order Calculation
Instead of using scores, movement uses specific answers:
- Flexibility answer → `order_mobility`
- Cardio frequency → `order_cardio`
- Strength answer → `order_strength`

### Conditional Assessments
- Fasting recommendations require BMI ≥ 18
- Pregnancy status affects movement recommendations
- Age factors into intensity recommendations

## Data Flow
1. **Typeform Response** → Raw answers
2. **Answer Mapping** → Convert to assessment inputs
3. **Score Calculation** → Individual pillar scores
4. **Rating Assignment** → OPTIMAL/AUSBAUFÄHIG/AKTIONSBEDARF
5. **Interpretation** → Human-readable feedback
6. **Action Plan Input** → Drive routine selection