"""Generate actionable insights from analytics data."""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class InsightsEngine:
    """Generate human-readable insights from analytics data."""
    
    def __init__(self):
        self.insight_templates = self._load_insight_templates()
    
    def generate_insights(self, 
                         metrics: Dict[str, Any], 
                         trends: Dict[str, Any],
                         health_scores: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Generate comprehensive insights from metrics and trends.
        
        Args:
            metrics: Current metrics from MetricsCalculator
            trends: Trend analysis from TrendAnalyzer
            health_scores: Optional current health scores
            
        Returns:
            Generated insights organized by category
        """
        insights = {
            'timestamp': datetime.utcnow().isoformat(),
            'account_id': metrics.get('account_id'),
            'executive_summary': self._generate_executive_summary(metrics, trends),
            'pillar_insights': self._generate_pillar_insights(metrics, trends),
            'routine_insights': self._generate_routine_insights(metrics, trends),
            'behavioral_insights': self._generate_behavioral_insights(metrics, trends),
            'health_impact_insights': self._generate_health_impact_insights(metrics, health_scores),
            'recommendations': self._generate_prioritized_recommendations(metrics, trends),
            'achievements': self._identify_achievements(metrics, trends),
            'alerts': self._generate_alerts(metrics, trends)
        }
        
        return insights
    
    def _generate_executive_summary(self, metrics: Dict[str, Any], trends: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary of user's performance."""
        engagement = metrics['engagement_metrics']
        performance = metrics['performance_indicators']
        
        # Determine overall status
        if engagement['engagement_score'] >= 70:
            status = 'excellent'
            message = "You're doing great! Your engagement is strong across most areas."
        elif engagement['engagement_score'] >= 50:
            status = 'good'
            message = "You're on the right track. A few adjustments can boost your results."
        else:
            status = 'needs_attention'
            message = "There's room for improvement. Let's focus on building consistency."
        
        summary = {
            'status': status,
            'message': message,
            'key_metrics': {
                'overall_engagement': f"{engagement['engagement_score']:.1f}%",
                'active_pillars': f"{engagement['active_pillars_percentage']*100:.0f}%",
                'habit_formation': f"{performance['habit_formation_index']:.1f}%",
                'completion_velocity': performance['completion_velocity']
            },
            'trend_summary': self._summarize_trends(trends),
            'focus_areas': self._identify_focus_areas(metrics)
        }
        
        return summary
    
    def _generate_pillar_insights(self, metrics: Dict[str, Any], trends: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate insights for each pillar."""
        pillar_insights = []
        pillar_metrics = metrics['pillar_metrics']
        pillar_trends = trends.get('pillar_trends', {})
        
        for pillar, data in pillar_metrics.items():
            trend_data = pillar_trends.get(pillar, {})
            
            insight = {
                'pillar': pillar,
                'performance_level': self._categorize_performance(data['completion_score']),
                'engagement_level': self._categorize_engagement(data['engagement_rate']),
                'trend': trend_data.get('completion_trend', {}).get('direction', 'stable'),
                'key_insights': []
            }
            
            # Generate specific insights
            if data['completion_score'] >= 70:
                insight['key_insights'].append({
                    'type': 'strength',
                    'message': f"Strong performance in {pillar} with {data['completion_score']:.0f}% completion score"
                })
            
            if data['consistency_score'] >= 80:
                insight['key_insights'].append({
                    'type': 'consistency',
                    'message': f"Excellent consistency in {pillar} routines"
                })
            
            if data['engagement_rate'] < 0.3:
                insight['key_insights'].append({
                    'type': 'concern',
                    'message': f"Low engagement in {pillar} - only {data['active_routines']} of {data['total_routines']} routines active"
                })
            
            if trend_data.get('momentum', 0) > 0.5:
                insight['key_insights'].append({
                    'type': 'momentum',
                    'message': f"Building strong momentum in {pillar} - keep it up!"
                })
            
            # Add top performer if exists
            if data.get('top_performer'):
                insight['key_insights'].append({
                    'type': 'highlight',
                    'message': f"'{data['top_performer']}' is your star routine in {pillar}"
                })
            
            pillar_insights.append(insight)
        
        return pillar_insights
    
    def _generate_routine_insights(self, metrics: Dict[str, Any], trends: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights about routine performance."""
        routine_metrics = metrics['routine_metrics']
        routine_trends = trends.get('routine_trends', {})
        
        insights = {
            'total_active_routines': len(routine_metrics),
            'performance_distribution': self._analyze_performance_distribution(routine_metrics),
            'top_performers': [],
            'needs_attention': [],
            'improving_routines': routine_trends.get('top_improving', [])[:3],
            'declining_routines': routine_trends.get('top_declining', [])[:3]
        }
        
        # Identify top performers and struggling routines
        for routine in routine_metrics[:5]:  # Top 5
            if routine['adherence_rate'] >= 0.8:
                insights['top_performers'].append({
                    'name': routine['routine_name'],
                    'pillar': routine['pillar'],
                    'adherence': f"{routine['adherence_rate']*100:.0f}%"
                })
        
        for routine in routine_metrics[-5:]:  # Bottom 5
            if routine['adherence_rate'] < 0.3:
                insights['needs_attention'].append({
                    'name': routine['routine_name'],
                    'pillar': routine['pillar'],
                    'adherence': f"{routine['adherence_rate']*100:.0f}%",
                    'suggestion': self._generate_routine_suggestion(routine)
                })
        
        return insights
    
    def _generate_behavioral_insights(self, metrics: Dict[str, Any], trends: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate insights about user behavior patterns."""
        insights = []
        patterns = trends.get('pattern_analysis', {})
        
        # Weekly pattern insights
        weekly_patterns = patterns.get('weekly_patterns', {})
        if weekly_patterns.get('best_day'):
            insights.append({
                'type': 'pattern',
                'category': 'weekly',
                'message': f"You're most active on {weekly_patterns['best_day']['day']}s - plan important routines for this day"
            })
        
        # Engagement cluster insights
        clusters = patterns.get('engagement_clusters', [])
        for cluster in clusters:
            if cluster['type'] == 'high_engagement' and cluster['duration_days'] >= 3:
                insights.append({
                    'type': 'pattern',
                    'category': 'engagement',
                    'message': f"You had a {cluster['duration_days']}-day streak of high engagement - what worked during this period?"
                })
        
        # Pillar correlation insights
        correlations = patterns.get('pillar_correlations', {})
        for pair, correlation in correlations.items():
            if correlation > 0.7:
                pillars = pair.split('_vs_')
                insights.append({
                    'type': 'correlation',
                    'category': 'synergy',
                    'message': f"{pillars[0]} and {pillars[1]} work well together - consider pairing these activities"
                })
        
        # Consistency pattern insights
        consistency = patterns.get('consistency_patterns', {})
        improving_consistency = [p for p, data in consistency.items() if data.get('is_improving', False)]
        if improving_consistency:
            insights.append({
                'type': 'improvement',
                'category': 'consistency',
                'message': f"Your consistency is improving in {', '.join(improving_consistency)}"
            })
        
        return insights
    
    def _generate_health_impact_insights(self, metrics: Dict[str, Any], health_scores: Optional[Dict[str, float]]) -> Dict[str, Any]:
        """Generate insights about health score impact."""
        impact_estimates = metrics['performance_indicators'].get('health_score_impact', {})
        
        insights = {
            'estimated_impacts': impact_estimates,
            'positive_impacts': [],
            'negative_impacts': [],
            'overall_trend': 'stable'
        }
        
        # Categorize impacts
        positive_total = 0
        negative_total = 0
        
        for pillar, impact in impact_estimates.items():
            if impact > 0.5:
                insights['positive_impacts'].append({
                    'pillar': pillar,
                    'impact': f"+{impact:.1f} points",
                    'message': f"Your efforts in {pillar} are boosting your health score"
                })
                positive_total += impact
            elif impact < -0.5:
                insights['negative_impacts'].append({
                    'pillar': pillar,
                    'impact': f"{impact:.1f} points",
                    'message': f"Low engagement in {pillar} may be affecting your health score"
                })
                negative_total += impact
        
        # Determine overall trend
        net_impact = positive_total + negative_total
        if net_impact > 1:
            insights['overall_trend'] = 'improving'
        elif net_impact < -1:
            insights['overall_trend'] = 'declining'
        
        # Add current scores if available
        if health_scores:
            insights['current_scores'] = health_scores
        
        return insights
    
    def _generate_prioritized_recommendations(self, metrics: Dict[str, Any], trends: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate prioritized recommendations."""
        recommendations = []
        
        # Add system-generated recommendations
        for rec in metrics['performance_indicators'].get('recommendations', []):
            recommendations.append({
                'priority': rec['priority'],
                'category': rec['type'],
                'recommendation': rec['message'],
                'expected_impact': 'medium'
            })
        
        # Add trend-based recommendations
        predictions = trends.get('predictions', {})
        
        # Risk mitigation recommendations
        for risk in predictions.get('risk_analysis', []):
            if risk['severity'] == 'high':
                recommendations.append({
                    'priority': 'high',
                    'category': 'risk_mitigation',
                    'recommendation': self._generate_risk_mitigation(risk),
                    'expected_impact': 'high'
                })
        
        # Opportunity recommendations
        for opp in predictions.get('opportunity_analysis', [])[:2]:
            recommendations.append({
                'priority': 'medium',
                'category': 'opportunity',
                'recommendation': opp['description'],
                'expected_impact': 'medium'
            })
        
        # Routine-specific recommendations
        routine_insights = self._generate_routine_insights(metrics, trends)
        if routine_insights['needs_attention']:
            worst_routine = routine_insights['needs_attention'][0]
            recommendations.append({
                'priority': 'high',
                'category': 'routine_improvement',
                'recommendation': f"Focus on improving '{worst_routine['name']}' - {worst_routine['suggestion']}",
                'expected_impact': 'high'
            })
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _identify_achievements(self, metrics: Dict[str, Any], trends: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify user achievements."""
        achievements = []
        
        # Check for high engagement achievement
        if metrics['engagement_metrics']['engagement_score'] >= 80:
            achievements.append({
                'type': 'engagement',
                'title': 'High Achiever',
                'description': 'Maintained 80%+ overall engagement'
            })
        
        # Check for consistency achievements
        for pillar, data in metrics['pillar_metrics'].items():
            if data['consistency_score'] >= 90:
                achievements.append({
                    'type': 'consistency',
                    'title': f'{pillar} Master',
                    'description': f'Achieved 90%+ consistency in {pillar}'
                })
        
        # Check for improvement achievements
        engagement_trend = trends.get('engagement_trends', {}).get('overall_engagement', {}).get('trend', {})
        if engagement_trend.get('direction') == 'increasing' and engagement_trend.get('strength', 0) > 0.5:
            achievements.append({
                'type': 'improvement',
                'title': 'Rising Star',
                'description': 'Showing strong improvement in overall engagement'
            })
        
        # Check for streak achievements
        for routine in metrics['routine_metrics']:
            if routine['completion_pattern'] == 'consistent_high':
                achievements.append({
                    'type': 'streak',
                    'title': 'Perfect Routine',
                    'description': f"Consistent high completion of '{routine['routine_name']}'"
                })
                break  # Only show one streak achievement
        
        return achievements
    
    def _generate_alerts(self, metrics: Dict[str, Any], trends: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate alerts for issues requiring attention."""
        alerts = []
        
        # Check for abandoned pillars
        for pillar, data in metrics['pillar_metrics'].items():
            if data['engagement_rate'] == 0:
                alerts.append({
                    'severity': 'high',
                    'type': 'abandoned_pillar',
                    'message': f'{pillar} pillar has no active routines',
                    'action': f'Consider reactivating at least one {pillar} routine'
                })
        
        # Check for rapid decline
        predictions = trends.get('predictions', {})
        next_engagement = predictions.get('next_week_engagement', {})
        
        if (next_engagement.get('predicted_score', 50) < 30 and 
            next_engagement.get('confidence') in ['high', 'medium']):
            alerts.append({
                'severity': 'high',
                'type': 'engagement_decline',
                'message': 'Engagement predicted to drop below 30%',
                'action': 'Review and simplify your routine schedule'
            })
        
        # Check for overload
        if metrics['summary']['total_routines'] > 30 and metrics['engagement_metrics']['engagement_score'] < 40:
            alerts.append({
                'severity': 'medium',
                'type': 'routine_overload',
                'message': 'Too many routines may be affecting engagement',
                'action': 'Consider focusing on 15-20 key routines'
            })
        
        return alerts
    
    def _categorize_performance(self, score: float) -> str:
        """Categorize performance based on score."""
        if score >= 80:
            return 'excellent'
        elif score >= 60:
            return 'good'
        elif score >= 40:
            return 'fair'
        else:
            return 'needs_improvement'
    
    def _categorize_engagement(self, rate: float) -> str:
        """Categorize engagement based on rate."""
        if rate >= 0.8:
            return 'high'
        elif rate >= 0.5:
            return 'moderate'
        elif rate >= 0.2:
            return 'low'
        else:
            return 'minimal'
    
    def _summarize_trends(self, trends: Dict[str, Any]) -> str:
        """Create a summary of overall trends."""
        if 'engagement_trends' not in trends:
            return "Insufficient data for trend analysis"
        
        engagement_trend = trends['engagement_trends']['overall_engagement']['trend']
        
        if engagement_trend['direction'] == 'increasing':
            return f"Your engagement is improving (↑{engagement_trend['slope']*100:.1f}% per period)"
        elif engagement_trend['direction'] == 'decreasing':
            return f"Your engagement is declining (↓{abs(engagement_trend['slope'])*100:.1f}% per period)"
        else:
            return "Your engagement is stable"
    
    def _identify_focus_areas(self, metrics: Dict[str, Any]) -> List[str]:
        """Identify top focus areas."""
        focus_areas = []
        
        # Find pillars needing attention
        pillar_scores = [
            (pillar, data['completion_score']) 
            for pillar, data in metrics['pillar_metrics'].items()
        ]
        pillar_scores.sort(key=lambda x: x[1])
        
        # Add bottom 2 pillars if they're below 50
        for pillar, score in pillar_scores[:2]:
            if score < 50:
                focus_areas.append(f"Improve {pillar} engagement")
        
        # Check for consistency issues
        low_consistency = [
            pillar for pillar, data in metrics['pillar_metrics'].items()
            if data['consistency_score'] < 40
        ]
        if low_consistency:
            focus_areas.append(f"Build consistency in {', '.join(low_consistency[:2])}")
        
        return focus_areas[:3]  # Top 3 focus areas
    
    def _analyze_performance_distribution(self, routine_metrics: List[Dict]) -> Dict[str, int]:
        """Analyze distribution of routine performance."""
        distribution = {
            'excellent': 0,
            'good': 0,
            'fair': 0,
            'needs_improvement': 0
        }
        
        for routine in routine_metrics:
            rating = routine['performance_rating']
            distribution[rating] += 1
        
        return distribution
    
    def _generate_routine_suggestion(self, routine: Dict) -> str:
        """Generate suggestion for improving a routine."""
        if routine['completion_pattern'] == 'consistent_low':
            return "This routine isn't working - consider replacing it or adjusting the schedule"
        elif routine['completion_pattern'] == 'declining':
            return "Engagement is dropping - try pairing with a successful routine"
        elif routine['schedule_category'] == 'DAILY_ROUTINE':
            return "Daily routines can be challenging - consider switching to weekly"
        else:
            return "Start small - aim for just once this week"
    
    def _generate_risk_mitigation(self, risk: Dict) -> str:
        """Generate mitigation recommendation for a risk."""
        risk_type = risk['type']
        
        if risk_type == 'engagement_decline':
            return "Simplify your routine schedule - focus on 3-5 key routines this week"
        elif risk_type == 'abandoned_pillar':
            return f"Reactivate {risk['description'].split()[0]} with just one simple routine"
        elif risk_type == 'high_volatility':
            return "Focus on consistency rather than perfection - small steps daily"
        else:
            return "Review and adjust your routine schedule to better fit your lifestyle"
    
    def _load_insight_templates(self) -> Dict[str, str]:
        """Load insight message templates."""
        return {
            'high_performer': "Excellent work on {routine}! You've maintained {rate}% completion.",
            'improving': "{pillar} is showing great improvement - up {percent}% this period!",
            'needs_attention': "{pillar} needs attention - only {rate}% of routines are active.",
            'consistency_champion': "Great consistency in {pillar} - keep up the steady progress!",
            'momentum_building': "You're building momentum in {pillar} - this is the perfect time to push forward!"
        }