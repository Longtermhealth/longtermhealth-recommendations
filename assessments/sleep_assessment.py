# rule_based_system/assessments/sleep_assessment.py


from .base_assessment import BaseAssessment

class SleepAssessment(BaseAssessment):
    def __init__(self, answers):
        """
        Initialize the SleepAssessment with the provided answers.

        :param answers: A dictionary containing the answers to the sleep assessment questions
        """
        super().__init__()
        sleep_problems = answers.get('Welche Schlafprobleme hast du?', [])
        self.sleep = self.convert_sleep(
            answers['Wie ist deine Schlafqualität?'],
            sleep_problems,
            answers['Wie viele Stunden schläfst du im Durchschnitt pro Nacht?'],
            int(answers.get('Fühlst du dich tagsüber müde?', 0)),
            answers['Wie viel Zeit verbringst du morgens draußen?'],
            answers['Wie viel Zeit verbringst du abends draußen?']
        )

    def convert_sleep(self, sleep_quality, sleep_problems, sleep_hours, sleep_tiredness, time_outside_morning, time_outside_evening):
        """
        Convert the answers to sleep assessment questions into corresponding scores.

        :param sleep_quality: Quality of sleep
        :param sleep_problems: List of sleep problems
        :param sleep_hours: Average sleep hours per night
        :param sleep_tiredness: Daytime tiredness level
        :param time_outside_morning: Time spent outside in the morning
        :param time_outside_evening: Time spent outside in the evening
        :return: A list of scores for each sleep-related question
        """
        sleep_quality_mapping = {'Sehr gut': 5, 'Gut': 4, 'Mittel': 3, 'Ich habe leichte Schlafprobleme': 2, 'Ich habe schwere Schlafprobleme': 0}
        sleep_hours_mapping = {'0-3': 1, '4-6': 3, '7-9': 5, '10-12': 3, '> 12': 2}
        sleep_problems_mapping = {'Einschlafprobleme': 1, 'Durchschlafprobleme': 1, 'Sonstige': 1}
        time_outside_morning_mapping = {'> 20 min': 5, '11-20 min': 4, '5-10 min': 3, '< 5 min': 2}
        time_outside_evening_mapping = {'> 20 min': 5, '11-20 min': 4, '5-10 min': 3, '< 5 min': 2}

        sleep_quality_value = sleep_quality_mapping[sleep_quality]
        sleep_hours_value = sleep_hours_mapping[sleep_hours]
        sleep_tiredness = 6 - sleep_tiredness
        time_outside_morning_value = time_outside_morning_mapping[time_outside_morning]
        time_outside_evening_value = time_outside_evening_mapping[time_outside_evening]

        if sleep_quality in ['Sehr gut', 'Gut', 'Mittel']:
            sleep_problems_value = 5
        else:
            sleep_problems_value = 5 - sum(
                sleep_problems_mapping[problem] for problem in sleep_problems if problem in sleep_problems_mapping)

        return [sleep_quality_value, sleep_problems_value, sleep_hours_value, sleep_tiredness, time_outside_morning_value, time_outside_evening_value]

    def calculate_sleep_score(self):
        """
        Calculate the sleep score based on the converted answers.

        :return: The calculated sleep score as a float
        """
        sleep_quality, sleep_problems, sleep_hours, sleep_tiredness, time_outside_morning, time_outside_evening = self.sleep

        if sleep_quality <= 2:
            weight_sleep_quality = 0.30
            weight_sleep_problems = 0.05
            weight_sleep_hours = 0.30
            weight_sleep_tiredness = 0.25
            weight_time_outside_morning = 0.075
            weight_time_outside_evening = 0.025
        else:
            weight_sleep_quality = 0.30
            weight_sleep_problems = 0
            weight_sleep_hours = 0.30
            weight_sleep_tiredness = 0.3
            weight_time_outside_morning = 0.075
            weight_time_outside_evening = 0.025

        score = (
            weight_sleep_quality * sleep_quality +
            weight_sleep_problems * sleep_problems +
            weight_sleep_hours * sleep_hours +
            weight_sleep_tiredness * sleep_tiredness +
            weight_time_outside_morning * time_outside_morning +
            weight_time_outside_evening * time_outside_evening
        )

        return self.normalize_score(score, 0, 100)

    def report(self):
        """
        Generate a report based on the sleep assessment score.

        :return: A string representation of the sleep assessment score
        """
        score = self.calculate_sleep_score()
        return f"{score:.2f}"

if __name__ == "__main__":
    answers = {
        'Wie ist deine Schlafqualität?': 'sehr gut',
        'Welche Schlafprobleme hast du?': [],
        'Wie viele Stunden schläfst du im Durchschnitt pro Nacht?': '7-9',
        'Fühlst du dich tagsüber müde?': '1',
        'Wie viel Zeit verbringst du morgens draußen?': 'mehr als 60 min',
        'Wie viel Zeit verbringst du abends draußen?': 'mehr als 60 min'
    }

    sleep_assessment = SleepAssessment(answers)
    print(sleep_assessment.report())
