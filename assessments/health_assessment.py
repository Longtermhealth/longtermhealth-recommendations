# rule_based_system/assessments/health_assessment.py


from assessments.nutrition_assessment import NutritionAssessment
from assessments.exercise_assessment import ExerciseAssessment
from assessments.sleep_assessment import SleepAssessment
from assessments.social_connections_assessment import SocialConnectionsAssessment
from assessments.stress_management_assessment import StressManagementAssessment
from assessments.gratitude_assessment import GratitudeAssessment
from assessments.cognition_assessment import CognitionAssessment

class HealthAssessment:
    def __init__(self, exercise, nutrition, sleep, social_connections, stress_management, gratitude, cognition):
        """
        Initialize the HealthAssessment with the provided answers for various assessments.

        :param exercise: Dictionary of answers related to exercise
        :param nutrition: Dictionary of answers related to nutrition
        :param sleep: Dictionary of answers related to sleep
        :param social_connections: Dictionary of answers related to social connections
        :param stress_management: Dictionary of answers related to stress management
        :param gratitude: Dictionary of answers related to gratitude
        :param cognition: Dictionary of answers related to cognition
        """
        self.exercise_assessment = ExerciseAssessment(exercise)
        self.nutrition_assessment = NutritionAssessment(nutrition)
        self.sleep_assessment = SleepAssessment(sleep)
        self.social_connections_assessment = SocialConnectionsAssessment(social_connections)
        self.gratitude_assessment = GratitudeAssessment(gratitude)
        self.cognition_assessment = CognitionAssessment(cognition)

        self.stress_management_assessment = StressManagementAssessment(stress_management)

    def calculate_total_score(self):
        """
        Calculate the total health score based on individual assessment scores.

        :return: The calculated total health score as a float
        """
        scores = [
            float(self.exercise_assessment.report()),
            float(self.sleep_assessment.report()),
            float(self.nutrition_assessment.report()),
            float(self.stress_management_assessment.report()),
            float(self.social_connections_assessment.report()),
            float(self.gratitude_assessment.report()),
            float(self.cognition_assessment.report())
        ]
        total_score = round(sum(scores) / len(scores), 2)
        return total_score

if __name__ == "__main__":
    exercise = {
        'Wie schätzt du deine Beweglichkeit ein? ': '5',
        'Wie körperlich aktiv bist du? ': '5',
        'Wie oft in der Woche treibst du eine Cardio-Sportart ': '5',
        'Welchen Schwerpunkt haben die Sportarten, die du betreibst?': 'Ausdauer, Kraft, Flexibilität, HIIT',
        'Welche Sportarten im Bereich Ausdauer machst du?': 'Laufen, Schwimmen',
        'Welche Sportarten im Bereich Flexibilität machst du?': 'Yoga',
        'Geburtsjahr': '1990'
    }
    nutrition = {
        'Welcher Ernährungsstil trifft bei dir am ehesten zu?': 'vegan',
        'Wie viele Gläser Flüssigkeit (200ml) nimmst du ca. täglich zu dir?': 'mehr als 12',
        'Wie viel Alkohol trinkst du in der Woche?': 'gar keinen',
        'Wie viel Zucker nimmst du zu dir?': '1',
        'Wie viel Obst nimmst du zu dir? ': '5',
        'Wie viel Gemüse nimmst du pro Tag zu dir?': '5',
        'Wie viel Fleisch nimmst du zu dir?': '1',
        'Wie viele Fertigprodukte nimmst du zu dir?': '1',
        'Wie viele Vollkornprodukte nimmst du zu dir?': '5',
        'Praktizierst du Intervallfasten und auf welche Art??': '16:8 (täglich 14-16 Stunden fasten)'
    }
    sleep = {
        'Wie ist deine Schlafqualität?': 'sehr gut',
        'Welche Schlafprobleme hast du?': [],
        'Wie viele Stunden schläfst du im Durchschnitt pro Nacht?': '7-9',
        'Fühlst du dich tagsüber müde?': '1',
        'Wie viel Zeit verbringst du morgens draußen?': 'mehr als 60 min',
        'Wie viel Zeit verbringst du abends draußen?': 'mehr als 60 min'
    }
    social_connections = {
        'Wie häufig nimmst du an sozialen Aktivitäten teil?': 'fast täglich',
        'Wie viele gute Freunde hast du?': 'viele gute Freunde',
        'Bist du in soziale Gruppen oder Organisationen eingebunden?': 'Kirche',
        'Wie häufig fühlst du dich einsam?': 1
    }
    stress_management = {
        'Leidest du unter Stress?': '1',
        'Welche der folgenden Stresssituationen trifft momentan auf dich zu? ': 'Gar keine',
        'Welche der folgenden Stresssymptome hast du in den letzten 6 Monaten beobachtet?': 'gar keine',
        'Ich versuche, die positive Seite von Stress und Druck zu sehen.': '5',
        'Ich tue alles, damit Stress erst gar nicht entsteht.': '5',
        'Wenn ich unter Druck gerate, habe ich Menschen, die mir helfen.': '5',
        'Bei Stress und Druck finde ich Halt im Glauben.': '5',
        'Wenn mir alles zu viel wird, greife ich manchmal zur Flasche oder Zigaretten.': '1'
    }
    gratitude = {
        'Ich liebe mich so, wie ich bin.': 5,
        'Ich habe so viel im Leben, wofür ich dankbar sein kann.': 5,
        'Jeder Tag ist eine Chance, es besser zu machen.': 5,
        'Im Nachhinein bin ich für jede Niederlage dankbar, denn sie haben mich weitergebracht.': 5,
        'Ich bin vielen verschiedenen Menschen dankbar.': 5
    }
    cognition = {
        'Wie würdest du deine Vergesslichkeit einstufen?': '1',
        'Welche Zahl gehört unter die letzte Abbildung?': '2002',
        'Ergänze die Zahlenreihenfolge 3,6,18,21,?': '63',
        'Welche Form kommt an die Stelle vom ?': 'choice 3',
        'Quark : Milch / Brot : ?': 'Schwarzbrot'
    }

    assessment = HealthAssessment(exercise, nutrition, sleep, social_connections, stress_management, gratitude, cognition)
