import json
import random
from collections import defaultdict

import math
from datetime import datetime

from chart.chart_generation import generate_polar_chart
from chart.converter import create_final_image
from scheduling.filter_service import main as get_routines_with_defaults
from utils.blob_upload import upload_to_blob
from utils.clickup_api import upload_file_to_clickup
from utils.strapi_api import strapi_post_action_plan, strapi_post_health_scores

WEIGHTINGS = {
    "MOVEMENT": 0.25,
    "NUTRITION": 0.25,
    "SLEEP": 0.15,
    "SOCIAL_ENGAGEMENT": 0.15,
    "STRESS": 0.10,
    "GRATITUDE": 0.05,
    "COGNITIVE_ENHANCEMENT": 0.05
}

THRESHOLDS = {
    "MOVEMENT": 100,
    "NUTRITION": 100,
    "SLEEP": 100,
    "SOCIAL_ENGAGEMENT": 100,
    "STRESS": 100,
    "GRATITUDE": 100,
    "COGNITIVE_ENHANCEMENT": 100
}

def filter_routines_by_pillar_and_time(pillar, total_duration_daily, filtered_routines):
    routines_for_pillar = []

    for routine in filtered_routines:
        if isinstance(routine, dict):
            pillar_value = routine.get('attributes', {}).get('pillar', None)

            if isinstance(pillar_value, list):
                print(f"Found list in pillar: {pillar_value}")
                pillar_value = pillar_value[0] if pillar_value else None

            if pillar_value:
                routine_pillar = pillar_value.get('pillar')

                if routine_pillar == pillar:
                    routine_duration = routine.get('attributes', {}).get('durationCalculated', 0)
                    routine_name = routine.get('attributes', {}).get('name', 0)
                    tags = [t['tag'] for t in routine.get('attributes', {}).get('tags', {})]
                    if 'cardio' in tags:
                        print("Routine with tag 'cardio'.", routine_name)
                        if routine_duration <= total_duration_daily and routine_duration > 1:
                            routines_for_pillar.append(routine)

    return routines_for_pillar

