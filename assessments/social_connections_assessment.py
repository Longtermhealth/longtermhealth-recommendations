# rule_based_system/assessments/social_connections_assessment.py

from assessments.base_assessment import BaseAssessment

class SocialConnectionsAssessment(BaseAssessment):
    REQUIRED_KEYS = [
        'Wie oft unternimmst du etwas mit anderen Menschen?',
        'Bist du sozial engagiert?',
        'Fühlst du dich einsam?'
    ]

    ACTIVITIES_MAPPING = {
        'Weniger als 2x pro Monat': 1,
        'Ca. 3-4x pro Monat': 3,
        'Mehrmals pro Woche': 4,
        'Fast täglich': 5
    }

    def __init__(self, answers):
        """
        Initialize the SocialConnectionsAssessment with the provided answers.

        :param answers: A dictionary containing the answers to the social connections assessment questions
        """
        super().__init__()
        self.validate_answers(answers)
        activities = answers.get('Wie oft unternimmst du etwas mit anderen Menschen?')
        engagement = answers.get('Bist du sozial engagiert?')
        loneliness = answers.get('Fühlst du dich einsam?')

        self.social_connections = self.convert_social_connections(
            activities,
            engagement,
            loneliness
        )

    def validate_answers(self, answers):
        """
        Validate that all required answers are present and conform to expected formats.

        :param answers: dict of user answers
        :raises ValueError: if a required key is missing or values are invalid
        """
        for key in self.REQUIRED_KEYS:
            if key not in answers:
                raise ValueError(f"Missing required key: '{key}' in answers.")

        activities = answers['Wie oft unternimmst du etwas mit anderen Menschen?']
        if activities not in self.ACTIVITIES_MAPPING:
            raise ValueError(f"Invalid activity frequency: {activities}")

        engagement = answers['Bist du sozial engagiert?']
        # We expect a boolean or something convertible. Let's treat non-empty strings as True, empty as False.
        # If you want strict boolean, adjust logic accordingly.
        if isinstance(engagement, str):
            # Convert a string engagement to a boolean: non-empty => True, empty => False
            engagement_bool = bool(engagement.strip())
        else:
            engagement_bool = bool(engagement)

        # Replace in original dict to store the boolean value
        answers['Bist du sozial engagiert?'] = engagement_bool

        loneliness = answers['Fühlst du dich einsam?']
        # Ensure loneliness is an integer
        # If it's already int, fine; if str, must be digit
        if isinstance(loneliness, str):
            if not loneliness.isdigit():
                raise ValueError(f"Value for 'Fühlst du dich einsam?' must be an integer, got: {loneliness}")
            loneliness = int(loneliness)
            answers['Fühlst du dich einsam?'] = loneliness
        elif not isinstance(loneliness, int):
            raise ValueError(f"Value for 'Fühlst du dich einsam?' must be an integer, got: {loneliness}")

    def convert_social_connections(self, activities, engagement, loneliness):
        """
        Convert the answers to social connections assessment questions into corresponding scores.
        """
        activities_value = self.ACTIVITIES_MAPPING[activities]
        engagement_points = 5 if engagement else 0

        # loneliness is an int
        loneliness_reversed_value = 6 - loneliness
        loneliness_value = loneliness_reversed_value

        return [activities_value, engagement_points, loneliness_value]

    def calculate_social_connections_score(self):
        """
        Calculate the social connections score based on the converted answers.
        """
        activities, engagement, loneliness = self.social_connections

        weight_activities = 0.30
        weight_engagement = 0.20
        weight_loneliness = 0.50

        score = (
            weight_activities * activities +
            weight_engagement * engagement +
            weight_loneliness * loneliness
        )

        return self.normalize_score(score, 0, 100)

    def report(self):
        """
        Generate a report based on the social connections assessment score.
        """
        score = self.calculate_social_connections_score()
        return f"{score:.2f}"


