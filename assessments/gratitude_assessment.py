# rule_based_system/assessments/gratitude_assessment.py

from assessments.base_assessment import BaseAssessment

class GratitudeAssessment(BaseAssessment):
    REQUIRED_KEYS = [
        'Ich liebe mich so, wie ich bin.',
        'Ich habe so viel im Leben, wofür ich dankbar sein kann.',
        'Jeder Tag ist eine Chance, es besser zu machen.',
        'Im Nachhinein bin ich für jede Niederlage dankbar, denn sie haben mich weitergebracht.',
        'Ich bin vielen verschiedenen Menschen dankbar.'
    ]

    def __init__(self, answers):
        """
        Initialize the GratitudeAssessment with the provided answers.

        :param answers: A dictionary containing the answers to the gratitude assessment questions
        """
        super().__init__()
        self.validate_answers(answers)
        self.gratitude = self.convert_gratitude(answers)

    def validate_answers(self, answers):
        """
        Validate that all required answers are present and can be converted to integers.

        :param answers: A dictionary containing the answers for the gratitude assessment
        :raises ValueError: If any required key is missing or answer is not an integer
        """
        for key in self.REQUIRED_KEYS:
            if key not in answers:
                raise ValueError(f"Missing required key: '{key}' in answers.")
            try:
                int(answers[key])
            except (ValueError, TypeError):
                raise ValueError(f"Value for '{key}' must be an integer, got: {answers[key]}")

    def convert_gratitude(self, answers):
        """
        Convert the answers to gratitude assessment questions into corresponding scores.

        :param answers: A dictionary containing the answers to the gratitude assessment questions
        :return: A list of scores for each gratitude-related question
        """
        gratitude = [
            int(answers.get('Ich liebe mich so, wie ich bin.', 0)),
            int(answers.get('Ich habe so viel im Leben, wofür ich dankbar sein kann.', 0)),
            int(answers.get('Jeder Tag ist eine Chance, es besser zu machen.', 0)),
            int(answers.get('Im Nachhinein bin ich für jede Niederlage dankbar, denn sie haben mich weitergebracht.', 0)),
            int(answers.get('Ich bin vielen verschiedenen Menschen dankbar.', 0))
        ]
        return gratitude

    def calculate_gratitude_score(self):
        """
        Calculate the gratitude score based on the converted answers.

        :return: The calculated gratitude score as a float
        """
        gratitude = self.gratitude.copy()
        if gratitude != [0, 0, 0, 0, 0]:
            total_gratitude_score = sum(gratitude)
            min_score = 5
            max_score = 25
            normalized_score = ((total_gratitude_score - min_score) / (max_score - min_score)) * 80
        else:
            normalized_score = 0

        return normalized_score

    def report(self):
        """
        Generate a report based on the gratitude assessment score.

        :return: A string representation of the gratitude assessment score
        """
        score = self.calculate_gratitude_score()
        return f"{score:.2f}"


