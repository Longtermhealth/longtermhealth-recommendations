"""Test that all imports work correctly"""

import pytest


def test_api_imports():
    """Test API module imports"""
    from src.api import create_app
    from src.api.routes import health, webhook, event
    from src.api.middleware.error_handler import register_error_handlers
    
    # Should be able to create app
    app = create_app('testing')
    assert app is not None


def test_service_imports():
    """Test service module imports"""
    from src.services.action_plan_service import ActionPlanService
    from src.services.health_score_service import HealthScoreService
    from src.services.routine_service import RoutineService
    
    # Should be able to instantiate
    assert ActionPlanService() is not None
    assert HealthScoreService() is not None
    assert RoutineService() is not None


def test_model_imports():
    """Test model module imports"""
    from src.models.action_plan import ActionPlan, Routine, WebhookPayload
    from src.models.health_score import HealthScores, PillarScore, PillarEnum, RatingEnum
    from src.models.routine_stats import RoutineCompletion, CompletionStatistic, PillarCompletionStats
    
    # Should be able to create instances
    assert ActionPlan() is not None
    assert Routine() is not None
    assert WebhookPayload() is not None


def test_utils_imports():
    """Test utils module imports"""
    from src.utils.logger import setup_logging, get_logger
    from src.utils.typeform_api import get_responses, trigger_followup
    from src.utils.strapi_api import strapi_get_old_action_plan
    
    # Should be importable
    assert setup_logging is not None
    assert get_responses is not None


def test_exception_imports():
    """Test exception imports"""
    from src.exceptions import (
        BusinessError, ValidationError, NotFoundError, 
        ExternalServiceError, ConfigurationError
    )
    
    # Should be able to raise
    with pytest.raises(ValidationError):
        raise ValidationError("test")


def test_config_imports():
    """Test configuration imports"""
    from src.config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
    
    # Should have required attributes
    assert hasattr(Config, 'TYPEFORM_API_KEY')
    assert hasattr(Config, 'STRAPI_API_KEY')
    assert hasattr(DevelopmentConfig, 'DEBUG')
    assert DevelopmentConfig.DEBUG is True
    assert ProductionConfig.DEBUG is False