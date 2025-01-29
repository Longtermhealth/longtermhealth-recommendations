import json
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Set
from scheduling.filter_service import main as get_routines_with_defaults
from utils.strapi_api import strapi_post_action_plan, strapi_post_health_scores

SUPER_ROUTINE_CONFIG = {
    "sleep_superroutine": {
        "routineId": 998,
        "pillar": "SLEEP",
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/998_1x1.jpg",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/998_16x9.jpg",
        "description": (
            "Entwickle ein tägliches Schlafritual, um den Körper und Geist auf die "
            "anstehende Schlafphase vorzubereiten und so ein einfacheres Einschlafen zu fördern."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "ROUTINE",
                "displayName": "Routine"
            }
        },
        "displayName": "Abendritual",
        "pillar_de": "Schlaf",
        "timeOfDay": "EVENING",
        "scheduleDays": [1, 2, 3, 4, 5, 6, 7],
        "scheduleCategory": "DAILY_ROUTINE",
    },
    "movement_superroutine": {
        "routineId": 997,
        "pillar": "MOVEMENT",
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/997_1x1.jpg",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/997_16x9.jpg",
        "description": (
            "Ein Fullbody Workout kombiniert Warm-up, Cardio, Krafttraining und Cool-down, um "
            "den ganzen Körper effektiv zu trainieren. Nach einer kurzen Aufwärmphase folgen "
            "Ausdauerübungen und gezielte Kraftübungen für alle Muskelgruppen. Abschließend "
            "sorgen Dehnübungen für eine bessere Regeneration und Entspannung."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "MINUTES",
                "displayName": "Minuten"
            }
        },
        "displayName": "Fullbody Workout",
        "pillar_de": "Bewegung",
        "timeOfDay": "ANY",
        "scheduleDays": [1, 2, 3, 4, 5],
        "scheduleCategory": "WEEKLY_ROUTINE",
    },
    "lower_body_strength_training_super_routine": {
        "routineId": 996,
        "pillar": "MOVEMENT",
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/997_1x1.jpg",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/997_16x9.jpg",
        "description": (
            "Ein Unterkörper-Krafttraining kombiniert Warm-up, Cardio, Krafttraining und Cool-down, um "
            "den ganzen Körper effektiv zu trainieren. Nach einer kurzen Aufwärmphase folgen "
            "Ausdauerübungen und gezielte Kraftübungen für alle Muskelgruppen. Abschließend "
            "sorgen Dehnübungen für eine bessere Regeneration und Entspannung."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "MINUTES",
                "displayName": "Minuten"
            }
        },
        "displayName": "Unterkörper-Krafttraining",
        "pillar_de": "Bewegung",
        "timeOfDay": "ANY",
        "scheduleDays": [1, 2, 3, 4, 5],
        "scheduleCategory": "WEEKLY_ROUTINE",
    },
    "core_strength_training_super_routine": {
        "routineId": 994,
        "pillar": "MOVEMENT",
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/994_1x1.jpg",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/994_16x9.jpg",
        "description": (
            "Ein Core-Krafttraining kombiniert Warm-up, Cardio, Krafttraining und Cool-down, um "
            "den ganzen Körper effektiv zu trainieren. Nach einer kurzen Aufwärmphase folgen "
            "Ausdauerübungen und gezielte Kraftübungen für alle Muskelgruppen. Abschließend "
            "sorgen Dehnübungen für eine bessere Regeneration und Entspannung."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "MINUTES",
                "displayName": "Minuten"
            }
        },
        "displayName": "Core-Krafttraining",
        "pillar_de": "Bewegung",
        "timeOfDay": "ANY",
        "scheduleDays": [1, 2, 3, 4, 5],
        "scheduleCategory": "WEEKLY_ROUTINE",
    },
    "upper_body_strength_training_super_routine": {
        "routineId": 995,
        "pillar": "MOVEMENT",
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/997_1x1.jpg",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/997_16x9.jpg",
        "description": (
            "Ein Oberkörper-Krafttraining kombiniert Warm-up, Cardio, Krafttraining und Cool-down, um "
            "den ganzen Körper effektiv zu trainieren. Nach einer kurzen Aufwärmphase folgen "
            "Ausdauerübungen und gezielte Kraftübungen für alle Muskelgruppen. Abschließend "
            "sorgen Dehnübungen für eine bessere Regeneration und Entspannung."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "MINUTES",
                "displayName": "Minuten"
            }
        },
        "displayName": "Oberkörper-Krafttraining",
        "pillar_de": "Bewegung",
        "timeOfDay": "ANY",
        "scheduleDays": [1, 2, 3, 4, 5],
        "scheduleCategory": "WEEKLY_ROUTINE",
    },
    "5_minute_cardio_1_superroutine": {
        "routineId": 988,
        "pillar": "MOVEMENT",
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/988_1x1.jpg",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/988_16x9.jpg",
        "description": (
            "Ein 5-minütiges Cardio-Workout steigert die Herzfrequenz, fördert die Durchblutung und verbrennt Kalorien in kurzer Zeit. Es verbessert Ausdauer, Energielevels und unterstützt die Fettverbrennung. Ideal für schnelle, effektive Fitnesseinheiten."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "MINUTES",
                "displayName": "Minuten"
            }
        },
        "displayName": "5 Minuten Cardio Workout, 1",
        "pillar_de": "Bewegung",
        "timeOfDay": "ANY",
        "scheduleDays": [1],
        "scheduleCategory": "WEEKLY_ROUTINE",
    },
    "5_minute_cardio_2_superroutine": {
        "routineId": 985,
        "pillar": "MOVEMENT",
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/988_1x1.jpg",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/988_16x9.jpg",
        "description": (
            "Ein 5-minütiges Cardio-Workout steigert die Herzfrequenz, fördert die Durchblutung und verbrennt Kalorien in kurzer Zeit. Es verbessert Ausdauer, Energielevels und unterstützt die Fettverbrennung. Ideal für schnelle, effektive Fitnesseinheiten."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "MINUTES",
                "displayName": "Minuten"
            }
        },
        "displayName": "5 Minuten Cardio Workout, 2",
        "pillar_de": "Bewegung",
        "timeOfDay": "ANY",
        "scheduleDays": [2],
        "scheduleCategory": "WEEKLY_ROUTINE",
    },
    "5_minute_cardio_3_superroutine": {
        "routineId": 984,
        "pillar": "MOVEMENT",
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/988_1x1.jpg",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/988_16x9.jpg",
        "description": (
            "Ein 5-minütiges Cardio-Workout steigert die Herzfrequenz, fördert die Durchblutung und verbrennt Kalorien in kurzer Zeit. Es verbessert Ausdauer, Energielevels und unterstützt die Fettverbrennung. Ideal für schnelle, effektive Fitnesseinheiten."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "MINUTES",
                "displayName": "Minuten"
            }
        },
        "displayName": "5 Minuten Cardio Workout, 3",
        "pillar_de": "Bewegung",
        "timeOfDay": "ANY",
        "scheduleDays": [3],
        "scheduleCategory": "WEEKLY_ROUTINE",
    },
    "5_minute_cardio_4_superroutine": {
        "routineId": 983,
        "pillar": "MOVEMENT",
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/988_1x1.jpg",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/988_16x9.jpg",
        "description": (
            "Ein 5-minütiges Cardio-Workout steigert die Herzfrequenz, fördert die Durchblutung und verbrennt Kalorien in kurzer Zeit. Es verbessert Ausdauer, Energielevels und unterstützt die Fettverbrennung. Ideal für schnelle, effektive Fitnesseinheiten."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "MINUTES",
                "displayName": "Minuten"
            }
        },
        "displayName": "5 Minuten Cardio Workout, 4",
        "pillar_de": "Bewegung",
        "timeOfDay": "ANY",
        "scheduleDays": [4],
        "scheduleCategory": "WEEKLY_ROUTINE",
    },
    "5_minute_cardio_5_superroutine": {
        "routineId": 982,
        "pillar": "MOVEMENT",
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/988_1x1.jpg",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/988_16x9.jpg",
        "description": (
            "Ein 5-minütiges Cardio-Workout steigert die Herzfrequenz, fördert die Durchblutung und verbrennt Kalorien in kurzer Zeit. Es verbessert Ausdauer, Energielevels und unterstützt die Fettverbrennung. Ideal für schnelle, effektive Fitnesseinheiten."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "MINUTES",
                "displayName": "Minuten"
            }
        },
        "displayName": "5 Minuten Cardio Workout, 5",
        "pillar_de": "Bewegung",
        "timeOfDay": "ANY",
        "scheduleDays": [5],
        "scheduleCategory": "WEEKLY_ROUTINE",
    },
    "5_minute_cardio_6_superroutine": {
        "routineId": 981,
        "pillar": "MOVEMENT",
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/988_1x1.jpg",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/988_16x9.jpg",
        "description": (
            "Ein 5-minütiges Cardio-Workout steigert die Herzfrequenz, fördert die Durchblutung und verbrennt Kalorien in kurzer Zeit. Es verbessert Ausdauer, Energielevels und unterstützt die Fettverbrennung. Ideal für schnelle, effektive Fitnesseinheiten."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "MINUTES",
                "displayName": "Minuten"
            }
        },
        "displayName": "5 Minuten Cardio Workout, 6",
        "pillar_de": "Bewegung",
        "timeOfDay": "ANY",
        "scheduleDays": [6],
        "scheduleCategory": "WEEKLY_ROUTINE",
    },
    "5_minute_cardio_7_superroutine": {
        "routineId": 980,
        "pillar": "MOVEMENT",
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/988_1x1.jpg",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/988_16x9.jpg",
        "description": (
            "Ein 5-minütiges Cardio-Workout steigert die Herzfrequenz, fördert die Durchblutung und verbrennt Kalorien in kurzer Zeit. Es verbessert Ausdauer, Energielevels und unterstützt die Fettverbrennung. Ideal für schnelle, effektive Fitnesseinheiten."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "MINUTES",
                "displayName": "Minuten"
            }
        },
        "displayName": "5 Minuten Cardio Workout, 7",
        "pillar_de": "Bewegung",
        "timeOfDay": "ANY",
        "scheduleDays": [7],
        "scheduleCategory": "WEEKLY_ROUTINE",
    },
    "nutrition_super_routine": {
        "routineId": 999,
        "pillar": "NUTRITION",
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/999_1x1.jpg",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/999_16x9.jpg",
        "description": (
            "Eine gesunde Ernährung basiert auf einer ausgewogenen Mischung aus frischen, "
            "unverarbeiteten Lebensmitteln wie Obst, Gemüse, Vollkornprodukten, gesunden Fetten "
            "und hochwertigen Proteinquellen. Sie liefert alle wichtigen Nährstoffe, fördert "
            "Energie, Wohlbefinden und unterstützt langfristig die Gesundheit. Ausreichendes "
            "Trinken von Wasser und das Reduzieren von Zucker, Salz und stark verarbeiteten "
            "Lebensmitteln gehören ebenfalls dazu."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "ROUTINE",
                "displayName": "Routine"
            }
        },
        "displayName": "Bewusste Ernährung",
        "pillar_de": "Ernährung",
        "timeOfDay": "ANY",
        "scheduleDays": [1, 2, 3, 4, 5, 6, 7],
        "scheduleCategory": "DAILY_ROUTINE",
    },
    "anti_inflammation_super_routine": {
        "routineId": 986,
        "pillar": "NUTRITION",
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/986_1x1.jpg",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/986_16x9.jpg",
        "description": (
            "Das Anti-Entzündungs-Paket umfasst gezielte Ernährung und Nahrungsergänzungsmittel, die entzündungshemmend wirken. Es fördert die Gelenkgesundheit, reduziert Entzündungen im Körper und unterstützt das allgemeine Wohlbefinden."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "ROUTINE",
                "displayName": "Routine"
            }
        },
        "displayName": "Anti-Entzündungs-Paket",
        "pillar_de": "Ernährung",
        "timeOfDay": "ANY",
        "scheduleDays": [1, 2, 3, 4, 5, 6, 7],
        "scheduleCategory": "DAILY_ROUTINE",
    },
    "gratitude_super_routine": {
        "routineId": 990,
        "pillar": "GRATITUDE",
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/999_1x1.jpg",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/999_16x9.jpg",
        "description": (
            "Das Dankbarkeitsritual stärkt positive Gedanken, steigert Wohlbefinden und Fokus. Es fördert Achtsamkeit, reduziert Stress und bringt mehr Freude in den Alltag."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "ROUTINE",
                "displayName": "Routine"
            }
        },
        "displayName": "Dankbarkeitsritual",
        "pillar_de": "Dankbarkeit",
        "timeOfDay": "ANY",
        "scheduleDays": [1, 2, 3, 4, 5, 6, 7],
        "scheduleCategory": "DAILY_ROUTINE",
    },
}


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


