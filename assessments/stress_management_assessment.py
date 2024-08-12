# rule_based_system/assessments/stress_management_assessment.py


from .base_assessment import BaseAssessment

class StressManagementAssessment(BaseAssessment):
    def __init__(self, answers, stress_situations_response_str, stress_symptoms_response_str):
        """
        Initialize the StressManagementAssessment with the provided answers.

        :param answers: A dictionary containing the answers to the stress management assessment questions
        :param stress_situations_response_str: A string response for stress situations
        :param stress_symptoms_response_str: A string response for stress symptoms
        """
        super().__init__()
        self.stress_management = self.convert_stress_management(answers, stress_situations_response_str, stress_symptoms_response_str)

    def convert_stress_management(self, answers, stress_situations_response_str, stress_symptoms_response_str):
        """
        Convert the answers to stress management assessment questions into corresponding scores.

        :param answers: A dictionary containing the answers to the stress management assessment questions
        :param stress_situations_response_str: A string response for stress situations
        :param stress_symptoms_response_str: A string response for stress symptoms
        :return: A list of scores for each stress management-related question
        """
        stress_level_mapping = {
            1: 5,
            2: 4,
            3: 3,
            4: 2,
            5: 0
        }
        stress_level = int(answers.get('Leidest du aktuell unter Stress?', 0))
        stress_level_value = stress_level_mapping.get(stress_level, 0)
        stress_situations_response = answers.get('Welche der folgenden Stresssituationen trifft momentan auf dich zu?', '')
        stress_symptoms_response = answers.get('Welche der folgenden Stresssymptome hast du in den letzten 6 Monaten beobachtet?', '')

        stress_situations = 5 if stress_situations_response == 'Gar keine' else len(stress_situations_response.split(', '))
        stress_symptoms = 5 if stress_symptoms_response == 'Gar keine' else len(stress_symptoms_response.split(', '))

        def calculate_points(length):
            if length == 1:
                return 4
            elif length == 2:
                return 3
            elif length == 3:
                return 2
            elif length == 4:
                return 1
            elif length > 4:
                return 0

        if stress_situations_response != 'gar keine':
            stress_situations_value = calculate_points(stress_situations)
        else:
            stress_situations_value = 5
        if stress_symptoms_response != 'gar keine':
            stress_symptoms_value = calculate_points(stress_symptoms)
        else:
            stress_symptoms_value = 5

        stress_coping_mapping = {
            'Ich versuche, die positive Seite von Stress und Druck zu sehen.': [5, 4, 3, 2, 1],
            'Ich tue alles, damit Stress erst gar nicht entsteht.': [5, 4, 3, 2, 1],
            'Wenn ich unter Druck gerate, habe ich Menschen, die mir helfen.': [5, 4, 3, 2, 1],
            'Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.': [5, 4, 3, 2, 1]
        }

        stress_coping_values = []

        for key in stress_coping_mapping.keys():
            key_trimmed = key.strip()
            value_str = answers.get(key_trimmed, 0)
            value = int(value_str)

            if key_trimmed == 'Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.':
                if value != 0:
                    reversed_value = 6 - value
                    stress_coping_values.append(reversed_value)
                else:
                    stress_coping_values.append(value)
            else:
                stress_coping_values.append(value)

        if stress_coping_values:
            stress_coping_average = sum(stress_coping_values) / len(stress_coping_values)
        else:
            stress_coping_average = 0

        if all(value == 5 for value in stress_coping_values):
            stress_coping_average = 5

        return [stress_level_value, stress_situations_value, stress_symptoms_value, stress_coping_average]

    def calculate_stress_management_score(self):
        """
        Calculate the stress management score based on the converted answers.

        :return: The calculated stress management score as a float
        """
        stress_level, stress_situations, stress_symptoms, stress_coping = self.stress_management

        weight_stress_level = 0.30
        weight_stress_situations = 0.20
        weight_stress_symptoms = 0.20
        weight_stress_coping = 0.30

        score = (
            weight_stress_level * stress_level +
            weight_stress_situations * stress_situations +
            weight_stress_symptoms * stress_symptoms +
            weight_stress_coping * stress_coping
        )
        normalized_score = score / 5 * 100
        return normalized_score

    def report(self):
        """
        Generate a report based on the stress management assessment score.

        :return: A string representation of the stress management assessment score
        """
        score = self.calculate_stress_management_score()
        return f"{score:.2f}"

if __name__ == "__main__":
    stress_management = StressManagementAssessment(
        answers={
            'Leidest aktuell du unter Stress?': '1',
            'Ich versuche, die positive Seite von Stress und Druck zu sehen.': '5',
            'Ich tue alles, damit Stress erst gar nicht entsteht.': '5',
            'Wenn ich unter Druck gerate, habe ich Menschen, die mir helfen.': '5',
            'Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.': '1',
            'Welche der folgenden Stresssituationen trifft momentan auf dich zu?': 'gar keine',
            'Welche der folgenden Stresssymptome hast du in den letzten 6 Monaten beobachtet?': 'gar keine'
        },
        stress_situations_response_str='gar keine',
        stress_symptoms_response_str='gar keine'
    )
    print(stress_management.report())
