# rule_based_system/utils/data_processing.py

def integrate_answers(answers):
    integrated_data = {
        'exercise': {
            'Wie schätzt du deine Beweglichkeit ein?': answers.get('Wie schätzt du deine Beweglichkeit ein?', 0),
            'Wie aktiv bist du im Alltag?': answers.get('Wie aktiv bist du im Alltag?', 0),
            'Wie oft in der Woche treibst du Sport?': answers.get('Wie oft in der Woche treibst du Sport?', 0),
            'Welchen Schwerpunkt haben die Sportarten, die du betreibst?': answers.get('Welchen Schwerpunkt haben die Sportarten, die du betreibst?', ''),
            'Geburtsjahr': answers.get('Geburtsjahr', 0)
        },
        'nutrition': {
            'Welcher Ernährungsstil trifft bei dir am ehesten zu?': answers.get(
                'Welcher Ernährungsstil trifft bei dir am ehesten zu?'),
            'Wie viel zuckerhaltige Produkte nimmst du zu dir?': answers.get('Wie viel zuckerhaltige Produkte nimmst du zu dir?'),
            'Wie viel Gemüse nimmst du pro Tag zu dir?': answers.get('Wie viel Gemüse nimmst du pro Tag zu dir?'),
            'Wie viel Obst nimmst du pro Tag zu dir?': answers.get('Wie viel Obst nimmst du pro Tag zu dir?'),
            'Wie häufig nimmst du Fertiggerichte zu dir?': answers.get('Wie häufig nimmst du Fertiggerichte zu dir?'),
            'Wie viel Vollkorn nimmst du zu dir?': answers.get('Wie viel Vollkorn nimmst du zu dir?'),
            'Praktizierst du Intervallfasten und auf welche Art??': answers.get('Praktizierst du Intervallfasten und auf welche Art??'),
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
            'Hast du gute Freunde?': answers.get('Hast du gute Freunde?'),
            'Bist du sozial engagiert?': answers.get('Bist du sozial engagiert?'),
            'Fühlst du dich einsam?': answers.get('Fühlst du dich einsam?')
        },
        'stress_management': {
            'Leidest du aktuell unter Stress?': answers.get('Leidest du aktuell unter Stress?'),
            'Welche der folgenden Stresssituationen trifft momentan auf dich zu?': answers.get(
                'Welche der folgenden Stresssituationen trifft momentan auf dich zu?'),
            'Welche der folgenden Stresssymptome hast du in den letzten 6 Monaten beobachtet?': answers.get(
                'Welche der folgenden Stresssymptome hast du in den letzten 6 Monaten beobachtet?'),
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
            'Ich habe so viel im Leben, wofür ich dankbar sein kann.': answers.get(
                'Ich habe so viel im Leben, wofür ich dankbar sein kann.'),
            'Wenn ich alles auflisten müsste, wofür ich dankbar bin, wäre es eine sehr lange Liste.': answers.get('Wenn ich alles auflisten müsste, wofür ich dankbar bin, wäre es eine sehr lange Liste.'),
            'Wenn ich die Welt betrachte, sehe ich nicht viel, wofür ich dankbar sein könnte.': answers.get(
                'Wenn ich die Welt betrachte, sehe ich nicht viel, wofür ich dankbar sein könnte.'),
            'Ich bin vielen verschiedenen Menschen dankbar.': answers.get(
                'Ich bin vielen verschiedenen Menschen dankbar.'),
            'Je älter ich werde, desto mehr schätze ich die Menschen, Ereignisse und Situationen, die Teil meiner Lebensgeschichte waren.': answers.get(
                'Je älter ich werde, desto mehr schätze ich die Menschen, Ereignisse und Situationen, die Teil meiner Lebensgeschichte waren.'),
            'Es können lange Zeiträume vergehen, bevor ich etwas oder jemandem dankbar bin.': answers.get(
                'Es können lange Zeiträume vergehen, bevor ich etwas oder jemandem dankbar bin.')
        },
        'cognition': {
            'Wie würdest du deine Vergesslichkeit einstufen?': answers.get(
                'Wie würdest du deine Vergesslichkeit einstufen?'),
            'Wie gut ist dein Konzentrationsvermögen?': answers.get(
                'Wie gut ist dein Konzentrationsvermögen?'),
            'Welche Zahl gehört unter die letzte Abbildung?': answers.get(
                'Welche Zahl gehört unter die letzte Abbildung?'),
            'Ergänze die Zahlenreihenfolge 3,6,18,21,?': answers.get('Ergänze die Zahlenreihenfolge 3,6,18,21,?'),
            'Welche Form kommt an die Stelle vom ?': answers.get('Welche Form kommt an die Stelle vom ?'),
            'Quark : Milch / Brot : ?': answers.get('Quark : Milch / Brot : ?')
        },
        'fasting_breakfast': str(answers.get('Frühstück', '')),
        'fasting_lunch': str(answers.get('Mittagessen', '')),
        'fasting_dinner': str(answers.get('Abendessen', ''))
    }

    return integrated_data