def load_routines_for_rules(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        routines_list = json.load(f)
    routines = {routine['id']: routine for routine in routines_list}
    return routines

def calculate_weighted_score_knapsack(routine, weights):
    base_score = routine.get("score_rules", 0)

    impact_values = {
        "Movement": routine.get('attributes', {}).get("impactMovement", 1),
        "Nutrition": routine.get('attributes', {}).get("impactNutrition", 1),
        "Sleep": routine.get('attributes', {}).get("impactSleep", 1),
        "Stress": routine.get('attributes', {}).get("impactStress", 1),
        "Social": routine.get('attributes', {}).get("impactSocial", 1),
        "Gratitude": routine.get('attributes', {}).get("impactGratitude", 1),
        "Cognitive": routine.get('attributes', {}).get("impactCognitive", 1)
    }

    weighted_score = 0

    for key, impact in impact_values.items():
        weight = weights.get(key.upper(), 1)
        weighted_score += impact * weight

    benefit_score = 0
    benefits = routine.get('attributes', {}).get('benefits', [])
    for benefit in benefits:
        benefit_impact = benefit.get('impact', 0)
        benefit_score += benefit_impact
    total_score = base_score + weighted_score + benefit_score
    return total_score


def calculate_weighted_score(routine, weights):
    base_score = routine.get("score_rules", 0)

    impact_values = {
        "Movement": routine.get("impactMovement", 1),
        "Nutrition": routine.get("impactNutrition", 1),
        "Sleep": routine.get("impactSleep", 1),
        "Stress": routine.get("impactStress", 1),
        "Social": routine.get("impactSocial", 1),
        "Gratitude": routine.get("impactGratitude", 1),
        "Cognitive": routine.get("impactCognitive", 1)
    }

    weighted_score = 0

    for key, impact in impact_values.items():
        weight = weights.get(key.upper(), 1)
        weighted_score += impact * weight

    return base_score + weighted_score

def calculate_daily_allocations_by_weightings(daily_time, weightings):
    return {pillar: daily_time * weight for pillar, weight in weightings.items()}
def calculate_daily_allocations_by_scores(daily_time, scores, thresholds):
    inverted_scores = {pillar: max(0, thresholds[pillar] - score) for pillar, score in scores.items()}
    total_inverted_score = sum(inverted_scores.values())
    if total_inverted_score == 0:
        return {pillar: 0 for pillar in scores.keys()}

    allocations = {pillar: daily_time * (inverted_score / total_inverted_score) for pillar, inverted_score in
                   inverted_scores.items()}

    rounded_allocations = {pillar: math.ceil(allocation) if allocation < 1 else round(allocation) for pillar, allocation
                           in allocations.items()}

    total_rounded_allocation = sum(rounded_allocations.values())
    difference = daily_time - total_rounded_allocation

    while difference != 0:
        for pillar in rounded_allocations.keys():
            if difference == 0:
                break
            if difference > 0:
                rounded_allocations[pillar] += 1
                difference -= 1
            elif difference < 0 and rounded_allocations[pillar] > 0:
                rounded_allocations[pillar] -= 1
                difference += 1
    return rounded_allocations

def combine_allocations(allocations_by_scores, allocations_by_weightings, score_weight=0.7):
    combined_allocations = {
        pillar: (score_weight * allocations_by_scores.get(pillar, 0) + (
                1 - score_weight) * allocations_by_weightings.get(pillar, 0))
        for pillar in allocations_by_weightings.keys()
    }
    combined_allocations = {pillar: round(time) for pillar, time in combined_allocations.items()}

    return combined_allocations


def get_routines_by_ids(routines, routine_ids):
    filtered_routines = {}
    for routine_id in routine_ids:
        for routine in routines:
            if routine['id'] == routine_id:
                filtered_routines[routine_id] = routine
                break
    return filtered_routines


def build_final_action_plan(routines, routine_schedule, account_id, daily_time, routines_for_super_routine,
                            super_routine_id, max_subroutines_per_superroutine=5):

    if super_routine_id == "sleep_superroutine" and len(routines_for_super_routine) == 0:
        return {"data": {"accountId": account_id, "totalDailyTimeInMins": daily_time, "routines": []}}, 0


    final_action_plan = {
        "data": {
            "accountId": account_id,
            "totalDailyTimeInMins": daily_time,
            "routines": []
        }
    }

    super_routine_mapping = {
        "nutrition_super_routine": 223,
        "movement_superroutine": 221,
        "sleep_superroutine": 222,
    }

    parentRoutineId_value = super_routine_mapping.get(super_routine_id, None)

    pillar_mapping = {
        "sleep_superroutine": "SLEEP",
        "movement_superroutine": "MOVEMENT",
        "nutrition_super_routine": "NUTRITION",
    }

    pillar = pillar_mapping.get(super_routine_id, None)

    image_url_mapping = {
        "movement_superroutine": "https://lthstore.blob.core.windows.net/images/997.jpg",
        "sleep_superroutine": "https://lthstore.blob.core.windows.net/images/998.jpg",
        "nutrition_super_routine": "https://lthstore.blob.core.windows.net/images/999.jpg",
    }

    imageUrl = image_url_mapping.get(super_routine_id, None)

    description_mapping = {
        "sleep_superroutine": "Entwickle ein tägliches Schlafritual, um den Körper und Geist auf die anstehende Schlafphase vorzubereiten und so ein einfacheres Einschlafen zu fördern.",
        "movement_superroutine": "Ein Fullbody Workout kombiniert Warm-up, Cardio, Krafttraining und Cool-down, um den ganzen Körper effektiv zu trainieren. Nach einer kurzen Aufwärmphase folgen Ausdauerübungen und gezielte Kraftübungen für alle Muskelgruppen. Abschließend sorgen Dehnübungen für eine bessere Regeneration und Entspannung.",
        "nutrition_super_routine": "Eine gesunde Ernährung basiert auf einer ausgewogenen Mischung aus frischen, unverarbeiteten Lebensmitteln wie Obst, Gemüse, Vollkornprodukten, gesunden Fetten und hochwertigen Proteinquellen. Sie liefert alle wichtigen Nährstoffe, fördert Energie, Wohlbefinden und unterstützt langfristig die Gesundheit. Ausreichendes Trinken von Wasser und das Reduzieren von Zucker, Salz und stark verarbeiteten Lebensmitteln gehören ebenfalls dazu.",
    }

    description = description_mapping.get(super_routine_id, None)

    display_name_mapping = {
        "sleep_superroutine": "Abendritual",
        "movement_superroutine": "Fullbody Workout",
        "nutrition_super_routine": "Gesunde Ernährung",
    }

    displayName = display_name_mapping.get(super_routine_id, None)

    pillar_de_mapping = {
        "sleep_superroutine": "Schlaf",
        "movement_superroutine": "Bewegung",
        "nutrition_super_routine": "Ernährung",
    }

    pillar_de = pillar_de_mapping.get(super_routine_id, None)

    timeOfDay_mapping = {
        "sleep_superroutine": "EVENING",
        "movement_superroutine": "ANY",
        "nutrition_super_routine": "ANY",
    }

    timeOfDay = timeOfDay_mapping.get(super_routine_id, None)


    scheduleDays_mapping = {
        "sleep_superroutine": [1, 2, 3, 4, 5, 6, 7],
        "movement_superroutine": [1, 2, 3, 4, 5],
        "nutrition_super_routine": [1, 2, 3, 4, 5, 6, 7],
    }

    scheduleDays = scheduleDays_mapping.get(super_routine_id, None)

    added_subroutines = set()
    subroutines_entries = []
    total_duration = 0

    subroutine_ids = list(routines_for_super_routine)[:max_subroutines_per_superroutine]
    print('subroutine_ids',subroutine_ids)

    routines_for_super_routine = get_routines_by_ids(routines, subroutine_ids)

    for subroutine_id, subroutine in routines_for_super_routine.items():
        subroutine_duration = (subroutine['attributes']['durationCalculated'])
        total_duration += subroutine_duration

        resource_image_url = subroutine.get('attributes', {}).get("resources", [{}])[0].get("imageUrl") or "https://longtermhealth.de"
        subroutine_entry = {
            "pillar": {
                "pillar": subroutine['attributes']['pillar']['pillar'],
                "pillar_de": subroutine['attributes']['pillar']['pillar_de'],
                "pillar_en": ""
            },
            "imageUrl": resource_image_url,
            "routineId": int(subroutine_id),
            "durationCalculated": round(subroutine_duration),
            "timeOfDay": "ANY",
            "goal": {
                "unit": {
                    "amountUnit": subroutine['attributes']['amountUnit']['amountUnit'],
                    "amountUnit_de": subroutine['attributes']['amountUnit']['amountUnit_de'],
                    "amountUnit_en": ""
                },
                "value": int(subroutine['attributes']['amount']),
            },
            "description": subroutine['attributes']['description'],
            "displayName": subroutine['attributes']['cleanedName'],
            "alternatives": [],
            "scheduleDays": scheduleDays,
            "scheduleWeeks": [
                1,
                2,
                3,
                4
            ],
            "parentRoutineId": parentRoutineId_value
        }
        subroutines_entries.append(subroutine_entry)


    super_routine_entry = {
        "pillar": {
            "pillar": pillar,
            "pillar_de": pillar_de,
            "pillar_en": ""
        },
        "imageUrl": imageUrl,
        "routineId": super_routine_id,
        "timeOfDay": timeOfDay,
        "goal": {
            "unit": {
                "amountUnit": "MINUTES",
                "amountUnit_de": "Minuten",
                "amountUnit_en": ""
            },
            "value": round(total_duration),
        },
        "description": description,
        "displayName": displayName,
        "durationCalculated": round(total_duration),
        "alternatives": [],
        "scheduleDays": scheduleDays,
        "scheduleWeeks": [1, 2, 3, 4]
    }
    total_duration_movement = ""
    if super_routine_id == "movement_superroutine":
        total_duration_movement = total_duration


    final_action_plan["data"]["routines"].append(super_routine_entry)

    for subroutine in subroutines_entries:
        final_action_plan["data"]["routines"].append(subroutine)


    return final_action_plan, total_duration_movement

def build_individual_routine_entry(routine):
    print()
    resource_image_url = routine.get('attributes', {}).get("resources", [{}])[0].get(
        "imageUrl") or "https://longtermhealth.de"

    individual_routine_entry = {
        "pillar": {
            "pillar": routine['attributes']['pillar']['pillar'],
            "pillar_de": routine['attributes']['pillar']['pillar_de'],
            "pillar_en": ""
        },
        "imageUrl": resource_image_url,
        "routineId": routine["id"],
        "durationCalculated": int(routine['attributes']['durationCalculated']),
        "timeOfDay": "ANY",
        "goal": {
            "unit": {
                "amountUnit": routine['attributes']['amountUnit']['amountUnit'],
                "amountUnit_de": routine['attributes']['amountUnit']['amountUnit_de'],
                "amountUnit_en": ""
            },
            "value": int(routine['attributes']["amount"]),
        },
        "description": routine['attributes']["description"],
        "displayName": routine['attributes']["cleanedName"],
        "alternatives": [],
        "scheduleDays": routine['attributes']["scheduleDays"],
        "scheduleWeeks": routine['attributes']["scheduleWeeks"],
        "parentRoutineId": None
    }
    return individual_routine_entry


def save_action_plan_json(final_action_plan, file_path='./data/action_plan.json'):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(final_action_plan, f, ensure_ascii=False,
                  indent=2)

def routine_has_tag(routine, tag):
    tags_field = routine.get("tags")
    if tags_field is None:
        return False

    tags = [t['tag'].lower() for t in tags_field]

    return tag.lower() in tags

def routine_has_pillar(routine, pillar):
    pillar_field = routine.get("pillar")

    if pillar_field is None:
        return False

    pillar_value = pillar_field.get("pillar")

    return pillar_value

def filter_and_select_routines_by_tag(routines, tag, weights, pillar, added_to_super_routine, selected_variations):
    filtered_routines = []

    for routine in routines:
        if isinstance(routine, dict):
            routine_name = routine['attributes']['name']
            routine_id = routine['id']
            routine_variations = [variation['variation'] for variation in routine['attributes']['variations']]
            if routine_id in added_to_super_routine:
                continue

            if selected_variations.intersection(set(routine_variations)):
                continue

            tags = [t['tag'] for t in routine['attributes']['tags']]

            if tag.lower() in (t.lower() for t in tags):
                pillar_value = routine['attributes']['pillar']['pillar']
                if pillar_value.upper() == pillar.upper():
                    weighted_score = calculate_weighted_score(routine, weights)

                    if weighted_score is None:
                        weighted_score = 0

                    duration = routine['attributes']['durationCalculated']

                    if not isinstance(duration, (int, float)):
                        duration = 0

                    filtered_routines.append({
                        "id": routine_id,
                        "cleanedName": routine_name,
                        "pillar": pillar_value,
                        "durationCalculated": duration,
                        "tags": tags,
                        'variations': routine_variations,
                        'impactMovement': routine['attributes']['impactMovement'],
                        'impactNutrition': routine['attributes']['impactNutrition'],
                        'impactSleep': routine['attributes']['impactSleep'],
                        'impactStress': routine['attributes']['impactStress'],
                        'impactSocial': routine['attributes']['impactSocial'],
                        'impactCognitive': routine['attributes']['impactCognitive'],
                        'impactGratitude': routine['attributes']['impactGratitude'],
                        'weighted_score': weighted_score,
                        'parentRoutineId': "movement_superroutine"
                    })


    filtered_routines.sort(key=lambda x: x['weighted_score'], reverse=True)

    seen_variations = set()
    unique_routines = []

    for routine in reversed(filtered_routines):
        variation_key = tuple(routine['variations'])
        if variation_key not in seen_variations:
            seen_variations.add(variation_key)
            unique_routines.append(routine)

    filtered_routines = list(reversed(unique_routines))

    return filtered_routines

def create_custom_super_routine_for_tags(routines, tag_counts, weights, pillar, allocated_time):
    super_routine = []
    current_time = 0
    added_to_super_routine = set()
    selected_variations = set()

    total_tags = sum(tag_counts.values())
    if total_tags > 0:
        time_per_tag = allocated_time / total_tags
    else:
        time_per_tag = 0

    for tag, count in tag_counts.items():
        filtered_routines = filter_and_select_routines_by_tag(
            routines, tag, weights, pillar, added_to_super_routine, selected_variations
        )

        routines_added_for_tag = 0
        remaining_time_for_tag = time_per_tag

        for routine in filtered_routines:
            if routines_added_for_tag >= count:
                break

            routine_duration = routine['durationCalculated']

            if not isinstance(routine_duration, (int, float)):
                continue

            if remaining_time_for_tag >= routine_duration:
                remaining_time_for_tag -= routine_duration
                current_time += routine_duration
                super_routine.append({
                    "id": routine["id"],
                    "cleanedName": routine["cleanedName"],
                    "durationCalculated": routine_duration,
                    "score": routine['weighted_score'],
                    "tags": routine["tags"],
                    "pillar": routine["pillar"]
                })
                added_to_super_routine.add(routine["id"])
                selected_variations.update(routine["variations"])
                routines_added_for_tag += 1

    remaining_time = allocated_time - current_time
    return super_routine, added_to_super_routine, remaining_time

def filter_excluded_routines(routines):
    filtered_routines = [routine for routine in routines if isinstance(routine, dict) and routine.get("rule_status") != "excluded"]
    return filtered_routines

def sort_routines_by_score_rules(routines):
    sorted_routines = sorted(routines, key=lambda routine: routine.get("score_rules", 0), reverse=True)
    return sorted_routines

def get_number_of_routines(score):
    if 80 <= score <= 100:
        return 2
    elif 50 <= score <= 79:
        return 2
    elif 0 <= score <= 49:
        return 1
    return 0


def get_number_of_routines_old(score):
    if 80 <= score <= 100:
        return 1
    elif 60 <= score <= 79:
        return 2
    elif 40 <= score <= 59:
        return 3
    elif 20 <= score <= 39:
        return 4
    elif 0 <= score <= 19:
        return 5
    return 0


def select_routines_for_pillar(pillar, health_scores, routines, allocated_time, weights, max_routines=None):
    if max_routines is None:
        max_routines = get_number_of_routines(health_scores.get(pillar, 0))

    max_routines = int(max_routines)

    routines_for_knapsack = []
    for routine in routines:
        if routine['attributes']['pillar']['pillar'] == pillar:
            print(routine['attributes']['name'])
            weighted_score = calculate_weighted_score_knapsack(routine, weights)

            routine_with_score = routine.copy()
            routine_with_score['weighted_score'] = weighted_score

            routines_for_knapsack.append(routine_with_score)

    routines_for_knapsack.sort(key=lambda x: x['weighted_score'], reverse=True)

    allocated_time = int(allocated_time)

    selected_routines, max_score = knapsack_with_routine_count(routines_for_knapsack, allocated_time, max_routines)
    pillar_duration_sums = {}
    duration_sum = 0

    for routine in selected_routines:
        attributes = routine.get('attributes', {})
        duration = attributes.get('durationCalculated', 0)
        duration_sum += duration
    pillar_duration_sums[pillar] = duration_sum
    time_difference = abs(allocated_time - duration_sum)
    time_delta = time_difference / allocated_time

    return selected_routines, max_score, pillar_duration_sums, time_delta


def knapsack_with_routine_count(routines, max_time, max_routines):
    num_routines = len(routines)

    print(f"Starting knapsack with {num_routines} routines, max_time = {max_time}, max_routines = {max_routines}")

    dp = [[[0 for _ in range(max_routines + 1)] for _ in range(max_time + 1)] for _ in range(num_routines + 1)]

    for i in range(1, num_routines + 1):
        routine = routines[i - 1]

        duration = int(round(routine['attributes']['durationCalculated']))
        score = routine['weighted_score']

        for w in range(max_time + 1):
            for r in range(max_routines + 1):
                dp[i][w][r] = dp[i - 1][w][r]

                if w >= duration and r > 0:
                    dp[i][w][r] = max(dp[i][w][r], dp[i - 1][w - duration][r - 1] + score)

        if max_routines > max_time:
            break

    max_score = 0
    for r in range(max_routines + 1):
        max_score = max(max_score, dp[num_routines][max_time][r])

    selected_routines = []
    w = max_time
    r = max_routines

    for i in range(num_routines, 0, -1):
        if dp[i][w][r] != dp[i - 1][w][r]:
            routine = routines[i - 1]
            selected_routines.append(routine)
            w -= int(routine['attributes']['durationCalculated'])
            r -= 1

    selected_routines.reverse()
    print('selected_routines after kanpsack', len(selected_routines))
    return selected_routines, max_score


def select_routines(health_scores, filtered_routines):

    selected_routines = []
    selected_variations = set()

    pillars = ['SOCIAL_ENGAGEMENT', 'STRESS', 'GRATITUDE', 'COGNITIVE_ENHANCEMENT']
    for pillar in pillars:
        score = health_scores.get(pillar, 0)
        num_routines_to_select = get_number_of_routines(score)

        pillar_routines = [routine for routine in filtered_routines if
                           routine.get('attributes', {}).get('pillar', {}).get('pillar') == pillar]

        for routine in pillar_routines:
            routine_variations = [variation['variation'] for variation in
                                  routine.get('attributes', {}).get('variations', [])]

            if not selected_variations.intersection(set(routine_variations)):
                selected_routines.append(routine)
                selected_variations.update(routine_variations)
                num_routines_to_select -= 1

            if num_routines_to_select <= 0:
                break

    return selected_routines

def calculate_weekly_allocations(daily_allocations):
    weekly_allocations = {pillar: daily * 7 for pillar, daily in daily_allocations.items()}
    return weekly_allocations

def calculate_monthly_allocations(daily_allocations):
    monthly_allocations = {pillar: daily * 28 for pillar, daily in daily_allocations.items()}
    return monthly_allocations


def schedule_routine(routine, daily_allocations, pillar, allocated_time, weekly_allocations, monthly_allocations, all_scheduled_routines, start_weekday):
    id = routine.get('id')
    name = routine['attributes']['name']
    period = routine['attributes']['period']
    duration = routine['attributes']['durationCalculated']
    period_min = routine['attributes']['periodMinimum']
    period_rec = routine['attributes']['periodRecommended']

    print(f"\n\nScheduling routine '{name}' '{id}' of type {period} with a duration of {duration} minutes.")
    print(f"Period: {period}, Period Recommended: {period_rec}, Period Minimum: {period_min}")
    print(f"Available time for pillar '{pillar}':")
    print(f"  Daily Allocation: {allocated_time} minutes")
    print(f"  Weekly Allocation: {weekly_allocations.get(pillar, 0)} minutes")
    print(f"  Monthly Allocation: {monthly_allocations.get(pillar, 0)} minutes")

    if routine['schedulePeriod'] == "WEEKLY":
        print(f"schedulePeriod is WEEKLY, trying to schedule the routine on available days.")
        scheduled_days = set()
        used_weekly_time = sum([r['duration'] for r in all_scheduled_routines if
                                r['schedulePeriod'] == 'WEEKLY' and r['pillar'] == pillar])
        remaining_weekly_time = weekly_allocations.get(pillar, 0) - used_weekly_time

        # Dynamically determine weekend and social engagement days based on start_weekday
        weekend_days = get_weekend_days(start_weekday)
        social_engagement_days = get_social_days(start_weekday)

        if pillar == 'MOVEMENT':
            print("MOVEMENT routine detected, scheduling only on actual weekend days.")
            for day in weekend_days:
                if remaining_weekly_time >= duration and day not in [r['scheduleDays'][0] for r in all_scheduled_routines if r['pillar'] == pillar]:
                    scheduled_days.add(day)
                    remaining_weekly_time -= duration
                    print(f"Routine scheduled on day {day} (actual weekend). Remaining weekly time: {remaining_weekly_time} minutes.")
                    break
                else:
                    print(f"No time available on day {day} or already scheduled. Trying next day.")

        elif pillar == 'SOCIAL_ENGAGEMENT':
            print("SOCIAL_ENGAGEMENT routine detected.")
            for day in social_engagement_days:
                if day not in [r['scheduleDays'][0] for r in all_scheduled_routines if r['pillar'] == pillar]:
                    scheduled_days.add(day)
                    remaining_weekly_time -= duration
                    print(f"Routine scheduled on day {day} (actual Wed/Thu). Remaining weekly time: {remaining_weekly_time} minutes.")
                    break
                else:
                    print(f"No time available on day {day} or already scheduled. Trying next day.")

        else:
            # For other pillars, pick any available day of the week
            print('remaining_weekly_time before', remaining_weekly_time)
            for day in range(1,8):
                if remaining_weekly_time >= duration and day not in [r['scheduleDays'][0] for r in all_scheduled_routines if r['pillar'] == pillar]:
                    scheduled_days.add(day)
                    remaining_weekly_time -= duration
                    print(f"Routine scheduled on day {day}. Remaining weekly time: {remaining_weekly_time} minutes.")
                    break
                else:
                    print(f"No time available on day {day} or already scheduled. Trying next day.")

        schedule_days = list(scheduled_days)
        schedule_weeks = [1, 2, 3, 4]
        print(f"Routine scheduled on days: {schedule_days}.")
        all_scheduled_routines.append({
            'id': id,
            'name': name,
            'pillar': pillar,
            'period': period,
            'schedulePeriod': routine['schedulePeriod'],
            'scheduleDays': schedule_days,
            'scheduleWeeks': schedule_weeks,
            'duration': duration
        })
        print(f"Final schedule for routine '{name}': Days: {schedule_days}, Weeks: {schedule_weeks}")
        return {
            "id": id,
            "scheduleDays": schedule_days,
            "scheduleWeeks": schedule_weeks,
            "all_scheduled_routines": all_scheduled_routines
        }

    else:
        # DAILY/WEEKLY/MONTHLY logic remains mostly the same except we no longer hardcode weekend days.
        # No changes to the logic of how days are picked here, just kept as original except we don't
        # rely on fixed weekend [6,7] references.
        if period == 'DAILY':
            used_daily_time = sum([r['duration'] for r in all_scheduled_routines if r['pillar'] == pillar])
            remaining_daily_time = daily_allocations.get(pillar, 0) - used_daily_time
            print('remaining_daily_time before', remaining_daily_time)
            print("Period is DAILY, scheduling routine for all 7 days.")
            schedule_days = [1, 2, 3, 4, 5, 6, 7]
            schedule_weeks = [1, 2, 3, 4]
            remaining_daily_time -= duration
            print('remaining_daily_time after', remaining_daily_time)

        elif period == 'WEEKLY':
            used_daily_time = sum([r['duration'] for r in all_scheduled_routines if r['pillar'] == pillar])
            remaining_daily_time = daily_allocations.get(pillar, 0) - used_daily_time
            print('remaining_daily_time before', remaining_daily_time)
            num_sessions = period_rec
            if num_sessions == 0:
                print(f"Routine cannot fit in allocated daily time of {allocated_time} min.")
                if weekly_allocations.get(pillar, 0) >= duration:
                    num_sessions = min(weekly_allocations[pillar] // duration, period_rec)
                    num_sessions = int(num_sessions)
            print(f"Routine can be scheduled for {(num_sessions)} sessions over the week.")
            schedule_days = list(range(1, 1 + num_sessions))
            schedule_weeks = [1, 2, 3, 4]
            remaining_daily_time -= duration
            print('remaining_daily_time after', remaining_daily_time)

        elif period == 'MONTHLY':
            print("Period is MONTHLY. Dynamically distributing sessions based on period_rec.")
            if period_rec <= 4:
                schedule_days = [1]
                schedule_weeks = list(range(1, period_rec+1))
            else:
                days_needed = math.ceil(period_rec / 4)
                weeks_needed = math.ceil(period_rec / days_needed)
                schedule_days = list(range(1, 1 + days_needed))
                schedule_weeks = list(range(1, min(weeks_needed, 4) + 1))
            print(f"Dynamically chosen: Days: {schedule_days}, Weeks: {schedule_weeks}")

        else:
            print(f"Unknown period type: {period}. Skipping scheduling.")
            schedule_days = []
            schedule_weeks = []

        print(f"Final schedule for routine '{name}': Days: {schedule_days}, Weeks: {schedule_weeks}")
        all_scheduled_routines.append({
            'id': id,
            'name': name,
            'pillar': pillar,
            'period': period,
            'schedulePeriod': routine['schedulePeriod'],
            'scheduleDays': schedule_days,
            'scheduleWeeks': schedule_weeks,
            'duration': duration
        })
        return {
            "id": id,
            "scheduleDays": schedule_days,
            "scheduleWeeks": schedule_weeks,
            "all_scheduled_routines": all_scheduled_routines
        }


def get_weekday_for_day(start_weekday, day):
    return (start_weekday + (day - 1)) % 7

def get_weekend_days(start_weekday):
    weekend_days = []
    for d in range(1, 8):
        wd = get_weekday_for_day(start_weekday, d)
        if wd in [5, 6]: # Saturday=5, Sunday=6
            weekend_days.append(d)
    return weekend_days

def get_social_days(start_weekday):
    social_days = []
    for d in range(1, 8):
        wd = get_weekday_for_day(start_weekday, d)
        if wd in [2, 3]:
            social_days.append(d)
    return social_days




def calculate_daily_allocations(daily_time, health_scores, thresholds):
    allocations = {pillar: daily_time * weight for pillar, weight in health_scores.items()}
    return allocations


def check_daily_conflict(day, pillar, routine_duration, daily_allocations):
    if pillar not in daily_allocations:
        return True
    available_time = daily_allocations[pillar]
    scheduled_time = sum([routine['durationCalculated'] for routine in daily_allocations.get(day, [])])
    return available_time - scheduled_time >= routine_duration


def reallocate_from_nutrition_sleep(daily_allocations):
    time_to_reallocate = int(daily_allocations["NUTRITION"]) + int(daily_allocations["SLEEP"])

    other_pillars = ["MOVEMENT", "SOCIAL_ENGAGEMENT", "STRESS", "GRATITUDE", "COGNITIVE_ENHANCEMENT"]

    allocation_per_pillar = time_to_reallocate // len(other_pillars)

    remainder = time_to_reallocate % len(other_pillars)

    reallocations = {pillar: allocation_per_pillar for pillar in other_pillars}

    reallocations["MOVEMENT"] += remainder

    daily_allocations["NUTRITION"] = 0
    daily_allocations["SLEEP"] = 0

    for pillar in other_pillars:
        daily_allocations[pillar] += reallocations[pillar]

    return reallocations, daily_allocations


def reallocate_to_specific_pillars(daily_allocations, target_pillars):
    time_to_reallocate = int(daily_allocations["NUTRITION"]) + int(daily_allocations["SLEEP"])

    if not set(target_pillars).issubset(daily_allocations.keys()):
        raise ValueError("All specified pillars must exist in daily_allocations.")

    allocation_per_pillar = time_to_reallocate // len(target_pillars)

    reallocations = {}
    for pillar in target_pillars:
        reallocations[pillar] = allocation_per_pillar

    daily_allocations["NUTRITION"] = 0
    daily_allocations["SLEEP"] = 0

    for pillar in target_pillars:
        daily_allocations[pillar] += reallocations[pillar]

    return reallocations, daily_allocations

def create_health_scores_with_tag(health_scores):
    health_scores_with_tag = {}

    for pillar, score in health_scores.items():
        if score < 50:
            tag = "focus"
        elif 50 <= score < 80:
            tag = "good"
        else:
            tag = "optimal"

        health_scores_with_tag[pillar] = {
            "score": score,
            "tag": tag
        }

    return health_scores_with_tag


def create_health_scores_with_structure(account_id, health_scores):
    score_interpretation_dict = {
        "MOVEMENT": {
            "FOCUS": "Es ist Zeit, mehr Bewegung in deinen Alltag zu integrieren. Kleine Schritte können einen großen Unterschied für deine Gesundheit machen!",
            "GOOD": "Deine körperliche Aktivität ist gut! Mit ein wenig mehr Bewegung kannst du deine Fitness auf das nächste Level heben.",
            "OPTIMAL": "Fantastische Leistung! Deine regelmäßige Bewegung stärkt deine Gesundheit optimal. Weiter so!"
        },
        "NUTRITION": {
            "FOCUS": "Achte mehr auf eine ausgewogene Ernährung. Gesunde Essgewohnheiten geben dir Energie und Wohlbefinden.",
            "GOOD": "Deine Ernährung ist auf einem guten Weg! Mit kleinen Anpassungen kannst du deine Nährstoffzufuhr weiter optimieren.",
            "OPTIMAL": "Exzellente Ernährungsgewohnheiten! Du versorgst deinen Körper optimal mit wichtigen Nährstoffen. Weiter so!"
        },
        "SLEEP": {
            "FOCUS": "Verbessere deine Schlafgewohnheiten für mehr Energie und bessere Gesundheit. Guter Schlaf ist essenziell!",
            "GOOD": "Dein Schlaf ist gut! Ein paar Änderungen können dir helfen, noch erholsamer zu schlafen.",
            "OPTIMAL": "Ausgezeichneter Schlaf! Du sorgst für optimale Erholung und Vitalität. Weiter so!"
        },
        "SOCIAL_ENGAGEMENT": {
            "FOCUS": "Pflege deine sozialen Beziehungen. Verbindungen zu anderen sind wichtig für dein emotionales Wohlbefinden.",
            "GOOD": "Deine sozialen Beziehungen sind gut! Mit ein wenig mehr Engagement kannst du deine Verbindungen weiter vertiefen.",
            "OPTIMAL": "Starke und erfüllende soziale Beziehungen! Du pflegst wertvolle Verbindungen, die dein Leben bereichern. Weiter so!"
        },
        "STRESS": {
            "FOCUS": "Es ist wichtig, Wege zu finden, um deinen Stress besser zu bewältigen. Kleine Pausen und Entspannungstechniken können helfen.",
            "GOOD": "Dein Umgang mit Stress ist gut! Mit weiteren Strategien kannst du deine Stressresistenz weiter stärken.",
            "OPTIMAL": "Du meisterst Stress hervorragend! Deine effektiven Bewältigungsstrategien tragen zu deinem Wohlbefinden bei. Weiter so!"
        },
        "GRATITUDE": {
            "FOCUS": "Nimm dir Zeit, die positiven Dinge im Leben zu schätzen. Dankbarkeit kann dein Wohlbefinden erheblich steigern.",
            "GOOD": "Du zeigst bereits Dankbarkeit! Mit kleinen Ergänzungen kannst du deine positive Einstellung noch weiter ausbauen.",
            "OPTIMAL": "Eine wunderbare Haltung der Dankbarkeit! Deine positive Sicht bereichert dein Leben und das deiner Mitmenschen. Weiter so!"
        },
        "COGNITIVE_ENHANCEMENT": {
            "FOCUS": "Fordere deinen Geist regelmäßig heraus. Neue Lernmöglichkeiten können deine geistige Fitness verbessern.",
            "GOOD": "Deine kognitive Förderung ist gut! Mit zusätzlichen Aktivitäten kannst du deine geistige Leistungsfähigkeit weiter steigern.",
            "OPTIMAL": "Hervorragende geistige Fitness! Du hältst deinen Verstand aktiv und stark. Weiter so!"
        }
    }

    # Function to get rating and interpretation
    def get_score_details(pillar, score):
        if score < 50:
            rating = "FOCUS"
        elif 50 <= score < 80:
            rating = "GOOD"
        else:
            rating = "OPTIMAL"
        return {
            "ratingEnum": rating,
            "displayName": rating.capitalize(),
            "scoreInterpretation": score_interpretation_dict.get(pillar, {}).get(rating, "No interpretation available.")
        }

    # Calculate total score as the average of all scores
    total_score = sum(health_scores.values()) / len(health_scores)

    # Build the pillars structure
    pillars = []
    for pillar_enum, score in health_scores.items():
        details = get_score_details(pillar_enum, score)
        pillars.append({
            "pillar": {
                "pillarEnum": pillar_enum,
                "displayName": pillar_enum.replace("_", " ").capitalize()
            },
            "score": f"{score:.2f}",
            "scoreInterpretation": details["scoreInterpretation"],
            "rating": {
                "ratingEnum": details["ratingEnum"],
                "displayName": details["displayName"]
            }
        })

    return {
        "data": {
            "totalScore": int(total_score),
            "accountId": account_id,
            "scoreChartImageUrl": f"https://lthstore.blob.core.windows.net/images/{account_id}_1.png",
            "pillarScores": pillars
            }
        }


def allocate_more_time_to_focus_areas(daily_allocations, health_scores_with_tag):
    # Calculate the total time we can reallocate from NUTRITION and SLEEP
    time_to_reallocate = int(daily_allocations["NUTRITION"]) + int(daily_allocations["SLEEP"])

    # Identify focus pillars other than NUTRITION and SLEEP
    focus_pillars = [
        pillar for pillar, data in health_scores_with_tag.items()
        if data["tag"] == "focus" and pillar not in ["NUTRITION", "SLEEP"]
    ]

    # If there are no additional focus pillars, revert to allocating equally among all other pillars
    if not focus_pillars:
        # Consider all pillars except NUTRITION and SLEEP for fallback reallocation
        # This includes pillars that may not have a "focus" tag.
        other_pillars = [p for p in daily_allocations.keys() if p not in ["NUTRITION", "SLEEP"]]

        # If there are still no other pillars, there's nothing to reallocate to
        if not other_pillars:
            # Just return with minimal changes
            daily_allocations["NUTRITION"] = 0.1
            daily_allocations["SLEEP"] = 0.1
            return {}, daily_allocations

        # Use the other pillars for reallocation
        focus_pillars = other_pillars

    # Perform the integer division allocation
    allocation_per_pillar = time_to_reallocate // len(focus_pillars)
    remainder = time_to_reallocate % len(focus_pillars)

    # Build the reallocation dictionary
    reallocations = {pillar: allocation_per_pillar for pillar in focus_pillars}

    # Distribute the remainder
    for i in range(remainder):
        reallocations[focus_pillars[i]] += 1

    # Reduce NUTRITION and SLEEP to minimal
    daily_allocations["NUTRITION"] = 0.1
    daily_allocations["SLEEP"] = 0.1

    # Apply the new allocations to the target pillars
    for pillar in focus_pillars:
        daily_allocations[pillar] = daily_allocations.get(pillar, 0) + reallocations[pillar]

    return reallocations, daily_allocations


def calculate_total_durations(routines_per_day, pillar_durations_per_day, allocated_time):
    total_allocated_durations = {}
    total_used_durations = {}

    total_used_all = 0
    total_allocated_all = 0

    for day in range(1, 29):
        print(f"Day {day}:")
        if day in routines_per_day:
            for routine in routines_per_day[day]:
                pillar = routine[1]
                duration = routine[2]

                if pillar not in total_used_durations:
                    total_used_durations[pillar] = 0
                total_used_durations[pillar] += duration

                if pillar == "movement":
                    if pillar not in total_allocated_durations:
                        total_allocated_durations[pillar] = 0
                    total_allocated_durations[pillar] += allocated_time * 28
                else:
                    if pillar not in total_allocated_durations:
                        total_allocated_durations[pillar] = 0
                    total_allocated_durations[pillar] += allocated_time

                total_used_all += duration

                if pillar == "movement":
                    total_allocated_all += allocated_time * 28
                else:
                    total_allocated_all += allocated_time

                print(f"  - {routine[0]} (Pillar: {pillar}, Duration: {duration} minutes)")

            print("Total duration per pillar for the day:")
            for pillar, total_duration in pillar_durations_per_day[day].items():
                print(f"Pillar {pillar}")
                print(f"used      {total_duration} minutes")
                print(f"allocated {allocated_time} minutes")
        else:
            print("  No routines scheduled.")
        print()

    print("Total duration per pillar across all 28 days:")
    for pillar in total_used_durations:
        used_duration = total_used_durations[pillar]
        allocated_duration = total_allocated_durations.get(pillar, 0)
        print(f"Pillar {pillar}:")
        print(f"  Total used:      {used_duration} minutes")
        print(f"  Total allocated: {allocated_duration} minutes")

    print("\nOverall total across all pillars:")
    print(f"Total used:      {total_used_all} minutes")
    print(f"Total allocated: {total_allocated_all} minutes")


def main():
    account_id, daily_time, routines, health_scores, user_data = get_routines_with_defaults()
    print('daily_time',daily_time)
    total_score = health_scores['Total Score']
    start_weekday = datetime.today().weekday()  # Monday=0,...Sunday=6
    print('start_weekday',start_weekday)
    file_path = "./data/routines_with_scores.json"
    routines = load_routines_for_rules(file_path)


    if isinstance(routines, dict):
        routines_list = list(routines.values())
    elif isinstance(routines, list):
        routines_list = routines
    else:
        return

    filtered_routines = filter_excluded_routines(routines_list)
    sorted_routines = sort_routines_by_score_rules(filtered_routines)

    routines = sorted_routines
    health_scores = {key: value for key, value in health_scores.items() if key != 'Total Score'}

    allocations_by_scores = calculate_daily_allocations_by_scores(daily_time, health_scores, THRESHOLDS)
    allocations_by_weightings = calculate_daily_allocations_by_weightings(daily_time, WEIGHTINGS)
    daily_allocations = combine_allocations(allocations_by_scores, allocations_by_weightings, score_weight=0.7)
    print("daily_allocations before reallocation:", daily_allocations)

    health_scores_with_tag = create_health_scores_with_tag(health_scores)
    print('health_scores_with_tag',health_scores_with_tag)
    health_scores_with_tag_payload_strapi = create_health_scores_with_structure(account_id, health_scores)
    print('health_scores_with_tag_payload_strapi',json.dumps(health_scores_with_tag_payload_strapi, indent=4, ensure_ascii=False))

    reallocations, updated_allocations = allocate_more_time_to_focus_areas(daily_allocations, health_scores_with_tag)

    print("Reallocations to Focus Areas:", reallocations)
    print("Updated Allocations allocate_more_time_to_focus_areas:", updated_allocations)

    daily_allocations = updated_allocations

    weights = {
        "MOVEMENT": (100 - health_scores["MOVEMENT"]) / 100,
        "NUTRITION": (100 - health_scores["NUTRITION"]) / 100,
        "SLEEP": (100 - health_scores["SLEEP"]) / 100,
        "SOCIAL_ENGAGEMENT": (100 - health_scores["SOCIAL_ENGAGEMENT"]) / 100,
        "STRESS": (100 - health_scores["STRESS"]) / 100,
        "GRATITUDE": (100 - health_scores["GRATITUDE"]) / 100,
        "COGNITIVE_ENHANCEMENT": (100 - health_scores["COGNITIVE_ENHANCEMENT"]) / 100
    }

    movement_tag_counts = {
        "warm-up": 1,
        "strength": 1,
        "cardio": 1,
        "basic mobility": 1
    }
    """
    pillars = ['SLEEP', 'NUTRITION']
    for pillar in pillars:
        score = health_scores.get(pillar, 0)
        if 80 <= score <= 100:
            sleep_tag_counts = {
                "environmental change": 1,
            }
            nutrition_tag_counts = {
                "LTH basic": 1,
            }

        elif 60 <= score <= 79:
            sleep_tag_counts = {
                "environmental change": 1,
                "behavioral change": 1
            }
            nutrition_tag_counts = {
                "LTH basic": 1,
                "mediterranean": 1
            }

        elif 40 <= score <= 59:
            sleep_tag_counts = {
                "environmental change": 2,
                "behavioral change": 1
            }
            nutrition_tag_counts = {
                "LTH basic": 1,
                "mediterranean": 1,
                "behavioral change": 1
            }

        elif 20 <= score <= 39:
            sleep_tag_counts = {
                "environmental change": 2,
                "behavioral change": 2
            }
            nutrition_tag_counts = {
                "LTH basic": 2,
                "mediterranean": 1,
                "behavioral change": 1
            }

        elif 0 <= score <= 19:
            sleep_tag_counts = {
                "environmental change": 3,
                "behavioral change": 2
            }
            nutrition_tag_counts = {
                "LTH basic": 2,
                "mediterranean": 2,
                "behavioral change": 1
            }
    """
    pillars = ['SLEEP', 'NUTRITION']
    for pillar in pillars:
        score = health_scores.get(pillar, 0)
        if 80 <= score <= 100:
            sleep_tag_counts = {
                "environmental change": 1,
            }
            nutrition_tag_counts = {
                "behavioral change": 1,
            }

        elif 50 <= score <= 79:
            sleep_tag_counts = {
                "environmental change": 1,
                "behavioral change": 1
            }
            nutrition_tag_counts = {
                "LTH basic": 1,
                "mediterranean": 1
            }

        elif 0 <= score <= 49:
            sleep_tag_counts = {
                "environmental change": 2,
                "behavioral change": 2
            }
            nutrition_tag_counts = {
                "behavioral change": 1,
            }



    movement_super_routine, added_to_super_routine_movement, remaining_time_movement = create_custom_super_routine_for_tags(
        routines,
        movement_tag_counts,
        weights,
        "MOVEMENT",
        5,
    )


    sleep_answer = user_data.get('SLEEP', {}).get('Wie ist deine Schlafqualität?')


    if sleep_answer == "Sehr gut":
        sleep_super_routine = []
        added_to_super_routine_sleep = []
        remaining_time_sleep = 0
        print('sleep_answer is sehr gut, skipping sleep super routine',sleep_answer)
    else:
        sleep_super_routine, added_to_super_routine_sleep, remaining_time_sleep = create_custom_super_routine_for_tags(
            routines,
            sleep_tag_counts,
            weights,
            "SLEEP",
            daily_allocations["SLEEP"]
        )

    nutrition_super_routine, added_to_super_routine_nutrition, remaining_time_nutrition = create_custom_super_routine_for_tags(
        routines,
        nutrition_tag_counts,
        weights,
        "NUTRITION",
        daily_allocations["NUTRITION"]
    )


    routines_for_super_routine_movement = get_routines_by_ids(routines, added_to_super_routine_movement)
    routines_for_super_routine_sleep = get_routines_by_ids(routines, added_to_super_routine_sleep)
    routines_for_super_routine_nutrition = get_routines_by_ids(routines, added_to_super_routine_nutrition)

    print('added_to_super_routine_movement',added_to_super_routine_movement)
    print('added_to_super_routine_sleep',added_to_super_routine_sleep)
    print('added_to_super_routine_nutrition',added_to_super_routine_nutrition)

    final_action_plan_sleep, total_duration_movement = build_final_action_plan(routines, {},
                                                        account_id, daily_time,
                                                        routines_for_super_routine_sleep,
                                                      "sleep_superroutine")

    final_action_plan_nutrition, total_duration_movement = build_final_action_plan(routines, {},
                                                        account_id, daily_time,
                                                        routines_for_super_routine_nutrition,
                                                      "nutrition_super_routine")

    final_action_plan_movement, total_duration_movement = build_final_action_plan(routines, {},
                                                         account_id, daily_time,
                                                         routines_for_super_routine_movement,
                                                      "movement_superroutine")


    print("total_duration_movement",total_duration_movement)

    final_action_plan = {
        "data": {
            "accountId": account_id,
            "totalDailyTimeInMins": daily_time,
            "routines": final_action_plan_movement["data"]["routines"] +
                        final_action_plan_sleep["data"]["routines"] +
                        final_action_plan_nutrition["data"]["routines"]
        }
    }



    pillars = ['SOCIAL_ENGAGEMENT', 'STRESS', 'GRATITUDE', 'COGNITIVE_ENHANCEMENT']
    final_routines = []
    print('QWERT')
    weekly_routines = {}

    pillar_movement = ['MOVEMENT']
    for pillar in pillar_movement:
        allocated_time = daily_allocations[pillar]
        allocated_time_weekly = allocated_time * 7
        print(f"TEST Allocating {allocated_time_weekly} minutes for pillar: {pillar}")
        filtered_routines_movement = filter_routines_by_pillar_and_time(pillar, allocated_time_weekly, filtered_routines)
        print('filtered_routines_movement', len(filtered_routines_movement))
        selected_routines, max_score, pillar_duration_sums, time_delta = select_routines_for_pillar(
            pillar, health_scores, filtered_routines_movement, allocated_time_weekly, weights, 2
        )
        total_time_selected = sum(routine['attributes']['durationCalculated'] for routine in selected_routines)
        print(f"\nPillar: {pillar} (Before Selection)")
        print(f"allocated_time_weekly Time: {allocated_time_weekly} min")

        if len(selected_routines) == 0:
            print(
                f"No routines fitting allocated time")
        else:
            print("\nSelected Routines (After Selection):")
            print("-" * 30)
            for routine in selected_routines:
                print(
                    f"Routine ID: {routine['id']}, Routine Name: {routine['attributes']['name']}, Duration: {routine['attributes']['durationCalculated']} min, Weighted Score: {routine['weighted_score']}")

            print(f"\nTEST Total time allocated for {pillar} (After Selection): {total_time_selected} min")
            print("-" * 30)


        for routine in selected_routines:
            routine['schedulePeriod'] = 'WEEKLY'
            print(
                f"Routine {routine['attributes']['name']} scheduled weekly with time allocation: {routine['attributes']['durationCalculated']}")
        final_routines.extend(selected_routines)

    for pillar in pillars:

        allocated_time = daily_allocations[pillar]

        print(f"Allocating {allocated_time} minutes for pillar: {pillar}")

        selected_routines, max_score, pillar_duration_sums, time_delta = select_routines_for_pillar(
            pillar, health_scores, filtered_routines, allocated_time, weights
        )
        print('Stage 1: allocated_time_daily', allocated_time)
        allocated_time_weekly = allocated_time * 7
        print('Stage 1: allocated_time_weekly', allocated_time_weekly)
        print('Stage 1: pillar_duration_sums_daily', pillar_duration_sums)
        remaining_time_daily = allocated_time - pillar_duration_sums[pillar]
        print('Stage 1: remaining_time_daily', remaining_time_daily)
        remaining_time_weekly = remaining_time_daily * 7
        print('Stage 1: remaining_time_weekly', remaining_time_weekly)
        print('Stage 1: Before retry: pillar_duration_sums',pillar_duration_sums)
        print('Stage 1: Before retry: time_delta',time_delta)

        print(f"Initial selection for {pillar}: {selected_routines}, Score: {max_score}")

        if max_score == 0:
            print(f"No routines selected for {pillar}. Retrying with weekly allocation (7 days).")

            allocated_time *= 7

            print(f"New weekly allocated time for {pillar}: {allocated_time}")

            selected_routines, max_score, pillar_duration_sums, time_delta = select_routines_for_pillar(
                pillar, health_scores, filtered_routines, allocated_time, weights
            )
            print('Stage 2: allocated_time_weekly', allocated_time_weekly)
            print('Stage 2: pillar_duration_sums_weekly', pillar_duration_sums)
            remaining_time_daily = allocated_time - pillar_duration_sums[pillar]
            print('Stage 2: remaining_time_daily', remaining_time_daily)
            remaining_time_weekly = remaining_time_daily * 7
            print('Stage 2: remaining_time_weekly', remaining_time_weekly)

            print('Stage 2: pillar_duration_sums_weekly',pillar_duration_sums)

            print(f"Retry selection for {pillar}: {selected_routines}, Score: {max_score}")

            for routine in selected_routines:
                routine['schedulePeriod'] = 'WEEKLY'
                print(f"Routine {routine['attributes']['name']} scheduled weekly with time allocation: {routine['attributes']['durationCalculated']}")

        elif time_delta >= 0.2:
            print(f'time_delta was more than 0.2. Retrying with weekly allocation (7 days) with remaining time {remaining_time_weekly}')

            selected_routines, max_score, pillar_duration_sums_weekly, time_delta_weekly = select_routines_for_pillar(
                pillar, health_scores, filtered_routines, remaining_time_weekly, weights
            )
            print('Stage 2: allocated_time_weekly', allocated_time_weekly)
            print('Stage 2: pillar_duration_sums_weekly', pillar_duration_sums_weekly)
            remaining_time_weekly = allocated_time_weekly - pillar_duration_sums_weekly[pillar]
            print('Stage 2: remaining_time_weekly', remaining_time_weekly)
            remaining_time_monthly = remaining_time_weekly * 4
            print('Stage 2: remaining_time_monthly', remaining_time_monthly)
            print('Stage 2: time_delta_weekly',time_delta_weekly)

            print(f"Retry selection for {pillar}: {selected_routines}, Score: {max_score}")

            for routine in selected_routines:
                routine['schedulePeriod'] = 'WEEKLY'
                print(
                    f"Routine {routine['attributes']['name']} scheduled weekly with time allocation: {routine['attributes']['durationCalculated']}")

            if time_delta_weekly >= 0.2:
                print(
                    f'time_delta_weekly was more than 0.2. Retrying with monthly allocation (28 days) with remaining time {remaining_time_monthly}')

                selected_routines, max_score, pillar_duration_sums_monthly, time_delta_weekly = select_routines_for_pillar(
                    pillar, health_scores, filtered_routines, remaining_time_monthly, weights
                )
                print('Stage 3: allocated_time_monthly', allocated_time_weekly*4)
                print('Stage 3: pillar_duration_sums_monthly', pillar_duration_sums_monthly)
                remaining_time_weekly = allocated_time_weekly - pillar_duration_sums_monthly[pillar]
                print('Stage 3: remaining_time_weekly', remaining_time_weekly)
                print('Stage 3: time_delta_weekly', time_delta_weekly)

                print(f"Retry selection for {pillar}: {selected_routines}, Score: {max_score}")

                for routine in selected_routines:
                    routine['schedulePeriod'] = 'WEEKLY'
                    print(
                        f"Routine {routine['attributes']['name']} scheduled weekly with time allocation: {routine['attributes']['durationCalculated']}")

        else:
            for routine in selected_routines:
                routine['schedulePeriod'] = 'DAILY'
                print(f"Routine {routine['attributes']['name']} scheduled daily with time allocation: {routine['attributes']['durationCalculated']}")

        total_time_selected = sum(routine['attributes']['durationCalculated'] for routine in selected_routines)
        print(f"\nPillar: {pillar} (Before Selection)")
        print(f"Allocated Time: {allocated_time} min")

        if len(selected_routines) == 0:
            print(
                f"No routines fitting allocated time")
        else:
             print("\nSelected Routines (After Selection):")
             print("-" * 30)
             for routine in selected_routines:
                 print(
                     f"Routine ID: {routine['id']}, Routine Name: {routine['attributes']['name']}, Duration: {routine['attributes']['durationCalculated']} min, Weighted Score: {routine['weighted_score']}")

             print(f"\nTotal time allocated for {pillar} (After Selection): {total_time_selected} min")
             print("-" * 30)

        final_routines.extend(selected_routines)



    print('len(final_routines)',len(final_routines))
    print('QWERTZ')
    all_scheduled_routines = []

    print("\nFinal selected routines (across all pillars):")
    for routine in final_routines:
        print(
            f"Pillar: {routine['attributes']['pillar']['pillar']} Routine ID: {routine['id']}, Duration: {routine['attributes']['durationCalculated']} min, Weighted Score: {routine['weighted_score']}")

    weekly_allocations = calculate_weekly_allocations(daily_allocations)
    monthly_allocations = calculate_monthly_allocations(daily_allocations)

    print("\nTotal daily time:", daily_time)
    print("\nDaily, Weekly, and Monthly Allocations per Pillar:")
    for pillar in daily_allocations.keys():
        print(f"\nPillar: {pillar}")
        print(f"  Daily Allocation: {daily_allocations[pillar]} min")
        print(f"  Weekly Allocation: {weekly_allocations[pillar]} min")
        print(f"  Monthly Allocation: {monthly_allocations[pillar]} min")

    for pillar in ['MOVEMENT', 'NUTRITION', 'SLEEP', 'SOCIAL_ENGAGEMENT', 'STRESS', 'GRATITUDE',
                   'COGNITIVE_ENHANCEMENT']:
        allocated_time = daily_allocations.get(pillar, 0)
        print(f"Scheduling routines for pillar '{pillar}' with allocated daily time: {allocated_time} minutes.")

        for routine in final_routines:
            if routine['attributes']['pillar']['pillar'] == pillar:
                schedule_result = schedule_routine(
                    routine,
                    daily_allocations,
                    pillar,
                    allocated_time,
                    weekly_allocations,
                    monthly_allocations,
                    all_scheduled_routines,
                    start_weekday
                )

                routine['attributes']['scheduleDays'] = schedule_result['scheduleDays']
                routine['attributes']['scheduleWeeks'] = schedule_result['scheduleWeeks']

                all_scheduled_routines = schedule_result['all_scheduled_routines']

    print('all_scheduled_routines',all_scheduled_routines)

    routines_per_day = defaultdict(list)
    pillar_durations_per_day = defaultdict(lambda: defaultdict(float))

    for routine in all_scheduled_routines:
        schedule_days = routine['scheduleDays']
        name = routine['name']
        pillar = routine['pillar']
        duration = routine['duration']

        if routine['schedulePeriod'] == 'DAILY':
            for week in routine['scheduleWeeks']:
                for day in schedule_days:
                    day_of_month = (week - 1) * 7 + day
                    routines_per_day[day_of_month].append((name, pillar, duration))
                    pillar_durations_per_day[day_of_month][pillar] += duration

        if routine['schedulePeriod'] == 'WEEKLY':
            for week in routine['scheduleWeeks']:
                for day in schedule_days:
                    day_of_month = (week - 1) * 7 + day
                    routines_per_day[day_of_month].append((name, pillar, duration))
                    pillar_durations_per_day[day_of_month][pillar] += duration

    calculate_total_durations(routines_per_day, pillar_durations_per_day, allocated_time)

    for routine in final_routines:
        individual_entry = build_individual_routine_entry(routine)
        final_action_plan["data"]["routines"].append(individual_entry)

    for routine in final_action_plan["data"]["routines"]:
        if isinstance(routine, dict):
            if routine.get("routineId") == "sleep_superroutine":
                routine["routineId"] = 222
            if routine.get("routineId") == "movement_superroutine":
                routine["routineId"] = 221
            if routine.get("routineId") == "nutrition_super_routine":
                routine["routineId"] = 223

    save_action_plan_json(final_action_plan)

    accountid_str = str(account_id) + "_1.png"
    generate_polar_chart(health_scores, accountid_str)
    total_score_str = str(round(total_score))
    create_final_image(total_score_str, accountid_str)
    upload_to_blob(accountid_str)
    strapi_post_health_scores(health_scores_with_tag_payload_strapi)
    strapi_post_action_plan(final_action_plan, account_id)


    return final_action_plan



if __name__ == "__main__":
    main()