def load_routines_for_rules(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        routines_list = json.load(f)
    routines = {routine['id']: routine for routine in routines_list}
    return routines


def save_action_plan_json(final_action_plan,
                          file_path='../data/action_plan.json'):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(final_action_plan, f, ensure_ascii=False, indent=2)


def filter_excluded_routines(routines):
    return [
        routine for routine in routines
        if isinstance(routine, dict) and routine.get("rule_status") != "excluded"
    ]


def sort_routines_by_score_rules(routines):
    return sorted(routines, key=lambda routine: routine.get("score_rules", 0), reverse=True)


def create_health_scores_with_structure(account_id, health_scores):
    """
    Builds the final health-scores structure (with interpretation) to post to Strapi.
    """
    score_interpretation_dict = {
        "MOVEMENT": {
            "FOKUS": "Es ist Zeit, mehr Bewegung in deinen Alltag zu integrieren. Kleine Schritte können einen großen Unterschied für deine Gesundheit machen!",
            "GUT": "Deine körperliche Aktivität ist gut! Mit ein wenig mehr Bewegung kannst du deine Fitness auf das nächste Level heben.",
            "OPTIMAL": "Fantastische Leistung! Deine regelmäßige Bewegung stärkt deine Gesundheit optimal. Weiter so!"
        },
        "NUTRITION": {
            "FOKUS": "Achte mehr auf eine ausgewogene Ernährung. Gesunde Essgewohnheiten geben dir Energie und Wohlbefinden.",
            "GUT": "Deine Ernährung ist auf einem guten Weg! Mit kleinen Anpassungen kannst du deine Nährstoffzufuhr weiter optimieren.",
            "OPTIMAL": "Exzellente Ernährungsgewohnheiten! Du versorgst deinen Körper optimal mit wichtigen Nährstoffen. Weiter so!"
        },
        "SLEEP": {
            "FOKUS": "Verbessere deine Schlafgewohnheiten für mehr Energie und bessere Gesundheit. Guter Schlaf ist essenziell!",
            "GUT": "Dein Schlaf ist gut! Ein paar Änderungen können dir helfen, noch erholsamer zu schlafen.",
            "OPTIMAL": "Ausgezeichneter Schlaf! Du sorgst für optimale Erholung und Vitalität. Weiter so!"
        },
        "SOCIAL_ENGAGEMENT": {
            "FOKUS": "Pflege deine sozialen Beziehungen. Verbindungen zu anderen sind wichtig für dein emotionales Wohlbefinden.",
            "GUT": "Deine sozialen Beziehungen sind gut! Mit ein wenig mehr Engagement kannst du deine Verbindungen weiter vertiefen.",
            "OPTIMAL": "Starke und erfüllende soziale Beziehungen! Du pflegst wertvolle Verbindungen, die dein Leben bereichern. Weiter so!"
        },
        "STRESS": {
            "FOKUS": "Es ist wichtig, Wege zu finden, um deinen Stress besser zu bewältigen. Kleine Pausen und Entspannungstechniken können helfen.",
            "GUT": "Dein Umgang mit Stress ist gut! Mit weiteren Strategien kannst du deine Stressresistenz weiter stärken.",
            "OPTIMAL": "Du meisterst Stress hervorragend! Deine effektiven Bewältigungsstrategien tragen zu deinem Wohlbefinden bei. Weiter so!"
        },
        "GRATITUDE": {
            "FOKUS": "Nimm dir Zeit, die positiven Dinge im Leben zu schätzen. Dankbarkeit kann dein Wohlbefinden erheblich steigern.",
            "GUT": "Du zeigst bereits Dankbarkeit! Mit kleinen Ergänzungen kannst du deine positive Einstellung noch weiter ausbauen.",
            "OPTIMAL": "Eine wunderbare Haltung der Dankbarkeit! Deine positive Sicht bereichert dein Leben und das deiner Mitmenschen. Weiter so!"
        },
        "COGNITIVE_ENHANCEMENT": {
            "FOKUS": "Fordere deinen Geist regelmäßig heraus. Neue Lernmöglichkeiten können deine geistige Fitness verbessern.",
            "GUT": "Deine kognitive Förderung ist gut! Mit zusätzlichen Aktivitäten kannst du deine geistige Leistungsfähigkeit weiter steigern.",
            "OPTIMAL": "Hervorragende geistige Fitness! Du hältst deinen Verstand aktiv und stark. Weiter so!"
        }
    }

    def get_score_details(pillar, score):
        if score < 50:
            rating = "FOKUS"
        elif 50 <= score < 80:
            rating = "GUT"
        else:
            rating = "OPTIMAL"
        return {
            "ratingEnum": rating,
            "displayName": rating.capitalize(),
            "scoreInterpretation": score_interpretation_dict.get(pillar, {}).get(rating, "No interpretation available.")
        }

    total_score = sum(health_scores.values()) / len(health_scores)
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
            "pillarScores": pillars
        }
    }


