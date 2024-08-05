# rule_based_system/assessments/gratitude_assessment.py


from .base_assessment import BaseAssessment

def convert_gratitude(answers):
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

class GratitudeAssessment(BaseAssessment):
    def __init__(self, answers):
        """
        Initialize the GratitudeAssessment with the provided answers.

        :param answers: A dictionary containing the answers to the gratitude assessment questions
        """
        super().__init__()
        self.gratitude = convert_gratitude(answers)

    def calculate_gratitude_score(self):
        """
        Calculate the gratitude score based on the converted answers.

        :return: The calculated gratitude score as a float
        """
        gratitude = self.gratitude.copy()
        if gratitude != [0, 0, 0, 0, 0, 0]:
            if len(gratitude) >= 3:
                gratitude[2] = 6 - gratitude[2]
                if len(gratitude) >= 6:
                    gratitude[5] = 6 - gratitude[5]
            total_gratitude_score = sum(gratitude)
            min_score = 5
            max_score = 30
            normalized_score = ((total_gratitude_score - min_score) / (max_score - min_score)) * 100
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

if __name__ == "__main__":
    answers = {
        'Ich habe so viel im Leben, wofür ich dankbar sein kann.': 5,
        'Wenn ich alles auflisten müsste, wofür ich dankbar bin, wäre es eine sehr lange Liste.': 5,
        'Wenn ich die Welt betrachte, sehe ich nicht viel, wofür ich dankbar sein könnte.': 1,
        'Ich bin vielen verschiedenen Menschen dankbar.': 5,
        'Je älter ich werde, desto mehr schätze ich die Menschen, Ereignisse und Situationen, die Teil meiner Lebensgeschichte waren.': 5,
        'Es können lange Zeiträume vergehen, bevor ich etwas oder jemandem dankbar bin.': 1
    }
    gratitude = GratitudeAssessment(answers=answers)
    print(gratitude.report())
