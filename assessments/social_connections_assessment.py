# rule_based_system/assessments/social_connections_assessment.py


from .base_assessment import BaseAssessment


class SocialConnectionsAssessment(BaseAssessment):
    def __init__(self, answers):
        """
        Initialize the SocialConnectionsAssessment with the provided answers.

        :param answers: A dictionary containing the answers to the social connections assessment questions
        """
        super().__init__()
        activities = answers.get('Wie oft unternimmst du etwas mit anderen Menschen ?', 'fast täglich')
        friends = answers.get('Hast du gute Freunde?', 'keine gute Freunde')
        engagement = answers.get('Bist du sozial engagiert?', False)
        loneliness = answers.get('Fühlst du dich einsam?', 0)

        self.social_connections = self.convert_social_connections(
            activities,
            friends,
            engagement,
            loneliness
        )

    def convert_social_connections(self, activities, friends, engagement, loneliness):
        """
        Convert the answers to social connections assessment questions into corresponding scores.

        :param activities: Frequency of social activities
        :param friends: Quality of friendships
        :param engagement: Level of social engagement
        :param loneliness: Level of loneliness
        :return: A list of scores for each social connections-related question
        """
        activities_mapping = {'weniger als 2x pro Monat': 1, 'ca. 3-4x pro Monat': 3, 'mehrmals pro Woche': 4, 'fast täglich': 5}
        friends_mapping = {'viele gute Freunde': 5, 'ein paar gute Freunde': 4, 'wenige gute Freunde': 2, 'keine gute Freunde': 0}
        engagement_points = 5 if engagement else 0

        activities_value = activities_mapping[activities]
        friends_value = friends_mapping[friends]

        if isinstance(loneliness, str):
            loneliness = int(loneliness) if loneliness.isdigit() else 0

        loneliness_reversed_value = 6 - loneliness
        loneliness = loneliness_reversed_value

        return [activities_value, friends_value, engagement_points, loneliness]

    def calculate_social_connections_score(self):
        """
        Calculate the social connections score based on the converted answers.

        :return: The calculated social connections score as a float
        """
        activities, friends, engagement, loneliness = self.social_connections

        weight_activities = 0.30
        weight_friends = 0.30
        weight_engagement = 0.20
        weight_loneliness = 0.20

        score = (
            weight_activities * activities +
            weight_friends * friends +
            weight_engagement * engagement +
            weight_loneliness * loneliness
        )

        return self.normalize_score(score, 0, 100)

    def report(self):
        """
        Generate a report based on the social connections assessment score.

        :return: A string representation of the social connections assessment score
        """
        score = self.calculate_social_connections_score()
        return f"{score:.2f}"

if __name__ == "__main__":
    answers = {
        'Wie oft unternimmst du etwas mit anderen Menschen ?': 'fast täglich',
        'Hast du gute Freunde?': 'viele gute Freunde',
        'Bist du sozial engagiert?': 'Kirche',
        'Fühlst du dich einsam?': 1
    }

    social_assessment = SocialConnectionsAssessment(answers)
    print(social_assessment.report())