def find_mapped_id(routine_unique_id_map, unique_id):
    return routine_unique_id_map.get(unique_id, None)


def add_individual_routine_entry(
        final_action_plan: dict,
        routines: List[Dict[str, Any]],
        routine_id: int,
        scheduleCategory: str,
        scheduleDays: str,
        scheduleWeeks: str,
        packageTag: str,
        routine_unique_id_map: Dict[int, int],
        parentRoutineId: Optional[int] = None,
) -> None:
    """
    Adds an individual routine entry to the final_action_plan by specifying the routine_id,
    scheduleCategory, scheduleDays, scheduleWeeks, and conditionally parentRoutineId.
    Also adds the corresponding super routine if parentRoutineId is provided.

    Args:
        final_action_plan (dict): The action plan to which the routine will be added.
        routines (List[Dict[str, Any]]): List of all available routines.
        routine_id (int): The unique ID of the routine to add.
        scheduleCategory (str): The schedule category of the routine.
        scheduleDays (str): The days on which the routine is scheduled.
        scheduleWeeks (str): The weeks during which the routine is scheduled.
        parentRoutineId (int, optional): The parent routine ID if applicable.

    Returns:
        None
    """

    routine = next((r for r in routines if r['id'] == routine_id), None)
    if not routine:
        print(f"Routine with id {routine_id} not found.")
        return

    if scheduleCategory == "MONTHLY_CHALLENGE":
        expiration_date = calculate_expiration_date(days=28)
    elif scheduleCategory == "WEEKLY_CHALLENGE":
        weeks_mapping = {
            "1": 7,
            "2": 14,
            "3": 21,
            "4": 28
        }
        expiration_days = weeks_mapping.get(scheduleWeeks, 7)
        if scheduleWeeks in weeks_mapping:
            expiration_date = calculate_expiration_date(days=expiration_days)
            print(
                f"Routine '{routine['attributes'].get('name')}' scheduled for {scheduleWeeks} week(s). Expiration set to {expiration_days} days.")
        else:
            print("Unsupported number of weeks. Setting default expiration to 7 days.")
            expiration_date = calculate_expiration_date(days=7)
    else:
        print("Unknown schedule category or unsupported number of weeks. Setting default expiration to 7 days.")
        expiration_date = calculate_expiration_date(days=7)

    routine_class = routine.get('attributes', {}).get('routineClass')
    print('routine_class',routine_class)
    if routine_class and isinstance(routine_class, dict):
        package_name = routine_class.get('routineClassEnum', 'DefaultEnum')
        routine_class_display_name = routine_class.get('displayName', 'test')
    else:
        package_name = 'DefaultEnum'
        routine_class_display_name = 'DefaultDisplayName'

    mapped_id = None

    if parentRoutineId:
        unique_id_to_find = parentRoutineId
        print('unique_id_to_find', unique_id_to_find)
        mapped_id = find_mapped_id(routine_unique_id_map, unique_id_to_find)
        print(f"Mapped ID for Unique ID {unique_id_to_find}: {mapped_id}")
        print('Processing routine with parentRoutineId:', parentRoutineId)

    individual_entry = {
        "pillar": {
            "pillarEnum": routine['attributes']['pillar']['pillarEnum'],
            "displayName": routine['attributes']['pillar']['displayName']
        },
        "imageUrl_1x1": routine.get('attributes', {}).get("resources", [{}])[0].get(
            "imageUrl_1x1") or "https://longtermhealth.de",
        "imageUrl_16x9": routine.get('attributes', {}).get("resources", [{}])[0].get(
            "imageUrl_16x9") or "https://longtermhealth.de",
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
        "packageName": routine_class_display_name,
        "packageTag": packageTag,
        "parentRoutineId": mapped_id,
        **({"expirationDate": expiration_date} if scheduleCategory in ["MONTHLY_CHALLENGE", "WEEKLY_CHALLENGE"] else {})
    }
    print(f"Added individual routine with ID {routine_id} to the action plan.")
    final_action_plan["data"]["routines"].append(individual_entry)

    if parentRoutineId:
        super_routine_key = next(
            (key for key, config in SUPER_ROUTINE_CONFIG.items() if config["routineId"] == parentRoutineId),
            None
        )

        if not super_routine_key:
            print(f"Super routine configuration for routineId {parentRoutineId} not found.")
            return

        super_routine_config = SUPER_ROUTINE_CONFIG[super_routine_key]

        super_routine_exists = any(
            routine_entry['routineId'] == mapped_id
            for routine_entry in final_action_plan["data"]["routines"]
        )

        if not super_routine_exists:
            super_routine_entry = {
                "pillar": {
                    "pillarEnum": super_routine_config['pillar'],
                    "displayName": super_routine_config['pillar_de']
                },
                "imageUrl_1x1": super_routine_config.get("imageUrl_1x1") or "https://longtermhealth.de",
                "imageUrl_16x9": super_routine_config.get("imageUrl_16x9") or "https://longtermhealth.de",
                "routineId": super_routine_config["routineId"],
                "durationCalculated": int(routine['attributes']['durationCalculated']),
                "timeOfDay": super_routine_config.get("timeOfDay", "ANY"),
                "goal": {
                    "unit": {
                        "amountUnitEnum": "MINUTES",
                        "displayName": "Minuten"
                    },
                    "value": int(routine['attributes']["durationCalculated"])
                },
                "description": super_routine_config.get("description", ""),
                "displayName": super_routine_config.get("displayName", "Unnamed Super Routine"),
                "alternatives": [],
                "scheduleDays": super_routine_config.get("scheduleDays", "1,2,3,4,5,6,7"),
                "scheduleWeeks": super_routine_config.get("scheduleWeeks", "1,2,3,4"),
                "scheduleCategory": super_routine_config.get("scheduleCategory", "DAILY_ROUTINE"),
                "packageName": routine_class_display_name,
                "packageTag": packageTag,
                "parentRoutineId": None,
                **({"expirationDate": calculate_expiration_date(days=28)} if super_routine_config.get(
                    "scheduleCategory") in ["MONTHLY_CHALLENGE", "WEEKLY_ROUTINE"] else {})
            }
            print(f"Added super routine with ID {super_routine_config['routineId']} to the action plan.")
            super_routine_entry["routineId"] = mapped_id
            final_action_plan["data"]["routines"].append(super_routine_entry)
        else:
            print(f"Super routine with ID {super_routine_config['routineId']} already exists in the action plan.")


