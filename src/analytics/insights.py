"""Generate actionable insights from analytics data"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter

from src.analytics.models import UserAnalytics, RoutineCompletion, Pillar

logger = logging.getLogger(__name__)


class InsightsGenerator:
    """Generate actionable insights and recommendations"""
    
    def generate_insights(self, analytics: UserAnalytics) -> Dict[str, any]:
        """
        Generate comprehensive insights from user analytics
        
        Returns:
            Dict containing various insights and recommendations
        """
        return {
            "summary": self._generate_summary(analytics),
            "strengths": self._identify_strengths(analytics),
            "opportunities": self._identify_opportunities(analytics),
            "recommendations": self._generate_recommendations(analytics),
            "predictions": self._generate_predictions(analytics),
            "alerts": self._generate_alerts(analytics)
        }
    
    def _generate_summary(self, analytics: UserAnalytics) -> Dict[str, any]:
        """Generate high-level summary"""
        return {
            "overall_completion_rate": round(analytics.overall_completion_rate, 1),
            "engagement_score": round(analytics.engagement_score, 1),
            "total_routines": len(analytics.routine_completions),
            "active_pillars": len(analytics.pillar_completions),
            "performance_level": self._get_performance_level(analytics.overall_completion_rate)
        }
    
    def _identify_strengths(self, analytics: UserAnalytics) -> List[Dict[str, any]]:
        """Identify user's strengths"""
        strengths = []
        
        # Top performing pillars
        top_pillars = [
            (pillar, data) for pillar, data in analytics.pillar_completions.items()
            if data.success_rate >= 80
        ]
        for pillar, data in sorted(top_pillars, key=lambda x: x[1].success_rate, reverse=True)[:3]:
            strengths.append({
                "type": "pillar_excellence",
                "pillar": pillar,
                "success_rate": round(data.success_rate, 1),
                "message": f"Excellent performance in {pillar} with {data.success_rate:.0f}% success rate"
            })
        
        # Successful routines
        for routine in analytics.successful_routines[:5]:
            strengths.append({
                "type": "routine_mastery",
                "routine": routine.routine_name,
                "completion_rate": round(routine.average_completion_rate, 1),
                "message": f"Consistently completing {routine.routine_name}"
            })
        
        # Improving routines
        improving = [r for r in analytics.routine_completions.values() if r.trend == "improving"]
        for routine in improving[:3]:
            strengths.append({
                "type": "positive_trend",
                "routine": routine.routine_name,
                "trend": "improving",
                "message": f"{routine.routine_name} is showing improvement"
            })
        
        return strengths
    
    def _identify_opportunities(self, analytics: UserAnalytics) -> List[Dict[str, any]]:
        """Identify improvement opportunities"""
        opportunities = []
        
        # Struggling routines
        for routine in analytics.struggling_routines:
            opportunities.append({
                "type": "low_completion",
                "routine": routine.routine_name,
                "pillar": routine.pillar.value,
                "completion_rate": round(routine.average_completion_rate, 1),
                "impact": "high" if routine.average_completion_rate < 30 else "medium",
                "message": f"{routine.routine_name} needs attention (only {routine.average_completion_rate:.0f}% completion)"
            })
        
        # Declining routines
        declining = [r for r in analytics.routine_completions.values() if r.trend == "declining"]
        for routine in declining:
            opportunities.append({
                "type": "negative_trend",
                "routine": routine.routine_name,
                "trend": "declining",
                "message": f"{routine.routine_name} completion is declining"
            })
        
        # Underperforming pillars
        weak_pillars = [
            (pillar, data) for pillar, data in analytics.pillar_completions.items()
            if data.success_rate < 50
        ]
        for pillar, data in weak_pillars:
            opportunities.append({
                "type": "pillar_weakness",
                "pillar": pillar,
                "success_rate": round(data.success_rate, 1),
                "message": f"{pillar} pillar needs improvement ({data.success_rate:.0f}% success rate)"
            })
        
        return opportunities
    
    def _generate_recommendations(self, analytics: UserAnalytics) -> List[Dict[str, any]]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Schedule adjustments for struggling routines
        for routine in analytics.struggling_routines[:3]:
            if routine.schedule_changes:
                # Has been adjusted before
                recommendations.append({
                    "type": "routine_replacement",
                    "routine": routine.routine_name,
                    "action": "replace",
                    "reason": "persistent_low_completion",
                    "message": f"Consider replacing {routine.routine_name} with an easier alternative"
                })
            else:
                # First time struggling
                recommendations.append({
                    "type": "schedule_adjustment",
                    "routine": routine.routine_name,
                    "action": "reschedule",
                    "reason": "low_completion",
                    "message": f"Try scheduling {routine.routine_name} at a different time"
                })
        
        # Pillar balance recommendations
        pillar_rankings = analytics.pillar_rankings
        if pillar_rankings:
            strongest_pillar = pillar_rankings[0][0]
            weakest_pillar = pillar_rankings[-1][0]
            
            if pillar_rankings[0][1] - pillar_rankings[-1][1] > 30:
                recommendations.append({
                    "type": "pillar_balance",
                    "action": "rebalance",
                    "strong_pillar": strongest_pillar,
                    "weak_pillar": weakest_pillar,
                    "message": f"Consider shifting focus from {strongest_pillar} to {weakest_pillar} for better balance"
                })
        
        # Engagement recommendations
        if analytics.engagement_score < 50:
            recommendations.append({
                "type": "engagement_boost",
                "action": "simplify",
                "message": "Reduce routine complexity to improve engagement"
            })
        elif analytics.engagement_score > 80:
            recommendations.append({
                "type": "engagement_boost",
                "action": "challenge",
                "message": "You're doing great! Consider adding more challenging routines"
            })
        
        return recommendations
    
    def _generate_predictions(self, analytics: UserAnalytics) -> Dict[str, any]:
        """Generate predictions based on current trends"""
        # Calculate projected completion rate
        improving_ratio = sum(
            1 for r in analytics.routine_completions.values() 
            if r.trend == "improving"
        ) / len(analytics.routine_completions) if analytics.routine_completions else 0
        
        # Simple linear projection
        trend_factor = 1 + (improving_ratio - 0.5) * 0.1  # ±5% based on trends
        projected_completion = min(100, analytics.overall_completion_rate * trend_factor)
        
        # Risk assessment
        at_risk_routines = [
            r for r in analytics.routine_completions.values()
            if r.trend == "declining" and r.average_completion_rate < 60
        ]
        
        return {
            "next_period_completion": round(projected_completion, 1),
            "trend_direction": "improving" if improving_ratio > 0.5 else "declining",
            "at_risk_routines": len(at_risk_routines),
            "success_probability": self._calculate_success_probability(analytics)
        }
    
    def _generate_alerts(self, analytics: UserAnalytics) -> List[Dict[str, any]]:
        """Generate alerts for immediate attention"""
        alerts = []
        
        # Critical low completion
        critical_routines = [
            r for r in analytics.routine_completions.values()
            if r.average_completion_rate < 20
        ]
        if critical_routines:
            alerts.append({
                "severity": "high",
                "type": "critical_low_completion",
                "count": len(critical_routines),
                "message": f"{len(critical_routines)} routines have critically low completion rates"
            })
        
        # Rapid decline
        rapid_decline = [
            r for r in analytics.routine_completions.values()
            if r.trend == "declining" and len(r.completion_stats) >= 2
            and r.completion_stats[-1].completion_percentage < r.completion_stats[-2].completion_percentage * 0.5
        ]
        if rapid_decline:
            alerts.append({
                "severity": "medium",
                "type": "rapid_decline",
                "routines": [r.routine_name for r in rapid_decline],
                "message": "Rapid decline detected in routine completion"
            })
        
        # Pillar imbalance
        if analytics.pillar_rankings:
            gap = analytics.pillar_rankings[0][1] - analytics.pillar_rankings[-1][1]
            if gap > 50:
                alerts.append({
                    "severity": "medium",
                    "type": "pillar_imbalance",
                    "gap": round(gap, 1),
                    "message": "Significant imbalance between pillars detected"
                })
        
        return alerts
    
    def _get_performance_level(self, completion_rate: float) -> str:
        """Categorize performance level"""
        if completion_rate >= 80:
            return "excellent"
        elif completion_rate >= 60:
            return "good"
        elif completion_rate >= 40:
            return "fair"
        else:
            return "needs_improvement"
    
    def _calculate_success_probability(self, analytics: UserAnalytics) -> float:
        """Calculate probability of maintaining/improving performance"""
        factors = {
            "completion_rate": min(analytics.overall_completion_rate / 100, 1) * 0.3,
            "engagement": min(analytics.engagement_score / 100, 1) * 0.3,
            "positive_trends": sum(1 for r in analytics.routine_completions.values() if r.trend == "improving") / 
                             len(analytics.routine_completions) * 0.2 if analytics.routine_completions else 0,
            "consistency": (1 - self._calculate_variance(analytics)) * 0.2
        }
        
        return sum(factors.values()) * 100
    
    def _calculate_variance(self, analytics: UserAnalytics) -> float:
        """Calculate variance in completion rates"""
        if not analytics.routine_completions:
            return 0
            
        rates = [r.average_completion_rate for r in analytics.routine_completions.values()]
        avg = sum(rates) / len(rates)
        variance = sum((rate - avg) ** 2 for rate in rates) / len(rates)
        return min(variance / 10000, 1)  # Normalize to 0-1