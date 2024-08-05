# rule_based_system/scheduling/scheduler.py

import math
import random
from collections import defaultdict
from rules.rule_evaluation import apply_rules

WEIGHTINGS = {
    "Movement&Exercise": 0.25,
    "HealthfulNutrition": 0.25,
    "RestorativeSleep": 0.15,
    "SocialEngagement": 0.15,
    "StressManagement": 0.10,
    "Gratitude&Reflection": 0.05,
    "Cognition": 0.05
}

THRESHOLDS = {
    "Movement&Exercise": 100,
    "HealthfulNutrition": 100,
    "RestorativeSleep": 100,
    "SocialEngagement": 100,
    "StressManagement": 100,
    "Gratitude&Reflection": 100,
    "Cognition": 100
}

def filter_routines_by_time_and_rules(routines, daily_time_limit, responses, rules):
    filtered_routines = []
    print('daily_time', daily_time_limit)
    for routine in routines:
        if routine['duration'] <= daily_time_limit:
            if apply_rules(routine['rules'], responses, rules):
                filtered_routines.append(routine)
            else:
                print(f"Routine {routine['name']} excluded due to rules.")
        else:
            print(f"Routine {routine['name']} excluded due to duration {routine['duration']} > {daily_time_limit} minutes.")
    return filtered_routines


def calculate_daily_allocations_by_weightings(daily_time, weightings):
    return {pillar: daily_time * weight for pillar, weight in weightings.items()}




def calculate_daily_allocations_by_scores(daily_time, scores, thresholds):
    inverted_scores = {pillar: max(0, thresholds[pillar] - score) for pillar, score in scores.items()}
    total_inverted_score = sum(inverted_scores.values())
    if total_inverted_score == 0:
        return {pillar: 0 for pillar in scores.keys()}

    allocations = {pillar: daily_time * (inverted_score / total_inverted_score) for pillar, inverted_score in
                   inverted_scores.items()}

    #Round up allocations less than 1
    rounded_allocations = {pillar: math.ceil(allocation) if allocation < 1 else round(allocation) for pillar, allocation
                           in allocations.items()}

    #Calculate the difference
    total_rounded_allocation = sum(rounded_allocations.values())
    difference = daily_time - total_rounded_allocation

    #Adjust allocations to match daily_time
    while difference != 0:
        for pillar in rounded_allocations.keys():
            if difference == 0:
                break
            if difference > 0:
                rounded_allocations[pillar] += 1
                difference -= 1
            elif difference < 0 and rounded_allocations[pillar] > 0:
                rounded_allocations[pillar] -= 1
                difference += 1
    return rounded_allocations


def fill_day_with_routines_by_pillar(routines, daily_allocations, remaining_time):
    schedule = []
    routines_by_pillar = defaultdict(list)
    for routine in routines:
        routines_by_pillar[routine["pillar"]].append(routine)
    for pillar, allocation in daily_allocations.items():
        available_time = allocation
        random.shuffle(routines_by_pillar[pillar])
        for routine in routines_by_pillar[pillar]:
            if routine['duration'] <= available_time:
                schedule.append(routine)
                available_time -= routine['duration']
                remaining_time -= routine['duration']
                if available_time <= 0:
                    break
    return schedule


def generate_schedule(responses, scores, routines, rules, score_weight=0.7):
    daily_time = responses.get('VIELEN DANK!\nWir erstellen nun deine erste individuelle Routine. Dazu müssen wir nur noch wissen, wie viel Zeit du täglich für deine langfristige Gesundheit investieren kannst.', 0)

    # Calculate allocations by scores
    allocations_by_scores = calculate_daily_allocations_by_scores(daily_time, scores, THRESHOLDS)

    # Calculate allocations by weightings
    allocations_by_weightings = calculate_daily_allocations_by_weightings(daily_time, WEIGHTINGS)

    # Combine the two allocation methods based on the score_weight
    daily_allocations = {
        pillar: (score_weight * allocations_by_scores[pillar] + (1 - score_weight) * allocations_by_weightings[pillar])
        for pillar in allocations_by_scores
    }

    filtered_routines = filter_routines_by_time_and_rules(routines, daily_time, responses, rules)
    schedule = {day: [] for day in range(1, 31)}
    for day in range(1, 31):
        remaining_time = daily_time
        schedule[day] = fill_day_with_routines_by_pillar(filtered_routines, daily_allocations, remaining_time)

    return schedule


def display_monthly_plan(schedule):
    results = []
    pillar_totals = defaultdict(int)
    total_month_time = 0

    # Calculate the total time for the entire month and pillar totals
    for day in range(1, 31):
        routines = schedule.get(day, [])
        for routine in routines:
            total_month_time += routine['duration']
            pillar_totals[routine["pillar"]] += routine['duration']

    # Print and append pillar totals
    pillar_totals_header = "Distribution Pillar:"
    print(pillar_totals_header)
    results.append(pillar_totals_header)
    for pillar, total in pillar_totals.items():
        average_daily = total / 30
        percentage = (total / total_month_time) * 100 if total_month_time else 0
        pillar_info = f"{pillar}: {total} minutes ({average_daily:.2f} minutes/day, {percentage:.2f}%)"
        results.append(pillar_info)
        print(pillar_info)

    # Calculate and print the day-by-day schedule
    for day in range(1, 31):
        routines = schedule.get(day, [])
        total_time = sum(routine['duration'] for routine in routines)
        routine_ids = [routine['id'] for routine in routines]
        day_info = f"Day {day}: Total time {total_time} minutes, Routines: {routine_ids}"
        results.append(day_info)
        print(day_info)

    return results