def add_individual_routine_entry_without_parent(
        final_action_plan: dict,
        routines: List[Dict[str, Any]],
        routine_id: int,
        scheduleCategory: str,
        scheduleDays: str,
        scheduleWeeks: str,
        packageTag: str,
        routine_unique_id_map: Dict[int, int],
        parentRoutineId: Optional[int] = None,
) -> None:
    """
    Adds an individual routine entry to the final_action_plan by specifying the routine_id,
    scheduleCategory, scheduleDays, scheduleWeeks, and conditionally parentRoutineId.
    Also adds the corresponding super routine if parentRoutineId is provided.

    Args:
        final_action_plan (dict): The action plan to which the routine will be added.
        routines (List[Dict[str, Any]]): List of all available routines.
        routine_id (int): The unique ID of the routine to add.
        scheduleCategory (str): The schedule category of the routine.
        scheduleDays (str): The days on which the routine is scheduled.
        scheduleWeeks (str): The weeks during which the routine is scheduled.
        parentRoutineId (int, optional): The parent routine ID if applicable.

    Returns:
        None
    """

    routine = next((r for r in routines if r['id'] == routine_id), None)
    if not routine:
        print(f"Routine with id {routine_id} not found.")
        return

    if scheduleCategory == "MONTHLY_CHALLENGE":
        expiration_date = calculate_expiration_date(days=28)
    elif scheduleCategory == "WEEKLY_CHALLENGE":
        weeks_mapping = {
            "1": 7,
            "2": 14,
            "3": 21,
            "4": 28
        }
        expiration_days = weeks_mapping.get(scheduleWeeks, 7)
        if scheduleWeeks in weeks_mapping:
            expiration_date = calculate_expiration_date(days=expiration_days)
            print(
                f"Routine '{routine['attributes'].get('name')}' scheduled for {scheduleWeeks} week(s). Expiration set to {expiration_days} days.")
        else:
            print("Unsupported number of weeks. Setting default expiration to 7 days.")
            expiration_date = calculate_expiration_date(days=7)
    else:
        print("Unknown schedule category or unsupported number of weeks. Setting default expiration to 7 days.")
        expiration_date = calculate_expiration_date(days=7)

    routine_class = routine.get('attributes', {}).get('routineClass')

    if routine_class and isinstance(routine_class, dict):
        package_name = routine_class.get('routineClassEnum', 'DefaultEnum')
        routine_class_display_name = routine_class.get('displayName', 'DefaultDisplayName')
    else:
        package_name = 'DefaultEnum'
        routine_class_display_name = 'DefaultDisplayName'

    mapped_id = None

    if parentRoutineId:
        unique_id_to_find = parentRoutineId
        print('unique_id_to_find', unique_id_to_find)
        mapped_id = find_mapped_id(routine_unique_id_map, unique_id_to_find)
        print(f"Mapped ID for Unique ID {unique_id_to_find}: {mapped_id}")
        print('Processing routine with parentRoutineId:', parentRoutineId)

    individual_entry = {
        "pillar": {
            "pillarEnum": routine['attributes']['pillar']['pillarEnum'],
            "displayName": routine['attributes']['pillar']['displayName']
        },
        "imageUrl_1x1": routine.get('attributes', {}).get("resources", [{}])[0].get(
            "imageUrl_1x1") or "https://longtermhealth.de",
        "imageUrl_16x9": routine.get('attributes', {}).get("resources", [{}])[0].get(
            "imageUrl_16x9") or "https://longtermhealth.de",
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
        "packageName": routine_class_display_name,
        "packageTag": packageTag,
        "parentRoutineId": mapped_id,
        **({"expirationDate": expiration_date} if scheduleCategory in ["MONTHLY_CHALLENGE", "WEEKLY_CHALLENGE"] else {})
    }
    print(f"Added individual routine with ID {routine_id} to the action plan.")
    final_action_plan["data"]["routines"].append(individual_entry)


