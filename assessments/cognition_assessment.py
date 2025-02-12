# rule_based_system/assessments/cognition_assessment.py

from assessments.base_assessment import BaseAssessment

class CognitionAssessment(BaseAssessment):
    REQUIRED_KEYS = [
        'Wie würdest du deine Vergesslichkeit einstufen?',
        'Wie gut ist dein Konzentrationsvermögen?',
        'Nimmst du dir im Alltag Zeit, noch neue Dinge/Fähigkeiten zu erlernen?'
    ]

    def __init__(self, answers):
        """
        Initialize the CognitionAssessment with the provided answers.

        :param answers: A dictionary containing the answers to the cognition assessment questions
        """
        super().__init__()
        self.validate_answers(answers)
        self.answers = answers
        self.cognition = self.convert_cognition(answers)

    def validate_answers(self, answers):
        """
        Validate that all required answers are present and can be converted to integers.

        :param answers: A dictionary containing the answers for the cognition assessment
        :raises ValueError: If any required key is missing or answer is not an integer
        """
        for key in self.REQUIRED_KEYS:
            if key not in answers:
                raise ValueError(f"Missing required key: '{key}' in answers.")
            try:
                int(answers[key])
            except (ValueError, TypeError):
                raise ValueError(f"Value for '{key}' must be an integer, got: {answers[key]}")

    def convert_cognition(self, answers):
        """
        Convert the answers to cognition assessment questions into corresponding scores.

        :param answers: A dictionary containing the answers to the cognition assessment questions
        :return: A tuple (forgetfulness, concentration, learning)
        """
        forgetfulness_raw = int(answers.get('Wie würdest du deine Vergesslichkeit einstufen?', 0))
        # Inversion: if user says "5" for forgetfulness, we map it to 1. Formula: forgetfulness = 6 - forgetfulness_raw
        forgetfulness = 6 - forgetfulness_raw

        concentration = int(answers.get('Wie gut ist dein Konzentrationsvermögen?', 0))
        learning = int(answers.get('Nimmst du dir im Alltag Zeit, noch neue Dinge/Fähigkeiten zu erlernen?', 0))

        return forgetfulness, concentration, learning

    def calculate_cognition_score(self):
        """
        Calculate the cognition score based on the converted answers.

        :return: The calculated cognition score as a float
        """
        forgetfulness, concentration, learning = self.cognition
        total_points = forgetfulness + concentration + learning
        # Max total points = (forgetfulness max = 5 if raw=1, concentration max=5, learning max=5) = 15
        score = total_points / 15 * 80
        return score

    def report(self):
        """
        Generate a report based on the cognition assessment score.

        :return: A string representation of the cognition assessment score
        """
        score = self.calculate_cognition_score()
        return f"{score:.2f}"


