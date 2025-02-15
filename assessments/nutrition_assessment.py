# rule_based_system/assessments/nutrition_assessment.py
from assessments.base_assessment import BaseAssessment


WEIGHTS_CONFIG = {
    'sugar': {
        'base_weight': 1,
        'score_func': lambda x: 5 if int(x) == 0 else max(1, min(5, 6 - int(x))),
        'dynamic': True
    },
    'processed': {
        'base_weight': 0.2,
        'score_func': lambda x: 5 if int(x) == 0 else max(1, min(5, 6 - int(x))),
        'dynamic': False
    },
    'whole_grain': {
        'base_weight': 0.2,
        'score_func': lambda x: max(1, min(5, int(x))),
        'dynamic': False
    },
    'fluids': {
        'base_weight': 1,
        'score_func': lambda x: {'0-3': 1, '4-6': 2, '7-9': 3, '10-12': 5, '> 12': 5}.get(x, 1),
        'dynamic': True
    },
    'alcohol': {
        'base_weight': 1,
        'score_func': lambda x: max(1, {'Gar keinen': 5, '1-3': 4, '4-6': 3, '7-9': 2, '10-12': 1, '> 12': 0}.get(x, 1)),
        'dynamic': True
    },
    'bmi': {
        'base_weight': 1,
        'score_func': lambda bmi: (
            1 if bmi < 16 else
            2 if 16 <= bmi < 18 else
            5 if 18 <= bmi < 25 else
            3 if 25 <= bmi < 30 else
            2 if 30 <= bmi < 35 else
            1 if 35 <= bmi < 40 else
            0
        ),
        'dynamic': True
    }
}

ANSWER_KEY_MAPPING = {
    'sugar': 'Wie viel zuckerhaltige Produkte nimmst du zu dir?',
    'processed': 'Wie häufig nimmst du Fertiggerichte zu dir?',
    'whole_grain': 'Wie viel Vollkorn nimmst du zu dir?',
    'fluids': 'Wie viele Gläser Flüssigkeit (200ml) nimmst du ca. täglich zu dir?',
    'alcohol': 'Wie viel Alkohol trinkst du in der Woche?'
}


def calculate_bmi(weight, height_m):
    """
    Calculate BMI given weight (kg) and height (m).
    :raises ValueError: if height_m is not greater than zero.
    """
    if height_m <= 0:
        raise ValueError("Height must be greater than zero.")
    return weight / (height_m ** 2)


class NutritionAssessment(BaseAssessment):
    REQUIRED_KEYS = [
        ANSWER_KEY_MAPPING['sugar'],
        ANSWER_KEY_MAPPING['processed'],
        ANSWER_KEY_MAPPING['whole_grain'],
        ANSWER_KEY_MAPPING['fluids'],
        ANSWER_KEY_MAPPING['alcohol']
    ]

    def __init__(self, answers):
        """
        Initialize the NutritionAssessment with the provided answers.

        :param answers: A dictionary containing the answers to the nutrition assessment questions.
        """
        super().__init__()
        self.validate_answers(answers)
        self.answers = answers

    def validate_answers(self, answers):
        """
        Validate that all required answers are present and that numeric fields are valid.

        :param answers: A dictionary containing the answers for the nutrition assessment.
        :raises ValueError: If any required key is missing or a field is not in the expected format.
        """
        for key in self.REQUIRED_KEYS:
            if key not in answers:
                raise ValueError(f"Missing required key: '{key}' in answers.")

        integer_fields = [
            ANSWER_KEY_MAPPING['sugar'],
            ANSWER_KEY_MAPPING['processed'],
            ANSWER_KEY_MAPPING['whole_grain']
        ]
        for field in integer_fields:
            try:
                int(answers[field])
            except (ValueError, TypeError):
                raise ValueError(f"Value for '{field}' must be an integer, got: {answers[field]}")

    def calculate_nutrition_score(self):
        """
        Calculate a nutrition score based on the new dynamic weighting mechanism,
        using both the assessment answers and BMI calculated from provided data.

        The BMI is calculated using:
            - 'Wie viel wiegst du (in kg)?'
            - 'Was ist deine Körpergröße (in cm)?'

        :return: The calculated nutrition score as a float on a 0-80 scale.
                 Returns 0.0 if BMI data is missing or invalid.
        """
        weight_raw = self.answers.get('Wie viel wiegst du (in kg)?', '')
        height_raw = self.answers.get('Was ist deine Körpergröße (in cm)?', '')

        try:
            weight_str = str(weight_raw).strip()
            height_str = str(height_raw).strip()
            weight = int(weight_str)
            height_cm = int(height_str)
        except (ValueError, AttributeError):
            print("Invalid weight or height data.")
            return 0.0

        if weight > 0 and height_cm > 0:
            height_m = height_cm / 100
            try:
                bmi = calculate_bmi(weight, height_m)
                print(f"[DEBUG] Calculated BMI: {bmi:.2f}")
            except ValueError as e:
                print(f"Error calculating BMI: {e}")
                return 0.0
        else:
            print("Insufficient data to calculate BMI.")
            return 0.0


        component_scores = {}
        effective_weights = {}

        for key in ANSWER_KEY_MAPPING:
            raw_value = self.answers.get(ANSWER_KEY_MAPPING[key])
            score = WEIGHTS_CONFIG[key]['score_func'](raw_value)
            component_scores[key] = score
            print(f"[DEBUG] Component '{key}': raw value = {raw_value}, score = {score}")

        bmi_score = WEIGHTS_CONFIG['bmi']['score_func'](bmi)
        component_scores['bmi'] = bmi_score
        print(f"[DEBUG] Component 'bmi': raw value = {bmi:.2f}, score = {bmi_score}")

        for key, config in WEIGHTS_CONFIG.items():
            base = config['base_weight']
            if config.get('dynamic', False):
                multiplier = (6 - component_scores[key]) / 5
            else:
                multiplier = 1
            effective_weight = base * multiplier
            effective_weights[key] = effective_weight
            print(f"[DEBUG] Effective weight for '{key}': base = {base}, "
            f"score = {component_scores[key]}, multiplier = {multiplier:.2f}, "
            f"effective weight = {effective_weight:.2f}")

        weighted_sum = sum(effective_weights[key] * component_scores[key] for key in component_scores)
        max_weighted_sum = sum(effective_weights[key] * 5 for key in effective_weights)
        normalized_score = weighted_sum / max_weighted_sum * 80
        print(f"[DEBUG] Weighted sum: {weighted_sum:.2f}, Max weighted sum: {max_weighted_sum:.2f}, "
        f"Normalized score: {normalized_score:.2f}")
        return normalized_score

    def report(self):
        """
        Generate a report based on the nutrition assessment score.

        :return: A string representation of the nutrition assessment score.
        """
        score = self.calculate_nutrition_score()
        return f"{score:.2f}"

