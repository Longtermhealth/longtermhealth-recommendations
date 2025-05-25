"""Pytest configuration and fixtures for the test suite"""

import pytest
import os
import sys

# Add src to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

@pytest.fixture
def sample_nutrition_answers():
    """Sample nutrition assessment answers for testing"""
    return {
        'Wie viel Liter Wasser trinkst du am Tag?': '3',
        'Wie viele Obst- und Gemüseportionen isst du am Tag?': '5',
        'Wie viele zuckerhaltige Getränke oder Süßigkeiten konsumierst du pro Tag?': '1',
        'Wie oft in der Woche isst du ein qualitativ hochwertiges Stück Fleisch?': '2',
        'Wie sieht es mit deinem Body-Mass-Index aus?': '2',
        'Wie oft greifst du zu Fast Food und Fertiggerichten?': '1'
    }

@pytest.fixture
def sample_exercise_answers():
    """Sample exercise assessment answers for testing"""
    return {
        'Wie schätzt du deine Beweglichkeit ein?': '3',
        'Wie aktiv bist du im Alltag?': '3',
        'Wie oft in der Woche treibst du eine Cardio-Sportart?': '3',
        'Wie schätzt du deine Kraft ein?': '3'
    }

@pytest.fixture
def sample_gratitude_answers():
    """Sample gratitude assessment answers for testing"""
    return {
        'Ich liebe mich so, wie ich bin.': '4',
        'Ich habe so viel im Leben, wofür ich dankbar sein kann.': '5',
        'Jeder Tag ist eine Chance, es besser zu machen.': '4',
        'Im Nachhinein bin ich für jede Niederlage dankbar, denn sie haben mich weitergebracht.': '4',
        'Ich bin vielen verschiedenen Menschen dankbar.': '5'
    }

@pytest.fixture
def sample_health_assessment_data():
    """Complete sample data for health assessment"""
    return {
        'exercise': {
            'Wie schätzt du deine Beweglichkeit ein?': '3',
            'Wie aktiv bist du im Alltag?': '3',
            'Wie oft in der Woche treibst du eine Cardio-Sportart?': '3',
            'Wie schätzt du deine Kraft ein?': '3'
        },
        'nutrition': {
            'Wie viel Liter Wasser trinkst du am Tag?': '3',
            'Wie viele Obst- und Gemüseportionen isst du am Tag?': '5',
            'Wie viele zuckerhaltige Getränke oder Süßigkeiten konsumierst du pro Tag?': '1',
            'Wie oft in der Woche isst du ein qualitativ hochwertiges Stück Fleisch?': '2',
            'Wie sieht es mit deinem Body-Mass-Index aus?': '2',
            'Wie oft greifst du zu Fast Food und Fertiggerichten?': '1'
        },
        'sleep': {
            'Wie ist deine Schlafqualität?': '3',
            'Welche Schlafprobleme hast du?': '2',
            'Wie viele Stunden schläfst du im Durchschnitt pro Nacht?': '7',
            'Fühlst du dich tagsüber müde?': '2',
            'Wie viel Zeit verbringst du morgens draußen?': '2',
            'Wann isst du die letzte Mahlzeit vor dem Schlafengehen?': '3'
        },
        'social_connections': {
            'Wie oft unternimmst du etwas mit anderen Menschen?': '3',
            'Bist du sozial engagiert?': '3',
            'Fühlst du dich einsam?': '2'
        },
        'stress_management': {
            'Leidest du aktuell unter Stress?': '3',
            'Ich versuche, die positive Seite von Stress und Druck zu sehen.': '3',
            'Ich tue alles, damit Stress erst gar nicht entsteht.': '3',
            'Wenn ich unter Druck gerate, habe ich Menschen, die mir helfen.': '4',
            'Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.': '2',
            'Machst du aktuell Übungen zur Stressprävention?': '3'
        },
        'gratitude': {
            'Ich liebe mich so, wie ich bin.': '4',
            'Ich habe so viel im Leben, wofür ich dankbar sein kann.': '5',
            'Jeder Tag ist eine Chance, es besser zu machen.': '4',
            'Im Nachhinein bin ich für jede Niederlage dankbar, denn sie haben mich weitergebracht.': '4',
            'Ich bin vielen verschiedenen Menschen dankbar.': '5'
        },
        'cognition': {
            'Wie würdest du deine Vergesslichkeit einstufen?': '2',
            'Wie gut ist dein Konzentrationsvermögen?': '3',
            'Nimmst du dir im Alltag Zeit, noch neue Dinge/Fähigkeiten zu erlernen?': '3'
        }
    }