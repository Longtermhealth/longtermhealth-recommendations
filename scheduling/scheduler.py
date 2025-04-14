import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Set
from scheduling.filter_service import main as get_routines_with_defaults
from utils.strapi_api import strapi_post_action_plan, strapi_post_health_scores


SUPER_ROUTINE_CONFIG = {
    "sleep_superroutine": {
        "routineId": 998,
        "pillar": "SLEEP",
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/routine_sleep_998_1x1.webp",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/routine_sleep_998_16x9.webp",
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
        "scheduleWeeks": [2, 3, 4],
        "scheduleCategory": "WEEKLY_ROUTINE",
    },
    "sleep_superroutine_sleeping_room": {
        "routineId": 964,
        "pillar": "SLEEP",
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/routine_sleep_964_1x1.webp",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/routine_sleep_964_16x9.webp",
        "description": (
            "Ein erholsamer Schlaf beginnt mit der richtigen Umgebung. Ein gut vorbereitetes Schlafzimmer hilft, schneller einzuschlafen und tiefer zu ruhen. Reduziere störende Faktoren und schaffe eine Atmosphäre, die deinen Schlaf fördert."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "ROUTINE",
                "displayName": "Routine"
            }
        },
        "displayName": "Schlafzimmer vorbereiten",
        "pillar_de": "Schlaf",
        "timeOfDay": "EVENING",
        "scheduleDays": [1, 2, 3, 4, 5, 6, 7],
        "scheduleWeeks": [1],
        "scheduleCategory": "WEEKLY_ROUTINE",
    },
    "sleep_superroutine_sleep_problem": {
        "routineId": 963,
        "pillar": "SLEEP",
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/routine_sleep_963_1x1.webp",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/routine_sleep_963_16x9.webp",
        "description": (
            "Eine gute Schlafqualität ist entscheidend für Erholung und Gesundheit. Diese Routine bietet verschiedene Ansätze, um deinen Schlaf zu verbessern und besser ausgeruht in den Tag zu starten."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "ROUTINE",
                "displayName": "Routine"
            }
        },
        "displayName": "Schlafqualität steigern",
        "pillar_de": "Schlaf",
        "timeOfDay": "EVENING",
        "scheduleDays": [1, 2, 3, 4, 5, 6, 7],
        "scheduleWeeks": [2, 3, 4],
        "scheduleCategory": "WEEKLY_ROUTINE",
    },
    "movement_superroutine": {
        "routineId": 997,
        "pillar": "MOVEMENT",
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/routine_movement_997_1x1.webp",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/routine_movement_997_16x9.webp",
        "description": (
            "Ein Fullbody Workout kombiniert Warm-up, Cardio, Krafttraining und Cool-down, um "
            "den ganzen Körper effektiv zu trainieren. Nach einer kurzen Aufwärmphase folgen "
            "Ausdauerübungen und gezielte Kraftübungen für alle Muskelgruppen. Abschließend "
            "sorgen Dehnübungen für eine bessere Regeneration und Entspannung."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "MINUTES",
                "displayName": "Min."
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
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/routine_movement_996_1x1.webp",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/routine_movement_996_16x9.webp",
        "description": (
            "Ein Unterkörper-Krafttraining kombiniert Warm-up, Cardio, Krafttraining und Cool-down, um "
            "den ganzen Körper effektiv zu trainieren. Nach einer kurzen Aufwärmphase folgen "
            "Ausdauerübungen und gezielte Kraftübungen für alle Muskelgruppen. Abschließend "
            "sorgen Dehnübungen für eine bessere Regeneration und Entspannung."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "MINUTES",
                "displayName": "Min."
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
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/routine_movement_994_1x1.webp",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/routine_movement_994_16x9.webp",
        "description": (
            "Ein Core-Krafttraining kombiniert Warm-up, Cardio, Krafttraining und Cool-down, um "
            "den ganzen Körper effektiv zu trainieren. Nach einer kurzen Aufwärmphase folgen "
            "Ausdauerübungen und gezielte Kraftübungen für alle Muskelgruppen. Abschließend "
            "sorgen Dehnübungen für eine bessere Regeneration und Entspannung."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "MINUTES",
                "displayName": "Min."
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
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/routine_movement_995_1x1.webp",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/routine_movement_995_16x9.webp",
        "description": (
            "Ein Oberkörper-Krafttraining kombiniert Warm-up, Cardio, Krafttraining und Cool-down, um "
            "den ganzen Körper effektiv zu trainieren. Nach einer kurzen Aufwärmphase folgen "
            "Ausdauerübungen und gezielte Kraftübungen für alle Muskelgruppen. Abschließend "
            "sorgen Dehnübungen für eine bessere Regeneration und Entspannung."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "MINUTES",
                "displayName": "Min."
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
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/routine_movement_988_1x1.webp",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/routine_movement_988_16x9.webp",
        "description": (
            "Ein 5-minütiges Cardio-Workout steigert die Herzfrequenz, fördert die Durchblutung und verbrennt Kalorien in kurzer Zeit. Es verbessert Ausdauer, Energielevels und unterstützt die Fettverbrennung. Ideal für schnelle, effektive Fitnesseinheiten."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "MINUTES",
                "displayName": "Min."
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
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/routine_movement_985_1x1.webp",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/routine_movement_985_16x9.webp",
        "description": (
            "Ein 5-minütiges Cardio-Workout steigert die Herzfrequenz, fördert die Durchblutung und verbrennt Kalorien in kurzer Zeit. Es verbessert Ausdauer, Energielevels und unterstützt die Fettverbrennung. Ideal für schnelle, effektive Fitnesseinheiten."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "MINUTES",
                "displayName": "Min."
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
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/routine_movement_984_1x1.webp",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/routine_movement_984_16x9.webp",
        "description": (
            "Ein 5-minütiges Cardio-Workout steigert die Herzfrequenz, fördert die Durchblutung und verbrennt Kalorien in kurzer Zeit. Es verbessert Ausdauer, Energielevels und unterstützt die Fettverbrennung. Ideal für schnelle, effektive Fitnesseinheiten."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "MINUTES",
                "displayName": "Min."
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
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/routine_movement_983_1x1.webp",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/routine_movement_983_16x9.webp",
        "description": (
            "Ein 5-minütiges Cardio-Workout steigert die Herzfrequenz, fördert die Durchblutung und verbrennt Kalorien in kurzer Zeit. Es verbessert Ausdauer, Energielevels und unterstützt die Fettverbrennung. Ideal für schnelle, effektive Fitnesseinheiten."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "MINUTES",
                "displayName": "Min."
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
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/routine_movement_982_1x1.webp",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/routine_movement_982_16x9.webp",
        "description": (
            "Ein 5-minütiges Cardio-Workout steigert die Herzfrequenz, fördert die Durchblutung und verbrennt Kalorien in kurzer Zeit. Es verbessert Ausdauer, Energielevels und unterstützt die Fettverbrennung. Ideal für schnelle, effektive Fitnesseinheiten."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "MINUTES",
                "displayName": "Min."
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
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/routine_movement_981_1x1.webp",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/routine_movement_981_16x9.webp",
        "description": (
            "Ein 5-minütiges Cardio-Workout steigert die Herzfrequenz, fördert die Durchblutung und verbrennt Kalorien in kurzer Zeit. Es verbessert Ausdauer, Energielevels und unterstützt die Fettverbrennung. Ideal für schnelle, effektive Fitnesseinheiten."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "MINUTES",
                "displayName": "Min."
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
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/routine_movement_980_1x1.webp",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/routine_movement_980_16x9.webp",
        "description": (
            "Ein 5-minütiges Cardio-Workout steigert die Herzfrequenz, fördert die Durchblutung und verbrennt Kalorien in kurzer Zeit. Es verbessert Ausdauer, Energielevels und unterstützt die Fettverbrennung. Ideal für schnelle, effektive Fitnesseinheiten."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "MINUTES",
                "displayName": "Min."
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
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/routine_nutrition_999_1x1.webp",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/routine_nutrition_999_16x9.webp",
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
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/routine_nutrition_986_1x1.webp",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/routine_nutrition_986_16x9.webp",
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
        "imageUrl_1x1": "https://lthstore.blob.core.windows.net/images/routine_gratitude_990_1x1.webp",
        "imageUrl_16x9": "https://lthstore.blob.core.windows.net/images/routine_gratitude_990_16x9.webp",
        "description": (
            "Das Dankbarkeitsritual stärkt positive Gedanken, steigert Wohlbefinden und Fokus. Es fördert Achtsamkeit, reduziert Stress und bringt mehr Freude in den Alltag."
        ),
        "goal": {
            "unit": {
                "amountUnitEnum": "ROUTINE",
                "displayName": "Routine"
            }
        },
        "displayName": "Gratitude Ritual",
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


def save_action_plan_json(final_action_plan, file_path='./data/action_plan.json'):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(final_action_plan, f, ensure_ascii=False, indent=2)


def filter_excluded_routines(routines):
    return [
        routine for routine in routines
        if isinstance(routine, dict) and routine.get("attributes", {}).get("rule_status") != "excluded"
    ]



def sort_routines_by_score_rules(routines):
    return sorted(routines, key=lambda routine: routine.get("score_rules", 0), reverse=True)

def create_health_scores_with_structure(account_id, health_scores):
    """
    Builds the final health-scores structure (with interpretation) to post to Strapi.
    """
    score_interpretation_dict = {
        "MOVEMENT": {
            "AKTIONSBEFARF": "Es ist Zeit, mehr Bewegung in deinen Alltag zu integrieren. Kleine Schritte können einen großen Unterschied für deine Gesundheit machen!",
            "AUSBAUFÄHIG": "Deine körperliche Aktivität ist gut! Mit ein wenig mehr Bewegung kannst du deine Fitness auf das nächste Level heben.",
            "OPTIMAL": "Fantastische Leistung! Deine regelmäßige Bewegung stärkt deine Gesundheit optimal. Weiter so!"
        },
        "NUTRITION": {
            "AKTIONSBEFARF": "Achte mehr auf eine ausgewogene Ernährung. Gesunde Essgewohnheiten geben dir Energie und Wohlbefinden.",
            "AUSBAUFÄHIG": "Deine Ernährung ist auf einem guten Weg! Mit kleinen Anpassungen kannst du deine Nährstoffzufuhr weiter optimieren.",
            "OPTIMAL": "Exzellente Ernährungsgewohnheiten! Du versorgst deinen Körper optimal mit wichtigen Nährstoffen. Weiter so!"
        },
        "SLEEP": {
            "AKTIONSBEFARF": "Verbessere deine Schlafgewohnheiten für mehr Energie und bessere Gesundheit. Guter Schlaf ist essenziell!",
            "AUSBAUFÄHIG": "Dein Schlaf ist gut! Ein paar Änderungen können dir helfen, noch erholsamer zu schlafen.",
            "OPTIMAL": "Ausgezeichneter Schlaf! Du sorgst für optimale Erholung und Vitalität. Weiter so!"
        },
        "SOCIAL_ENGAGEMENT": {
            "AKTIONSBEFARF": "Pflege deine sozialen Beziehungen. Verbindungen zu anderen sind wichtig für dein emotionales Wohlbefinden.",
            "AUSBAUFÄHIG": "Deine sozialen Beziehungen sind gut! Mit ein wenig mehr Engagement kannst du deine Verbindungen weiter vertiefen.",
            "OPTIMAL": "Starke und erfüllende soziale Beziehungen! Du pflegst wertvolle Verbindungen, die dein Leben bereichern. Weiter so!"
        },
        "STRESS": {
            "AKTIONSBEFARF": "Es ist wichtig, Wege zu finden, um deinen Stress besser zu bewältigen. Kleine Pausen und Entspannungstechniken können helfen.",
            "AUSBAUFÄHIG": "Dein Umgang mit Stress ist gut! Mit weiteren Strategien kannst du deine Stressresistenz weiter stärken.",
            "OPTIMAL": "Du meisterst Stress hervorragend! Deine effektiven Bewältigungsstrategien tragen zu deinem Wohlbefinden bei. Weiter so!"
        },
        "GRATITUDE": {
            "AKTIONSBEFARF": "Nimm dir Zeit, die positiven Dinge im Leben zu schätzen. Dankbarkeit kann dein Wohlbefinden erheblich steigern.",
            "AUSBAUFÄHIG": "Du zeigst bereits Dankbarkeit! Mit kleinen Ergänzungen kannst du deine positive Einstellung noch weiter ausbauen.",
            "OPTIMAL": "Eine wunderbare Haltung der Dankbarkeit! Deine positive Sicht bereichert dein Leben und das deiner Mitmenschen. Weiter so!"
        },
        "COGNITIVE_ENHANCEMENT": {
            "AKTIONSBEFARF": "Fordere deinen Geist regelmäßig heraus. Neue Lernmöglichkeiten können deine geistige Fitness verbessern.",
            "AUSBAUFÄHIG": "Deine kognitive Förderung ist gut! Mit zusätzlichen Aktivitäten kannst du deine geistige Leistungsfähigkeit weiter steigern.",
            "OPTIMAL": "Hervorragende geistige Fitness! Du hältst deinen Verstand aktiv und stark. Weiter so!"
        }
    }

    def get_score_details(pillar, score):
        if score < 40:
            rating = "AKTIONSBEFARF"
        elif 40 <= score < 64:
            rating = "AUSBAUFÄHIG"
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
    routine = next((r for r in routines if r['id'] == routine_id), None)
    if not routine:
        return

    if scheduleCategory == "MONTHLY_CHALLENGE":
        expiration_date = calculate_expiration_date(days=28)
    elif scheduleCategory == "WEEKLY_CHALLENGE":
        weeks_mapping = {1: 7, 2: 14, 3: 21, 4: 28}
        try:
            scheduleWeeks_value = int(scheduleWeeks[0]) if (isinstance(scheduleWeeks, list) and scheduleWeeks) else int(scheduleWeeks)
        except ValueError:
            scheduleWeeks_value = 1
        expiration_days = weeks_mapping.get(scheduleWeeks_value, 7)
        expiration_date = calculate_expiration_date(days=expiration_days)
    else:
        expiration_date = calculate_expiration_date(days=7)

    routine_class = routine.get('attributes', {}).get('routineClass')
    if routine_class and isinstance(routine_class, dict):
        routine_class_display_name = routine_class.get('displayName', 'DefaultDisplayName')
    else:
        routine_class_display_name = 'DefaultDisplayName'

    routine_unique = routine['attributes'].get("routineUniqueId")
    individual_entry = {
        "pillar": {
            "pillarEnum": routine['attributes']['pillar']['pillarEnum'],
            "displayName": routine['attributes']['pillar']['displayName']
        },
        "imageUrl_1x1": routine.get('attributes', {}).get("resources", [{}])[0].get("imageUrl_1x1") or "https://longtermhealth.de",
        "imageUrl_16x9": routine.get('attributes', {}).get("resources", [{}])[0].get("imageUrl_16x9") or "https://longtermhealth.de",
        "routineUniqueId": routine_unique,
        "durationCalculated": float(routine['attributes']['durationCalculated']),
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
        "parentRoutineUniqueId": parentRoutineId,
        "sets": routine.get('attributes', {}).get('sets', 0),
        **({"expirationDate": expiration_date} if scheduleCategory in ["MONTHLY_CHALLENGE", "WEEKLY_CHALLENGE"] else {})
    }
    final_action_plan["data"]["routines"].append(individual_entry)

    if parentRoutineId:
        super_routine_key = next(
            (key for key, config in SUPER_ROUTINE_CONFIG.items() if config["routineId"] == parentRoutineId),
            None
        )
        if not super_routine_key:
            return

        super_routine_config = SUPER_ROUTINE_CONFIG[super_routine_key]
        super_routine_exists = any(
            routine_entry.get('routineUniqueId') == parentRoutineId
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
                "routineId": parentRoutineId,
                "durationCalculated": float(routine['attributes']['durationCalculated']),
                "timeOfDay": super_routine_config.get("timeOfDay", "ANY"),
                "goal": {
                    "unit": {
                        "amountUnitEnum": "MINUTES",
                        "displayName": "Min."
                    },
                    "value": int(routine['attributes']["durationCalculated"])
                },
                "description": super_routine_config.get("description", ""),
                "displayName": super_routine_config.get("displayName", "Unnamed Super Routine"),
                "alternatives": [],
                "scheduleDays": super_routine_config.get("scheduleDays", [1, 2, 3, 4, 5, 6, 7]),
                "scheduleWeeks": super_routine_config.get("scheduleWeeks", [1, 2, 3, 4]),
                "scheduleCategory": super_routine_config.get("scheduleCategory", "DAILY_ROUTINE"),
                "packageName": routine_class_display_name,
                "packageTag": packageTag,
                "parentRoutineUniqueId": None,
                "sets": routine.get('attributes', {}).get('sets', 0),
                **({"expirationDate": calculate_expiration_date(days=28)}
                   if super_routine_config.get("scheduleCategory") in ["MONTHLY_CHALLENGE", "WEEKLY_CHALLENGE"] else {})
            }
            final_action_plan["data"]["routines"].append(super_routine_entry)


def add_individual_routine_entry_without_parent(
        final_action_plan: dict,
        routines: List[Dict[str, Any]],
        routine_id: int,
        scheduleCategory: str,
        scheduleDays,
        scheduleWeeks,
        packageTag: str,
        routine_unique_id_map: Dict[int, int],
        parentRoutineId: Optional[int] = None,
) -> None:
    routine = next((r for r in routines if r['id'] == routine_id), None)
    if not routine:
        return

    if scheduleCategory == "MONTHLY_CHALLENGE":
        expiration_date = calculate_expiration_date(days=28)
    elif scheduleCategory == "WEEKLY_CHALLENGE":
        weeks_mapping = {1: 7, 2: 14, 3: 21, 4: 28}
        try:
            scheduleWeeks_value = int(scheduleWeeks[0]) if (isinstance(scheduleWeeks, list) and scheduleWeeks) else int(scheduleWeeks)
        except ValueError:
            scheduleWeeks_value = 1
        expiration_days = weeks_mapping.get(scheduleWeeks_value, 7)
        expiration_date = calculate_expiration_date(days=expiration_days)
    else:
        expiration_date = calculate_expiration_date(days=7)

    routine_class = routine.get('attributes', {}).get('routineClass')
    if routine_class and isinstance(routine_class, dict):
        routine_class_display_name = routine_class.get('displayName', 'DefaultDisplayName')
    else:
        routine_class_display_name = 'DefaultDisplayName'

    routine_unique = routine['attributes'].get("routineUniqueId")
    individual_entry = {
        "pillar": {
            "pillarEnum": routine['attributes']['pillar']['pillarEnum'],
            "displayName": routine['attributes']['pillar']['displayName']
        },
        "imageUrl_1x1": routine.get('attributes', {}).get("resources", [{}])[0].get("imageUrl_1x1") or "https://longtermhealth.de",
        "imageUrl_16x9": routine.get('attributes', {}).get("resources", [{}])[0].get("imageUrl_16x9") or "https://longtermhealth.de",
        "routineUniqueId": routine_unique,
        "durationCalculated": float(routine['attributes']['durationCalculated']),
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
        "parentRoutineUniqueId": parentRoutineId,
        "sets": routine.get('attributes', {}).get('sets', 0),
        **({"expirationDate": expiration_date} if scheduleCategory in ["MONTHLY_CHALLENGE", "WEEKLY_CHALLENGE"] else {})
    }
    final_action_plan["data"]["routines"].append(individual_entry)


def create_individual_routines(selected_pkgs, routines_data, target_package='GRATITUDE BASICS'):
    routine_ids_set = set()  # Track unique routine ids that have been added
    individual_routines_local = []

    matching_packages = [pkg for pkg in selected_pkgs if pkg['packageTag'].upper() == target_package.upper()]
    if not matching_packages:
        return []

    for target_package in matching_packages:
        package_tag = target_package.get('packageTag')
        package_routines = target_package.get('selected_package', {}).get('routines', [])
        for routine_pkg in package_routines:
            routine_unique_id = routine_pkg.get('packageRoutineId')
            # Skip this routine if its unique id has already been processed
            if routine_unique_id in routine_ids_set:
                continue

            routine_ids_set.add(routine_unique_id)

            schedule_category = routine_pkg.get('scheduleCategory')
            schedule_days = routine_pkg.get('scheduleDays')
            schedule_weeks = routine_pkg.get('scheduleWeeks')
            routine_affiliation = routine_pkg.get('routineAffiliation')
            parent_routine_id = routine_pkg.get('parentRoutineId')

            matching_routine = next(
                (r for r in routines_data if r['attributes'].get('routineUniqueId') == routine_unique_id), None
            )
            if not matching_routine:
                continue

            if schedule_category != 'WEEKLY_CHALLENGE':
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

    return individual_routines_local


def build_routine_unique_id_map(routines_data):
    mapping = {}
    for rt in routines_data:
        unique_id = rt.get('attributes', {}).get('routineUniqueId')
        if unique_id is not None:
            mapping[unique_id] = rt.get('id')
    return mapping


def get_primary_muscle(routine):
    """
    Extracts the primary muscle group from a routine.
    Assumes the 'title' field in the routine's resources is a string like:
      "abs (primary), obliques (secondary), hip abductors (secondary), ..."
    """
    tags = routine.get('attributes', {}).get('muscleTags')
    if isinstance(tags, str):
        parts = tags.split(',')
        if parts:
            primary_part = parts[0].strip()
            primary = primary_part.split('(')[0].strip()
            return primary
    return None


def reorder_by_primary_muscle(routines):
    """
    Reorders a list of routines so that routines with the same primary muscle
    are not scheduled directly one after the other if alternatives exist.

    If no alternative is available, routines with the same primary muscle will be placed consecutively.
    """
    if not routines:
        return routines

    # We'll work with a copy of the list.
    pool = routines.copy()
    result = []

    # Start with the first candidate.
    result.append(pool.pop(0))

    # Greedy algorithm: at each step, try to pick a routine from the pool whose primary muscle
    # is different from the one last added.
    while pool:
        last_primary = get_primary_muscle(result[-1])
        candidate_index = None
        for i, candidate in enumerate(pool):
            if get_primary_muscle(candidate) != last_primary:
                candidate_index = i
                break
        if candidate_index is not None:
            result.append(pool.pop(candidate_index))
        else:
            # No alternative found; take the first candidate even if it has the same primary muscle.
            result.append(pool.pop(0))
    return result


def map_movement_orders(answers: dict) -> dict:
    """
    Maps movement-related answers to individual order variables.

    Expected keys in the answers dictionary:
      - "Wie schätzt du deine Beweglichkeit ein?" is mapped to "order_mobility"
      - "Wie oft in der Woche treibst du eine Cardio-Sportart?" is mapped to "order_cardio"
      - "Wie schätzt du deine Kraft ein?" is mapped to "order_strength"

    Each answer is expected to be a number (1–5). If an answer is missing or cannot be
    converted to an integer, the default value of 3 is used.

    Returns:
      A dictionary with keys:
        - "order_mobility"
        - "order_cardio"
        - "order_strength"
    """

    def get_order(key: str) -> int:
        try:
            return int(answers.get(key, 3))
        except (ValueError, TypeError):
            return 3

    return {
        "order_mobility": get_order("Wie schätzt du deine Beweglichkeit ein?"),
        "order_cardio": get_order("Wie oft in der Woche treibst du eine Cardio-Sportart?"),
        "order_strength": get_order("Wie schätzt du deine Kraft ein?")
    }

def target_order_for_tags(tags: List[str], movement_orders: dict) -> int:
    """
    Computes a target order based on a list of tags by mapping each tag to an order key using movement_orders,
    and then averaging the results.
    """
    # Mapping from individual tag (in lowercase) to a key in movement_orders.
    tag_to_order_key = {
        "warm-up": "order_mobility",
        "mobility": "order_mobility",
        "walk": "order_mobility",
        "cardio": "order_cardio",
        "lower body": "order_strength",
        "upper body": "order_strength",
        "lower_body_strength_training": "order_strength",
        "upper_body_strength_training": "order_strength",
        "core_strength_training": "order_strength",
        "core": "order_strength",
        "strength": "order_strength"
    }
    values = []
    for tag in tags:
        key = tag_to_order_key.get(tag.lower())
        if key:
            order_val = movement_orders.get(key, 3)
            print("For tag '%s', using movement_orders key '%s' with value %s" % (tag, key, order_val))
            values.append(order_val)
    if values:
        target = round(sum(values) / len(values))
        print("Computed target order for tags %s is %d" % (tags, target))
        return target
    return 3


def select_routines(tag_counts: Dict[str, int], routines: List[Dict[str, Any]], movement_orders: dict) -> List[Dict[str, Any]]:
    """
    Selects routines based on tag combinations and their required counts. For each tag combination, it:
      - Finds matching routines using match_routines_by_tags.
      - Computes a target order from the individual tags (using movement_orders).
      - Sorts the matched routines by the absolute difference between their internal "order" and the target.
      - Then selects routines while respecting variation constraints.
    Finally, routines are reordered by primary muscle.
    """
    selected_routines = []
    selected_ids: Set[int] = set()
    used_variations: Set[str] = set()

    print("Starting select_routines with tag_counts:", tag_counts)

    # Process tag combinations in order of highest priority (most tags) first.
    sorted_tag_combinations = sorted(tag_counts.keys(), key=lambda x: len(x.split(',')), reverse=True)
    print("Sorted tag combinations:", sorted_tag_combinations)

    for tag_combination in sorted_tag_combinations:
        required_count = tag_counts[tag_combination]
        tags = [tag.strip() for tag in tag_combination.split(',')]
        print(
            "Processing tag combination '%s' requiring %d routines; tags: %s" % (tag_combination, required_count, tags))

        matched = match_routines_by_tags(routines, tags)
        print("Found %d routines matching tags %s" % (len(matched), tags))

        # Compute target order based on the individual tags and movement_orders.
        target_order = target_order_for_tags(tags, movement_orders)

        # Sort matched routines by the absolute difference of their internal order to target_order.
        matched = sorted(matched, key=lambda r: abs(int(r.get("attributes", {}).get("order", 999)) - target_order))
        for r in matched:
            order_val = r.get("attributes", {}).get("order", "N/A")
            print("Routine ID %s has order %s (target %d)" % (r.get("id"), order_val, target_order))

        count_added = 0

        for routine in matched:
            if count_added >= required_count:
                break

            routine_id = routine.get('id')
            if routine_id in selected_ids:
                print("Routine ID %s already selected; skipping." % routine_id)
                continue

            routine_variations = routine.get('attributes', {}).get('variations', [])
            variation_names = {variation['variation'] for variation in routine_variations if 'variation' in variation}
            if not used_variations.isdisjoint(variation_names):
                print("Routine ID %s has overlapping variations %s with already used %s; skipping." %
                      (routine_id, variation_names, used_variations))
                continue

            selected_routines.append(routine)
            selected_ids.add(routine_id)
            used_variations.update(variation_names)
            count_added += 1
            print("Selected routine ID %s for tag combination '%s'. Total added: %d" % (
            routine_id, tag_combination, count_added))

    reordered = reorder_by_primary_muscle(selected_routines)
    print("After reordering, final selected routine IDs:", [r.get('id') for r in reordered])
    return reordered


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
    #print(f"Matching routines for tags: {tags}")
    for routine in routines:
        routine_tags = [tag['tag'] for tag in routine['attributes'].get('tags', [])]
        if all(tag.strip() in routine_tags for tag in tags):
            matched.append(routine)
    #print(f"Total matched routines for tags {tags}: {len(matched)}")
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
    #print(f"All present tags: {present_tags}")
    return present_tags


def update_parent_durationCalculated_and_goal(
        final_action_plan: dict,
        SUPER_ROUTINE_CONFIG: dict,
        routine_unique_id_map: dict
) -> None:
    """
    Updates the durationCalculated and goal.value fields of parent routines in the final_action_plan.
    The new value is the sum of durationCalculated from all child routines that belong to that parent,
    plus a break time after each routine. The break time is 20 seconds per set, which is converted to minutes.

    The parent routine is identified by its unique ID from SUPER_ROUTINE_CONFIG.
    If a child routine stores a parentRoutineId that is not directly one of the tracked unique IDs,
    the reverse mapping is used to convert it.

    Both the durationCalculated field and the goal.value of the parent routine are updated.

    Note: The routine durations are in minutes. Therefore, the 20-second break per set is converted to minutes.

    Args:
        final_action_plan (dict): The action plan containing routines.
        SUPER_ROUTINE_CONFIG (dict): Dictionary containing superroutine configurations.
        routine_unique_id_map (dict): Mapping from routine unique IDs to routine IDs.

    Returns:
        None. The function updates the final_action_plan in place.
    """
    #print("\n--- Updating durationCalculated and goal.value for parent routines ---")

    tracked_parent_ids = set(config['routineId'] for config in SUPER_ROUTINE_CONFIG.values())
    #print("Tracked parent routine unique IDs from SUPER_ROUTINE_CONFIG:", tracked_parent_ids)

    reverse_map = {mapped: unique for unique, mapped in routine_unique_id_map.items()}
    ##print("Reverse mapping (mapped id -> unique id):", reverse_map)

    parent_durations = {pid: 0.0 for pid in tracked_parent_ids}

    routines = final_action_plan.get("data", {}).get("routines", [])
    #print(f"Found {len(routines)} routines in final_action_plan.")

    for routine in routines:
        stored_parent = routine.get("parentRoutineId")
        child_duration = routine.get("durationCalculated", 0)

        try:
            sets = int(routine.get("sets", 0))
        except (ValueError, TypeError):
            sets = 1

        if sets > 0:
            break_time_minutes = (sets * 20) / 60.0
        else:
            break_time_minutes = 0.0


        total_time = child_duration + break_time_minutes

        if stored_parent is not None:
            effective_parent = None
            if stored_parent in tracked_parent_ids:
                effective_parent = stored_parent
            else:
                effective_parent = reverse_map.get(stored_parent)
                if effective_parent not in tracked_parent_ids:
                    effective_parent = None
            if effective_parent is not None:
                parent_durations[effective_parent] += total_time
                """
                #print(
                    f"Added {child_duration} (duration in minutes) + {break_time_minutes:.2f} (break in minutes) = "
                    f"{total_time:.2f} from child (parentRoutineId: {stored_parent}) to parent unique id {effective_parent}. "
                    f"Running total: {parent_durations[effective_parent]:.2f}"
                )
                """

    #print("Computed total durations for parent routines (including breaks in minutes):", parent_durations)


    updated_count = 0
    for routine in routines:
        routine_id = routine.get("routineId")
        effective_parent = None
        if routine_id in tracked_parent_ids:
            effective_parent = routine_id
        else:
            candidate = reverse_map.get(routine_id)
            if candidate in tracked_parent_ids:
                effective_parent = candidate
        if effective_parent is not None:
            new_total = parent_durations.get(effective_parent, 0.0)

            routine["durationCalculated"] = int(round(new_total))
            if "goal" in routine and isinstance(routine["goal"], dict):
                routine["goal"]["value"] = int(round(new_total))
            updated_count += 1
            #print(f"Updated parent routine (routineId {routine_id} → unique id {effective_parent}) with "f"durationCalculated = {new_total:.2f} minutes and goal.value = {new_total:.2f} minutes")

    #print(f"Updated {updated_count} parent routines with new durationCalculated and goal.value values.")
    #print("--- Finished updating parent routines ---\n")


def convert_durations_to_int(action_plan: dict) -> None:
    for routine in action_plan.get("data", {}).get("routines", []):
        if "durationCalculated" in routine:
            routine["durationCalculated"] = int(round(routine["durationCalculated"]))
        if "goal" in routine and isinstance(routine["goal"], dict) and "value" in routine["goal"]:
            routine["goal"]["value"] = int(round(routine["goal"]["value"]))


ALLOWED_CATEGORIES = {"DAILY_CHALLENGE", "WEEKLY_CHALLENGE", "MONTHLY_CHALLENGE"}
TARGET_PILLAR = "COGNITIVE_ENHANCEMENT"
TARGET_PILLAR_SOCIAL = "SOCIAL_ENGAGEMENT"

def filter_routines(routines):
    daily, weekly, monthly = [], [], []
    for routine in routines:
        attrs = routine.get("attributes", {})
        pillar_data = attrs.get("pillar", {})
        if pillar_data.get("pillarEnum") == TARGET_PILLAR:
            sc = attrs.get("scheduleCategory")
            if sc in ALLOWED_CATEGORIES:
                name = attrs.get("displayName") or attrs.get("name")
                pillar_name = pillar_data.get("displayName") or pillar_data.get("pillarEnum")
                entry = {
                    "id": routine.get("id"),
                    "name": name,
                    "pillar": pillar_name,
                    "scheduleCategory": sc,
                    "scheduleDays": attrs.get("scheduleDays", ""),
                    "scheduleWeeks": attrs.get("scheduleWeeks", "")
                }
                if sc == "DAILY_CHALLENGE":
                    daily.append(entry)
                elif sc == "WEEKLY_CHALLENGE":
                    weekly.append(entry)
                elif sc == "MONTHLY_CHALLENGE":
                    monthly.append(entry)
    return daily, weekly, monthly

def filter_routines_social(routines):
    daily, weekly, monthly = [], [], []
    for routine in routines:
        attrs = routine.get("attributes", {})
        pillar_data = attrs.get("pillar", {})
        if pillar_data.get("pillarEnum") == TARGET_PILLAR_SOCIAL:
            sc = attrs.get("scheduleCategory")
            if sc in ALLOWED_CATEGORIES:
                name = attrs.get("displayName") or attrs.get("name")
                pillar_name = pillar_data.get("displayName") or pillar_data.get("pillarEnum")
                entry = {
                    "id": routine.get("id"),
                    "name": name,
                    "pillar": pillar_name,
                    "scheduleCategory": sc,
                    "scheduleDays": attrs.get("scheduleDays", ""),
                    "scheduleWeeks": attrs.get("scheduleWeeks", "")
                }
                if sc == "DAILY_CHALLENGE":
                    daily.append(entry)
                elif sc == "WEEKLY_CHALLENGE":
                    weekly.append(entry)
                elif sc == "MONTHLY_CHALLENGE":
                    monthly.append(entry)
    return daily, weekly, monthly


def filter_final_action_plan(final_action_plan):
    data = final_action_plan.get("data", {})
    routines = data.get("routines", [])
    daily, weekly, monthly = [], [], []
    for routine in routines:
        sc = routine.get("scheduleCategory")
        if sc in ALLOWED_CATEGORIES:
            name = routine.get("displayName") or routine.get("name")
            pillar_data = routine.get("pillar", {})
            pillar_name = pillar_data.get("displayName") or pillar_data.get("pillarEnum")
            entry = {
                "id": routine.get("routineId"),
                "name": name,
                "pillar": pillar_name,
                "scheduleCategory": sc,
                "scheduleDays": routine.get("scheduleDays", ""),
                "scheduleWeeks": routine.get("scheduleWeeks", "")
            }
            if sc == "DAILY_CHALLENGE":
                daily.append(entry)
            elif sc == "WEEKLY_CHALLENGE":
                weekly.append(entry)
            elif sc == "MONTHLY_CHALLENGE":
                monthly.append(entry)
    return daily, weekly, monthly


def get_monthly_challenge_id(final_action_plan, routines):
    """
    Returns the ID to use for a monthly challenge routine.

    First, it checks the final action plan:
      - If there is at least one monthly challenge in the final action plan, it returns the ID of the first one.
    Otherwise, it falls back to the cognitive enhancement routines from the `routines` list:
      - If at least one monthly challenge is found there, it returns its ID.
    If neither source provides a monthly challenge, returns None.

    Parameters:
        final_action_plan (dict): Your final action plan data.
        routines (list): Your list of routines (with cognitive enhancement routines under attributes).

    Returns:
        The routine ID (e.g. an integer) or None if not found.
    """
    _, _, monthly_final = filter_final_action_plan(final_action_plan)
    if monthly_final:
        already_scheduled = True
        return monthly_final[0]["id"], already_scheduled

    _, _, monthly_cognitive = filter_routines(routines)
    if monthly_cognitive:
        already_scheduled = False
        return monthly_cognitive[0]["id"], already_scheduled


    return None


def remove_entry_from_action_plan(final_action_plan, id_to_remove):
    """
    Removes an entry (routine) from the final action plan that has the specified routine ID.

    Parameters:
        final_action_plan (dict): Your final action plan, expected to have routines under final_action_plan["data"]["routines"].
        id_to_remove: The ID of the routine to remove (this is matched against routine["routineId"]).

    Returns:
        dict: The updated final action plan with the specified routine removed.
    """
    data = final_action_plan.get("data", {})
    routines = data.get("routines", [])


    updated_routines = [routine for routine in routines if routine.get("routineId") != id_to_remove]

    data["routines"] = updated_routines
    final_action_plan["data"] = data
    return final_action_plan


def check_weekly_challenges_in_final_action_plan(final_action_plan):
    """
    Checks weekly challenges in the final action plan and removes duplicate entries
    scheduled on the same week so that only one challenge remains per week (or only those
    with a packageTag containing "BASICS" if any exist).

    For each week (determined by the "scheduleWeeks" field):
      - If more than one weekly challenge is scheduled:
          a. Partition the challenges into two groups:
             - Those whose "packageTag" contains "BASICS".
             - Those that do not.
          b. If one or more challenges have "BASICS" in their packageTag:
             - Keep all challenges with "BASICS" and remove the others.
          c. If no challenge in that week has "BASICS" in the packageTag:
             - Keep only the first challenge and remove the rest.

    The function updates the final_action_plan in-place (under final_action_plan["data"]["routines"])
    and returns the updated action plan.
    """
    data = final_action_plan.get("data", {})
    routines = data.get("routines", [])

    weekly_challenges = [r for r in routines if r.get("scheduleCategory") == "WEEKLY_CHALLENGE"]
    #print(f"Found {len(weekly_challenges)} weekly challenge(s) in the action plan.")

    week_to_challenges = {}
    for routine in weekly_challenges:
        schedule_weeks = routine.get("scheduleWeeks", "")
        if isinstance(schedule_weeks, list):
            weeks = [str(w).strip() for w in schedule_weeks if str(w).strip()]
        else:
            weeks = [w.strip() for w in schedule_weeks.split(",") if w.strip()]
        for week in weeks:
            week_to_challenges.setdefault(week, []).append(routine)

    #print("Grouped weekly challenges by schedule week:")
    #for week, group in week_to_challenges.items():
        #print(f"  Week {week}: {len(group)} challenge(s)")

    ids_to_remove = set()

    for week, group in week_to_challenges.items():
        if len(group) > 1:
            #print(f"\nProcessing week {week} with {len(group)} challenges:")
            #for r in group:
                #print(f"  - Routine ID {r.get('routineId')}, Name: {r.get('displayName') or r.get('name')}, PackageTag: {r.get('packageTag')}")

            basics = [r for r in group if "BASICS" in r.get("packageTag", "")]
            non_basics = [r for r in group if "BASICS" not in r.get("packageTag", "")]

            if basics:
                #print("  Found BASICS challenge(s) in this week:")
                #for r in basics:
                    #print(f"    - Routine ID {r.get('routineId')}, Name: {r.get('displayName') or r.get('name')}")

                for r in non_basics:
                    r_id = r.get("routineId")
                    if r_id is not None:
                        ids_to_remove.add(r_id)
                        #print(f"  Removing non-BASICS challenge: ID {r_id}, Name: {r.get('displayName') or r.get('name')}")
            else:
                #print("  No BASICS challenge found in this week. Keeping the first challenge and removing the rest.")
                for r in group[1:]:
                    r_id = r.get("routineId")
                    if r_id is not None:
                        ids_to_remove.add(r_id)
                        #print(f"  Removing challenge: ID {r_id}, Name: {r.get('displayName') or r.get('name')}")
        #else:
            #print(f"\nWeek {week} has only one challenge; no action needed.")

    updated_routines = [r for r in routines if r.get("routineId") not in ids_to_remove]
    final_action_plan.setdefault("data", {})["routines"] = updated_routines

    #print(f"\nRemoved {len(ids_to_remove)} duplicate routine(s).")
    return final_action_plan

def add_missing_weekly_challenges(final_action_plan: dict, routines: List[Dict[str, Any]], routine_unique_id_map: dict) -> None:
    """
    Checks if weekly challenges for all 4 weeks (weeks 1 through 4) are present
    in the final_action_plan. For any missing week, adds a unique cognition weekly challenge.
    Each available cognition challenge is used at most once.
    The scheduleDays and scheduleWeeks values are set as lists of integers.
    """
    _, weekly_final, _ = filter_final_action_plan(final_action_plan)
    existing_weeks = set()
    used_routine_ids = set()
    for challenge in weekly_final:
        schedule_weeks = challenge.get("scheduleWeeks", "")
        if isinstance(schedule_weeks, list):
            existing_weeks.update({str(w).strip() for w in schedule_weeks if str(w).strip()})
        else:
            existing_weeks.update({w.strip() for w in schedule_weeks.split(",") if w.strip()})
        if challenge.get("routineId") is not None:
            used_routine_ids.add(challenge["routineId"])
    #print(f"Existing weekly challenge weeks: {existing_weeks}")

    expected_weeks = {"1", "2", "3", "4"}
    missing_weeks = sorted(list(expected_weeks - existing_weeks))
    if not missing_weeks:
        #print("All 4 weekly challenges are present. No need to add extra cognition challenges.")
        return

    #print(f"Missing weekly challenge weeks: {missing_weeks}")

    _, weekly_cognition, _ = filter_routines(routines)
    if not weekly_cognition:
        #print("No cognition weekly challenges available to add.")
        return

    available_cognition = [r for r in weekly_cognition if r["id"] not in used_routine_ids]
    if not available_cognition:
        #print("No unique cognition challenges remain to assign.")
        return

    #print(f"Available unique cognition challenges: {[r['id'] for r in available_cognition]}")

    for week, cognition_routine in zip(missing_weeks, available_cognition):
        week_int = int(week)
        #print(f"Adding cognition weekly challenge (ID {cognition_routine['id']}) for week {week_int}.")

        add_individual_routine_entry_without_parent(
            final_action_plan,
            routines,
            cognition_routine["id"],
            "WEEKLY_CHALLENGE",
            [week_int],
            [week_int],
            "COGNITIVE BASICS",
            routine_unique_id_map,
            parentRoutineId=None
        )


import random


def schedule_daily_cognitive_challenges(final_action_plan: dict, routines: List[Dict[str, Any]],
                                        routine_unique_id_map: dict) -> None:
    """
    Schedules daily challenges from the cognition pillar.

    Requirements:
      - Only 2 challenges per week are scheduled for 4 weeks (total of 8 challenges).
      - There must be at least 3 days between the two challenges within a week.
      - The day assignments are randomized (from a set of valid pairs).
      - Each challenge is used only once.

    This function extracts cognition daily challenges (i.e. routines with pillar "COGNITIVE_ENHANCEMENT"
    and scheduleCategory "DAILY_CHALLENGE") and then assigns two challenges per week using a random valid day pair.
    """
    daily_cognition, _, _ = filter_routines(routines)

    if not daily_cognition:
        #print("No cognition daily challenges available.")
        return

    total_needed = 8
    if len(daily_cognition) < total_needed:
        #print(f"Not enough unique cognition daily challenges available. Found only {len(daily_cognition)}.")
        available = daily_cognition.copy()
    else:
        available = daily_cognition.copy()

    valid_pairs = [(1, 5), (1, 6), (1, 7), (2, 6), (2, 7), (3, 7)]

    for week in range(1, 5):
        if not valid_pairs:
            #print("No valid day pairs available for scheduling.")
            return

        day_pair = random.choice(valid_pairs)
        first_day, second_day = day_pair
        #print(f"Week {week}: Randomly chosen day pair: {first_day} and {second_day}.")

        if available:
            challenge_first = available.pop(0)
            #print(f"Scheduling cognition daily challenge ID {challenge_first['id']} on week {week}, day {first_day}.")
            add_individual_routine_entry_without_parent(
                final_action_plan,
                routines,
                challenge_first["id"],
                "DAILY_CHALLENGE",
                [first_day],
                [week],
                "COGNITIVE BASICS",
                routine_unique_id_map,
                parentRoutineId=None
            )
        else:
            #print("No more unique daily cognition challenges available to schedule for the first day.")
            return

        if available:
            challenge_second = available.pop(0)
            #print(f"Scheduling cognition daily challenge ID {challenge_second['id']} on week {week}, day {second_day}.")
            add_individual_routine_entry_without_parent(
                final_action_plan,
                routines,
                challenge_second["id"],
                "DAILY_CHALLENGE",
                [second_day],
                [week],
                "COGNITIVE BASICS",
                routine_unique_id_map,
                parentRoutineId=None
            )
        else:
            #print("No more unique daily cognition challenges available to schedule for the second day.")
            return


def schedule_daily_cognitive_and_social_challenges(final_action_plan: dict,
                                                   routines: List[Dict[str, Any]],
                                                   routine_unique_id_map: dict,
                                                   health_scores: dict) -> None:
    """
    Schedules daily challenges (max 3 per week, 12 per month) from the cognition and social pillars.

    The allocation per week is decided as follows:
      - If both pillars are optimal: alternate week patterns so that over 4 weeks each pillar gets 6 challenges.
          * For odd weeks: schedule 2 cognition and 1 social challenges.
          * For even weeks: schedule 1 cognition and 2 social challenges.
      - If cognition is in focus (i.e. its health score is lower while social is optimal):
          * Use pattern (2 cognition, 1 social) every week.
      - If social is in focus (i.e. its health score is lower while cognition is optimal):
          * Use pattern (1 cognition, 2 social) every week.
      - If both are non-optimal, default to the (2,1) pattern.

    Each week uses a fixed day set [1, 4, 7] to spread the challenges.
    """
    total_weeks = 4
    max_per_week = 3  # no more than 3 daily challenges per week

    # Retrieve available daily challenges for each pillar.
    # Note: filter_routines returns a tuple (daily, weekly, monthly) for the cognition pillar.
    daily_cognition, _, _ = filter_routines(routines)
    daily_social, _, _ = filter_routines_social(routines)

    # Helper: determine a simple rating from a score.
    def get_rating(score: float) -> str:
        if score < 50:
            return "AKTIONSBEFARF"
        elif score < 80:
            return "AUSBAUFÄHIG"
        else:
            return "OPTIMAL"

    cog_score = health_scores.get("COGNITIVE_ENHANCEMENT", 0)
    social_score = health_scores.get("SOCIAL_ENGAGEMENT", 0)
    cog_rating = get_rating(cog_score)
    social_rating = get_rating(social_score)
    #print(f"Daily scheduling: Cognition = {cog_score} ({cog_rating}), Social = {social_score} ({social_rating})")

    # Determine week-by-week challenge allocation pattern.
    # Patterns are represented as a tuple: (num_cognition, num_social)
    # Total per week must be 3.
    if cog_rating == "OPTIMAL" and social_rating == "OPTIMAL":
        # Alternate between (2,1) and (1,2) for odd/even weeks.
        def pattern_for_week(week: int):
            return (2, 1) if (week % 2 == 1) else (1, 2)
    elif cog_rating != "OPTIMAL" and social_rating == "OPTIMAL":
        # Cognition is in focus: always (2,1)
        def pattern_for_week(week: int):
            return (2, 1)
    elif social_rating != "OPTIMAL" and cog_rating == "OPTIMAL":
        # Social is in focus: always (1,2)
        def pattern_for_week(week: int):
            return (1, 2)
    else:
        # Both are non-optimal; default to (2,1)
        def pattern_for_week(week: int):
            return (2, 1)

    # Pre-define a set of days (within a week) to assign the challenges.
    # For 3 daily challenges per week, we choose days that are well spread out.
    day_set = [1, 4, 7]

    # Schedule challenges week by week.
    for week in range(1, total_weeks + 1):
        num_cog, num_social = pattern_for_week(week)
        #print(f"Week {week}: Scheduling {num_cog} cognition and {num_social} social daily challenges.")

        # For each week, we want to assign exactly 3 challenges.
        # For pattern (2,1): assign cognition challenges to day_set[0] and day_set[2] and social challenge to day_set[1].
        # For pattern (1,2): assign social challenges to day_set[0] and day_set[2] and cognition challenge to day_set[1].
        if (num_cog, num_social) == (2, 1):
            assignments = [
                ("COGNITION", day_set[0]),
                ("SOCIAL", day_set[1]),
                ("COGNITION", day_set[2])
            ]
        elif (num_cog, num_social) == (1, 2):
            assignments = [
                ("SOCIAL", day_set[0]),
                ("COGNITION", day_set[1]),
                ("SOCIAL", day_set[2])
            ]
        else:
            # Fallback to one of the above if an unexpected pattern occurs.
            assignments = [
                ("COGNITION", day_set[0]),
                ("SOCIAL", day_set[1]),
                ("COGNITION", day_set[2])
            ]

        # Process each assignment for the current week.
        for pillar, day in assignments:
            if pillar == "COGNITION":
                if daily_cognition:
                    challenge = daily_cognition.pop(0)
                    #print(f"Week {week}, Day {day}: Scheduling cognition daily challenge ID {challenge['id']}.")
                    add_individual_routine_entry_without_parent(
                        final_action_plan,
                        routines,
                        challenge["id"],
                        "DAILY_CHALLENGE",
                        [day],
                        [week],
                        "COGNITIVE BASICS",
                        routine_unique_id_map,
                        parentRoutineId=None
                    )
                #else:
                    #print(f"Week {week}, Day {day}: No available cognition daily challenge.")
            elif pillar == "SOCIAL":
                if daily_social:
                    challenge = daily_social.pop(0)
                    #print(f"Week {week}, Day {day}: Scheduling social daily challenge ID {challenge['id']}.")
                    add_individual_routine_entry_without_parent(
                        final_action_plan,
                        routines,
                        challenge["id"],
                        "DAILY_CHALLENGE",
                        [day],
                        [week],
                        "SOCIAL BASICS",
                        routine_unique_id_map,
                        parentRoutineId=None
                    )
                #else:
                    #print(f"Week {week}, Day {day}: No available social daily challenge.")

    # At this point, up to 3 challenges per week (total up to 12 per month) have been scheduled.


def schedule_weekly_cognitive_and_social_challenges(final_action_plan: dict,
                                                    routines: List[Dict[str, Any]],
                                                    routine_unique_id_map: dict,
                                                    health_scores: dict) -> None:
    """
    Ensures that the final action plan contains exactly 4 weekly challenges per month.

    First, it examines the already scheduled weekly challenges (from any pillar). Then, based
    on the number of missing weekly challenges to reach a total of 4, it schedules additional
    challenges from the cognition and social pillars. The rules are:
      - If no cognitive weekly challenge is scheduled, add at least one.
      - If no social weekly challenge is scheduled, add at least one.
      - Any remaining slots are filled by assigning challenges from the pillar that has a
        lower (i.e. worse) health score (i.e. that pillar is prioritized).

    The new challenges are assigned to the missing week numbers (weeks 1–4 that aren’t already used).
    """
    # Step 1. Get already scheduled weekly challenges.
    existing = final_action_plan.get("data", {}).get("routines", [])
    weekly_existing = [r for r in existing if r.get("scheduleCategory") == "WEEKLY_CHALLENGE"]
    total_weekly = len(weekly_existing)
    #print(f"Currently scheduled weekly challenges: {total_weekly}")

    # We need exactly 4 weekly challenges.
    missing_count = 4 - total_weekly
    if missing_count <= 0:
        #print("No missing weekly challenges; nothing to add.")
        return

    # Step 2. Check which of the cognition/social challenges are already scheduled.
    scheduled_cog = [r for r in weekly_existing if r.get("packageTag") == "COGNITIVE BASICS"]
    scheduled_social = [r for r in weekly_existing if r.get("packageTag") == "SOCIAL BASICS"]
    #print(f"Already scheduled: {len(scheduled_cog)} cognition, {len(scheduled_social)} social weekly challenges.")

    # Step 3. Build a list of pillars that must be scheduled.
    # We want at least one from each if not already present.
    pillars_to_schedule = []
    if len(scheduled_cog) == 0:
        pillars_to_schedule.append("COGNITION")
    if len(scheduled_social) == 0:
        pillars_to_schedule.append("SOCIAL")

    # Count how many slots remain after ensuring at least one each.
    remaining_slots = missing_count - len(pillars_to_schedule)

    # Step 4. Determine extra allocations based on health scores.
    def get_rating(score: float) -> str:
        # A simple rating function; adjust thresholds as needed.
        if score < 50:
            return "AKTIONSBEFARF"
        elif score < 80:
            return "AUSBAUFÄHIG"
        else:
            return "OPTIMAL"

    cog_score = health_scores.get("COGNITIVE_ENHANCEMENT", 0)
    social_score = health_scores.get("SOCIAL_ENGAGEMENT", 0)
    cog_rating = get_rating(cog_score)
    social_rating = get_rating(social_score)
    #print(f"Health scores: Cognition = {cog_score} ({cog_rating}), Social = {social_score} ({social_rating})")

    # For each extra slot, assign it to the pillar with the lower score (i.e. more in need).
    for i in range(remaining_slots):
        if cog_score < social_score:
            pillars_to_schedule.append("COGNITION")
        elif social_score < cog_score:
            pillars_to_schedule.append("SOCIAL")
        else:
            # If scores are equal, alternate.
            pillars_to_schedule.append("COGNITION" if i % 2 == 0 else "SOCIAL")

    #print(f"Pillars chosen for the missing weekly slots: {pillars_to_schedule}")

    # Step 5. Identify which week numbers (1-4) are not yet assigned.
    taken_weeks = set()
    for r in weekly_existing:
        weeks = r.get("scheduleWeeks", [])
        if isinstance(weeks, list):
            taken_weeks.update(weeks)
        elif isinstance(weeks, str):
            try:
                taken_weeks.add(int(weeks.strip()))
            except ValueError:
                pass
    all_weeks = {1, 2, 3, 4}
    missing_weeks = sorted(list(all_weeks - taken_weeks))
    #print(f"Missing week numbers: {missing_weeks}")

    # Make sure we have as many missing weeks as slots to fill.
    if len(missing_weeks) < len(pillars_to_schedule):
        #print("Warning: Fewer missing week numbers than scheduled pillars. Adjusting...")
        pillars_to_schedule = pillars_to_schedule[:len(missing_weeks)]

    # Step 6. For each missing week, schedule a challenge from the designated pillar.
    for week, pillar in zip(missing_weeks, pillars_to_schedule):
        if pillar == "COGNITION":
            # Get available weekly cognition routines.
            # filter_routines returns (daily, weekly, monthly) for cognition routines.
            _, weekly_cognition, _ = filter_routines(routines)
            # Exclude those already scheduled for cognition.
            used_ids = {r.get("routineId") for r in scheduled_cog}
            available = [r for r in weekly_cognition if r.get("id") not in used_ids]
            if available:
                challenge = available[0]
                #print(f"Week {week}: Scheduling cognition weekly challenge ID {challenge['id']}.")
                add_individual_routine_entry_without_parent(
                    final_action_plan,
                    routines,
                    challenge["id"],
                    "WEEKLY_CHALLENGE",
                    [week],
                    [week],
                    "COGNITIVE BASICS",
                    routine_unique_id_map,
                    parentRoutineId=None
                )
            #else:
                #print(f"Week {week}: No available cognition weekly challenge found.")
        elif pillar == "SOCIAL":
            # Get available weekly social routines.
            _, weekly_social, _ = filter_routines_social(routines)
            used_ids = {r.get("routineId") for r in scheduled_social}
            available = [r for r in weekly_social if r.get("id") not in used_ids]
            if available:
                challenge = available[0]
                #print(f"Week {week}: Scheduling social weekly challenge ID {challenge['id']}.")
                add_individual_routine_entry_without_parent(
                    final_action_plan,
                    routines,
                    challenge["id"],
                    "WEEKLY_CHALLENGE",
                    [week],
                    [week],
                    "SOCIAL BASICS",
                    routine_unique_id_map,
                    parentRoutineId=None
                )
            #else:
                #print(f"Week {week}: No available social weekly challenge found.")

def update_duration_for_specific_routines(final_action_plan: dict, routine_unique_id_map: dict,
                                          daily_time: int) -> None:
    """
    Updates the durationCalculated and goal.value fields for routines corresponding to unique IDs 991, 992, and 993.

    Args:
        final_action_plan (dict): The action plan containing routines under final_action_plan["data"]["routines"].
        routine_unique_id_map (dict): Mapping from unique routine IDs to routine IDs.
        daily_time (int): The daily time parameter.
    """
    target_uids = [991, 992, 993]
    uid_to_routineid = {
        uid: routine_unique_id_map.get(uid)
        for uid in target_uids
        if routine_unique_id_map.get(uid) is not None
    }

    new_value_other = None
    if daily_time == 20:
        new_value_other = 20
    elif daily_time in (40, 50):
        new_value_other = 40
    elif daily_time == 90:
        new_value_other = 60

    new_value_991 = None
    if daily_time == 20:
        new_value_991 = 10
    elif daily_time in (40, 50):
        new_value_991 = 20
    elif daily_time == 90:
        new_value_991 = 30

    for routine in final_action_plan.get("data", {}).get("routines", []):
        r_id = routine.get("routineId")
        if not r_id:
            continue

        for uid, mapped_routine_id in uid_to_routineid.items():
            if r_id == mapped_routine_id:
                if uid == 991 and new_value_991 is not None:
                    routine["durationCalculated"] = new_value_991
                    if "goal" in routine and isinstance(routine["goal"], dict):
                        routine["goal"]["value"] = new_value_991
                elif uid in (992, 993) and new_value_other is not None:
                    routine["durationCalculated"] = new_value_other
                    if "goal" in routine and isinstance(routine["goal"], dict):
                        routine["goal"]["value"] = new_value_other
                break

def schedule_all_daily_challenges(final_action_plan, routines, routine_unique_id_map, health_scores):
    """
    Schedule up to 3 daily challenges per week (one per day) for all pillars.

    Process:
      1. Gather available routines with scheduleCategory "DAILY_CHALLENGE" and group them by pillar.
      2. For each week (of 4 weeks), choose 3 days (e.g. days 1, 4, and 7) as daily slots.
      3. For each day, pick one challenge from a pillar that hasn’t yet been scheduled in that week.
         Pillars can be prioritized (for example, by a lower health score).
    """
    daily_routines_by_pillar = {}
    for routine in routines:
        attrs = routine.get("attributes", {})
        if attrs.get("scheduleCategory") == "DAILY_CHALLENGE":
            pillar = attrs.get("pillar", {}).get("pillarEnum")
            if pillar:
                daily_routines_by_pillar.setdefault(pillar, []).append(routine)

    total_weeks = 4
    day_slots = [1, 4, 7]

    for week in range(1, total_weeks + 1):
        sorted_pillars = sorted(daily_routines_by_pillar.keys(), key=lambda p: health_scores.get(p, 100))
        used_pillars = set()
        for day in day_slots:
            for pillar in sorted_pillars:
                if pillar not in used_pillars and daily_routines_by_pillar.get(pillar):
                    challenge = daily_routines_by_pillar[pillar].pop(0)
                    used_pillars.add(pillar)
                    add_individual_routine_entry_without_parent(
                        final_action_plan,
                        routines,
                        challenge["id"],
                        "DAILY_CHALLENGE",
                        [day],
                        [week],
                        pillar + " BASICS",
                        routine_unique_id_map,
                        parentRoutineId=None
                    )
                    break


def schedule_all_weekly_challenges(final_action_plan, routines, routine_unique_id_map, health_scores):
    """
    Schedule exactly 1 weekly challenge per week (over 4 weeks) for all pillars.

    Process:
      1. Group available routines with scheduleCategory "WEEKLY_CHALLENGE" by pillar.
      2. Sort the pillars (for example, by health score so that pillars in more need get scheduled first).
      3. For each pillar (in order), assign its challenge to the next available week until 4 weeks are filled.
    """
    print("Scheduling weekly challenges...")

    weekly_routines_by_pillar = {}
    for routine in routines:
        attrs = routine.get("attributes", {})
        if attrs.get("scheduleCategory") == "WEEKLY_CHALLENGE":
            pillar = attrs.get("pillar", {}).get("pillarEnum")
            if pillar:
                weekly_routines_by_pillar.setdefault(pillar, []).append(routine)

    total_weeks = 4
    sorted_pillars = sorted(weekly_routines_by_pillar.keys(), key=lambda p: health_scores.get(p, 100))

    print("Sorted pillars:")
    for pillar in sorted_pillars:
        print(f"{pillar}")

    week_index = 1
    for pillar in sorted_pillars:
        if week_index > total_weeks:
            break
        routines_for_pillar = weekly_routines_by_pillar.get(pillar)
        if routines_for_pillar:
            challenge = routines_for_pillar.pop(0)
            add_individual_routine_entry_without_parent(
                final_action_plan,
                routines,
                challenge["id"],
                "WEEKLY_CHALLENGE",
                [1],
                [week_index],
                pillar + " BASICS",
                routine_unique_id_map,
                parentRoutineId=None
            )
            print(f"Scheduled weekly challenge for {pillar} in week: {week_index}")
            print('week_index',week_index)
            week_index += 1
    print("Weekly challenges scheduled.")



def main(host):

    if host == "lthrecommendation-dev-g2g0hmcqdtbpg8dw.germanywestcentral-01.azurewebsites.net":
        app_env = "development"
    else:
        app_env = "production"
    print('app_env', app_env)

    account_id, daily_time, routines, health_scores, user_data, answers, gender, selected_packages = get_routines_with_defaults(app_env)

    print('answers', answers)
    print('account_id',account_id)
    print('daily_time',daily_time)
    print('health_scores',health_scores)
    if gender == "Weiblich":
        gender = "FEMALE"
    else:
        gender = "MALE"

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

    #for routine in filtered_routines:
        #print('filtered:routines',routine.get("attributes", {}).get("cleanedName"))

    health_scores_with_tag = create_health_scores_with_structure(account_id, health_scores)
    #print('health_scores_with_tag for posting:', json.dumps(health_scores_with_tag, indent=4, ensure_ascii=False))


    packages_file_path = "./data/packages_with_id.json"
    with open(packages_file_path, "r") as file:
        data = json.load(file)
    #print('selected_packages', selected_packages)
    #print('data', data)

    ids_by_package_name = {}
    for pillar_name, pillar_data in data["packages"]["pillars"].items():
        for package_tag, tag_data in pillar_data.items():
            for package_name, package_data in tag_data.items():
                ids_by_package_name[package_name] = []
                for routine in package_data["routines"]:
                    if routine["id"] is not None:
                        ids_by_package_name[package_name].append(routine["id"])

    for package_name, ids in ids_by_package_name.items():
        #print(f"{package_name}: {ids}")
        pass


    final_action_plan = {
        "data": {
            "actionPlanUniqueId": str(uuid.uuid4()),
            "previousActionPlanUniqueId": None,
            "accountId": account_id,
            "periodInDays": 28,
            "gender": gender.upper(),
            "totalDailyTimeInMins": daily_time,
            "routines": []
        }
    }


    routine_unique_id_map = build_routine_unique_id_map(routines)
    #print("Routine Unique ID -> ID Mapping:", routine_unique_id_map)


    if daily_time == 20:

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
                "warm-up, lower body": 2,
                "lower_body_strength_training": 6
            }
        }

        upper_body_strength_training_tag_counts = {
            "parentRoutineId": 995,
            "tags": {
                "warm-up, upper body": 2,
                "upper_body_strength_training": 5
            }
        }
        core_strength_training_tag_counts = {
            "parentRoutineId": 994,
            "tags": {
                "warm-up": 2,
                "core_strength_training": 5
            }
        }
    elif daily_time in (40, 50):

        full_body_training_tag_counts = {
            "parentRoutineId": 997,
            "tags": {
                "warm-up": 2,
                "lower_body_strength_training": 4,
                "upper_body_strength_training": 4,
                "core_strength_training": 4,
                "mobility_sport": 2
            }
        }

        lower_body_strength_training_tag_counts = {
            "parentRoutineId": 996,
            "tags": {
                "warm-up, lower body": 2,
                "lower_body_strength_training": 14
            }
        }

        upper_body_strength_training_tag_counts = {
            "parentRoutineId": 995,
            "tags": {
                "warm-up, upper body": 2,
                "upper_body_strength_training": 14
            }
        }
        core_strength_training_tag_counts = {
            "parentRoutineId": 994,
            "tags": {
                "warm-up": 2,
                "core_strength_training": 13
            }
        }
    elif daily_time == 90:

        full_body_training_tag_counts = {
            "parentRoutineId": 997,
            "tags": {
                "warm-up": 3,
                "lower_body_strength_training": 5,
                "upper_body_strength_training": 5,
                "core_strength_training": 6,
                "mobility_sport": 3
            }
        }

        lower_body_strength_training_tag_counts = {
            "parentRoutineId": 996,
            "tags": {
                "warm-up, lower body": 2,
                "lower_body_strength_training": 18
            }
        }

        upper_body_strength_training_tag_counts = {
            "parentRoutineId": 995,
            "tags": {
                "warm-up, upper body": 2,
                "upper_body_strength_training": 18
            }
        }
        core_strength_training_tag_counts = {
            "parentRoutineId": 994,
            "tags": {
                "warm-up": 2,
                "core_strength_training": 18
            }
        }

    tag_counts_list = [
        full_body_training_tag_counts,
        lower_body_strength_training_tag_counts,
        upper_body_strength_training_tag_counts,
        core_strength_training_tag_counts
    ]

    matched_ids = check_parent_routine_ids(selected_packages, tag_counts_list)
    #print('matched_ids',matched_ids)

    movement_orders = map_movement_orders(answers)

    if 997 in matched_ids:
        tag_counts_input = full_body_training_tag_counts['tags']


        #print("\nStarting routine selection based on tag counts.")
        selected_routines = select_routines(tag_counts_input, filtered_routines, movement_orders)
        #print("Routine selection completed.")

        for routine in selected_routines:
            parent_id = full_body_training_tag_counts.get("parentRoutineId")
            #print(f"\nAdding routine ID {routine['id']} to the action plan with parent ID {parent_id}.")
            add_individual_routine_entry_without_parent(
                final_action_plan,
                filtered_routines,
                routine["id"],
                "WEEKLY_ROUTINE",
                [1,2,3,4,5],
                [1],
                "MOVEMENT BASICS",
                routine_unique_id_map,
                parent_id
            )
    if 996 in matched_ids:
        tag_counts_input = lower_body_strength_training_tag_counts['tags']


        #print("\nStarting routine selection based on tag counts.")
        selected_routines = select_routines(tag_counts_input, filtered_routines, movement_orders)
        #print("Routine selection completed.")

        for routine in selected_routines:
            parent_id = lower_body_strength_training_tag_counts.get("parentRoutineId")
            #print(f"\nAdding routine ID {routine['id']} to the action plan with parent ID {parent_id}.")
            add_individual_routine_entry_without_parent(
                final_action_plan,
                filtered_routines,
                routine["id"],
                "WEEKLY_ROUTINE",
                [1,2,3,4,5],
                [1,2,3,4,5],
                "MOVEMENT BASICS",
                routine_unique_id_map,
                parent_id
            )
    if 995 in matched_ids:
        tag_counts_input = upper_body_strength_training_tag_counts['tags']


        #print("\nStarting routine selection based on tag counts.")
        selected_routines = select_routines(tag_counts_input, filtered_routines, movement_orders)
        #print("Routine selection completed.")

        for routine in selected_routines:
            parent_id = upper_body_strength_training_tag_counts.get("parentRoutineId")
            #print(f"\nAdding routine ID {routine['id']} to the action plan with parent ID {parent_id}.")
            add_individual_routine_entry_without_parent(
                final_action_plan,
                filtered_routines,
                routine["id"],
                "WEEKLY_ROUTINE",
                [1,2,3,4,5],
                [1],
                "MOVEMENT BASICS",
                routine_unique_id_map,
                parent_id
            )

    if 994 in matched_ids:
        tag_counts_input = core_strength_training_tag_counts['tags']


        #print("\nStarting routine selection based on tag counts.")
        selected_routines = select_routines(tag_counts_input, filtered_routines, movement_orders)
        #print("Routine selection completed.")

        for routine in selected_routines:
            parent_id = core_strength_training_tag_counts.get("parentRoutineId")
            #print(f"\nAdding routine ID {routine['id']} to the action plan with parent ID {parent_id}.")
            add_individual_routine_entry_without_parent(
                final_action_plan,
                filtered_routines,
                routine["id"],
                "WEEKLY_ROUTINE",
                [1,2,3,4,5],
                [1],
                "MOVEMENT BASICS",
                routine_unique_id_map,
                parent_id
            )


    TAG_TO_FUNCTION_MAP = {
        'STRESS BASICS': create_individual_routines,
        'SLEEP BASICS': create_individual_routines,
        'SLEEPING ROOM': create_individual_routines,
        'SLEEP PROBLEM': create_individual_routines,
        'GRATITUDE BASICS 1': create_individual_routines,
        'GRATITUDE BASICS 2': create_individual_routines,
        'GRATITUDE BASICS 3': create_individual_routines,
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
            #print(f"\nProcessing tag: {tag}")
            individual_routines = func(selected_packages, routines, target_package=tag)
            #print(f"Created individual routines for tag: {tag}")

            for entry in individual_routines:
                #print('entry',entry)
                if entry.get('routineAffiliation') == 'INDIVIDUAL':
                    parent_id = None
                else:
                    parent_id = entry.get('parentRoutineId', 0)

                add_individual_routine_entry(
                    final_action_plan,
                    filtered_routines,
                    entry["routineUniqueId"],
                    entry["scheduleCategory"],
                    entry["scheduleDays"],
                    entry["scheduleWeeks"],
                    entry["packageTag"],
                    routine_unique_id_map,
                    parent_id
                )
        #else:
            #print(f"No function mapped for tag: {tag}. Skipping.")



    daily_routines, weekly_routines, monthly_routines = filter_routines(routines)
    daily_routines_social, weekly_routines_social, monthly_routines_social = filter_routines_social(routines)
    daily_final, weekly_final, monthly_final = filter_final_action_plan(final_action_plan)
    """
    def print_entries(header, entries):
        #print(f"{header}:")
        for entry in entries:
            #print(
                f"ID: {entry['id']}, Name: {entry['name']}, Pillar: {entry['pillar']},   "
                f"Schedule Category: {entry['scheduleCategory']}, "
                f"Schedule Days: {entry['scheduleDays']}, "
                f"Schedule Weeks: {entry['scheduleWeeks']}"
            )
        #print()
    """
    #print_entries("Daily Challenge Routines (routines cognition)", daily_routines)
    #print_entries("Weekly Challenge Routines (routines cognition)", weekly_routines)
    #print_entries("Monthly Challenge Routines (routines cognition)", monthly_routines)

    #print_entries("Daily Challenge Routines (routines social)", daily_routines_social)
    #print_entries("Weekly Challenge Routines (routines social)", weekly_routines_social)
    #print_entries("Monthly Challenge Routines (routines social)", monthly_routines_social)

    #print_entries("Daily Challenge Routines (final action plan)", daily_final)
    #print_entries("Weekly Challenge Routines (final action plan)", weekly_final)
    #print_entries("Monthly Challenge Routines (final action plan)", monthly_final)

    monthly_id, already_scheduled = get_monthly_challenge_id(final_action_plan, routines)
    if already_scheduled:
        already_scheduled = True
        #print(f'Monthly Challenge with id {monthly_id} already scheduled')
    else:
        add_individual_routine_entry_without_parent(
            final_action_plan,
            filtered_routines,
            monthly_id,
            "MONTHLY_CHALLENGE",
            [1],
            [1],
            "COGNITIVE BASICS",
            routine_unique_id_map
        )

    #print("Monthly Challenge ID to use:", monthly_id)

    schedule_all_daily_challenges(final_action_plan, filtered_routines, routine_unique_id_map, health_scores)
    schedule_all_weekly_challenges(final_action_plan, filtered_routines, routine_unique_id_map, health_scores)

    update_parent_durationCalculated_and_goal(final_action_plan, SUPER_ROUTINE_CONFIG, routine_unique_id_map)
    convert_durations_to_int(final_action_plan)
    update_duration_for_specific_routines(final_action_plan, routine_unique_id_map, daily_time)

    save_action_plan_json(final_action_plan)
    if app_env == "development":
        strapi_post_action_plan(final_action_plan, account_id, 'development')
        strapi_post_health_scores(health_scores_with_tag, 'development')
    else:
        strapi_post_action_plan(final_action_plan, account_id, 'production')
        strapi_post_health_scores(health_scores_with_tag, 'production')


    return final_action_plan


if __name__ == "__main__":
    main(host)