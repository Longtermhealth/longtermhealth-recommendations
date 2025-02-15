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


def calculate_nutrition_score(answers, bmi_value):
    """
    Calculate a nutrition score based on answers and BMI, applying dynamic weighting.

    The overall score is a weighted sum of each component's score. For dynamic components,
    the weight increases when the score is lower.
    """
    component_scores = {}
    effective_weights = {}

    for key in ANSWER_KEY_MAPPING:
        raw_value = answers.get(ANSWER_KEY_MAPPING[key])
        score = WEIGHTS_CONFIG[key]['score_func'](raw_value)
        component_scores[key] = score
        print(f"[DEBUG] Component '{key}': raw value = {raw_value}, score = {score}")

    bmi_score = WEIGHTS_CONFIG['bmi']['score_func'](bmi_value)
    component_scores['bmi'] = bmi_score
    print(f"[DEBUG] Component 'bmi': raw value = {bmi_value}, score = {bmi_score}")

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
    print(f"[DEBUG] Weighted sum of scores: {weighted_sum:.2f}")

    max_weighted_sum = sum(effective_weights[key] * 5 for key in effective_weights)
    print(f"[DEBUG] Maximum possible weighted sum: {max_weighted_sum:.2f}")

    normalized_score = weighted_sum / max_weighted_sum * 80
    print(f"[DEBUG] Normalized score (0-80 scale): {normalized_score:.2f}")
    return normalized_score

