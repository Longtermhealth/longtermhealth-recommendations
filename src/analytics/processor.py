"""Analytics processor for webhook data"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from src.analytics.models import (
    CompletionStatistic, PillarCompletion, RoutineCompletion,
    UserAnalytics, CompletionUnit, PeriodUnit, Pillar
)

logger = logging.getLogger(__name__)


class AnalyticsProcessor:
    """Process webhook data into actionable analytics"""
    
    def __init__(self):
        self.completion_threshold_low = 50.0
        self.completion_threshold_high = 80.0
        self.trend_window = 3  # Number of periods to analyze for trends
    
    def process_webhook_data(self, webhook_data: Dict) -> UserAnalytics:
        """
        Process raw webhook data into structured analytics
        
        Args:
            webhook_data: Raw webhook payload
            
        Returns:
            UserAnalytics object with processed data
        """
        user_id = webhook_data.get('userId', 'unknown')
        
        # Process pillar completions
        pillar_completions = self._process_pillar_completions(
            webhook_data.get('pillarCompletionStats', {})
        )
        
        # Process routine completions
        routine_completions = self._process_routine_completions(
            webhook_data.get('routineCompletionStats', {}),
            webhook_data.get('completionStatistics', []),
            webhook_data.get('changeLog', [])
        )
        
        # Calculate overall metrics
        overall_completion = self._calculate_overall_completion(routine_completions)
        engagement_score = self._calculate_engagement_score(
            pillar_completions, routine_completions
        )
        
        return UserAnalytics(
            user_id=user_id,
            timestamp=datetime.utcnow(),
            pillar_completions=pillar_completions,
            routine_completions=routine_completions,
            overall_completion_rate=overall_completion,
            engagement_score=engagement_score
        )
    
    def _process_pillar_completions(self, pillar_stats: Dict) -> Dict[str, PillarCompletion]:
        """Process pillar completion statistics"""
        completions = {}
        
        for pillar_name, stats in pillar_stats.items():
            try:
                pillar = Pillar(pillar_name)
                completion_rate = float(stats.get('completionRate', 0))
                total = int(stats.get('totalRoutines', 0))
                completed = int(stats.get('completedRoutines', 0))
                
                completions[pillar_name] = PillarCompletion(
                    pillar=pillar,
                    completion_rate=completion_rate,
                    total_routines=total,
                    completed_routines=completed
                )
            except (ValueError, KeyError) as e:
                logger.warning(f"Error processing pillar {pillar_name}: {e}")
                
        return completions
    
    def _process_routine_completions(
        self, 
        routine_stats: Dict,
        completion_statistics: List[Dict],
        change_log: List[Dict]
    ) -> Dict[str, RoutineCompletion]:
        """Process routine completion data"""
        completions = {}
        
        # Group statistics by routine
        stats_by_routine = defaultdict(list)
        for stat in completion_statistics:
            routine_id = stat.get('routineId')
            if routine_id:
                stats_by_routine[routine_id].append(stat)
        
        # Group changes by routine
        changes_by_routine = defaultdict(list)
        for change in change_log:
            routine_id = change.get('routineId')
            if routine_id:
                changes_by_routine[routine_id].append(change)
        
        # Create routine completion objects
        for routine_id, stats in stats_by_routine.items():
            routine_info = routine_stats.get(routine_id, {})
            
            completion_stats = []
            for stat in stats:
                try:
                    completion_stats.append(CompletionStatistic(
                        completion_rate=int(stat.get('completionRate', 0)),
                        completion_rate_period_unit=PeriodUnit(stat.get('completionRatePeriodUnit', 'WEEK')),
                        period_sequence_no=int(stat.get('periodSequenceNo', 0)),
                        completion_unit=CompletionUnit(stat.get('completionUnit', 'ROUTINE')),
                        completion_target_total=float(stat.get('completionTargetTotal', 0)),
                        completed_value_total=float(stat.get('completedValueTotal', 0))
                    ))
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error processing completion stat for routine {routine_id}: {e}")
            
            completions[routine_id] = RoutineCompletion(
                routine_id=routine_id,
                routine_name=routine_info.get('name', f'Routine {routine_id}'),
                pillar=Pillar(routine_info.get('pillar', 'MOVEMENT')),
                completion_stats=completion_stats,
                schedule_changes=changes_by_routine.get(routine_id, [])
            )
        
        return completions
    
    def _calculate_overall_completion(self, routine_completions: Dict[str, RoutineCompletion]) -> float:
        """Calculate overall completion rate across all routines"""
        if not routine_completions:
            return 0.0
            
        total_completion = sum(
            routine.average_completion_rate 
            for routine in routine_completions.values()
        )
        return total_completion / len(routine_completions)
    
    def _calculate_engagement_score(
        self,
        pillar_completions: Dict[str, PillarCompletion],
        routine_completions: Dict[str, RoutineCompletion]
    ) -> float:
        """
        Calculate user engagement score (0-100)
        
        Factors:
        - Overall completion rate (40%)
        - Consistency across pillars (30%)
        - Trend direction (30%)
        """
        # Overall completion component
        overall_completion = self._calculate_overall_completion(routine_completions)
        completion_score = overall_completion * 0.4
        
        # Pillar consistency component
        if pillar_completions:
            success_rates = [p.success_rate for p in pillar_completions.values()]
            avg_rate = sum(success_rates) / len(success_rates)
            variance = sum((rate - avg_rate) ** 2 for rate in success_rates) / len(success_rates)
            consistency_score = max(0, (100 - variance) * 0.3)
        else:
            consistency_score = 0
        
        # Trend component
        improving_count = sum(
            1 for routine in routine_completions.values()
            if routine.trend == "improving"
        )
        total_routines = len(routine_completions)
        trend_score = (improving_count / total_routines * 100 * 0.3) if total_routines > 0 else 0
        
        return completion_score + consistency_score + trend_score