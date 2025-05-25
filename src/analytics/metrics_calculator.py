"""Calculate various analytics metrics from processed event data."""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Calculate analytics metrics from processed completion data."""
    
    def __init__(self):
        self.metrics_cache = {}
    
    def calculate_metrics(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive metrics from analytics data.
        
        Args:
            analytics_data: Processed analytics data from EventProcessor
            
        Returns:
            Calculated metrics
        """
        metrics = {
            'account_id': analytics_data['account_id'],
            'timestamp': analytics_data['timestamp'],
            'pillar_metrics': self._calculate_pillar_metrics(analytics_data['pillar_analytics']),
            'routine_metrics': self._calculate_routine_metrics(analytics_data['pillar_analytics']),
            'engagement_metrics': self._calculate_engagement_metrics(analytics_data),
            'performance_indicators': self._calculate_performance_indicators(analytics_data)
        }
        
        # Cache metrics for trend analysis
        self._cache_metrics(metrics)
        
        return metrics
    
    def _calculate_pillar_metrics(self, pillar_analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics for each pillar."""
        pillar_metrics = {}
        
        for pillar, data in pillar_analytics.items():
            metrics = {
                'engagement_rate': data['engagement_rate'],
                'active_routines': data['routines_with_data'],
                'total_routines': data['total_routines'],
                'completion_score': self._calculate_completion_score(data),
                'consistency_score': self._calculate_consistency_score(data),
                'weekly_trend': self._calculate_period_trend(data['completion_by_period']['week']),
                'monthly_trend': self._calculate_period_trend(data['completion_by_period']['month'])
            }
            
            # Calculate routine-level statistics
            routine_stats = self._analyze_routine_performance(data['routine_details'])
            metrics.update(routine_stats)
            
            pillar_metrics[pillar] = metrics
        
        return pillar_metrics
    
    def _calculate_routine_metrics(self, pillar_analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate metrics for individual routines."""
        routine_metrics = []
        
        for pillar, data in pillar_analytics.items():
            for routine in data['routine_details']:
                if not routine['has_completion_data']:
                    continue
                
                metrics = {
                    'routine_id': routine['routine_id'],
                    'routine_name': routine['display_name'],
                    'pillar': pillar,
                    'schedule_category': routine['schedule_category'],
                    'total_completions': routine['total_completions'],
                    'adherence_rate': self._calculate_adherence_rate(routine),
                    'completion_pattern': self._analyze_completion_pattern(routine),
                    'performance_rating': self._rate_routine_performance(routine)
                }
                
                routine_metrics.append(metrics)
        
        # Sort by performance
        routine_metrics.sort(key=lambda x: x['adherence_rate'], reverse=True)
        
        return routine_metrics
    
    def _calculate_engagement_metrics(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall engagement metrics."""
        summary = analytics_data['summary']
        
        engagement = {
            'overall_engagement_rate': summary['overall_engagement_rate'],
            'active_pillars_percentage': summary['active_pillars'] / summary['total_pillars'] if summary['total_pillars'] > 0 else 0,
            'routine_activation_rate': summary['engaged_routines'] / summary['total_routines'] if summary['total_routines'] > 0 else 0,
            'engagement_distribution': self._calculate_engagement_distribution(analytics_data['pillar_analytics']),
            'engagement_score': self._calculate_overall_engagement_score(summary)
        }
        
        return engagement
    
    def _calculate_performance_indicators(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate key performance indicators."""
        indicators = {
            'health_score_impact': self._estimate_health_score_impact(analytics_data),
            'completion_velocity': self._calculate_completion_velocity(analytics_data),
            'habit_formation_index': self._calculate_habit_formation_index(analytics_data),
            'recommendations': self._generate_recommendations(analytics_data)
        }
        
        return indicators
    
    def _calculate_completion_score(self, pillar_data: Dict[str, Any]) -> float:
        """Calculate completion score for a pillar (0-100)."""
        if pillar_data['total_routines'] == 0:
            return 0
        
        # Weight factors
        engagement_weight = 0.4
        completion_weight = 0.6
        
        engagement_score = pillar_data['engagement_rate'] * 100
        
        # Average completion rate across all routines
        total_completion_rate = 0
        routine_count = 0
        
        for routine in pillar_data['routine_details']:
            if routine['has_completion_data']:
                avg_rate = sum(stat['completion_rate'] for stat in routine['completion_stats']) / len(routine['completion_stats'])
                total_completion_rate += avg_rate
                routine_count += 1
        
        completion_score = (total_completion_rate / routine_count * 100) if routine_count > 0 else 0
        
        return (engagement_score * engagement_weight + completion_score * completion_weight)
    
    def _calculate_consistency_score(self, pillar_data: Dict[str, Any]) -> float:
        """Calculate consistency score based on completion patterns."""
        weekly_completions = pillar_data['completion_by_period']['week']
        
        if len(weekly_completions) < 2:
            return 0
        
        # Calculate variance in weekly completions
        values = list(weekly_completions.values())
        avg = sum(values) / len(values)
        variance = sum((x - avg) ** 2 for x in values) / len(values)
        
        # Lower variance = higher consistency
        # Normalize to 0-100 scale
        max_variance = avg ** 2  # Maximum possible variance
        consistency = (1 - (variance / max_variance if max_variance > 0 else 0)) * 100
        
        return max(0, min(100, consistency))
    
    def _calculate_period_trend(self, period_data: Dict[int, int]) -> str:
        """Calculate trend direction for a period."""
        if len(period_data) < 2:
            return 'stable'
        
        sorted_periods = sorted(period_data.items())
        recent = sorted_periods[-1][1]
        previous = sorted_periods[-2][1]
        
        if recent > previous * 1.1:
            return 'increasing'
        elif recent < previous * 0.9:
            return 'decreasing'
        else:
            return 'stable'
    
    def _analyze_routine_performance(self, routines: List[Dict]) -> Dict[str, Any]:
        """Analyze performance across routines in a pillar."""
        if not routines:
            return {'top_performer': None, 'needs_attention': None, 'average_adherence': 0}
        
        performances = []
        for routine in routines:
            if routine['has_completion_data']:
                avg_completion = sum(stat['completion_rate'] for stat in routine['completion_stats']) / len(routine['completion_stats'])
                performances.append((routine['display_name'], avg_completion))
        
        if not performances:
            return {'top_performer': None, 'needs_attention': None, 'average_adherence': 0}
        
        performances.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'top_performer': performances[0][0] if performances else None,
            'needs_attention': performances[-1][0] if performances[-1][1] < 0.5 else None,
            'average_adherence': sum(p[1] for p in performances) / len(performances)
        }
    
    def _calculate_adherence_rate(self, routine: Dict) -> float:
        """Calculate adherence rate for a routine."""
        if not routine['completion_stats']:
            return 0
        
        total_rate = sum(stat['completion_rate'] for stat in routine['completion_stats'])
        return total_rate / len(routine['completion_stats'])
    
    def _analyze_completion_pattern(self, routine: Dict) -> str:
        """Analyze completion pattern for a routine."""
        if not routine['completion_stats']:
            return 'no_data'
        
        rates = [stat['completion_rate'] for stat in routine['completion_stats']]
        
        if all(r >= 0.8 for r in rates):
            return 'consistent_high'
        elif all(r <= 0.2 for r in rates):
            return 'consistent_low'
        elif rates[-1] > rates[0]:
            return 'improving'
        elif rates[-1] < rates[0]:
            return 'declining'
        else:
            return 'variable'
    
    def _rate_routine_performance(self, routine: Dict) -> str:
        """Rate routine performance."""
        adherence = self._calculate_adherence_rate(routine)
        
        if adherence >= 0.8:
            return 'excellent'
        elif adherence >= 0.6:
            return 'good'
        elif adherence >= 0.4:
            return 'fair'
        else:
            return 'needs_improvement'
    
    def _calculate_engagement_distribution(self, pillar_analytics: Dict[str, Any]) -> Dict[str, float]:
        """Calculate how engagement is distributed across pillars."""
        total_engagement = sum(data['total_completions'] for data in pillar_analytics.values())
        
        if total_engagement == 0:
            return {pillar: 0 for pillar in pillar_analytics}
        
        return {
            pillar: (data['total_completions'] / total_engagement) * 100
            for pillar, data in pillar_analytics.items()
        }
    
    def _calculate_overall_engagement_score(self, summary: Dict[str, Any]) -> float:
        """Calculate overall engagement score (0-100)."""
        factors = {
            'engagement_rate': summary['overall_engagement_rate'] * 0.4,
            'active_pillars': (summary['active_pillars'] / summary['total_pillars']) * 0.3 if summary['total_pillars'] > 0 else 0,
            'completion_density': min(summary['total_completions'] / (summary['total_routines'] * 2), 1) * 0.3
        }
        
        return sum(factors.values()) * 100
    
    def _estimate_health_score_impact(self, analytics_data: Dict[str, Any]) -> Dict[str, float]:
        """Estimate impact on health scores based on completion data."""
        # This is a simplified estimation - in production, this would use the actual health score calculation
        impacts = {}
        
        for pillar, data in analytics_data['pillar_analytics'].items():
            completion_score = self._calculate_completion_score(data)
            # Estimate +/- 5 points max impact based on completion
            impact = (completion_score - 50) * 0.1
            impacts[pillar] = round(impact, 2)
        
        return impacts
    
    def _calculate_completion_velocity(self, analytics_data: Dict[str, Any]) -> str:
        """Calculate the velocity of completion changes."""
        velocities = []
        
        for pillar_data in analytics_data['pillar_analytics'].values():
            weekly = pillar_data['completion_by_period']['week']
            if len(weekly) >= 2:
                sorted_weeks = sorted(weekly.items())
                recent_change = sorted_weeks[-1][1] - sorted_weeks[-2][1]
                velocities.append(recent_change)
        
        if not velocities:
            return 'stable'
        
        avg_velocity = sum(velocities) / len(velocities)
        
        if avg_velocity > 0.5:
            return 'accelerating'
        elif avg_velocity < -0.5:
            return 'decelerating'
        else:
            return 'stable'
    
    def _calculate_habit_formation_index(self, analytics_data: Dict[str, Any]) -> float:
        """Calculate habit formation index based on consistency and frequency."""
        indices = []
        
        for pillar_data in analytics_data['pillar_analytics'].values():
            consistency = self._calculate_consistency_score(pillar_data)
            engagement = pillar_data['engagement_rate'] * 100
            
            # Habit formation = consistency * engagement
            index = (consistency * 0.6 + engagement * 0.4)
            indices.append(index)
        
        return sum(indices) / len(indices) if indices else 0
    
    def _generate_recommendations(self, analytics_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate actionable recommendations based on analytics."""
        recommendations = []
        summary = analytics_data['summary']
        
        # Check for inactive pillars
        if summary['least_active_pillar']:
            recommendations.append({
                'type': 'engagement',
                'priority': 'high',
                'message': f"Focus on {summary['least_active_pillar']} pillar - it has the lowest engagement"
            })
        
        # Check for low overall engagement
        if summary['overall_engagement_rate'] < 0.3:
            recommendations.append({
                'type': 'activation',
                'priority': 'high',
                'message': "Consider reducing the number of routines to improve focus and engagement"
            })
        
        # Check for unbalanced engagement
        distribution = self._calculate_engagement_distribution(analytics_data['pillar_analytics'])
        max_dist = max(distribution.values()) if distribution else 0
        
        if max_dist > 50:
            recommendations.append({
                'type': 'balance',
                'priority': 'medium',
                'message': "Your engagement is heavily focused on one pillar - try to balance across all areas"
            })
        
        return recommendations
    
    def _cache_metrics(self, metrics: Dict[str, Any]):
        """Cache metrics for historical analysis."""
        account_id = metrics['account_id']
        
        if account_id not in self.metrics_cache:
            self.metrics_cache[account_id] = []
        
        self.metrics_cache[account_id].append(metrics)
        
        # Keep only last 30 entries
        self.metrics_cache[account_id] = self.metrics_cache[account_id][-30:]
    
    def get_historical_metrics(self, account_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """Get historical metrics for an account."""
        if account_id not in self.metrics_cache:
            return []
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        return [
            m for m in self.metrics_cache[account_id]
            if datetime.fromisoformat(m['timestamp']) > cutoff
        ]