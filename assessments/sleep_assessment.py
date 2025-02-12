# rule_based_system/assessments/sleep_assessment.py

from assessments.base_assessment import BaseAssessment

class SleepAssessment(BaseAssessment):
    REQUIRED_KEYS = [
        'Wie ist deine Schlafqualität?',
        'Welche Schlafprobleme hast du?',
        'Wie viele Stunden schläfst du im Durchschnitt pro Nacht?',
        'Fühlst du dich tagsüber müde?',
        'Wie viel Zeit verbringst du morgens draußen?',
        'Wie viel Zeit verbringst du abends draußen?'
    ]

    sleep_quality_mapping = {
        'Sehr gut': 5,
        'Gut': 4,
        'Mittel': 3,
        'Ich habe leichte Schlafprobleme': 2,
        'Ich habe schwere Schlafprobleme': 0
    }

    sleep_hours_mapping = {
        '0-3': 1,
        '4-6': 3,
        '7-9': 5,
        '10-12': 3,
        '> 12': 2
    }

    sleep_problems_mapping = {
        'Einschlafprobleme': 1,
        'Durchschlafprobleme': 1,
        'Sonstige': 1
    }

    time_outside_morning_mapping = {
        '> 20 min': 5,
        '11-20 min': 4,
        '5-10 min': 3,
        '< 5 min': 2
    }

    time_outside_evening_mapping = {
        '> 20 min': 5,
        '11-20 min': 4,
        '5-10 min': 3,
        '< 5 min': 2
    }

    def __init__(self, answers):
        """
        Initialize the SleepAssessment with the provided answers.

        Expected value formats:
        - 'Wie ist deine Schlafqualität?' must be one of: Sehr gut, Gut, Mittel, Ich habe leichte Schlafprobleme, Ich habe schwere Schlafprobleme
        - 'Welche Schlafprobleme hast du?' must be a list of zero or more problems: Einschlafprobleme, Durchschlafprobleme, Sonstige
        - 'Wie viele Stunden schläfst du im Durchschnitt pro Nacht?' must be one of: 0-3, 4-6, 7-9, 10-12, > 12
        - 'Fühlst du dich tagsüber müde?' must be an integer (0-5 recommended)
        - 'Wie viel Zeit verbringst du morgens draußen?' must be one of: > 20 min, 11-20 min, 5-10 min, < 5 min
        - 'Wie viel Zeit verbringst du abends draußen?' must be one of: > 20 min, 11-20 min, 5-10 min, < 5 min
        """
        super().__init__()
        self.validate_answers(answers)
        sleep_problems = answers.get('Welche Schlafprobleme hast du?', [])
        self.sleep = self.convert_sleep(
            answers['Wie ist deine Schlafqualität?'],
            sleep_problems,
            answers['Wie viele Stunden schläfst du im Durchschnitt pro Nacht?'],
            int(answers.get('Fühlst du dich tagsüber müde?', 0)),
            answers['Wie viel Zeit verbringst du morgens draußen?'],
            answers['Wie viel Zeit verbringst du abends draußen?']
        )

    def validate_answers(self, answers):
        """
        Validate that all required answers are present and conform to expected formats.

        :param answers: dict of user answers
        :raises ValueError: if a required key is missing or values are invalid
        """
        # Check for missing keys
        for key in self.REQUIRED_KEYS:
            if key not in answers:
                raise ValueError(f"Missing required key: '{key}' in answers.")

        # Validate data types and expected values
        # Schlafqualität
        if answers['Wie ist deine Schlafqualität?'] not in self.sleep_quality_mapping:
            raise ValueError(f"Invalid sleep quality: {answers['Wie ist deine Schlafqualität?']}")

        # Schlafprobleme should be a list
        if not isinstance(answers['Welche Schlafprobleme hast du?'], list):
            raise ValueError("Value for 'Welche Schlafprobleme hast du?' must be a list.")

        # Check each problem in the list is known or not - it's allowed to have unknown but they won't count, still not an error.
        # If you want strictly allowed values, uncomment the following lines:
        # for problem in answers['Welche Schlafprobleme hast du?']:
        #     if problem not in self.sleep_problems_mapping:
        #         raise ValueError(f"Invalid sleep problem: {problem}")

        # Schlafstunden
        if answers['Wie viele Stunden schläfst du im Durchschnitt pro Nacht?'] not in self.sleep_hours_mapping:
            raise ValueError(f"Invalid sleep hours: {answers['Wie viele Stunden schläfst du im Durchschnitt pro Nacht?']}")

        # Tiredness must be integer
        try:
            int(answers['Fühlst du dich tagsüber müde?'])
        except ValueError:
            raise ValueError(f"Value for 'Fühlst du dich tagsüber müde?' must be an integer.")

        # Check times outside
        if answers['Wie viel Zeit verbringst du morgens draußen?'] not in self.time_outside_morning_mapping:
            raise ValueError(f"Invalid morning outside time: {answers['Wie viel Zeit verbringst du morgens draußen?']}")

        if answers['Wie viel Zeit verbringst du abends draußen?'] not in self.time_outside_evening_mapping:
            raise ValueError(f"Invalid evening outside time: {answers['Wie viel Zeit verbringst du abends draußen?']}")

    def convert_sleep(self, sleep_quality, sleep_problems, sleep_hours, sleep_tiredness, time_outside_morning, time_outside_evening):
        """
        Convert the answers to sleep assessment questions into corresponding scores.
        """
        sleep_quality_value = self.sleep_quality_mapping[sleep_quality]
        sleep_hours_value = self.sleep_hours_mapping[sleep_hours]
        sleep_tiredness = 6 - sleep_tiredness
        time_outside_morning_value = self.time_outside_morning_mapping[time_outside_morning]
        time_outside_evening_value = self.time_outside_evening_mapping[time_outside_evening]

        if sleep_quality in ['Sehr gut', 'Gut', 'Mittel']:
            sleep_problems_value = 5
        else:
            # Calculate penalty for problems
            penalty = sum(self.sleep_problems_mapping.get(problem, 0) for problem in sleep_problems)
            sleep_problems_value = 5 - penalty

        return [
            sleep_quality_value,
            sleep_problems_value,
            sleep_hours_value,
            sleep_tiredness,
            time_outside_morning_value,
            time_outside_evening_value
        ]

    def calculate_sleep_score(self):
        """
        Calculate the sleep score based on the converted answers.
        """
        sleep_quality, sleep_problems, sleep_hours, sleep_tiredness, time_outside_morning, time_outside_evening = self.sleep

        if sleep_quality <= 2:  # Poor quality
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

        return self.normalize_score(score, 0, 80)

    def report(self):
        """
        Generate a report based on the sleep assessment score.
        """
        score = self.calculate_sleep_score()
        return f"{score:.2f}"


