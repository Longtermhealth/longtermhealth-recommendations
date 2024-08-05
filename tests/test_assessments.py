# rule_based_system/tests/test_assessments.py

import unittest
from rule_based_system.assessments.health_assessment import HealthAssessment

class TestHealthAssessment(unittest.TestCase):

    def setUp(self):
        self.answers = {
            'Wie schätzt du deine Beweglichkeit ein?': '5',
            'Wie aktiv bist du im Alltag?': '5',
            'Wie oft in der Woche treibst du Sport?': '5',
            'Welchen Schwerpunkt haben die Sportarten, die du betreibst?': 'Ausdauer, Kraft, Flexibilität, HIIT',
            'Geburtsjahr': '1990',
            'Welcher Ernährungsstil trifft bei dir am ehesten zu?': 'vegan',
            'Wie viel Fleisch nimmst du zu dir?': '1',
            'Wie viel zuckerhaltige Produkte nimmst du zu dir?': '1',
            'Wie viel Gemüse nimmst du pro Tag zu dir?': '5',
            'Wie viel Obst nimmst du pro Tag zu dir?': '5',
            'Wie häufig nimmst du Fertiggerichte zu dir?': '1',
            'Wie viel Vollkorn nimmst du zu dir?': '5',
            'Praktizierst du Intervallfasten und auf welche Art??': '16:8 (täglich 14-16 Stunden fasten)',
            'Wie viele Gläser Flüssigkeit (200ml) nimmst du ca. täglich zu dir?': 'mehr als 12',
            'Wie viel Alkohol trinkst du in der Woche?': 'gar keinen',
            'Wie ist deine Schlafqualität?': 'sehr gut',
            'Wie viele Stunden schläfst du im Durchschnitt pro Nacht?': '7-9',
            'Fühlst du dich tagsüber müde?': '1',
            'Wie viel Zeit verbringst du morgens draußen?': 'mehr als 60 min',
            'Wie viel Zeit verbringst du abends draußen?': 'mehr als 60 min',
            'Welche Schlafprobleme hast du?': [],
            'Wie oft unternimmst du etwas mit anderen Menschen?': 'fast täglich',
            'Hast du gute Freunde?': 'viele gute Freunde',
            'Bist du sozial engagiert?': 'Kirche',
            'Fühlst du dich einsam?': '1',
            'Leidest du unter Stress?': '1',
            'Welche der folgenden Stresssituationen trifft momentan auf dich zu?': 'gar keine',
            'Welche der folgenden Stresssymptome hast du in den letzten 6 Monaten beobachtet?': 'gar keine',
            'Ich versuche, die positive Seite von Stress und Druck zu sehen.': '5',
            'Ich tue alles, damit Stress erst gar nicht entsteht.': '5',
            'Wenn ich unter Druck gerate, habe ich Menschen, die mir helfen.': '5',
            'Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.': '1',
            'Ich habe so viel im Leben, wofür ich dankbar sein kann.': '5',
            'Wenn ich alles auflisten müsste, wofür ich dankbar bin, wäre es eine sehr lange Liste.': '5',
            'Wenn ich die Welt betrachte, sehe ich nicht viel, wofür ich dankbar sein könnte.': '1',
            'Ich bin vielen verschiedenen Menschen dankbar.': '5',
            'Je älter ich werde, desto mehr schätze ich die Menschen, Ereignisse und Situationen, die Teil meiner Lebensgeschichte waren.': '5',
            'Es können lange Zeiträume vergehen, bevor ich etwas oder jemandem dankbar bin.': '1',
            'Wie würdest du deine Vergesslichkeit einstufen?': '1',
            'Welche Zahl gehört unter die letzte Abbildung?': '2002',
            'Ergänze die Zahlenreihenfolge 3,6,18,21,?': '63',
            'Welche Form kommt an die Stelle vom ?': 'choice 3',
            'Quark : Milch / Brot : ?': 'Mehl',
            'Frühstück': '',
            'Mittagessen': '',
            'Abendessen': ''
        }

        self.exercise = {
            'Wie schätzt du deine Beweglichkeit ein?': self.answers.get('Wie schätzt du deine Beweglichkeit ein?', 0),
            'Wie aktiv bist du im Alltag?': self.answers.get('Wie aktiv bist du im Alltag?', 0),
            'Wie oft in der Woche treibst du Sport?': self.answers.get('Wie oft in der Woche treibst du Sport?', 0),
            'Welchen Schwerpunkt haben die Sportarten, die du betreibst?': self.answers.get('Welchen Schwerpunkt haben die Sportarten, die du betreibst?', ''),
            'Geburtsjahr': self.answers.get('Geburtsjahr', 0)
        }
        self.nutrition = {
            'Welcher Ernährungsstil trifft bei dir am ehesten zu?': self.answers.get('Welcher Ernährungsstil trifft bei dir am ehesten zu?'),
            'Wie viel Fleisch nimmst du zu dir?': self.answers.get('Wie viel Fleisch nimmst du zu dir?'),
            'Wie viel zuckerhaltige Produkte nimmst du zu dir?': self.answers.get('Wie viel zuckerhaltige Produkte nimmst du zu dir?'),
            'Wie viel Gemüse nimmst du pro Tag zu dir?': self.answers.get('Wie viel Gemüse nimmst du pro Tag zu dir?'),
            'Wie viel Obst nimmst du pro Tag zu dir?': self.answers.get('Wie viel Obst nimmst du pro Tag zu dir?'),
            'Wie häufig nimmst du Fertiggerichte zu dir?': self.answers.get('Wie häufig nimmst du Fertiggerichte zu dir?'),
            'Wie viel Vollkorn nimmst du zu dir?': self.answers.get('Wie viel Vollkorn nimmst du zu dir?'),
            'Praktizierst du Intervallfasten und auf welche Art??': self.answers.get('Praktizierst du Intervallfasten und auf welche Art??'),
            'Wie viele Gläser Flüssigkeit (200ml) nimmst du ca. täglich zu dir?': self.answers.get('Wie viele Gläser Flüssigkeit (200ml) nimmst du ca. täglich zu dir?'),
            'Wie viel Alkohol trinkst du in der Woche?': self.answers.get('Wie viel Alkohol trinkst du in der Woche?')
        }
        self.sleep = {
            'Wie ist deine Schlafqualität?': self.answers.get('Wie ist deine Schlafqualität?', 'mittel'),
            'Wie viele Stunden schläfst du im Durchschnitt pro Nacht?': self.answers.get('Wie viele Stunden schläfst du im Durchschnitt pro Nacht?', '7-9'),
            'Fühlst du dich tagsüber müde?': self.answers.get('Fühlst du dich tagsüber müde?', 0),
            'Wie viel Zeit verbringst du morgens draußen?': self.answers.get('Wie viel Zeit verbringst du morgens draußen?','0-15 min'),
            'Wie viel Zeit verbringst du abends draußen?': self.answers.get('Wie viel Zeit verbringst du abends draußen?', '0-15 min'),
            'Welche Schlafprobleme hast du?': self.answers.get('Welche Schlafprobleme hast du?', [])
        }
        self.social_connections = {
            'Wie oft unternimmst du etwas mit anderen Menschen?': self.answers.get('Wie oft unternimmst du etwas mit anderen Menschen?', 'fast täglich'),
            'Hast du gute Freunde?': self.answers.get('Hast du gute Freunde?'),
            'Bist du sozial engagiert?': self.answers.get('Bist du sozial engagiert?'),
            'Fühlst du dich einsam?': self.answers.get('Fühlst du dich einsam?')
        }
        self.stress_management = {
            'Leidest du unter Stress?': self.answers.get('Leidest du unter Stress?'),
            'Welche der folgenden Stresssituationen trifft momentan auf dich zu?': self.answers.get('Welche der folgenden Stresssituationen trifft momentan auf dich zu?'),
            'Welche der folgenden Stresssymptome hast du in den letzten 6 Monaten beobachtet?': self.answers.get('Welche der folgenden Stresssymptome hast du in den letzten 6 Monaten beobachtet?'),
            'Ich versuche, die positive Seite von Stress und Druck zu sehen.': self.answers.get('Ich versuche, die positive Seite von Stress und Druck zu sehen.'),
            'Ich tue alles, damit Stress erst gar nicht entsteht.': self.answers.get('Ich tue alles, damit Stress erst gar nicht entsteht.'),
            'Wenn ich unter Druck gerate, habe ich Menschen, die mir helfen.': self.answers.get('Wenn ich unter Druck gerate, habe ich Menschen, die mir helfen.'),
            'Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.': self.answers.get('Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.')
        }
        self.gratitude = {
            'Ich habe so viel im Leben, wofür ich dankbar sein kann.': self.answers.get('Ich habe so viel im Leben, wofür ich dankbar sein kann.'),
            'Wenn ich alles auflisten müsste, wofür ich dankbar bin, wäre es eine sehr lange Liste.': self.answers.get('Wenn ich alles auflisten müsste, wofür ich dankbar bin, wäre es eine sehr lange Liste.'),
            'Wenn ich die Welt betrachte, sehe ich nicht viel, wofür ich dankbar sein könnte.': self.answers.get('Wenn ich die Welt betrachte, sehe ich nicht viel, wofür ich dankbar sein könnte.'),
            'Ich bin vielen verschiedenen Menschen dankbar.': self.answers.get('Ich bin vielen verschiedenen Menschen dankbar.'),
            'Je älter ich werde, desto mehr schätze ich die Menschen, Ereignisse und Situationen, die Teil meiner Lebensgeschichte waren.': self.answers.get('Je älter ich werde, desto mehr schätze ich die Menschen, Ereignisse und Situationen, die Teil meiner Lebensgeschichte waren.'),
            'Es können lange Zeiträume vergehen, bevor ich etwas oder jemandem dankbar bin.': self.answers.get('Es können lange Zeiträume vergehen, bevor ich etwas oder jemandem dankbar bin.')
        }
        self.cognition = {
            'Wie würdest du deine Vergesslichkeit einstufen?': self.answers.get('Wie würdest du deine Vergesslichkeit einstufen?'),
            'Welche Zahl gehört unter die letzte Abbildung?': self.answers.get('Welche Zahl gehört unter die letzte Abbildung?'),
            'Ergänze die Zahlenreihenfolge 3,6,18,21,?': self.answers.get('Ergänze die Zahlenreihenfolge 3,6,18,21,?'),
            'Welche Form kommt an die Stelle vom ?': self.answers.get('Welche Form kommt an die Stelle vom ?'),
            'Quark : Milch / Brot : ?': self.answers.get('Quark : Milch / Brot : ?')
        }

        self.assessment = HealthAssessment(
            exercise=self.exercise,
            nutrition=self.nutrition,
            sleep=self.sleep,
            social_connections=self.social_connections,
            stress_management=self.stress_management,
            gratitude=self.gratitude,
            cognition=self.cognition
        )

    def test_exercise_assessment(self):
        score = self.assessment.exercise_assessment.report()
        self.assertEqual(float(score), 100.0)

    def test_nutrition_assessment(self):
        score = self.assessment.nutrition_assessment.report()
        self.assertEqual(float(score), 100.0)

    def test_sleep_assessment(self):
        score = self.assessment.sleep_assessment.report()
        self.assertEqual(float(score), 100.0)

    def test_social_connections_assessment(self):
        score = self.assessment.social_connections_assessment.report()
        self.assertEqual(float(score), 100.0)

    def test_stress_management_assessment(self):
        score = self.assessment.stress_management_assessment.report()
        self.assertEqual(float(score), 100.0)

    def test_gratitude_assessment(self):
        score = self.assessment.gratitude_assessment.report()
        self.assertEqual(float(score), 100.0)

    def test_cognition_assessment(self):
        score = self.assessment.cognition_assessment.report()
        self.assertEqual(float(score), 100.0)

    def test_calculate_total_score(self):
        total_score = self.assessment.calculate_total_score()
        self.assertEqual(float(total_score), 100.0)


if __name__ == '__main__':
    unittest.main()
