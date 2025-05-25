"""Analytics module for processing and analyzing user completion data."""

from .event_processor import EventProcessor
from .metrics_calculator import MetricsCalculator
from .trend_analyzer import TrendAnalyzer
from .insights_engine import InsightsEngine
from .analytics_service import AnalyticsService

__all__ = ['EventProcessor', 'MetricsCalculator', 'TrendAnalyzer', 'InsightsEngine', 'AnalyticsService']