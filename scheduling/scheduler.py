#scheduling/scheduler.py

import json
import math
from scheduling.filter_service import main as get_routines_with_defaults
from utils.strapi_api import strapi_post_action_plan

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

def load_routines_for_rules(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        routines_list = json.load(f)
    routines = {routine['id']: routine for routine in routines_list}
    return routines

def transform_routines(data):
    routines = {item['id']: item['attributes'] for item in data}
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
    return {routine_id: routines[routine_id] for routine_id in routine_ids if routine_id in routines}

def build_final_action_plan(routines, routine_schedule, account_id, daily_time, routines_for_super_routine,
                            super_routine_id, max_subroutines_per_superroutine=5):
    final_action_plan = {
        "data": {
            "accountId": account_id,
            "totalDailyTimeInMins": daily_time,
            "routines": []
        }
    }

    super_routine_mapping = {
        "nutrition_super_routine": 6316,
        "movement_superroutine": 6314,
        "sleep_superroutine": 6315,
    }

    parentRoutineId_value = super_routine_mapping.get(super_routine_id, None)

    pillar_mapping = {
        "sleep_superroutine": "SLEEP",
        "movement_superroutine": "MOVEMENT",
        "nutrition_super_routine": "NUTRITION",
    }

    pillar = pillar_mapping.get(super_routine_id, None)

    image_url_mapping = {
        "movement_superroutine": "https://lthstore.blob.core.windows.net/images/203.jpg",
        "sleep_superroutine": "https://lthstore.blob.core.windows.net/images/204.jpg",
        "nutrition_super_routine": "https://lthstore.blob.core.windows.net/images/205.jpg",
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

    added_subroutines = set()
    subroutines_entries = []
    total_duration = 0

    subroutine_ids = list(routines_for_super_routine.keys())[:max_subroutines_per_superroutine]

    for subroutine_id in subroutine_ids:
        if subroutine_id in routines_for_super_routine:
            subroutine = routines_for_super_routine[subroutine_id]
            subroutine_duration = int(subroutine.get("durationCalculated", 0))
            total_duration += subroutine_duration

            resource_image_url = subroutine.get("resources", [{}])[0].get("imageUrl") or "https://longtermhealth.de"
            subroutine_entry = {
                "pillar": {
                    "pillar": subroutine.get("pillar", {}).get("pillar"),
                    "pillar_de": subroutine.get("pillar", {}).get("pillar_de"),
                    "pillar_en": ""
                },
                "imageUrl": resource_image_url,
                "routineId": int(subroutine_id),
                "durationCalculated": subroutine_duration,
                "timeOfDay": "ANY",
                "goal": {
                    "unit": {
                        "amountUnit": subroutine.get("amountUnit", {}).get("amountUnit", "MINUTES"),
                        "amountUnit_de": subroutine.get("amountUnit", {}).get("amountUnit_de", "MINUTES"),
                        "amountUnit_en": ""
                    },
                    "value": int(subroutine.get("amount", 0)),
                },
                "description": subroutine.get("description", "No description available"),
                "displayName": subroutine["cleanedName"],
                "alternatives": [],
                "scheduleDays": [
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7
                ],
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
            "value": total_duration,
        },
        "description": description,
        "displayName": displayName,
        "durationCalculated": total_duration,
        "alternatives": [],
        "scheduleDays": [1, 2, 3, 4, 5, 6, 7],
        "scheduleWeeks": [1, 2, 3, 4]
    }

    final_action_plan["data"]["routines"].append(super_routine_entry)

    for subroutine in subroutines_entries:
        final_action_plan["data"]["routines"].append(subroutine)

    return final_action_plan

def build_individual_routine_entry(routine, routine_id):
    return {
        "pillar": {
            "pillar": routine.get("pillar", {}).get("pillar"),
            "pillar_de": routine.get("pillar", {}).get("pillar_de"),
            "pillar_en": ""
        },
        "imageUrl": routine.get("resources", [{}])[0].get("imageUrl") or "https://longtermhealth.de",
        "routineId": routine_id,
        "durationCalculated": int(routine.get("durationCalculated", 0)),
        "timeOfDay": "ANY",
        "goal": {
            "unit": {
                "amountUnit": routine.get("amountUnit", {}).get("amountUnit", "MINUTES"),
                "amountUnit_de": routine.get("amountUnit", {}).get("amountUnit_de", "MINUTES"),
                "amountUnit_en": ""
            },
            "value": int(routine.get("amount", 0)),
        },
        "description": routine.get("description", "No description available"),
        "displayName": routine.get("cleanedName", "No Name"),
        "alternatives": [],
        "scheduleDays": [1, 2, 3, 4, 5, 6, 7],
        "scheduleWeeks": [1, 2, 3, 4],
        "parentRoutineId": None
    }

def save_action_plan_json(final_action_plan, file_path='../data/action_plan.json'):
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
    """
    Filters routines by a specific tag and pillar, sorts them by weighted score,
    and returns the sorted list.
    """

    pre_filtered_by_pillar_routines = [
        {**routine, "id": routine_id} for routine_id, routine in routines.items()
        if isinstance(routine, dict) and routine_has_pillar(routine, pillar)
    ]

    filtered_routines = []

    for routine in pre_filtered_by_pillar_routines:
        if isinstance(routine, dict):
            routine_name = routine.get('name', 'No Name')
            routine_id = routine.get('id')
            routine_variations = [variation['variation'] for variation in routine.get('variations', [])]

            if routine_id in added_to_super_routine:
                continue

            if selected_variations.intersection(set(routine_variations)):
                continue

            tags = [t['tag'] for t in routine.get('tags', [])]

            if tag.lower() in (t.lower() for t in tags):
                pillar_value = routine.get('pillar', {})
                if pillar_value.get('pillar', '').upper() == pillar.upper():
                    weighted_score = calculate_weighted_score(routine, weights)

                    if weighted_score is None:
                        weighted_score = 0

                    duration = routine.get("durationCalculated", 0)
                    if not isinstance(duration, (int, float)):
                        duration = 0

                    filtered_routines.append({
                        "id": routine_id,
                        "cleanedName": routine_name,
                        "pillar": pillar_value.get('pillar'),
                        "durationCalculated": duration,
                        "tags": tags,
                        'variations': routine_variations,
                        'impactMovement': routine.get("impactMovement", 0),
                        'impactNutrition': routine.get("impactNutrition", 0),
                        'impactSleep': routine.get("impactSleep", 0),
                        'impactStress': routine.get("impactStress", 0),
                        'impactSocial': routine.get("impactSocial", 0),
                        'impactCognitive': routine.get("impactCognitive", 0),
                        'impactGratitude': routine.get("impactGratitude", 0),
                        'score_rules': routine.get("score_rules", 0),
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
    """
    Creates a custom super routine for a specific pillar by selecting routines matching specific tags,
    ensuring the total time stays within the allocated time.
    """
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

            routine_duration = routine.get("durationCalculated", 0)

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
                selected_variations.update(routine.get('variations', []))
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


def select_routines_for_pillar(pillar, health_scores, routines, allocated_time, weights):
    max_routines = get_number_of_routines(health_scores.get(pillar, 0))

    max_routines = int(max_routines)

    routines_for_knapsack = []
    for routine in routines:
        if routine['attributes']['pillar']['pillar'] == pillar:

            weighted_score = calculate_weighted_score_knapsack(routine, weights)

            routine_with_score = routine.copy()
            routine_with_score['weighted_score'] = weighted_score

            print(
                f"Routine {routine['id']} with weighted_score = {weighted_score} and durationCalculated = {routine_with_score['attributes']['durationCalculated']}")

            routines_for_knapsack.append(routine_with_score)

    routines_for_knapsack.sort(key=lambda x: x['weighted_score'], reverse=True)

    allocated_time = int(allocated_time)

    selected_routines, max_score = knapsack_with_routine_count(routines_for_knapsack, allocated_time, max_routines)

    return selected_routines, max_score


def knapsack_with_routine_count(routines, max_time, max_routines):
    num_routines = len(routines)

    print(f"\nStarting knapsack with {num_routines} routines, max_time = {max_time}, max_routines = {max_routines}")

    dp = [[[0 for _ in range(max_routines + 1)] for _ in range(max_time + 1)] for _ in range(num_routines + 1)]

    for i in range(1, num_routines + 1):
        routine = routines[i - 1]

        print(f"Considering routine {i}: {{'name': '{routine['attributes']['name']}', 'durationCalculated': {routine['attributes']['durationCalculated']}, 'weighted_score': {routine['weighted_score']}}}")

        duration = int(round(routine['attributes']['durationCalculated']))
        score = routine['weighted_score']

        for w in range(max_time + 1):
            for r in range(max_routines + 1):
                dp[i][w][r] = dp[i - 1][w][r]
                if w >= duration and r > 0:
                    dp[i][w][r] = max(dp[i][w][r], dp[i - 1][w - duration][r - 1] + score)

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


def main():
    account_id, daily_time, routines, health_scores = get_routines_with_defaults()
    print('daily_time', daily_time)

    file_path = "../data/routines_with_scores.json"
    routines = load_routines_for_rules(file_path)


    if isinstance(routines, dict):
        routines_list = list(routines.values())
    elif isinstance(routines, list):
        routines_list = routines
    else:
        return

    filtered_routines = filter_excluded_routines(routines_list)
    sorted_routines = sort_routines_by_score_rules(filtered_routines)



    individual_routines = select_routines(health_scores, sorted_routines)
    individual_routines = transform_routines(individual_routines)
    routines = transform_routines(sorted_routines)

    health_scores = {key: value for key, value in health_scores.items() if key != 'Total Score'}

    allocations_by_scores = calculate_daily_allocations_by_scores(daily_time, health_scores, THRESHOLDS)
    allocations_by_weightings = calculate_daily_allocations_by_weightings(daily_time, WEIGHTINGS)
    daily_allocations = combine_allocations(allocations_by_scores, allocations_by_weightings, score_weight=0.7)

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

    movement_super_routine, added_to_super_routine_movement, remaining_time_movement = create_custom_super_routine_for_tags(
        routines,
        movement_tag_counts,
        weights,
        "MOVEMENT",
        daily_allocations["MOVEMENT"]
    )

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

    final_action_plan_movement = build_final_action_plan(routines, {},
                                                         account_id, daily_time,
                                                         routines_for_super_routine_movement,
                                                      "movement_superroutine")

    final_action_plan_sleep = build_final_action_plan(routines, {},
                                                        account_id, daily_time,
                                                        routines_for_super_routine_sleep,
                                                      "sleep_superroutine")

    final_action_plan_nutrition = build_final_action_plan(routines, {},
                                                        account_id, daily_time,
                                                        routines_for_super_routine_nutrition,
                                                      "nutrition_super_routine")

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

    for pillar in pillars:
        allocated_time = daily_allocations[pillar]

        selected_routines, max_score = select_routines_for_pillar(
            pillar, health_scores, filtered_routines, allocated_time, weights
        )

        total_time_selected = sum(routine['attributes']['durationCalculated'] for routine in selected_routines)
        print(f"\nPillar: {pillar} (Before Selection)")
        print(f"Allocated Time: {allocated_time} min")

        print("\nSelected Routines (After Selection):")
        print("-" * 30)
        for routine in selected_routines:
            print(
                f"Routine ID: {routine['id']}, Routine Name: {routine['attributes']['name']}, Duration: {routine['attributes']['durationCalculated']} min, Weighted Score: {routine['weighted_score']}")

        print(f"\nTotal time allocated for {pillar} (After Selection): {total_time_selected} min")
        print("-" * 30)

        final_routines.extend(selected_routines)

    print("\nFinal selected routines (across all pillars):")
    for routine in final_routines:
        print(
            f"Routine ID: {routine['id']}, Duration: {routine['attributes']['durationCalculated']} min, Weighted Score: {routine['weighted_score']}")


    final_routines = transform_routines(final_routines)

    for routine_id in final_routines:
        routine = routines[routine_id]
        individual_entry = build_individual_routine_entry(routine, routine_id)
        final_action_plan["data"]["routines"].append(individual_entry)

    for routine in final_action_plan["data"]["routines"]:
        if isinstance(routine, dict):
            if routine.get("routineId") == "sleep_superroutine":
                routine["routineId"] = 6315
            if routine.get("routineId") == "movement_superroutine":
                routine["routineId"] = 6314
            if routine.get("routineId") == "nutrition_super_routine":
                routine["routineId"] = 6316

    save_action_plan_json(final_action_plan)
    #strapi_post_action_plan(final_action_plan, account_id)



    return final_action_plan

if __name__ == "__main__":
    main()
