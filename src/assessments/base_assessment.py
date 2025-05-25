# rule_based_system/assessments/base_assessment.py

class BaseAssessment:
    def __init__(self):
        pass

    def calculate_score(self):
        raise NotImplementedError("This method should be overridden by subclasses")

    @staticmethod
    def normalize_score(score, min_score, max_score):
        """
        Normalize the score to a 0-80 scale.

        :param score: The raw score to be normalized
        :param min_score: The minimum possible raw score
        :param max_score: The maximum possible raw score
        :return: The normalized score on a 0-80 scale
        """
        return (((score / 5 * 80) - min_score) / (max_score - min_score)) * 80

    @staticmethod
    def validate_input(data, valid_values):
        """
        Validate the input data against a set of valid values.

        :param data: The input data to be validated
        :param valid_values: A list or set of valid values
        :return: True if the data is valid, False otherwise
        """
        return data in valid_values

    def report(self):
        """
        Generate a report based on the assessment score.
        Subclasses can override this to provide specific report formats.

        :return: A string representation of the assessment report
        """
        score = self.calculate_score()
        return f"Assessment score: {score:.2f}"

class ExampleAssessment(BaseAssessment):
    def __init__(self, example_param):
        super().__init__()
        self.example_param = example_param

    def calculate_score(self):
        raw_score = self.example_param
        return self.normalize_score(raw_score, 0, 80)


if __name__ == "__main__":
    example = ExampleAssessment(5)
    print(example.report())
