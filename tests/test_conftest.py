"""Comprehensive test fixtures for refactored app testing"""

import pytest
import json
from unittest.mock import Mock, patch
from datetime import datetime

from src.api import create_app
from src.models.action_plan import ActionPlan, Routine
from src.models.health_score import HealthScores, PillarScore, PillarEnum, RatingEnum


@pytest.fixture
def app():
    """Create Flask app for testing"""
    app = create_app('testing')
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create Flask test client"""
    return app.test_client()


@pytest.fixture
def production_host():
    """Production host string"""
    return "lthrecommendation-hpdphma0ehf3bacn.germanywestcentral-01.azurewebsites.net"


@pytest.fixture
def dev_host():
    """Development host string"""
    return "lthrecommendation-dev-g2g0hmcqdtbpg8dw.germanywestcentral-01.azurewebsites.net"


@pytest.fixture
def complete_typeform_answers():
    """Complete set of Typeform answers matching production data"""
    return {
        'accountid': '494',
        'Welches Geschlecht ist in Ihren Dokumenten angegeben?': 'Männlich',
        'Geburtsjahr': 1990,
        'Was ist deine Körpergröße (in cm)?': 190,
        'Wie viel wiegst du (in kg)?': 90,
        'Rauchst du?': False,
        'Wie oft in der Woche treibst du eine Cardio-Sportart?': 5,
        'Wie schätzt du deine Kraft ein?': 5,
        'Wie schätzt du deine Beweglichkeit ein?': 5,
        'Wie aktiv bist du im Alltag?': 5,
        'Welcher Ernährungsstil trifft bei dir am ehesten zu?': 'Keine tierischen Produkte (vegan)',
        'Wie viel zuckerhaltige Produkte nimmst du zu dir?': 5,
        'Wie häufig nimmst du Fertiggerichte zu dir?': 5,
        'Wie viel Vollkorn nimmst du zu dir?': 5,
        'Praktizierst du Intervallfasten und auf welche Art?': '12:12 (täglich 12 Stunden fasten)',
        'Wie viele Gläser Flüssigkeit (200ml) nimmst du ca. täglich zu dir?': '10-12',
        'Wie viel Alkohol trinkst du in der Woche?': '10-12',
        'Wie viele Stunden schläfst du im Durchschnitt pro Nacht?': '> 12',
        'Wie ist deine Schlafqualität?': 'Ich habe schwere Schlafprobleme',
        'Fühlst du dich tagsüber müde?': 2,
        'Wie viel Zeit verbringst du morgens draußen?': '11-20 min',
        'Wie viel Zeit verbringst du abends draußen?': '> 20 min',
        'Wie oft unternimmst du etwas mit anderen Menschen?': 'Weniger als 2x pro Monat',
        'Bist du sozial engagiert?': 'Freiwilligenarbeit',
        'Fühlst du dich einsam?': 3,
        'Leidest du aktuell unter Stress?': 3,
        'Ich versuche, die positive Seite von Stress und Druck zu sehen.': 4,
        'Ich tue alles, damit Stress erst gar nicht entsteht.': 3,
        'Wenn ich unter Druck gerate, habe ich Menschen, die mir helfen.': 4,
        'Wenn mir alles zu viel wird, neige ich zu ungesunden Verhaltensmustern, wie Alkohol, Tabak oder Frustessen.': 3,
        'Machst du aktuell Übungen zur Stressprävention?': 'Habe ich schon mal',
        'Ich liebe mich so, wie ich bin.': 5,
        'Ich habe so viel im Leben, wofür ich dankbar sein kann.': 5,
        'Jeder Tag ist eine Chance, es besser zu machen.': 5,
        'Im Nachhinein bin ich für jede Niederlage dankbar, denn sie haben mich weitergebracht.': 5,
        'Ich bin vielen verschiedenen Menschen dankbar.': 5,
        'Wie würdest du deine Vergesslichkeit einstufen?': 5,
        'Wie gut ist dein Konzentrationsvermögen?': 5,
        'Nimmst du dir im Alltag Zeit, noch neue Dinge/Fähigkeiten zu erlernen?': 5,
        'Wie viel Zeit am Tag verbringst du im Büro/Ausbildung vor dem Bildschirm?': '> 8 Stunden',
        'Wie viel Zeit am Tag verbringst du in der Freizeit vor dem Bildschirm?': '> 4 Stunden',
        'Wie viel Zeit möchtest du am Tag ungefähr in deine Gesundheit investieren?': '> 60 Minuten'
    }


@pytest.fixture
def old_action_plan_response():
    """Response from Strapi for old action plan"""
    return {
        "data": [{
            "attributes": {
                "actionPlanUniqueId": "test-plan-123",
                "accountId": 494,
                "periodInDays": 28,
                "gender": "MÄNNLICH",
                "totalDailyTimeInMins": 60,
                "routines": [
                    {
                        "routineUniqueId": 1,
                        "routineId": 1,
                        "displayName": "Morning Meditation",
                        "scheduleDays": [1, 3, 5],
                        "pillar": {"pillarEnum": "STRESS"}
                    },
                    {
                        "routineUniqueId": 2,
                        "routineId": 2,
                        "displayName": "Evening Walk",
                        "scheduleDays": [2, 4, 6],
                        "pillar": {"pillarEnum": "MOVEMENT"}
                    }
                ]
            }
        }],
        "routines": [
            {
                "routineUniqueId": 1,
                "displayName": "Morning Meditation"
            },
            {
                "routineUniqueId": 2,
                "displayName": "Evening Walk"
            }
        ]
    }


@pytest.fixture
def recalculate_event_payload():
    """RECALCULATE_ACTION_PLAN event payload"""
    return {
        "eventEnum": "RECALCULATE_ACTION_PLAN",
        "eventPayload": json.dumps({
            "actionPlanUniqueId": "test-plan-123",
            "accountId": 494,
            "pillarCompletionStats": [
                {
                    "pillarEnum": "STRESS",
                    "routineCompletionStats": [
                        {
                            "routineId": 1,
                            "routineUniqueId": 1,
                            "displayName": "Morning Meditation",
                            "completionStatistics": [
                                {
                                    "completionRate": 3,
                                    "completionRatePeriodUnit": "WEEK",
                                    "periodSequenceNo": 1
                                },
                                {
                                    "completionRate": 4,
                                    "completionRatePeriodUnit": "MONTH",
                                    "periodSequenceNo": 1
                                }
                            ]
                        }
                    ]
                },
                {
                    "pillarEnum": "MOVEMENT",
                    "routineCompletionStats": [
                        {
                            "routineId": 2,
                            "routineUniqueId": 2,
                            "displayName": "Evening Walk",
                            "completionStatistics": [
                                {
                                    "completionRate": 2,
                                    "completionRatePeriodUnit": "WEEK",
                                    "periodSequenceNo": 1
                                }
                            ]
                        }
                    ]
                }
            ]
        })
    }


@pytest.fixture
def renew_event_payload():
    """RENEW_ACTION_PLAN event payload"""
    return {
        "eventEnum": "RENEW_ACTION_PLAN",
        "eventPayload": json.dumps({
            "actionPlanUniqueId": "test-plan-123",
            "accountId": 494,
            "changeLog": [
                {
                    "eventEnum": "ROUTINE_SCHEDULE_CHANGE",
                    "changeTarget": "ROUTINE",
                    "targetId": "1",
                    "eventDate": "2025-01-25T10:00:00Z",
                    "eventDetails": {"scheduleCategory": "WEEKLY_ROUTINE"},
                    "changes": [
                        {
                            "changedProperty": "SCHEDULE_DAYS",
                            "newValue": "[1,2,3,4,5]"
                        }
                    ]
                }
            ]
        })
    }


@pytest.fixture
def initial_health_scores():
    """Initial health scores from Strapi"""
    return {
        "MOVEMENT": 50.0,
        "NUTRITION": 50.0,
        "SLEEP": 50.0,
        "SOCIAL_ENGAGEMENT": 50.0,
        "STRESS": 50.0,
        "GRATITUDE": 50.0,
        "COGNITIVE_ENHANCEMENT": 50.0
    }


@pytest.fixture
def mock_external_apis(old_action_plan_response, initial_health_scores):
    """Mock all external API calls"""
    with patch('src.utils.strapi_api.strapi_get_old_action_plan') as mock_get_plan, \
         patch('src.utils.strapi_api.strapi_post_action_plan') as mock_post_plan, \
         patch('src.utils.strapi_api.strapi_get_health_scores') as mock_get_scores, \
         patch('src.utils.strapi_api.strapi_get_action_plan') as mock_get_action_plan, \
         patch('src.utils.typeform_api.get_responses') as mock_responses, \
         patch('src.utils.typeform_api.get_field_mapping') as mock_mapping, \
         patch('src.utils.typeform_api.trigger_followup') as mock_followup, \
         patch('src.scheduling.scheduler.main') as mock_scheduler:
        
        # Configure Strapi mocks
        mock_get_plan.return_value = old_action_plan_response
        mock_get_action_plan.return_value = old_action_plan_response
        mock_post_plan.return_value = {"success": True}
        mock_get_scores.return_value = initial_health_scores
        
        # Configure Typeform mocks
        mock_responses.return_value = {
            "items": [{
                "submitted_at": "2025-01-25T10:00:00Z",
                "hidden": {"accountid": "494"},
                "answers": []
            }]
        }
        mock_mapping.return_value = {}
        mock_followup.return_value = None
        
        # Configure scheduler mock
        mock_scheduler.return_value = {
            "data": {
                "actionPlanUniqueId": "new-plan-123",
                "accountId": 494,
                "periodInDays": 28,
                "gender": "MÄNNLICH",
                "totalDailyTimeInMins": 60,
                "routines": []
            }
        }
        
        yield {
            'strapi': {
                'get_plan': mock_get_plan,
                'get_action_plan': mock_get_action_plan,
                'post_plan': mock_post_plan,
                'get_scores': mock_get_scores
            },
            'typeform': {
                'get_responses': mock_responses,
                'get_field_mapping': mock_mapping,
                'trigger_followup': mock_followup
            },
            'scheduler': mock_scheduler
        }