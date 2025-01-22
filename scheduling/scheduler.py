import json
import random
from collections import defaultdict

import math
from datetime import datetime, timedelta, timezone
from chart.chart_generation import generate_polar_chart
from chart.converter import create_final_image
from scheduling.filter_service import main as get_routines_with_defaults
from utils.blob_upload import upload_to_blob
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


def calculate_expiration_date(start_date=None):
    """
    Calculates the expiration date as 28 days from the start_date until midnight UTC.
    If no start_date is provided, it uses the current UTC datetime.

    Returns:
        str: ISO formatted expiration date with 'Z' to indicate UTC timezone.
    """
    if start_date is None:
        start_date = datetime.now(timezone.utc)
    else:
        start_date = start_date.astimezone(timezone.utc)

    expiration_datetime = start_date + timedelta(days=27)
    print('start_date',start_date)
    print('expiration_datetime', expiration_datetime)
    expiration_datetime = expiration_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
    expiration_date_str = expiration_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    return expiration_date_str

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

    image_url_mapping_1x1 = {
        "movement_superroutine": "https://lthstore.blob.core.windows.net/images/997_1x1.jpg",
        "sleep_superroutine": "https://lthstore.blob.core.windows.net/images/998_1x1.jpg",
        "nutrition_super_routine": "https://lthstore.blob.core.windows.net/images/999_1x1.jpg",
    }
    image_url_mapping_16x9 = {
        "movement_superroutine": "https://lthstore.blob.core.windows.net/images/997_16x9.jpg",
        "sleep_superroutine": "https://lthstore.blob.core.windows.net/images/998_16x9.jpg",
        "nutrition_super_routine": "https://lthstore.blob.core.windows.net/images/999_16x9.jpg",
    }
    imageUrl_1x1 = image_url_mapping_1x1.get(super_routine_id, None)
    imageUrl_16x9 = image_url_mapping_16x9.get(super_routine_id, None)

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

    displayName_mapping = {
        "sleep_superroutine": "Schlaf",
        "movement_superroutine": "Bewegung",
        "nutrition_super_routine": "Ernährung",
    }

    displayName = displayName_mapping.get(super_routine_id, None)

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

    scheduleCategory_mapping = {
        "sleep_superroutine": "DAILY_ROUTINE",
        "movement_superroutine": "WEEKLY_ROUTINE",
        "nutrition_super_routine": "DAILY_ROUTINE",
    }

    scheduleCategory = scheduleCategory_mapping.get(super_routine_id, None)

    expiration_date = calculate_expiration_date()

    added_subroutines = set()
    subroutines_entries = []
    total_duration = 0

    subroutine_ids = list(routines_for_super_routine)[:max_subroutines_per_superroutine]
    #print('subroutine_ids',subroutine_ids)

    routines_for_super_routine = get_routines_by_ids(routines, subroutine_ids)

    for subroutine_id, subroutine in routines_for_super_routine.items():
        subroutine_duration = (subroutine['attributes']['durationCalculated'])
        total_duration += subroutine_duration

        resource_image_url_1x1 = subroutine.get('attributes', {}).get("resources", [{}])[0].get("imageUrl_1x1") or "https://longtermhealth.de"
        resource_image_url_16x9 = subroutine.get('attributes', {}).get("resources", [{}])[0].get("imageUrl_16x9") or "https://longtermhealth.de"
        subroutine_entry = {
            "pillar": {
                "pillarEnum": subroutine['attributes']['pillar']['pillarEnum'],
                "displayName": subroutine['attributes']['pillar']['displayName']
            },
            "imageUrl_1x1": resource_image_url_1x1,
            "imageUrl_16x9": resource_image_url_16x9,
            "scheduleCategory": subroutine.get('attributes', {}).get("scheduleCategory", 'DAILY_ROUTINE'),
            "routineId": int(subroutine_id),
            "durationCalculated": round(subroutine_duration),
            "timeOfDay": "ANY",
            "goal": {
                "unit": {
                    "amountUnitEnum": subroutine['attributes']['amountUnit']['amountUnitEnum'],
                    "displayName": subroutine['attributes']['amountUnit']['displayName']
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
            "parentRoutineId": parentRoutineId_value,
            "packageName": "packageName",
            "packageTag": "packageTag",
            **({"expirationDate": expiration_date} if subroutine.get('attributes', {}).get("scheduleCategory") == "MONTHLY_CHALLENGE" or "WEEKLY_CHALLENGE" else {})
        }
        subroutines_entries.append(subroutine_entry)


    super_routine_entry = {
        "pillar": {
            "pillarEnum": pillar,
            "displayName": displayName
        },
        "imageUrl_1x1": imageUrl_1x1,
        "imageUrl_16x9": imageUrl_16x9,
        "routineId": super_routine_id,
        "scheduleCategory": scheduleCategory,
        "timeOfDay": timeOfDay,
        "goal": {
            "unit": {
                "amountUnitEnum": "MINUTES",
                "displayName": "Minuten"
            },
            "value": round(total_duration),
        },
        "description": description,
        "displayName": displayName,
        "durationCalculated": round(total_duration),
        "alternatives": [],
        "scheduleDays": scheduleDays,
        "scheduleWeeks": [1, 2, 3, 4],
        "packageName": "packageName",
        "packageTag": "packageTag",
        **({"expirationDate": expiration_date} if scheduleCategory == "MONTHLY_CHALLENGE" or "WEEKLY_CHALLENGE" else {})
    }
    total_duration_movement = ""
    if super_routine_id == "movement_superroutine":
        total_duration_movement = total_duration


    final_action_plan["data"]["routines"].append(super_routine_entry)

    for subroutine in subroutines_entries:
        final_action_plan["data"]["routines"].append(subroutine)


    return final_action_plan, total_duration_movement

def build_individual_routine_entry(routine):

    expiration_date = calculate_expiration_date()
    resource_image_url = routine.get('attributes', {}).get("resources", [{}])[0].get(
        "imageUrl") or "https://longtermhealth.de"

    individual_routine_entry = {
        "pillar": {
            "pillarEnum": routine['attributes']['pillar']['pillarEnum'],
            "displayName": routine['attributes']['pillar']['displayName']
        },
        "imageUrl_1x1": routine.get('attributes', {}).get("resources", [{}])[0].get("imageUrl_1x1") or "https://longtermhealth.de",
        "imageUrl_16x9": routine.get('attributes', {}).get("resources", [{}])[0].get("imageUrl_16x9") or "https://longtermhealth.de",
        "routineId": routine["id"],
        "durationCalculated": int(routine['attributes']['durationCalculated']),
        "timeOfDay": "ANY",
        "goal": {
            "unit": {
                "amountUnitEnum": routine['attributes']['amountUnit']['amountUnitEnum'],
                "displayName": routine['attributes']['amountUnit']['displayName']
            },
            "value": int(routine['attributes']["amount"]),
        },
        "description": routine['attributes']["description"],
        "displayName": routine['attributes']["cleanedName"],
        "alternatives": [],
        "scheduleDays": routine['attributes']["scheduleDays"],
        "scheduleWeeks": routine['attributes']["scheduleWeeks"],
        "scheduleCategory": routine['attributes']["scheduleCategory"],
        "packageName": "packageName",
        "packageTag": "packageTag",
        "parentRoutineId": None,
        **({"expirationDate": expiration_date} if routine['attributes']["scheduleCategory"] == "MONTHLY_CHALLENGE" or "WEEKLY_CHALLENGE" else {})
    }
    return individual_routine_entry


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
                pillar_value = routine['attributes']['pillar']['pillarEnum']
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
        #print(f"Day {day}:")
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

                #print(f"  - {routine[0]} (Pillar: {pillar}, Duration: {duration} minutes)")

            #print("Total duration per pillar for the day:")
            for pillar, total_duration in pillar_durations_per_day[day].items():
                print(f"Pillar {pillar}")
                #print(f"used      {total_duration} minutes")
                #print(f"allocated {allocated_time} minutes")
        else:
            print("  No routines scheduled.")
        #print()

    #print("Total duration per pillar across all 28 days:")
    for pillar in total_used_durations:
        used_duration = total_used_durations[pillar]
        allocated_duration = total_allocated_durations.get(pillar, 0)
        #print(f"Pillar {pillar}:")
        #print(f"  Total used:      {used_duration} minutes")
        #print(f"  Total allocated: {allocated_duration} minutes")

    #print("\nOverall total across all pillars:")
    #print(f"Total used:      {total_used_all} minutes")
    #print(f"Total allocated: {total_allocated_all} minutes")

def create_individual_routines(selected_pkgs, routines_data, target_package='GRATITUDE BASICS'):
    target_package = next(
        (pkg for pkg in selected_pkgs if pkg['packageTag'].upper() == target_package.upper()), None
    )
    if not target_package:
        print(f"No package found for pillar '{target_package}'.")
        return []
    package_routines = target_package.get('selected_package', {}).get('routines', [])
    individual_routines_local = []
    for routine_pkg in package_routines:
        package_routine_id = routine_pkg.get('packageRoutineId')
        schedule_category = routine_pkg.get('scheduleCategory')
        schedule_days = routine_pkg.get('scheduleDays')
        schedule_weeks = routine_pkg.get('scheduleWeeks')
        routine_affiliation = routine_pkg.get('routineAffiliation')
        matching_routine = next(
            (r for r in routines_data if r['attributes'].get('routineUniqueId') == package_routine_id), None
        )
        if not matching_routine:
            continue
        individual_routines_local.append({
            'routineUniqueId': matching_routine['id'],
            'name': routine_pkg['name'],
            'scheduleCategory': schedule_category,
            'scheduleDays': schedule_days,
            'scheduleWeeks': schedule_weeks,
            'routineAffiliation': routine_affiliation
        })
    return individual_routines_local



def build_routine_unique_id_map(routines_data):
    mapping = {}
    for rt in routines_data:
        unique_id = rt.get('attributes', {}).get('routineUniqueId')
        if unique_id is not None:
            mapping[unique_id] = rt.get('id')
    return mapping


def add_individual_routine_entry(final_action_plan, routines, routine_id, scheduleCategory, scheduleDays, scheduleWeeks, parentRoutineId = None):
    """
    Adds an individual routine entry to the final_action_plan by specifying the routine_id,
    scheduleCategory, scheduleDays, and scheduleWeeks.
    """
    routine = next((r for r in routines if r['id'] == routine_id), None)
    if not routine:
        print(f"Routine with id {routine_id} not found.")
        return

    if scheduleCategory == "MONTHLY_CHALLENGE":
        expiration_date = calculate_expiration_date(days=28)
    elif scheduleCategory == "WEEKLY_CHALLENGE" and scheduleWeeks == "1":
        expiration_date = calculate_expiration_date(days=7)
        print('routine1', routine)
    elif scheduleCategory == "WEEKLY_CHALLENGE" and scheduleWeeks == "2":
        expiration_date = calculate_expiration_date(days=14)
        print('routine2',routine)
    elif scheduleCategory == "WEEKLY_CHALLENGE" and scheduleWeeks == "3":
        expiration_date = calculate_expiration_date(days=21)
        print('routine1', routine)
    elif scheduleCategory == "WEEKLY_CHALLENGE" and scheduleWeeks == "4":
        expiration_date = calculate_expiration_date(days=28)
    else:
        print("Unknown schedule category or unsupported number of weeks. Setting default expiration to 7 days.")
        expiration_date = calculate_expiration_date(days=1)

    individual_entry = {
        "pillar": {
            "pillarEnum": routine['attributes']['pillar']['pillarEnum'],
            "displayName": routine['attributes']['pillar']['displayName']
        },
        "imageUrl_1x1": routine.get('attributes', {}).get("resources", [{}])[0].get("imageUrl_1x1") or "https://longtermhealth.de",
        "imageUrl_16x9": routine.get('attributes', {}).get("resources", [{}])[0].get("imageUrl_16x9") or "https://longtermhealth.de",
        "routineId": routine["id"],
        "durationCalculated": int(routine['attributes']['durationCalculated']),
        "timeOfDay": "ANY",
        "goal": {
            "unit": {
                "amountUnitEnum": routine['attributes']['amountUnit']['amountUnitEnum'],
                "displayName": routine['attributes']['amountUnit']['displayName']
            },
            "value": int(routine['attributes']["amount"]),
        },
        "description": routine['attributes']["description"],
        "displayName": routine['attributes']["cleanedName"],
        "alternatives": [],
        "scheduleDays": scheduleDays,
        "scheduleWeeks": scheduleWeeks,
        "scheduleCategory": scheduleCategory,
        "packageName": "packageName",
        "packageTag": "packageTag",
        "parentRoutineId": parentRoutineId,
        **({"expirationDate": expiration_date} if scheduleCategory in ["MONTHLY_CHALLENGE", "WEEKLY_CHALLENGE"] else {})
    }
    print(f"Added individual routine with ID {routine_id} to the action plan.")
    final_action_plan["data"]["routines"].append(individual_entry)

def calculate_expiration_date(start_date=None, days=28):
    """
    Calculates the expiration date as 'days' from the start_date until midnight UTC.
    If no start_date is provided, it uses the current UTC datetime.
    """
    if start_date is None:
        start_date = datetime.now(timezone.utc)
    else:
        start_date = start_date.astimezone(timezone.utc)

    expiration_datetime = start_date + timedelta(days=days - 1)
    expiration_datetime = expiration_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
    expiration_date_str = expiration_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    return expiration_date_str


def main():
    account_id, daily_time, routines, health_scores, user_data, answers, gender, selected_packages = get_routines_with_defaults()
    print('daily_time',daily_time)
    print('health_scores', health_scores)

    total_score = health_scores['Total Score']
    start_weekday = datetime.today().weekday()  # Monday=0,...Sunday=6
    #print('start_weekday',start_weekday)
    #file_path = "./data/routines_with_scores.json"
    #routines = load_routines_for_rules(file_path)

    if gender == "Weiblich":
        gender = "FEMALE"
    else:
        gender = "MALE"



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
    #print("daily_allocations before reallocation:", daily_allocations)

    health_scores_with_tag = create_health_scores_with_tag(health_scores)
    #print('health_scores_with_tag',health_scores_with_tag)
    health_scores_with_tag_payload_strapi = create_health_scores_with_structure(account_id, health_scores)
    #print('health_scores_with_tag_payload_strapi',json.dumps(health_scores_with_tag_payload_strapi, indent=4, ensure_ascii=False))

    reallocations, updated_allocations = allocate_more_time_to_focus_areas(daily_allocations, health_scores_with_tag)

    #print("Reallocations to Focus Areas:", reallocations)
    #print("Updated Allocations allocate_more_time_to_focus_areas:", updated_allocations)

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
        #print('sleep_answer is sehr gut, skipping sleep super routine',sleep_answer)
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

    packages_file_path = "../data/packages_with_id.json"
    with open(packages_file_path, "r") as file:
        data = json.load(file)
    print('selected_packages', selected_packages)
    print('data', data)

    ids_by_package_name = {}
    for pillar_name, pillar_data in data["packages"]["pillars"].items():
        for package_tag, tag_data in pillar_data.items():
            for package_name, package_data in tag_data.items():
                ids_by_package_name[package_name] = []
                for routine in package_data["routines"]:
                    if routine["id"] is not None:
                        ids_by_package_name[package_name].append(routine["id"])

    for package_name, ids in ids_by_package_name.items():
        print(f"{package_name}: {ids}")
        pass


    if len(sleep_super_routine) == 0:
        final_action_plan_sleep = {"data": {"routines": []}}
    else:
        final_action_plan_sleep, _ = build_final_action_plan(
            routines,
            {},
            account_id,
            daily_time,
            {sr['id']: sr for sr in sleep_super_routine},
            "sleep_superroutine"
        )

    final_action_plan_nutrition, _ = build_final_action_plan(
        routines,
        {},
        account_id,
        daily_time,
        {sr['id']: sr for sr in nutrition_super_routine},
        "nutrition_super_routine"
    )

    final_action_plan_movement, total_duration_movement = build_final_action_plan(
        routines,
        {},
        account_id,
        daily_time,
        {sr['id']: sr for sr in movement_super_routine},
        "movement_superroutine"
    )


    final_action_plan = {
        "data": {
            "accountId": account_id,
            "periodInDays": 28,
            "gender": gender.upper(),
            "totalDailyTimeInMins": daily_time,
            "routines": final_action_plan_movement["data"]["routines"] +
                        final_action_plan_sleep["data"]["routines"] +
                        final_action_plan_nutrition["data"]["routines"]
        }
    }



    pillars = ['SOCIAL_ENGAGEMENT', 'STRESS', 'GRATITUDE', 'COGNITIVE_ENHANCEMENT']
    final_routines = []


    routine_unique_id_map = build_routine_unique_id_map(routines)

    individual_routines_stress = create_individual_routines(selected_packages, routines, target_package='STRESS BASICS')
    individual_routines_gratitude = create_individual_routines(selected_packages, routines, target_package='GRATITUDE BASICS')
    individual_routines_fasting = create_individual_routines(selected_packages, routines, target_package='FASTING BASICS')
    individual_routines_nutrition = create_individual_routines(selected_packages, routines, target_package='NUTRITION BASICS')

    for entry in individual_routines_stress:
        add_individual_routine_entry(
            final_action_plan,
            routines_list,
            entry["routineUniqueId"],
            entry["scheduleCategory"],
            entry["scheduleDays"],
            entry["scheduleWeeks"],
            2219
        )
    for entry in individual_routines_gratitude:
        add_individual_routine_entry(
            final_action_plan,
            routines_list,
            entry["routineUniqueId"],
            entry["scheduleCategory"],
            entry["scheduleDays"],
            entry["scheduleWeeks"],
            2218
        )
    for entry in individual_routines_fasting:
        add_individual_routine_entry(
            final_action_plan,
            routines_list,
            entry["routineUniqueId"],
            entry["scheduleCategory"],
            entry["scheduleDays"],
            entry["scheduleWeeks"],
            3266
        )


    for entry in individual_routines_nutrition:
        add_individual_routine_entry(
            final_action_plan,
            routines_list,
            entry["routineUniqueId"],
            entry["scheduleCategory"],
            entry["scheduleDays"],
            entry["scheduleWeeks"],
            999
        )











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
