# rule_based_system/assessments/cognition_assessment.py

from .base_assessment import BaseAssessment

class CognitionAssessment(BaseAssessment):
    def __init__(self, answers):
        """
        Initialize the CognitionAssessment with the provided answers.

        :param answers: A dictionary containing the answers to the cognition assessment questions
        """
        super().__init__()
        self.answers = answers
        self.cognition = self.convert_cognition(answers)

    def convert_cognition(self, answers):
        """
        Convert the answers to cognition assessment questions into corresponding scores.

        :param answers: A dictionary containing the answers to the cognition assessment questions
        :return: A tuple of scores for each cognition question
        """
        forgetfulness = int(answers.get('Wie würdest du deine Vergesslichkeit einstufen?', 0))
        forgetfulness = 6 - forgetfulness


        concentration = answers.get('Wie gut ist dein Konzentrationsvermögen?')
        if concentration is None:
            concentration = 0
        else:
            concentration = int(concentration)
        #screentime_work_mapping = {'0-2 Stunden': 1, '2-4 Stunden': 2, '4-6 Stunden': 3, '6-8 Stunden': 5, '> 8 Stunden': 5}
        #screentime_work = screentime_work_mapping.get(answers.get('Wie viel Zeit am Tag verbringst du im Büro/Ausbildung vor dem Bildschirm?', ''), 0)


        #screentime_private_mapping = {'0-1 Stunde': 5, '1-2 Stunden': 4, '2-3 Stunden': 3, '3-4 Stunden': 2, '> 4 Stunden': 1}
        #screentime_private = screentime_private_mapping.get(answers.get('Wie viel Zeit am Tag verbringst du in der Freizeit vor dem Bildschirm?', ''), 0)


        color_puzzle = int(answers.get('Welche Zahl gehört unter die letzte Abbildung?', 0))
        if color_puzzle == 2002:
            color_puzzle = 5
        else:
            color_puzzle = 0

        numerical_series = answers.get('Ergänze die Zahlenreihenfolge 3,6,18,21,?')
        if numerical_series == '63':
            numerical_series = 5
        else:
            numerical_series = 0

        form_quiz = answers.get('Welche Form kommt an die Stelle vom ?')
        if form_quiz == 'choice 3':
            form_quiz = 5
        else:
            form_quiz = 0

        word_allocation = answers.get('Quark : Milch / Brot : ?')
        if word_allocation == 'Mehl':
            word_allocation = 5
        else:
            word_allocation = 0

        return forgetfulness, concentration, color_puzzle, numerical_series, form_quiz, word_allocation

    def calculate_cognition_score(self):
        """
        Calculate the cognition score based on the converted answers.

        :return: The calculated cognition score as a float
        """
        forgetfulness, concentration, color_puzzle, numerical_series, form_quiz, word_allocation = self.cognition
        total_points = forgetfulness + concentration + color_puzzle + numerical_series + form_quiz + word_allocation
        score = total_points / 30 * 100
        return score

    def report(self):
        """
        Generate a report based on the cognition assessment score.

        :return: A string representation of the cognition assessment score
        """
        score = self.calculate_cognition_score()
        return f"{score:.2f}"

if __name__ == "__main__":
    answers = {
        'Wie würdest du deine Vergesslichkeit einstufen?': '1',
        'Welche Zahl gehört unter die letzte Abbildung? ': '2002',
        'Ergänze die Zahlenreihenfolge 3,6,18,21,?': '63',
        'Welche Form kommt an die Stelle vom ?': 'choice 3',
        'Quark : Milch / Brot : ?': 'Mehl'
    }
    cognition = CognitionAssessment(answers)
    print(cognition.report())
