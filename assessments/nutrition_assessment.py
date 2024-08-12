# rule_based_system/assessments/nutrition_assessment.py


from .base_assessment import BaseAssessment

class NutritionAssessment(BaseAssessment):
    def __init__(self, answers):
        """
        Initialize the NutritionAssessment with the provided answers.

        :param answers: A dictionary containing the answers to the nutrition assessment questions
        """
        super().__init__()
        self.nutrition = self.convert_nutrition(answers)

    def convert_nutrition(self, answers):
        """
        Convert the answers to nutrition assessment questions into corresponding scores.

        :param answers: A dictionary containing the answers to the nutrition assessment questions
        :return: A tuple of scores for each nutrition-related question
        """
        fasting = 0
        fasting_type = answers.get('Praktizierst du Intervallfasten und auf welche Art??', '')
        if (fasting_type == '16:8 (täglich 14-16 Stunden fasten)'
                or fasting_type == 'Alternierendes Fasten (jeden zweiten Tag fasten oder stark reduzierte Kalorieneinnahme)'):
            fasting = 5
        elif (fasting_type == 'Eat Stop Eat (1-2 x pro Woche für 24 Stunden fasten)'
                or fasting_type == '5:2 (an 2 Tagen der Woche nur Einnahme von 500 bzw. 600 Kalorien)'):
            fasting = 4
        elif (fasting_type == 'Warrior Diät (Einnahme kleiner Mengen rohen Obst und Gemüses tagsüber und eine große Abendmahlzeit)'
                or fasting_type == 'Spontanes Auslassen einer Mahlzeit (regelmäßiges Auslassen einzelner Mahlzeiten)'):
            fasting = 3
        else:
            fasting = 1

        fluids_mapping = {'0-3': 1, '4-6': 2, '7-9': 3, '10-12': 5, '> 12': 5}
        fluids = fluids_mapping.get(answers.get('Wie viele Gläser Flüssigkeit (200ml) nimmst du ca. täglich zu dir?', ''), 0)
        alcohol_mapping = {'Gar keinen': 5, '1-3': 4, '4-6': 3, '7-9': 2, '10-12': 1, '> 12': 0}
        alcohol = alcohol_mapping.get(answers.get('Wie viel Alkohol trinkst du in der Woche?', ''), 0)

        sugar = int(answers.get('Wie viel zuckerhaltige Produkte nimmst du zu dir?', 0))
        if sugar != 0:
            sugar = 6 - sugar

        fruits = int(answers.get('Wie viel Obst nimmst du pro Tag zu dir?', 0))
        if fruits >= 3:
            fruits = 5
        vegetables = int(answers.get('Wie viel Gemüse nimmst du pro Tag zu dir?', 0))
        """
        meat = int(answers.get('Wie viel Fleisch nimmst du zu dir?', 0) or 0)
        if meat != 0:
            meat = 6 - meat
        elif meat == 0:
            meat = 5
        """
        processed = int(answers.get('Wie häufig nimmst du Fertiggerichte zu dir?', 0))
        if processed != 0:
            processed = 6 - processed

        whole_grain = int(answers.get('Wie viel Vollkorn nimmst du zu dir?', 0))

        return fasting, fasting_type, fluids, alcohol, sugar, fruits, vegetables, processed, whole_grain

    def calculate_nutrition_score(self):
        """
        Calculate the nutrition score based on the converted answers.

        :return: The calculated nutrition score as a float
        """
        fasting, fasting_type, fluids, alcohol, sugar, fruits, vegetables, processed, whole_grain = self.nutrition

        weight_sugar = 0.20
        weight_fruits = 0.10
        weight_vegetables = 0.25
        #weight_meat = 0.10
        weight_processed = 0.25
        weight_whole_grain = 0.20

        nutri_score = (weight_sugar * sugar +
                       weight_fruits * fruits +
                       weight_vegetables * vegetables +
                       #weight_meat * meat +
                       weight_processed * processed +
                       weight_whole_grain * whole_grain)

        weight_nutrition = 0
        weight_fasting = 0
        weight_fluids = 0
        weight_alcohol = 0

        if fluids == 2:
            weight_nutrition += 0.7
            weight_fasting += 0.1
            weight_fluids += 0.1
        elif fluids == 1:
            weight_nutrition += 0.6
            weight_fasting += 0.1
            weight_fluids += 0.2
        else:
            weight_nutrition += 0.8
            weight_fasting += 0.1

        if alcohol == 3:
            weight_nutrition += 0.7
            weight_fasting += 0.1
            weight_alcohol += 0.3
        elif alcohol == 2:
            weight_nutrition += 0.65
            weight_fasting += 0.1
            weight_alcohol += 0.5
        elif alcohol == 1:
            weight_nutrition += 0.6
            weight_fasting += 0.1
            weight_alcohol += 0.7
        elif alcohol == 0:
            weight_nutrition += 0.5
            weight_fasting += 0.1
            weight_alcohol += 0.9
        else:
            weight_nutrition += 0.8
            weight_fasting += 0.1

        total_weight = weight_nutrition + weight_fasting + weight_fluids + weight_alcohol

        weight_nutrition /= total_weight
        weight_fasting /= total_weight
        weight_fluids /= total_weight
        weight_alcohol /= total_weight
        score = (
            weight_nutrition * nutri_score +
            weight_fasting * fasting +
            weight_fluids * fluids +
            weight_alcohol * alcohol
        )

        normalized_score = score / 5 * 100
        return normalized_score

    def report(self):
        """
        Generate a report based on the nutrition assessment score.

        :return: A string representation of the nutrition assessment score
        """
        score = self.calculate_nutrition_score()
        return f"{score:.2f}"


if __name__ == "__main__":
    answers = {
        'Welcher Ernährungsstil trifft bei dir am ehesten zu?': 'vegan',
        'Wie viele Gläser Flüssigkeit (200ml) nimmst du ca. täglich zu dir?': 'mehr als 12',
        'Wie viel Alkohol trinkst du in der Woche?': 'gar keinen',
        'Wie viel zuckerhaltige Produkte nimmst du zu dir?': '1',
        'Wie viel Obst nimmst du pro Tag zu dir?': '5',
        'Wie viel Gemüse nimmst du pro Tag zu dir?': '5',
        'Wie viel Fleisch nimmst du zu dir?': '1',
        'Wie häufig nimmst du Fertiggerichte zu dir?': '1',
        'Wie viel Vollkorn nimmst du zu dir?': '5',
        'Praktizierst du Intervallfasten und auf welche Art??': '16:8 (täglich 14-16 Stunden fasten)'
    }
    nutrition = NutritionAssessment(answers)
    print(nutrition.report())
