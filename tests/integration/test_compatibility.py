"""Test compatibility between old and new implementations"""

import pytest
import json
from unittest.mock import patch, Mock
import sys
import os


# Try to import old app for comparison (if available)
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from app import (
        compute_routine_completion, 
        get_insights,
        calculate_first_month_update_from_pretty_final,
        compute_scheduled_by_pillar,
        extract_pretty_completions
    )
    OLD_APP_AVAILABLE = True
except ImportError:
    OLD_APP_AVAILABLE = False


class TestCompatibility:
    """Test that new implementation produces same results as old"""
    
    @pytest.mark.skipif(not OLD_APP_AVAILABLE, reason="Old app.py not available")
    def test_routine_completion_calculation(self):
        """Test routine completion calculation matches"""
        from src.services.routine_service import RoutineService
        
        # Test data
        routine_data = {
            "routineId": 1,
            "displayName": "Test Routine",
            "completionStatistics": [
                {
                    "completionRate": 3,
                    "completionRatePeriodUnit": "WEEK",
                    "periodSequenceNo": 1
                },
                {
                    "completionRate": 4,
                    "completionRatePeriodUnit": "WEEK", 
                    "periodSequenceNo": 2
                }
            ]
        }
        
        # Old implementation
        old_result = compute_routine_completion(routine_data)
        
        # New implementation
        service = RoutineService()
        new_result = service.calculate_routine_completion(routine_data)
        
        # Compare results
        assert new_result['scheduled'] == old_result['scheduled']
        assert new_result['completed'] == old_result['completed']
        assert new_result['percentage'] == pytest.approx(old_result['percentage'])
    
    @pytest.mark.skipif(not OLD_APP_AVAILABLE, reason="Old app.py not available")
    def test_insights_generation(self):
        """Test insights generation matches"""
        from src.services.routine_service import RoutineService
        
        # Test data
        payload = {
            "pillarCompletionStats": [
                {
                    "pillarEnum": "STRESS",
                    "routineCompletionStats": [
                        {
                            "routineId": 1,
                            "displayName": "Meditation",
                            "completionStatistics": [
                                {"completionRate": 3, "completionRatePeriodUnit": "WEEK", "periodSequenceNo": 1}
                            ]
                        }
                    ]
                }
            ]
        }
        
        # Old implementation
        old_insights = get_insights(payload)
        
        # New implementation
        service = RoutineService()
        new_insights = service.get_pillar_insights(payload['pillarCompletionStats'])
        
        # Compare structure
        assert set(new_insights.keys()) == set(old_insights.keys())
        
        for pillar in old_insights:
            assert new_insights[pillar]['numRoutines'] == old_insights[pillar]['numRoutines']
    
    def test_health_score_structure(self):
        """Test health score response structure matches original"""
        from src.services.health_score_service import HealthScoreService
        
        service = HealthScoreService()
        scores = {
            "MOVEMENT": 75.5,
            "NUTRITION": 82.3,
            "SLEEP": 45.2,
            "SOCIAL_ENGAGEMENT": 60.0,
            "STRESS": 55.8,
            "GRATITUDE": 90.0,
            "COGNITIVE_ENHANCEMENT": 70.5
        }
        
        result = service.create_health_scores_structure(494, scores)
        result_dict = result.to_dict()
        
        # Verify structure matches original
        assert 'data' in result_dict
        assert 'totalScore' in result_dict['data']
        assert 'accountId' in result_dict['data']
        assert 'pillarScores' in result_dict['data']
        
        # Verify pillar structure
        for pillar_data in result_dict['data']['pillarScores']:
            assert 'pillar' in pillar_data
            assert 'pillarEnum' in pillar_data['pillar']
            assert 'displayName' in pillar_data['pillar']
            assert 'score' in pillar_data
            assert 'scoreInterpretation' in pillar_data
            assert 'rating' in pillar_data
            assert 'ratingEnum' in pillar_data['rating']
            assert 'displayName' in pillar_data['rating']
            
            # Score should be formatted as string with 2 decimals
            assert isinstance(pillar_data['score'], str)
            assert pillar_data['score'].count('.') == 1
            assert len(pillar_data['score'].split('.')[1]) == 2
    
    def test_action_plan_structure(self):
        """Test action plan response structure matches original"""
        from src.models.action_plan import ActionPlan, Routine
        
        plan = ActionPlan(
            action_plan_unique_id="test-123",
            account_id=494,
            period_in_days=28,
            gender="männlich",
            total_daily_time_in_mins=60,
            routines=[
                Routine(
                    routine_unique_id=1,
                    display_name="Test",
                    schedule_days=[1, 2, 3]
                )
            ]
        )
        
        result = plan.to_dict()
        
        # Verify structure
        assert 'data' in result
        data = result['data']
        assert data['actionPlanUniqueId'] == "test-123"
        assert data['accountId'] == 494
        assert data['periodInDays'] == 28
        assert data['gender'] == "MÄNNLICH"  # Should be uppercase
        assert data['totalDailyTimeInMins'] == 60
        assert 'routines' in data
        assert len(data['routines']) == 1
        
        # Verify routine structure
        routine = data['routines'][0]
        assert routine['routineUniqueId'] == 1
        assert routine['displayName'] == "Test"
        assert routine['scheduleDays'] == [1, 2, 3]