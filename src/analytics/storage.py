"""Analytics storage service for persisting and retrieving analytics data"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

from src.analytics.models import UserAnalytics
from src.analytics.processor import AnalyticsProcessor
from src.analytics.insights import InsightsGenerator

logger = logging.getLogger(__name__)


class AnalyticsStorage:
    """Store and retrieve analytics data"""
    
    def __init__(self, storage_path: str = "analytics_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.processor = AnalyticsProcessor()
        self.insights_generator = InsightsGenerator()
    
    def process_and_store_webhook(self, webhook_data: Dict) -> Dict[str, any]:
        """
        Process webhook data and store analytics
        
        Args:
            webhook_data: Raw webhook payload
            
        Returns:
            Dict containing analytics and insights
        """
        try:
            # Process webhook data
            analytics = self.processor.process_webhook_data(webhook_data)
            
            # Generate insights
            insights = self.insights_generator.generate_insights(analytics)
            
            # Store analytics
            self._store_analytics(analytics)
            
            # Store raw webhook for future reprocessing
            self._store_raw_webhook(webhook_data)
            
            return {
                "analytics": self._analytics_to_dict(analytics),
                "insights": insights,
                "timestamp": analytics.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            raise
    
    def get_user_analytics_history(
        self, 
        user_id: str, 
        days: int = 30
    ) -> List[Dict[str, any]]:
        """
        Retrieve analytics history for a user
        
        Args:
            user_id: User identifier
            days: Number of days of history to retrieve
            
        Returns:
            List of analytics snapshots
        """
        history = []
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        user_dir = self.storage_path / user_id
        if not user_dir.exists():
            return history
        
        for file_path in sorted(user_dir.glob("analytics_*.json")):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                timestamp = datetime.fromisoformat(data['timestamp'])
                if timestamp >= cutoff_date:
                    history.append(data)
                    
            except Exception as e:
                logger.warning(f"Error reading analytics file {file_path}: {e}")
        
        return history
    
    def get_aggregated_analytics(
        self, 
        user_id: str, 
        period: str = "week"
    ) -> Dict[str, any]:
        """
        Get aggregated analytics for a time period
        
        Args:
            user_id: User identifier
            period: Time period ('week', 'month', 'quarter')
            
        Returns:
            Aggregated analytics data
        """
        days = {
            "week": 7,
            "month": 30,
            "quarter": 90
        }.get(period, 7)
        
        history = self.get_user_analytics_history(user_id, days)
        
        if not history:
            return {"error": "No data available"}
        
        # Aggregate metrics
        total_snapshots = len(history)
        avg_completion = sum(h['analytics']['overall_completion_rate'] for h in history) / total_snapshots
        avg_engagement = sum(h['analytics']['engagement_score'] for h in history) / total_snapshots
        
        # Trend analysis
        if total_snapshots > 1:
            first_half = history[:total_snapshots//2]
            second_half = history[total_snapshots//2:]
            
            first_avg = sum(h['analytics']['overall_completion_rate'] for h in first_half) / len(first_half)
            second_avg = sum(h['analytics']['overall_completion_rate'] for h in second_half) / len(second_half)
            
            trend = "improving" if second_avg > first_avg else "declining"
        else:
            trend = "insufficient_data"
        
        return {
            "period": period,
            "snapshots": total_snapshots,
            "average_completion_rate": round(avg_completion, 1),
            "average_engagement_score": round(avg_engagement, 1),
            "trend": trend,
            "date_range": {
                "start": history[0]['timestamp'],
                "end": history[-1]['timestamp']
            }
        }
    
    def _store_analytics(self, analytics: UserAnalytics):
        """Store analytics data to disk"""
        user_dir = self.storage_path / analytics.user_id
        user_dir.mkdir(exist_ok=True)
        
        timestamp = analytics.timestamp.strftime("%Y%m%d_%H%M%S")
        file_path = user_dir / f"analytics_{timestamp}.json"
        
        with open(file_path, 'w') as f:
            json.dump(self._analytics_to_dict(analytics), f, indent=2)
    
    def _store_raw_webhook(self, webhook_data: Dict):
        """Store raw webhook data for future reprocessing"""
        user_id = webhook_data.get('userId', 'unknown')
        user_dir = self.storage_path / user_id / "webhooks"
        user_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_path = user_dir / f"webhook_{timestamp}.json"
        
        with open(file_path, 'w') as f:
            json.dump(webhook_data, f, indent=2)
    
    def _analytics_to_dict(self, analytics: UserAnalytics) -> Dict[str, any]:
        """Convert analytics object to dictionary"""
        return {
            "user_id": analytics.user_id,
            "timestamp": analytics.timestamp.isoformat(),
            "overall_completion_rate": analytics.overall_completion_rate,
            "engagement_score": analytics.engagement_score,
            "pillar_completions": {
                pillar: {
                    "success_rate": data.success_rate,
                    "total_routines": data.total_routines,
                    "completed_routines": data.completed_routines
                }
                for pillar, data in analytics.pillar_completions.items()
            },
            "routine_summary": {
                "total": len(analytics.routine_completions),
                "successful": len(analytics.successful_routines),
                "struggling": len(analytics.struggling_routines)
            },
            "pillar_rankings": analytics.pillar_rankings
        }