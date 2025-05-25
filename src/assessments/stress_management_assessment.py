# rule_based_system/assessments/stress_management_assessment.py

from src.assessments.base_assessment import BaseAssessment


class StressManagementAssessment(BaseAssessment):
    REQUIRED_KEYS = [
        'Leidest du aktuell unter Stress?',
        'Ich versuche, die positive Seite von Stress und Druck zu sehen.',
        'Ich tue alles, damit Stress erst gar nicht entsteht.',
        'Wenn ich unter Druck gerate, habe ich Menschen, die mir helfen.',
        'Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.'
    ]

    def __init__(self, answers):
        """
        Initialize the StressManagementAssessment with the provided answers.

        :param answers: A dictionary containing the answers to the stress management assessment questions
        """
        super().__init__()
        self.validate_answers(answers)
        self.stress_management = self.convert_stress_management(answers)

    def validate_answers(self, answers):
        """
        Validate that all required answers are present and can be converted to integers.

        :param answers: A dictionary containing answers to assessment questions
        :raises ValueError: If any required key is missing or value is not a valid integer
        """
        for key in self.REQUIRED_KEYS:
            if key not in answers:
                raise ValueError(f"Missing required key: '{key}' in answers.")
            # Validate that values are integers (as strings)
            try:
                int(answers[key])
            except (ValueError, TypeError):
                raise ValueError(f"Value for '{key}' must be an integer, got: {answers[key]}")

    def convert_stress_management(self, answers):
        """
        Convert the answers to stress management assessment questions into corresponding scores.

        :param answers: A dictionary containing the answers to the stress management assessment questions
        :return: A list [stress_level_value, stress_coping_average]
        """
        stress_level_mapping = {
            1: 5,
            2: 4,
            3: 3,
            4: 2,
            5: 0
        }

        # Convert and map stress level
        stress_level_raw = int(answers.get('Leidest du aktuell unter Stress?', 0))
        stress_level_value = stress_level_mapping.get(stress_level_raw, 0)

        stress_coping_mapping = {
            'Ich versuche, die positive Seite von Stress und Druck zu sehen.': [5, 4, 3, 2, 1],
            'Ich tue alles, damit Stress erst gar nicht entsteht.': [5, 4, 3, 2, 1],
            'Wenn ich unter Druck gerate, habe ich Menschen, die mir helfen.': [5, 4, 3, 2, 1],
            'Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.': [
                5, 4, 3, 2, 1]
        }

        # Convert coping strategies
        stress_coping_values = []
        for key in stress_coping_mapping.keys():
            key_trimmed = key.strip()
            value_str = answers.get(key_trimmed, 0)
            value = int(value_str)

            # Reverse scoring for the unhealthy coping pattern question
            if key_trimmed == 'Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.':
                if value != 0:
                    reversed_value = 6 - value
                    stress_coping_values.append(reversed_value)
                else:
                    stress_coping_values.append(value)
            else:
                stress_coping_values.append(value)

        # Calculate average
        if stress_coping_values:
            stress_coping_average = sum(stress_coping_values) / len(stress_coping_values)
        else:
            stress_coping_average = 0

        # Special case: all 5
        if all(value == 5 for value in stress_coping_values):
            stress_coping_average = 5

        return [stress_level_value, stress_coping_average]

    def calculate_stress_management_score(self):
        """
        Calculate the stress management score based on the converted answers.

        :return: The calculated stress management score as a float
        """
        stress_level, stress_coping = self.stress_management

        weight_stress_level = 0.60
        weight_stress_coping = 0.40

        score = (
                weight_stress_level * stress_level +
                weight_stress_coping * stress_coping
        )
        normalized_score = score / 5 * 80
        return normalized_score

    def report(self):
        """
        Generate a report based on the stress management assessment score.

        :return: A string representation of the stress management assessment score
        """
        score = self.calculate_stress_management_score()
        return f"{score:.2f}"