def create_individual_routines(selected_pkgs, routines_data, target_package='GRATITUDE BASICS'):
    routine_ids_with_parent = []

    matching_packages = [pkg for pkg in selected_pkgs if pkg['packageTag'].upper() == target_package.upper()]

    if not matching_packages:
        print(f"No packages found for tag '{target_package}'.")
        return []

    individual_routines_local = []

    for target_package in matching_packages:
        package_tag = target_package.get('packageTag')
        package_routines = target_package.get('selected_package', {}).get('routines', [])

        for routine_pkg in package_routines:
            package_routine_id = routine_pkg.get('packageRoutineId')
            schedule_category = routine_pkg.get('scheduleCategory')
            schedule_days = routine_pkg.get('scheduleDays')
            schedule_weeks = routine_pkg.get('scheduleWeeks')
            routine_affiliation = routine_pkg.get('routineAffiliation')
            parent_routine_id = routine_pkg.get('parentRoutineId')

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
                'routineAffiliation': routine_affiliation,
                'parentRoutineId': parent_routine_id,
                'packageTag': package_tag
            })

            if routine_affiliation == "PARENT":
                routine_ids_with_parent.append(routine_pkg['parentRoutineId'])

            print('routine_ids_with_parent', routine_ids_with_parent)

    return individual_routines_local


