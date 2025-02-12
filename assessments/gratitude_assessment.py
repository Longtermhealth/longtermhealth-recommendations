# rule_based_system/assessments/gratitude_assessment.py

from assessments.base_assessment import BaseAssessment

class GratitudeAssessment(BaseAssessment):
    REQUIRED_KEYS = [
        'Ich habe so viel im Leben, wofür ich dankbar sein kann.',
        'Wenn ich alles auflisten müsste, wofür ich dankbar bin, wäre es eine sehr lange Liste.',
        'Wenn ich die Welt betrachte, sehe ich nicht viel, wofür ich dankbar sein könnte.',
        'Ich bin vielen verschiedenen Menschen dankbar.',
        'Je älter ich werde, desto mehr schätze ich die Menschen, Ereignisse und Situationen, die Teil meiner Lebensgeschichte waren.',
        'Es können lange Zeiträume vergehen, bevor ich etwas oder jemandem dankbar bin.'
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
            int(answers.get('Ich habe so viel im Leben, wofür ich dankbar sein kann.', 0)),
            int(answers.get('Wenn ich alles auflisten müsste, wofür ich dankbar bin, wäre es eine sehr lange Liste.', 0)),
            int(answers.get('Wenn ich die Welt betrachte, sehe ich nicht viel, wofür ich dankbar sein könnte.', 0)),
            int(answers.get('Ich bin vielen verschiedenen Menschen dankbar.', 0)),
            int(answers.get('Je älter ich werde, desto mehr schätze ich die Menschen, Ereignisse und Situationen, die Teil meiner Lebensgeschichte waren.', 0)),
            int(answers.get('Es können lange Zeiträume vergehen, bevor ich etwas oder jemandem dankbar bin.', 0))
        ]
        return gratitude

    def calculate_gratitude_score(self):
        """
        Calculate the gratitude score based on the converted answers.

        :return: The calculated gratitude score as a float
        """
        gratitude = self.gratitude.copy()
        if gratitude != [0, 0, 0, 0, 0, 0]:
            # The 3rd question (index 2) and the 6th question (index 5) are reversed
            # According to the logic: reversed scoring means 6 - given_answer
            if len(gratitude) >= 3:
                gratitude[2] = 6 - gratitude[2]
                if len(gratitude) >= 6:
                    gratitude[5] = 6 - gratitude[5]

            total_gratitude_score = sum(gratitude)
            min_score = 5
            max_score = 30
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


