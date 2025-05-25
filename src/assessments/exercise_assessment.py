# rule_based_system/assessments/exercise_assessment.py

from src.assessments.base_assessment import (BaseAssessment)

class ExerciseAssessment(BaseAssessment):
    REQUIRED_KEYS = [
        'Wie schätzt du deine Beweglichkeit ein?',
        'Wie aktiv bist du im Alltag?',
        'Wie oft in der Woche treibst du eine Cardio-Sportart?',
        'Wie schätzt du deine Kraft ein?'
    ]

    def __init__(self, answers):
        """
        Initialize the ExerciseAssessment with the provided answers.

        :param answers: A dictionary containing the answers to the exercise assessment questions
        """
        super().__init__()
        self.validate_answers(answers)
        self.exercise = self.convert_exercise(answers)

    def validate_answers(self, answers):
        """
        Validate that all required answers are present and can be converted to integers.

        :param answers: A dictionary containing the answers for the exercise assessment
        :raises ValueError: If any required key is missing or answer is not an integer
        """

        for key in self.REQUIRED_KEYS:
            try:
                int(answers[key])
            except (ValueError, TypeError):
                raise ValueError(f"Value for '{key}' must be an integer, got: {answers[key]}")

    def convert_exercise(self, answers):
        """
        Convert the answers to exercise assessment questions into corresponding scores.

        :param answers: A dictionary containing the answers to the exercise assessment questions
        :return: A list of scores for each exercise-related question
        """
        flexibility = int(answers.get('Wie schätzt du deine Beweglichkeit ein?', 0))
        activity = int(answers.get('Wie aktiv bist du im Alltag?', 0))
        sports_per_week = int(answers.get('Wie oft in der Woche treibst du eine Cardio-Sportart?', 0))
        strength = int(answers.get('Wie schätzt du deine Kraft ein?', 0))

        return [flexibility, activity, sports_per_week, strength]

    def calculate_exercise_score(self):
        """
        Calculate the exercise score based on the converted answers.

        :return: The calculated exercise score as a float
        """
        flexibility, activity, sports_per_week, strength = self.exercise
        weight_flexibility = 0.10
        weight_frequency_of_sport = 0.40
        weight_activity = 0.30
        weight_strength = 0.20

        score = (
            weight_flexibility * flexibility +
            weight_frequency_of_sport * sports_per_week +
            weight_activity * activity +
            weight_strength * strength
        )

        normalized_score = score / 5 * 80
        return normalized_score

    def report(self):
        """
        Generate a report based on the exercise assessment score.

        :return: A string representation of the exercise assessment score
        """
        score = self.calculate_exercise_score()
        return f"{score:.2f}"