def build_routine_unique_id_map(routines_data):
    mapping = {}
    for rt in routines_data:
        unique_id = rt.get('attributes', {}).get('routineUniqueId')
        if unique_id is not None:
            mapping[unique_id] = rt.get('id')
    return mapping


def select_routines(tag_counts: Dict[str, int], routines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Selects routines based on tag combinations and their required counts, ensuring no duplicates.

    Args:
        tag_counts (Dict[str, int]): Dictionary where keys are tag combinations (comma-separated) and values are counts.
        routines (List[Dict[str, Any]]): List of all available routines.

    Returns:
        List[Dict[str, Any]]: Selected routines based on tag combinations.
    """
    selected_routines = []
    selected_ids: Set[int] = set()

    sorted_tag_combinations = sorted(tag_counts.keys(), key=lambda x: len(x.split(',')), reverse=True)
    print(f"Sorted tag combinations (prioritized): {sorted_tag_combinations}")

    for tag_combination in sorted_tag_combinations:
        required_count = tag_counts[tag_combination]
        tags = [tag.strip() for tag in tag_combination.split(',')]
        print(f"\nProcessing tag combination: {tags} with required count: {required_count}")

        matched = match_routines_by_tags(routines, tags)

        available = [routine for routine in matched if routine['id'] not in selected_ids]
        print(f"Available routines after filtering duplicates: {len(available)}")

        to_add = available[:required_count]
        print(f"Selecting {len(to_add)} routines for tags {tags}")

        selected_routines.extend(to_add)
        selected_ids.update(routine['id'] for routine in to_add)

        if len(to_add) < required_count:
            print(f"Warning: Only {len(to_add)} routines available for tags {tags}, but {required_count} required.")
        else:
            print(f"Successfully selected {len(to_add)} routines for tags {tags}.")

    print(f"\nTotal selected routines: {len(selected_routines)}")
    return selected_routines


def match_routines_by_tags(routines: List[Dict[str, Any]], tags: List[str]) -> List[Dict[str, Any]]:
    """
    Matches routines that contain all specified tags.

    Args:
        routines (List[Dict[str, Any]]): List of all available routines.
        tags (List[str]): List of tags to match.

    Returns:
        List[Dict[str, Any]]: Routines that match all the specified tags.
    """
    matched = []
    print(f"Matching routines for tags: {tags}")
    for routine in routines:
        routine_tags = [tag['tag'] for tag in routine['attributes'].get('tags', [])]
        print(f"Checking routine ID {routine['id']} with tags: {routine_tags}")
        if all(tag.strip() in routine_tags for tag in tags):
            print(f"Routine ID {routine['id']} matches all tags.")
            matched.append(routine)
        else:
            print(f"Routine ID {routine['id']} does not match all tags.")
    print(f"Total matched routines for tags {tags}: {len(matched)}")
    return matched


def check_parent_routine_ids(selected_packages, tag_counts_dicts):
    """
    Checks if any parentRoutineId from the tag_counts_dicts is present in the selected_packages.
    Returns a list of matching parentRoutineIds.

    :param selected_packages: List of selected package dictionaries.
    :param tag_counts_dicts: List of tag count dictionaries.
    :return: List of matching parentRoutineIds.
    """
    selected_parent_ids = set()
    for package in selected_packages:
        routines = package.get("selected_package", {}).get("routines", [])
        for routine in routines:
            pid = routine.get("parentRoutineId")
            if pid is not None:
                selected_parent_ids.add(pid)

    matching_parent_ids = []
    for tag_counts in tag_counts_dicts:
        parent_id = tag_counts.get("parentRoutineId")
        if parent_id in selected_parent_ids:
            matching_parent_ids.append(parent_id)

    return matching_parent_ids


def get_all_present_tags(selected_packages: List[Dict[str, Any]]) -> Set[str]:
    """
    Extracts all unique package tags from the selected_packages.

    Args:
        selected_packages (List[Dict[str, Any]]): The list of selected package dictionaries.

    Returns:
        Set[str]: A set of unique package tags.
    """
    present_tags = set()
    for package in selected_packages:
        tag = package.get('packageTag', '').strip().upper()
        if tag:
            present_tags.add(tag)
    print(f"All present tags: {present_tags}")
    return present_tags


def main():
    account_id, daily_time, routines, health_scores, user_data, answers, gender, selected_packages = get_routines_with_defaults()

    if gender == "Weiblich":
        gender = "FEMALE"
    else:
        gender = "MALE"

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
    routines = sorted_routines
    health_scores = {key: value for key, value in health_scores.items() if key != 'Total Score'}

    health_scores_with_tag = create_health_scores_with_structure(account_id, health_scores)
    print('health_scores_with_tag for posting:', json.dumps(health_scores_with_tag, indent=4, ensure_ascii=False))

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

    final_action_plan = {
        "data": {
            "accountId": account_id,
            "periodInDays": 28,
            "gender": gender.upper(),
            "totalDailyTimeInMins": daily_time,
            "routines": []
        }
    }

    routine_unique_id_map = build_routine_unique_id_map(routines)
    print("Routine Unique ID -> ID Mapping:", routine_unique_id_map)

    full_body_training_tag_counts = {
        "parentRoutineId": 997,
        "tags": {
            "warm-up": 2,
            "lower_body_strength_training": 2,
            "upper_body_strength_training": 2,
            "core_strength_training": 2,
            "mobility_sport": 2
        }
    }

    lower_body_strength_training_tag_counts = {
        "parentRoutineId": 996,
        "tags": {
            "warm-up, lower_body_strength_training": 2,
            "lower_body_strength_training": 6,
            "mobility_sport": 2
        }
    }

    upper_body_strength_training_tag_counts = {
        "parentRoutineId": 995,
        "tags": {
            "warm-up": 2,
            "upper_body_strength_training": 6,
            "mobility_sport": 2
        }
    }
    core_strength_training_tag_counts = {
        "parentRoutineId": 994,
        "tags": {
            "warm-up": 2,
            "core_strength_training": 6,
            "mobility_sport": 2
        }
    }

    tag_counts_list = [
        full_body_training_tag_counts,
        lower_body_strength_training_tag_counts,
        upper_body_strength_training_tag_counts,
        core_strength_training_tag_counts
    ]

    matched_ids = check_parent_routine_ids(selected_packages, tag_counts_list)
    print('matched_ids', matched_ids)

    if 997 in matched_ids:
        tag_counts_input = full_body_training_tag_counts['tags']

        print("\nStarting routine selection based on tag counts.")
        selected_routines = select_routines(tag_counts_input, routines_list)
        print("Routine selection completed.")

        for routine in selected_routines:
            parent_id = full_body_training_tag_counts.get("parentRoutineId")
            print(f"\nAdding routine ID {routine['id']} to the action plan with parent ID {parent_id}.")
            add_individual_routine_entry_without_parent(
                final_action_plan,
                routines_list,
                routine["id"],
                "WEEKLY_ROUTINE",
                "1,2,3,4,5",
                "1",
                "MOVEMENT BASICS",
                routine_unique_id_map,
                parent_id
            )
    if 996 in matched_ids:
        tag_counts_input = lower_body_strength_training_tag_counts['tags']

        print("\nStarting routine selection based on tag counts.")
        selected_routines = select_routines(tag_counts_input, routines_list)
        print("Routine selection completed.")

        for routine in selected_routines:
            parent_id = lower_body_strength_training_tag_counts.get("parentRoutineId")
            print(f"\nAdding routine ID {routine['id']} to the action plan with parent ID {parent_id}.")
            add_individual_routine_entry_without_parent(
                final_action_plan,
                routines_list,
                routine["id"],
                "WEEKLY_ROUTINE",
                "1,2,3,4,5",
                "1",
                "MOVEMENT BASICS",
                routine_unique_id_map,
                parent_id
            )
    if 995 in matched_ids:
        tag_counts_input = upper_body_strength_training_tag_counts['tags']

        print("\nStarting routine selection based on tag counts.")
        selected_routines = select_routines(tag_counts_input, routines_list)
        print("Routine selection completed.")

        for routine in selected_routines:
            parent_id = upper_body_strength_training_tag_counts.get("parentRoutineId")
            print(f"\nAdding routine ID {routine['id']} to the action plan with parent ID {parent_id}.")
            add_individual_routine_entry_without_parent(
                final_action_plan,
                routines_list,
                routine["id"],
                "WEEKLY_ROUTINE",
                "1,2,3,4,5",
                "1",
                "MOVEMENT BASICS",
                routine_unique_id_map,
                parent_id
            )

    if 994 in matched_ids:
        tag_counts_input = core_strength_training_tag_counts['tags']

        print("\nStarting routine selection based on tag counts.")
        selected_routines = select_routines(tag_counts_input, routines_list)
        print("Routine selection completed.")

        for routine in selected_routines:
            parent_id = core_strength_training_tag_counts.get("parentRoutineId")
            print(f"\nAdding routine ID {routine['id']} to the action plan with parent ID {parent_id}.")
            add_individual_routine_entry_without_parent(
                final_action_plan,
                routines_list,
                routine["id"],
                "WEEKLY_ROUTINE",
                "1,2,3,4,5",
                "1",
                "MOVEMENT BASICS",
                routine_unique_id_map,
                parent_id
            )

    TAG_TO_FUNCTION_MAP = {
        'STRESS BASICS': create_individual_routines,
        'SLEEP BASICS': create_individual_routines,
        'GRATITUDE BASICS': create_individual_routines,
        'FASTING BASICS': create_individual_routines,
        'NUTRITION BASICS': create_individual_routines,
        'MOVEMENT BASICS SHORT': create_individual_routines,
        'MOVEMENT BASICS MEDIUM': create_individual_routines,
        'MOVEMENT BASICS LONG': create_individual_routines,
        '5 MINUTE CARDIO': create_individual_routines,
        'ANTI INFLAMMATION': create_individual_routines,
    }
    present_tags = get_all_present_tags(selected_packages)
    for tag in present_tags:
        func = TAG_TO_FUNCTION_MAP.get(tag)
        if func:
            print(f"\nProcessing tag: {tag}")
            individual_routines = func(selected_packages, routines, target_package=tag)
            print(f"Created individual routines for tag: {tag}")

            for entry in individual_routines:
                if entry.get('routineAffiliation') == 'INDIVIDUAL':
                    parent_id = None
                else:
                    parent_id = entry.get('parentRoutineId', 0)

                add_individual_routine_entry(
                    final_action_plan,
                    routines_list,
                    entry["routineUniqueId"],
                    entry["scheduleCategory"],
                    entry["scheduleDays"],
                    entry["scheduleWeeks"],
                    entry["packageTag"],
                    routine_unique_id_map,
                    parent_id
                )
        else:
            print(f"No function mapped for tag: {tag}. Skipping.")

    save_action_plan_json(final_action_plan)
    strapi_post_action_plan(final_action_plan, account_id)
    strapi_post_health_scores(health_scores_with_tag)

    print(health_scores_with_tag)
    return final_action_plan


if __name__ == "__main__":
    main()
