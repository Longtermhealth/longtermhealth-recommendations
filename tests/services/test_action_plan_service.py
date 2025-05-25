"""Tests for ActionPlanService"""

import pytest
import uuid
from unittest.mock import patch, Mock

from src.services.action_plan_service import ActionPlanService
from src.models.action_plan import WebhookPayload
from src.exceptions import ValidationError, NotFoundError, ExternalServiceError


class TestActionPlanService:
    """Test ActionPlanService"""
    
    @pytest.fixture
    def service(self):
        return ActionPlanService()
    
    def test_create_new_plan_success(self, service, production_host, mock_external_apis):
        """Test creating a new action plan"""
        result = service.create_new_plan(production_host)
        
        assert result['data']['actionPlanUniqueId'] == 'new-plan-123'
        assert result['data']['accountId'] == 494
        
        # Should call scheduler
        mock_external_apis['scheduler'].assert_called_once_with(production_host)
    
    def test_create_new_plan_failure(self, service, production_host, mock_external_apis):
        """Test handling scheduler failure"""
        mock_external_apis['scheduler'].side_effect = Exception("Scheduler error")
        
        with pytest.raises(ExternalServiceError) as exc_info:
            service.create_new_plan(production_host)
        
        assert "Action Plan Creation" in str(exc_info.value)
    
    def test_recalculate_plan_success(self, service, production_host, 
                                     old_action_plan_response, mock_external_apis):
        """Test recalculating an action plan"""
        payload = WebhookPayload(
            action_plan_unique_id="test-plan-123",
            account_id=494,
            pillar_completion_stats=[
                {
                    "pillarEnum": "STRESS",
                    "routineCompletionStats": [
                        {
                            "routineUniqueId": 1,
                            "displayName": "Morning Meditation",
                            "completionStatistics": []
                        }
                    ]
                }
            ]
        )
        
        result = service.recalculate_plan(payload, production_host)
        
        assert result['actionPlanUniqueId'] == 'test-plan-123'
        assert 'matches' in result
        assert len(result['matches']) == 1
        assert result['matches'][0]['id'] == 1
    
    def test_recalculate_missing_action_plan_id(self, service, production_host):
        """Test recalculate without action plan ID"""
        payload = WebhookPayload(account_id=494)
        
        with pytest.raises(ValidationError) as exc_info:
            service.recalculate_plan(payload, production_host)
        
        assert "Missing actionPlanUniqueId" in str(exc_info.value)
    
    def test_recalculate_missing_account_id(self, service, production_host):
        """Test recalculate without account ID"""
        payload = WebhookPayload(action_plan_unique_id="test-123")
        
        with pytest.raises(ValidationError) as exc_info:
            service.recalculate_plan(payload, production_host)
        
        assert "Missing accountId" in str(exc_info.value)
    
    def test_recalculate_plan_not_found(self, service, production_host, mock_external_apis):
        """Test recalculate when plan doesn't exist"""
        mock_external_apis['strapi']['get_plan'].return_value = None
        
        payload = WebhookPayload(
            action_plan_unique_id="non-existent",
            account_id=494
        )
        
        with pytest.raises(NotFoundError) as exc_info:
            service.recalculate_plan(payload, production_host)
        
        assert "Action Plan" in str(exc_info.value)
    
    def test_renew_plan_success(self, service, production_host, 
                               old_action_plan_response, mock_external_apis):
        """Test renewing an action plan"""
        payload = WebhookPayload(
            action_plan_unique_id="test-plan-123",
            account_id=494,
            change_log=[
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
        )
        
        with patch('uuid.uuid4', return_value='new-uuid-123'):
            result = service.renew_plan(payload, production_host)
        
        assert result['data']['actionPlanUniqueId'] == 'new-uuid-123'
        assert result['data']['previousActionPlanUniqueId'] == 'test-plan-123'
        assert result['data']['accountId'] == 494
        
        # Check schedule was updated
        assert result['data']['routines'][0]['scheduleDays'] == [1, 2, 3, 4, 5]
        
        # Should post to Strapi
        mock_external_apis['strapi']['post_plan'].assert_called_once()
    
    def test_renew_with_invalid_json_days(self, service, production_host, 
                                         old_action_plan_response, mock_external_apis):
        """Test renew with invalid JSON in schedule days"""
        payload = WebhookPayload(
            action_plan_unique_id="test-plan-123",
            account_id=494,
            change_log=[
                {
                    "eventEnum": "ROUTINE_SCHEDULE_CHANGE",
                    "changeTarget": "ROUTINE",
                    "targetId": "1",
                    "eventDate": "2025-01-25T10:00:00Z",
                    "eventDetails": {"scheduleCategory": "WEEKLY_ROUTINE"},
                    "changes": [
                        {
                            "changedProperty": "SCHEDULE_DAYS",
                            "newValue": "135"  # Not valid JSON
                        }
                    ]
                }
            ]
        )
        
        result = service.renew_plan(payload, production_host)
        
        # Should parse digits from string
        assert result['data']['routines'][0]['scheduleDays'] == [1, 3, 5]
    
    def test_get_app_env_production(self, service, production_host):
        """Test environment detection for production"""
        env = service._get_app_env(production_host)
        assert env == "production"
    
    def test_get_app_env_development(self, service, dev_host):
        """Test environment detection for development"""
        env = service._get_app_env(dev_host)
        assert env == "development"