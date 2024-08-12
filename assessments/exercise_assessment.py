# rule_based_system/assessments/exercise_assessment.py

from .base_assessment import BaseAssessment

class ExerciseAssessment(BaseAssessment):
    def __init__(self, answers):
        """
        Initialize the ExerciseAssessment with the provided answers.

        :param answers: A dictionary containing the answers to the exercise assessment questions
        """
        super().__init__()
        self.exercise = self.convert_exercise(answers)

    def convert_exercise(self, answers):
        """
        Convert the answers to exercise assessment questions into corresponding scores.

        :param answers: A dictionary containing the answers to the exercise assessment questions
        :return: A list of scores for each exercise-related question
        """
        flexibility = int(answers.get('Wie schätzt du deine Beweglichkeit ein?', 0))
        activity = int(answers.get('Wie aktiv bist du im Alltag?', 0))
        sports_per_week = int(answers.get('Wie oft in der Woche treibst du Sport?', 0))
        sports = answers.get('Welchen Schwerpunkt haben die Sportarten, die du betreibst?', '').split(', ')
        sports_cardio = answers.get('Welche Sportarten im Bereich Ausdauer machst du?', '').split(', ')
        sports_flexibility = answers.get('Welche Sportarten im Bereich Flexibilität machst du?', '').split(', ')

        if answers.get('Geburtsjahr') is None:
            age = 0
        else:
            age = (2024 - int(answers.get('Geburtsjahr')))

        if age < 40:
            points_mapping = {
                'Ausdauer': 1.25,    # 25% of 5 points
                'Kraft': 1.25,       # 25% of 5 points
                'HIIT': 2.0,         # 40% of 5 points
                'Flexibilität': 0.5  # 10% of 5 points
            }
        else:
            points_mapping = {
                'Ausdauer': 0.5,     # 10% of 5 points
                'Kraft': 2.0,        # 40% of 5 points
                'HIIT': 2.0,         # 40% of 5 points
                'Flexibilität': 0.5  # 10% of 5 points
            }

        total_points = 0

        for sport in sports:
            if sport in points_mapping:
                total_points += points_mapping[sport]

        sports = total_points
        return [flexibility, activity, sports_per_week, sports]

    def calculate_exercise_score(self):
        """
        Calculate the exercise score based on the converted answers.

        :return: The calculated exercise score as a float
        """
        flexibility, activity, sports_per_week, sports = self.exercise
        weight_flexibility = 0.10
        weight_frequency_of_sport = 0.40
        weight_activity = 0.30
        weight_types_of_sport = 0.20

        score = (
            weight_flexibility * flexibility +
            weight_frequency_of_sport * sports_per_week +
            weight_activity * activity +
            weight_types_of_sport * sports
        )

        normalized_score = score / 5 * 100
        return normalized_score

    def report(self):
        """
        Generate a report based on the exercise assessment score.

        :return: A string representation of the exercise assessment score
        """
        score = self.calculate_exercise_score()
        return f"{score:.2f}"

if __name__ == "__main__":
    answers = {
        'Wie schätzt du deine Beweglichkeit ein?': '5',
        'Wie aktiv bist du im Alltag?': '5',
        'Wie oft in der Woche treibst du Sport?': '5',
        'Welchen Schwerpunkt haben die Sportarten, die du betreibst?': 'Ausdauer, Kraft, Flexibilität, HIIT',
        'Welche Sportarten im Bereich Ausdauer machst du?': 'Laufen, Schwimmen',
        'Welche Sportarten im Bereich Flexibilität machst du?': 'Yoga',
        'Geburtsjahr': '1990'
    }

    exercise_assessment = ExerciseAssessment(answers)
    print(exercise_assessment.report())
