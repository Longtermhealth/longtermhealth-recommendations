# rule_based_system/utils/data_processing.py

def integrate_answers(answers):
    integrated_data = {
        'exercise': {
            'Wie schätzt du deine Beweglichkeit ein?': answers.get('Wie schätzt du deine Beweglichkeit ein?', 0),
            'Wie aktiv bist du im Alltag?': answers.get('Wie aktiv bist du im Alltag?', 0),
            'Wie oft in der Woche treibst du eine Cardio-Sportart?': answers.get('Wie oft in der Woche treibst du eine Cardio-Sportart?', 0),
            'Wie schätzt du deine Kraft ein?': answers.get('Wie schätzt du deine Kraft ein?', ''),
            'Geburtsjahr': answers.get('Geburtsjahr', 0)
        },
        'nutrition': {
            'Was ist deine Körpergröße (in cm)?': answers.get('Was ist deine Körpergröße (in cm)?'),
            'Wie viel wiegst du (in kg)?': answers.get('Wie viel wiegst du (in kg)?'),
            'Welcher Ernährungsstil trifft bei dir am ehesten zu?': answers.get(
                'Welcher Ernährungsstil trifft bei dir am ehesten zu?'),
            'Wie viel zuckerhaltige Produkte nimmst du zu dir?': answers.get('Wie viel zuckerhaltige Produkte nimmst du zu dir?'),
            'Wie häufig nimmst du Fertiggerichte zu dir?': answers.get('Wie häufig nimmst du Fertiggerichte zu dir?'),
            'Wie viel Vollkorn nimmst du zu dir?': answers.get('Wie viel Vollkorn nimmst du zu dir?'),
            'Praktizierst du Intervallfasten und auf welche Art?': answers.get('Praktizierst du Intervallfasten und auf welche Art?'),
            'Wie viele Gläser Flüssigkeit (200ml) nimmst du ca. täglich zu dir?': answers.get('Wie viele Gläser Flüssigkeit (200ml) nimmst du ca. täglich zu dir?'),
            'Wie viel Alkohol trinkst du in der Woche?': answers.get('Wie viel Alkohol trinkst du in der Woche?')
        },
        'sleep': {
            'Wie ist deine Schlafqualität?': answers.get('Wie ist deine Schlafqualität?', 'mittel'),
            'Wie viele Stunden schläfst du im Durchschnitt pro Nacht?': answers.get(
                'Wie viele Stunden schläfst du im Durchschnitt pro Nacht?', '7-9'),
            'Fühlst du dich tagsüber müde?': answers.get('Fühlst du dich tagsüber müde?', 0),
            'Wie viel Zeit verbringst du morgens draußen?': answers.get('Wie viel Zeit verbringst du morgens draußen?','0-15 min'),
            'Wie viel Zeit verbringst du abends draußen?': answers.get('Wie viel Zeit verbringst du abends draußen?', '0-15 min'),
            'Welche Schlafprobleme hast du?': answers.get('Welche Schlafprobleme hast du?', [])
        },
        'social_connections': {
            'Wie oft unternimmst du etwas mit anderen Menschen?': answers.get('Wie oft unternimmst du etwas mit anderen Menschen?', 'fast täglich'),
            'Bist du sozial engagiert?': answers.get('Bist du sozial engagiert?'),
            'Fühlst du dich einsam?': answers.get('Fühlst du dich einsam?')
        },
        'stress_management': {
            'Leidest du aktuell unter Stress?': answers.get('Leidest du aktuell unter Stress?'),
            'Ich versuche, die positive Seite von Stress und Druck zu sehen.': answers.get(
                'Ich versuche, die positive Seite von Stress und Druck zu sehen.'),
            'Ich tue alles, damit Stress erst gar nicht entsteht.': answers.get(
                'Ich tue alles, damit Stress erst gar nicht entsteht.'),
            'Wenn ich unter Druck gerate, habe ich Menschen, die mir helfen.': answers.get(
                'Wenn ich unter Druck gerate, habe ich Menschen, die mir helfen.'),
            'Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.': answers.get(
                'Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.')
        },
        'gratitude': {
            'Ich liebe mich so, wie ich bin.': answers.get(
                'Ich liebe mich so, wie ich bin.'),
            'Ich habe so viel im Leben, wofür ich dankbar sein kann.': answers.get(
                'Ich habe so viel im Leben, wofür ich dankbar sein kann.'),
            'Jeder Tag ist eine Chance, es besser zu machen.': answers.get(
                'Jeder Tag ist eine Chance, es besser zu machen.'),
            'Im Nachhinein bin ich für jede Niederlage dankbar, denn sie haben mich weitergebracht.': answers.get(
                'Im Nachhinein bin ich für jede Niederlage dankbar, denn sie haben mich weitergebracht.'),
            'Ich bin vielen verschiedenen Menschen dankbar.': answers.get(
                'Ich bin vielen verschiedenen Menschen dankbar.')
        },
        'cognition': {
            'Wie würdest du deine Vergesslichkeit einstufen?': answers.get(
                'Wie würdest du deine Vergesslichkeit einstufen?'),
            'Wie gut ist dein Konzentrationsvermögen?': answers.get(
                'Wie gut ist dein Konzentrationsvermögen?'),
            'Nimmst du dir im Alltag Zeit, noch neue Dinge/Fähigkeiten zu erlernen?': answers.get(
                'Nimmst du dir im Alltag Zeit, noch neue Dinge/Fähigkeiten zu erlernen?'),
        }
    }

    return integrated_data
