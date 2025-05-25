"""Analyze trends in completion data over time."""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """Analyze trends and patterns in user completion data."""
    
    def __init__(self):
        self.trend_cache = defaultdict(list)
    
    def analyze_trends(self, historical_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze trends from historical metrics data.
        
        Args:
            historical_metrics: List of historical metrics from MetricsCalculator
            
        Returns:
            Trend analysis results
        """
        if len(historical_metrics) < 2:
            return self._empty_trends()
        
        trends = {
            'period_analyzed': {
                'start': historical_metrics[0]['timestamp'],
                'end': historical_metrics[-1]['timestamp'],
                'days': self._calculate_days_between(historical_metrics[0]['timestamp'], historical_metrics[-1]['timestamp'])
            },
            'pillar_trends': self._analyze_pillar_trends(historical_metrics),
            'routine_trends': self._analyze_routine_trends(historical_metrics),
            'engagement_trends': self._analyze_engagement_trends(historical_metrics),
            'pattern_analysis': self._analyze_patterns(historical_metrics),
            'predictions': self._generate_predictions(historical_metrics)
        }
        
        return trends
    
    def _analyze_pillar_trends(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends for each pillar."""
        pillar_trends = {}
        
        # Extract time series for each pillar
        pillar_series = defaultdict(lambda: {'completion_scores': [], 'engagement_rates': [], 'timestamps': []})
        
        for metric in metrics:
            timestamp = datetime.fromisoformat(metric['timestamp'])
            
            for pillar, data in metric['pillar_metrics'].items():
                pillar_series[pillar]['completion_scores'].append(data['completion_score'])
                pillar_series[pillar]['engagement_rates'].append(data['engagement_rate'])
                pillar_series[pillar]['timestamps'].append(timestamp)
        
        # Analyze each pillar
        for pillar, series in pillar_series.items():
            pillar_trends[pillar] = {
                'completion_trend': self._calculate_trend(series['completion_scores']),
                'engagement_trend': self._calculate_trend(series['engagement_rates']),
                'volatility': self._calculate_volatility(series['completion_scores']),
                'momentum': self._calculate_momentum(series['completion_scores']),
                'forecast': self._forecast_next_period(series['completion_scores'])
            }
        
        return pillar_trends
    
    def _analyze_routine_trends(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends for individual routines."""
        routine_performance = defaultdict(lambda: {'adherence_rates': [], 'timestamps': []})
        
        for metric in metrics:
            timestamp = datetime.fromisoformat(metric['timestamp'])
            
            for routine in metric['routine_metrics']:
                key = f"{routine['routine_id']}_{routine['routine_name']}"
                routine_performance[key]['adherence_rates'].append(routine['adherence_rate'])
                routine_performance[key]['timestamps'].append(timestamp)
        
        # Identify top improving and declining routines
        improvements = []
        declines = []
        
        for routine_key, data in routine_performance.items():
            if len(data['adherence_rates']) >= 2:
                trend = self._calculate_trend(data['adherence_rates'])
                
                if trend['direction'] == 'increasing' and trend['strength'] > 0.1:
                    improvements.append({
                        'routine': routine_key.split('_', 1)[1],
                        'improvement_rate': trend['slope'],
                        'current_adherence': data['adherence_rates'][-1]
                    })
                elif trend['direction'] == 'decreasing' and abs(trend['strength']) > 0.1:
                    declines.append({
                        'routine': routine_key.split('_', 1)[1],
                        'decline_rate': abs(trend['slope']),
                        'current_adherence': data['adherence_rates'][-1]
                    })
        
        # Sort by rate of change
        improvements.sort(key=lambda x: x['improvement_rate'], reverse=True)
        declines.sort(key=lambda x: x['decline_rate'], reverse=True)
        
        return {
            'top_improving': improvements[:5],
            'top_declining': declines[:5],
            'total_routines_analyzed': len(routine_performance)
        }
    
    def _analyze_engagement_trends(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall engagement trends."""
        engagement_scores = []
        completion_velocities = []
        habit_indices = []
        timestamps = []
        
        for metric in metrics:
            engagement_scores.append(metric['engagement_metrics']['engagement_score'])
            completion_velocities.append(metric['performance_indicators']['completion_velocity'])
            habit_indices.append(metric['performance_indicators']['habit_formation_index'])
            timestamps.append(datetime.fromisoformat(metric['timestamp']))
        
        # Calculate trends
        engagement_trend = self._calculate_trend(engagement_scores)
        habit_trend = self._calculate_trend(habit_indices)
        
        # Analyze velocity changes
        velocity_distribution = {
            'accelerating': completion_velocities.count('accelerating'),
            'stable': completion_velocities.count('stable'),
            'decelerating': completion_velocities.count('decelerating')
        }
        
        return {
            'overall_engagement': {
                'trend': engagement_trend,
                'current_score': engagement_scores[-1] if engagement_scores else 0,
                'average_score': np.mean(engagement_scores) if engagement_scores else 0,
                'peak_score': max(engagement_scores) if engagement_scores else 0
            },
            'habit_formation': {
                'trend': habit_trend,
                'current_index': habit_indices[-1] if habit_indices else 0,
                'improvement_rate': habit_trend['slope'] if habit_trend else 0
            },
            'velocity_analysis': velocity_distribution
        }
    
    def _analyze_patterns(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in user behavior."""
        patterns = {
            'weekly_patterns': self._analyze_weekly_patterns(metrics),
            'pillar_correlations': self._analyze_pillar_correlations(metrics),
            'engagement_clusters': self._identify_engagement_clusters(metrics),
            'consistency_patterns': self._analyze_consistency_patterns(metrics)
        }
        
        return patterns
    
    def _analyze_weekly_patterns(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze weekly patterns in completion data."""
        # Group metrics by day of week
        day_patterns = defaultdict(list)
        
        for metric in metrics:
            timestamp = datetime.fromisoformat(metric['timestamp'])
            day_of_week = timestamp.strftime('%A')
            
            # Calculate total completions for this metric
            total_completions = sum(
                data['total_completions'] 
                for data in metric.get('pillar_analytics', {}).values()
            )
            
            day_patterns[day_of_week].append(total_completions)
        
        # Calculate average completions by day
        avg_by_day = {
            day: np.mean(completions) if completions else 0
            for day, completions in day_patterns.items()
        }
        
        # Find best and worst days
        if avg_by_day:
            best_day = max(avg_by_day.items(), key=lambda x: x[1])
            worst_day = min(avg_by_day.items(), key=lambda x: x[1])
        else:
            best_day = worst_day = ('N/A', 0)
        
        return {
            'average_by_day': avg_by_day,
            'best_day': {'day': best_day[0], 'average_completions': best_day[1]},
            'worst_day': {'day': worst_day[0], 'average_completions': worst_day[1]}
        }
    
    def _analyze_pillar_correlations(self, metrics: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze correlations between pillar performances."""
        # Extract time series for each pillar
        pillar_scores = defaultdict(list)
        
        for metric in metrics:
            for pillar, data in metric['pillar_metrics'].items():
                pillar_scores[pillar].append(data['completion_score'])
        
        # Calculate correlations
        correlations = {}
        pillars = list(pillar_scores.keys())
        
        for i in range(len(pillars)):
            for j in range(i + 1, len(pillars)):
                pillar1, pillar2 = pillars[i], pillars[j]
                
                if len(pillar_scores[pillar1]) >= 3 and len(pillar_scores[pillar2]) >= 3:
                    # Check if arrays have variance (not constant)
                    if np.std(pillar_scores[pillar1]) > 0 and np.std(pillar_scores[pillar2]) > 0:
                        correlation, _ = stats.pearsonr(pillar_scores[pillar1], pillar_scores[pillar2])
                        correlations[f"{pillar1}_vs_{pillar2}"] = round(correlation, 3)
        
        return correlations
    
    def _identify_engagement_clusters(self, metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify clusters of high/low engagement periods."""
        engagement_scores = [m['engagement_metrics']['engagement_score'] for m in metrics]
        
        if len(engagement_scores) < 3:
            return []
        
        # Simple clustering based on standard deviation
        mean_engagement = np.mean(engagement_scores)
        std_engagement = np.std(engagement_scores)
        
        clusters = []
        current_cluster = None
        
        for i, (metric, score) in enumerate(zip(metrics, engagement_scores)):
            if score > mean_engagement + std_engagement:
                cluster_type = 'high_engagement'
            elif score < mean_engagement - std_engagement:
                cluster_type = 'low_engagement'
            else:
                cluster_type = 'normal'
            
            if current_cluster and current_cluster['type'] == cluster_type:
                current_cluster['end'] = metric['timestamp']
                current_cluster['duration_days'] += 1
                current_cluster['average_score'] = (
                    current_cluster['average_score'] * (current_cluster['duration_days'] - 1) + score
                ) / current_cluster['duration_days']
            else:
                if current_cluster and current_cluster['duration_days'] >= 2:
                    clusters.append(current_cluster)
                
                current_cluster = {
                    'type': cluster_type,
                    'start': metric['timestamp'],
                    'end': metric['timestamp'],
                    'duration_days': 1,
                    'average_score': score
                }
        
        if current_cluster and current_cluster['duration_days'] >= 2:
            clusters.append(current_cluster)
        
        return clusters
    
    def _analyze_consistency_patterns(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze consistency patterns across pillars."""
        consistency_scores = defaultdict(list)
        
        for metric in metrics:
            for pillar, data in metric['pillar_metrics'].items():
                consistency_scores[pillar].append(data.get('consistency_score', 0))
        
        # Calculate consistency trends
        consistency_analysis = {}
        
        for pillar, scores in consistency_scores.items():
            if len(scores) >= 2:
                trend = self._calculate_trend(scores)
                consistency_analysis[pillar] = {
                    'current_consistency': scores[-1] if scores else 0,
                    'average_consistency': np.mean(scores),
                    'trend': trend['direction'],
                    'is_improving': trend['direction'] == 'increasing'
                }
        
        return consistency_analysis
    
    def _generate_predictions(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate predictions based on historical trends."""
        if len(metrics) < 3:
            return {'status': 'insufficient_data'}
        
        predictions = {
            'next_week_engagement': self._predict_next_engagement(metrics),
            'pillar_forecasts': self._predict_pillar_performance(metrics),
            'risk_analysis': self._analyze_risks(metrics),
            'opportunity_analysis': self._analyze_opportunities(metrics)
        }
        
        return predictions
    
    def _predict_next_engagement(self, metrics: List[Dict[str, Any]]) -> Dict[str, float]:
        """Predict next week's engagement score."""
        engagement_scores = [m['engagement_metrics']['engagement_score'] for m in metrics]
        
        if len(engagement_scores) < 3:
            return {'predicted_score': engagement_scores[-1] if engagement_scores else 50}
        
        # Simple linear regression prediction
        x = np.arange(len(engagement_scores))
        slope, intercept, _, _, _ = stats.linregress(x, engagement_scores)
        
        next_score = slope * len(engagement_scores) + intercept
        
        # Bound prediction between 0 and 100
        next_score = max(0, min(100, next_score))
        
        return {
            'predicted_score': round(next_score, 1),
            'confidence': 'high' if abs(slope) > 0.5 else 'medium' if abs(slope) > 0.1 else 'low',
            'trend_strength': abs(slope)
        }
    
    def _predict_pillar_performance(self, metrics: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """Predict performance for each pillar."""
        pillar_predictions = {}
        
        # Extract pillar scores
        pillar_scores = defaultdict(list)
        for metric in metrics:
            for pillar, data in metric['pillar_metrics'].items():
                pillar_scores[pillar].append(data['completion_score'])
        
        # Predict for each pillar
        for pillar, scores in pillar_scores.items():
            if len(scores) >= 3:
                forecast = self._forecast_next_period(scores)
                pillar_predictions[pillar] = {
                    'predicted_score': forecast['value'],
                    'trend': forecast['trend'],
                    'confidence': forecast['confidence']
                }
        
        return pillar_predictions
    
    def _analyze_risks(self, metrics: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Analyze risks based on trends."""
        risks = []
        
        # Check for declining engagement
        engagement_scores = [m['engagement_metrics']['engagement_score'] for m in metrics[-3:]]
        if len(engagement_scores) == 3 and all(engagement_scores[i] > engagement_scores[i+1] for i in range(2)):
            risks.append({
                'type': 'engagement_decline',
                'severity': 'high',
                'description': 'Engagement has been declining for 3 consecutive periods'
            })
        
        # Check for abandoned pillars
        latest_metric = metrics[-1]
        for pillar, data in latest_metric['pillar_metrics'].items():
            if data['engagement_rate'] < 0.1:
                risks.append({
                    'type': 'abandoned_pillar',
                    'severity': 'medium',
                    'description': f'{pillar} pillar has very low engagement (<10%)'
                })
        
        # Check for high volatility
        for pillar, trends in self._analyze_pillar_trends(metrics).items():
            if trends['volatility'] > 30:
                risks.append({
                    'type': 'high_volatility',
                    'severity': 'low',
                    'description': f'{pillar} pillar shows high volatility in performance'
                })
        
        return risks
    
    def _analyze_opportunities(self, metrics: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Identify opportunities for improvement."""
        opportunities = []
        
        latest_metric = metrics[-1]
        
        # Check for pillars with momentum
        pillar_trends = self._analyze_pillar_trends(metrics)
        for pillar, trends in pillar_trends.items():
            if trends['momentum'] > 0.5 and trends['completion_trend']['direction'] == 'increasing':
                opportunities.append({
                    'type': 'positive_momentum',
                    'pillar': pillar,
                    'description': f'{pillar} pillar is showing strong positive momentum - capitalize on this trend'
                })
        
        # Check for quick wins
        for routine in latest_metric['routine_metrics']:
            if 0.3 <= routine['adherence_rate'] <= 0.6:
                opportunities.append({
                    'type': 'quick_win',
                    'routine': routine['routine_name'],
                    'description': f'{routine["routine_name"]} is at {routine["adherence_rate"]*100:.0f}% - small effort could push it to consistent completion'
                })
        
        return opportunities[:5]  # Top 5 opportunities
    
    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend from a series of values."""
        if len(values) < 2:
            return {'direction': 'insufficient_data', 'slope': 0, 'strength': 0}
        
        x = np.arange(len(values))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
        
        # Determine direction
        if abs(slope) < 0.01:
            direction = 'stable'
        elif slope > 0:
            direction = 'increasing'
        else:
            direction = 'decreasing'
        
        return {
            'direction': direction,
            'slope': round(slope, 4),
            'strength': abs(r_value),
            'p_value': p_value
        }
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility as coefficient of variation."""
        if len(values) < 2:
            return 0
        
        mean_val = np.mean(values)
        if mean_val == 0:
            return 0
        
        std_val = np.std(values)
        return (std_val / mean_val) * 100
    
    def _calculate_momentum(self, values: List[float]) -> float:
        """Calculate momentum as rate of change."""
        if len(values) < 3:
            return 0
        
        recent_change = values[-1] - values[-2]
        previous_change = values[-2] - values[-3]
        
        if previous_change == 0:
            return 0
        
        return recent_change / abs(previous_change)
    
    def _forecast_next_period(self, values: List[float]) -> Dict[str, Any]:
        """Simple forecast for next period."""
        if len(values) < 2:
            return {'value': values[-1] if values else 50, 'trend': 'stable', 'confidence': 'low'}
        
        trend = self._calculate_trend(values)
        
        # Simple linear extrapolation
        next_value = values[-1] + trend['slope']
        
        # Bound between 0 and 100
        next_value = max(0, min(100, next_value))
        
        # Determine confidence based on trend strength
        if trend['strength'] > 0.8:
            confidence = 'high'
        elif trend['strength'] > 0.5:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        return {
            'value': round(next_value, 1),
            'trend': trend['direction'],
            'confidence': confidence
        }
    
    def _calculate_days_between(self, start: str, end: str) -> int:
        """Calculate days between two ISO format timestamps."""
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        return (end_dt - start_dt).days
    
    def _empty_trends(self) -> Dict[str, Any]:
        """Return empty trends structure when insufficient data."""
        return {
            'status': 'insufficient_data',
            'message': 'At least 2 data points required for trend analysis'
        }