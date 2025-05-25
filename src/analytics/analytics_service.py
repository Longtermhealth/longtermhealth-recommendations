"""Main analytics service that integrates all analytics components."""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from .event_processor import EventProcessor
from .metrics_calculator import MetricsCalculator
from .trend_analyzer import TrendAnalyzer
from .insights_engine import InsightsEngine

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Unified analytics service for processing completion events."""
    
    def __init__(self):
        self.event_processor = EventProcessor()
        self.metrics_calculator = MetricsCalculator()
        self.trend_analyzer = TrendAnalyzer()
        self.insights_engine = InsightsEngine()
    
    def process_event(self, event_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a completion event and generate comprehensive analytics.
        
        Args:
            event_payload: Event webhook payload
            
        Returns:
            Complete analytics response including metrics, trends, and insights
        """
        try:
            logger.info(f"Processing analytics event for account {event_payload.get('accountId')}")
            
            # Step 1: Process the raw event
            analytics_data = self.event_processor.process_completion_event(event_payload)
            
            # Step 2: Calculate metrics
            metrics = self.metrics_calculator.calculate_metrics(analytics_data)
            
            # Step 3: Get historical data for trend analysis
            account_id = event_payload.get('accountId')
            historical_metrics = self.metrics_calculator.get_historical_metrics(account_id, days=30)
            historical_metrics.append(metrics)  # Include current metrics
            
            # Step 4: Analyze trends
            trends = self.trend_analyzer.analyze_trends(historical_metrics)
            
            # Step 5: Generate insights
            # Extract health scores if available (would come from health score calculation)
            health_scores = self._extract_health_scores(event_payload)
            # Add summary data to metrics for insights generation
            metrics['summary'] = analytics_data['summary']
            insights = self.insights_engine.generate_insights(metrics, trends, health_scores)
            
            # Compile complete response
            response = {
                'account_id': account_id,
                'action_plan_id': event_payload.get('actionPlanUniqueId'),
                'timestamp': datetime.utcnow().isoformat(),
                'summary': analytics_data['summary'],
                'metrics': {
                    'current': self._format_current_metrics(metrics),
                    'historical_summary': self._summarize_historical_metrics(historical_metrics)
                },
                'trends': self._format_trends(trends),
                'insights': self._format_insights(insights),
                'recommendations': insights['recommendations'],
                'alerts': insights['alerts']
            }
            
            logger.info(f"Analytics processing complete for account {account_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing analytics event: {e}", exc_info=True)
            raise
    
    def get_analytics_summary(self, account_id: int, days: int = 7) -> Dict[str, Any]:
        """
        Get analytics summary for an account over a period.
        
        Args:
            account_id: Account ID
            days: Number of days to analyze
            
        Returns:
            Analytics summary
        """
        try:
            # Get historical metrics
            historical_metrics = self.metrics_calculator.get_historical_metrics(account_id, days)
            
            if not historical_metrics:
                return {
                    'status': 'no_data',
                    'message': f'No analytics data found for account {account_id}'
                }
            
            # Analyze trends
            trends = self.trend_analyzer.analyze_trends(historical_metrics)
            
            # Get latest insights
            latest_metrics = historical_metrics[-1]
            insights = self.insights_engine.generate_insights(latest_metrics, trends)
            
            return {
                'account_id': account_id,
                'period_days': days,
                'data_points': len(historical_metrics),
                'executive_summary': insights['executive_summary'],
                'key_trends': self._extract_key_trends(trends),
                'top_recommendations': insights['recommendations'][:3],
                'achievements': insights['achievements']
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics summary: {e}", exc_info=True)
            raise
    
    def get_pillar_analytics(self, account_id: int, pillar: str) -> Dict[str, Any]:
        """Get detailed analytics for a specific pillar."""
        try:
            historical_metrics = self.metrics_calculator.get_historical_metrics(account_id, days=30)
            
            if not historical_metrics:
                return {'status': 'no_data'}
            
            # Extract pillar-specific data
            pillar_history = []
            for metric in historical_metrics:
                if pillar in metric['pillar_metrics']:
                    pillar_data = metric['pillar_metrics'][pillar]
                    pillar_data['timestamp'] = metric['timestamp']
                    pillar_history.append(pillar_data)
            
            # Analyze pillar trends
            trends = self.trend_analyzer.analyze_trends(historical_metrics)
            pillar_trend = trends.get('pillar_trends', {}).get(pillar, {})
            
            return {
                'pillar': pillar,
                'current_metrics': pillar_history[-1] if pillar_history else None,
                'historical_data': pillar_history,
                'trends': pillar_trend,
                'performance_summary': self._summarize_pillar_performance(pillar_history)
            }
            
        except Exception as e:
            logger.error(f"Error getting pillar analytics: {e}", exc_info=True)
            raise
    
    def _extract_health_scores(self, event_payload: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """Extract health scores from event payload if available."""
        # This would integrate with the health score calculation
        # For now, return None as health scores come from a separate process
        return None
    
    def _format_current_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Format current metrics for response."""
        return {
            'engagement_score': metrics['engagement_metrics']['engagement_score'],
            'overall_engagement_rate': metrics['engagement_metrics']['overall_engagement_rate'],
            'active_pillars': len([p for p, d in metrics['pillar_metrics'].items() 
                                 if d['engagement_rate'] > 0]),
            'total_pillars': len(metrics['pillar_metrics']),
            'habit_formation_index': metrics['performance_indicators']['habit_formation_index'],
            'completion_velocity': metrics['performance_indicators']['completion_velocity']
        }
    
    def _summarize_historical_metrics(self, historical_metrics: List[Dict]) -> Dict[str, Any]:
        """Summarize historical metrics."""
        if not historical_metrics:
            return {}
        
        engagement_scores = [m['engagement_metrics']['engagement_score'] for m in historical_metrics]
        
        return {
            'average_engagement': sum(engagement_scores) / len(engagement_scores),
            'peak_engagement': max(engagement_scores),
            'lowest_engagement': min(engagement_scores),
            'data_points': len(historical_metrics)
        }
    
    def _format_trends(self, trends: Dict[str, Any]) -> Dict[str, Any]:
        """Format trends for response."""
        if trends.get('status') == 'insufficient_data':
            return trends
        
        return {
            'overall_direction': trends['engagement_trends']['overall_engagement']['trend']['direction'],
            'pillar_trends': {
                pillar: data['completion_trend']['direction']
                for pillar, data in trends['pillar_trends'].items()
            },
            'momentum_analysis': {
                pillar: 'positive' if data['momentum'] > 0.5 else 'negative' if data['momentum'] < -0.5 else 'neutral'
                for pillar, data in trends['pillar_trends'].items()
            },
            'predictions': trends['predictions']
        }
    
    def _format_insights(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Format insights for response."""
        return {
            'executive_summary': insights['executive_summary'],
            'pillar_insights': self._summarize_pillar_insights(insights['pillar_insights']),
            'behavioral_patterns': insights['behavioral_insights'][:3],  # Top 3
            'achievements': insights['achievements']
        }
    
    def _summarize_pillar_insights(self, pillar_insights: List[Dict]) -> Dict[str, List[str]]:
        """Summarize pillar insights by category."""
        summary = {
            'strengths': [],
            'opportunities': [],
            'concerns': []
        }
        
        for pillar_data in pillar_insights:
            pillar_name = pillar_data['pillar']
            
            for insight in pillar_data['key_insights']:
                if insight['type'] in ['strength', 'consistency', 'highlight']:
                    summary['strengths'].append(f"{pillar_name}: {insight['message']}")
                elif insight['type'] in ['momentum']:
                    summary['opportunities'].append(f"{pillar_name}: {insight['message']}")
                elif insight['type'] in ['concern']:
                    summary['concerns'].append(f"{pillar_name}: {insight['message']}")
        
        return summary
    
    def _extract_key_trends(self, trends: Dict[str, Any]) -> List[str]:
        """Extract key trends as readable messages."""
        if trends.get('status') == 'insufficient_data':
            return ["Insufficient data for trend analysis"]
        
        key_trends = []
        
        # Overall engagement trend
        engagement_trend = trends['engagement_trends']['overall_engagement']['trend']
        if engagement_trend['direction'] != 'stable':
            key_trends.append(f"Overall engagement is {engagement_trend['direction']}")
        
        # Pillar trends
        improving_pillars = []
        declining_pillars = []
        
        for pillar, data in trends['pillar_trends'].items():
            if data['completion_trend']['direction'] == 'increasing':
                improving_pillars.append(pillar)
            elif data['completion_trend']['direction'] == 'decreasing':
                declining_pillars.append(pillar)
        
        if improving_pillars:
            key_trends.append(f"Improving in: {', '.join(improving_pillars)}")
        
        if declining_pillars:
            key_trends.append(f"Declining in: {', '.join(declining_pillars)}")
        
        # Velocity
        velocity = trends['engagement_trends'].get('velocity_analysis', {})
        if velocity.get('accelerating', 0) > velocity.get('decelerating', 0):
            key_trends.append("Completion rates are accelerating")
        
        return key_trends[:5]  # Top 5 trends
    
    def _summarize_pillar_performance(self, pillar_history: List[Dict]) -> Dict[str, Any]:
        """Summarize performance for a specific pillar."""
        if not pillar_history:
            return {}
        
        completion_scores = [d['completion_score'] for d in pillar_history]
        engagement_rates = [d['engagement_rate'] for d in pillar_history]
        
        return {
            'average_completion': sum(completion_scores) / len(completion_scores),
            'average_engagement': sum(engagement_rates) / len(engagement_rates),
            'best_completion': max(completion_scores),
            'consistency': self._calculate_consistency(completion_scores),
            'trend': 'improving' if completion_scores[-1] > completion_scores[0] else 'declining'
        }
    
    def _calculate_consistency(self, values: List[float]) -> str:
        """Calculate consistency level from values."""
        if len(values) < 2:
            return 'unknown'
        
        import numpy as np
        std_dev = np.std(values)
        mean = np.mean(values)
        
        if mean == 0:
            return 'unknown'
        
        cv = (std_dev / mean) * 100
        
        if cv < 10:
            return 'very_consistent'
        elif cv < 25:
            return 'consistent'
        elif cv < 50:
            return 'variable'
        else:
            return 'highly_variable'