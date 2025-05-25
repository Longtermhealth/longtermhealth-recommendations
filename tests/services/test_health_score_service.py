"""Tests for HealthScoreService"""

import pytest
import math
from unittest.mock import patch

from src.services.health_score_service import HealthScoreService
from src.models.health_score import PillarEnum, RatingEnum
from src.models.routine_stats import PillarCompletionStats, RoutineCompletion, CompletionStatistic
from src.exceptions import ExternalServiceError


class TestHealthScoreService:
    """Test HealthScoreService"""
    
    @pytest.fixture
    def service(self):
        return HealthScoreService()
    
    def test_get_initial_scores_success(self, service, production_host, initial_health_scores, 
                                      mock_external_apis):
        """Test getting initial health scores"""
        scores = service.get_initial_scores(494, production_host)
        
        assert scores == initial_health_scores
        mock_external_apis['strapi']['get_scores'].assert_called_once_with(494, production_host)
    
    def test_get_initial_scores_failure(self, service, production_host, mock_external_apis):
        """Test handling Strapi failure"""
        mock_external_apis['strapi']['get_scores'].side_effect = Exception("API error")
        
        with pytest.raises(ExternalServiceError) as exc_info:
            service.get_initial_scores(494, production_host)
        
        assert "Failed to fetch health scores" in str(exc_info.value)
    
    def test_calculate_updated_scores(self, service, initial_health_scores):
        """Test calculating updated health scores"""
        # Create completion stats
        completion_stats = [
            PillarCompletionStats(
                pillar_enum="STRESS",
                routine_completions=[
                    RoutineCompletion(
                        routine_id=1,
                        display_name="Meditation",
                        completion_statistics=[
                            CompletionStatistic(
                                completion_rate=4,
                                completion_rate_period_unit="MONTH",
                                period_sequence_no=1
                            )
                        ]
                    )
                ]
            )
        ]
        
        # Create action plan with scheduled routines
        action_plan = {
            "pillarCompletionStats": [
                {
                    "pillarEnum": "STRESS",
                    "routineCompletionStats": [
                        {"routineId": 1, "displayName": "Meditation"}
                    ]
                }
            ]
        }
        
        result = service.calculate_updated_scores(
            account_id=494,
            action_plan=action_plan,
            completion_stats=completion_stats,
            initial_scores=initial_health_scores
        )
        
        assert result.account_id == 494
        assert len(result.pillar_scores) == 1
        
        stress_score = result.pillar_scores[0]
        assert stress_score.pillar_enum == PillarEnum.STRESS
        assert stress_score.score > initial_health_scores["STRESS"]  # Should increase
        assert stress_score.delta > 0
        assert stress_score.rating_enum in [RatingEnum.AKTIONSBEFARF, RatingEnum.AUSBAUFAEHIG, RatingEnum.OPTIMAL]
    
    def test_score_calculation_formula(self, service):
        """Test the score calculation formula matches original"""
        # Test with known values
        init_score = 50.0
        completed_count = 4
        scheduled_total = 5
        not_completed_count = scheduled_total - completed_count
        
        # Calculate using service constants
        dampening = (100 - init_score) / 90.0
        delta_completed = 10 * dampening * (1 - math.exp(-service.K * completed_count))
        delta_not = 10 * dampening * (1 - math.exp(-service.K * not_completed_count))
        final_delta = delta_completed - (delta_not / 3.0)
        new_score = init_score + final_delta
        
        # Verify calculation
        assert dampening == pytest.approx((100 - 50) / 90.0)
        assert service.K == 0.025  # Matches original k value
        assert new_score > init_score  # Completing more than not completing should increase score
    
    def test_get_rating(self, service):
        """Test rating assignment"""
        assert service._get_rating(39.9) == RatingEnum.AKTIONSBEFARF
        assert service._get_rating(40.0) == RatingEnum.AUSBAUFAEHIG
        assert service._get_rating(63.9) == RatingEnum.AUSBAUFAEHIG
        assert service._get_rating(64.0) == RatingEnum.OPTIMAL
        assert service._get_rating(100.0) == RatingEnum.OPTIMAL
    
    def test_create_health_scores_structure(self, service, initial_health_scores):
        """Test creating health scores structure"""
        result = service.create_health_scores_structure(494, initial_health_scores)
        
        assert result.account_id == 494
        assert len(result.pillar_scores) == 7
        assert result.total_score == pytest.approx(sum(initial_health_scores.values()) / 7)
        
        # Check structure matches original
        result_dict = result.to_dict()
        assert result_dict['data']['accountId'] == 494
        assert result_dict['data']['totalScore'] == int(result.total_score)
        assert len(result_dict['data']['pillarScores']) == 7
        
        # Check each pillar
        for pillar_data in result_dict['data']['pillarScores']:
            assert 'pillar' in pillar_data
            assert 'score' in pillar_data
            assert 'scoreInterpretation' in pillar_data
            assert 'rating' in pillar_data
    
    def test_score_interpretations(self, service):
        """Test that all pillars have interpretations"""
        for pillar in PillarEnum:
            for rating in RatingEnum:
                interpretation = service._get_interpretation(pillar, rating)
                assert interpretation != "No interpretation available."
                assert len(interpretation) > 0
    
    def test_handle_unknown_pillar(self, service, initial_health_scores):
        """Test handling unknown pillar in scores"""
        scores = initial_health_scores.copy()
        scores["UNKNOWN_PILLAR"] = 50.0
        
        result = service.create_health_scores_structure(494, scores)
        
        # Should skip unknown pillar
        assert len(result.pillar_scores) == 7  # Only valid pillars
    
    def test_completions_by_pillar_extraction(self, service):
        """Test extracting completions by pillar"""
        completion_stats = [
            PillarCompletionStats(
                pillar_enum="STRESS",
                routine_completions=[
                    RoutineCompletion(
                        completion_statistics=[
                            CompletionStatistic(
                                completion_rate=3,
                                completion_rate_period_unit="MONTH",
                                period_sequence_no=1
                            )
                        ]
                    ),
                    RoutineCompletion(
                        completion_statistics=[
                            CompletionStatistic(
                                completion_rate=2,
                                completion_rate_period_unit="MONTH",
                                period_sequence_no=1
                            )
                        ]
                    )
                ]
            )
        ]
        
        result = service._get_completions_by_pillar(completion_stats)
        
        assert result["STRESS"]["completed"] == 5  # 3 + 2