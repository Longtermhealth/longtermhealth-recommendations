"""Process incoming completion events and extract analytics data."""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EventProcessor:
    """Process completion events from webhooks and extract analytics data."""
    
    def __init__(self):
        self.processed_events = []
    
    def process_completion_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a completion event payload and extract analytics data.
        
        Args:
            payload: The webhook payload containing completion statistics
            
        Returns:
            Processed analytics data
        """
        logger.info(f"Processing completion event for account {payload.get('accountId')}")
        
        analytics_data = {
            'account_id': payload.get('accountId'),
            'action_plan_id': payload.get('actionPlanUniqueId'),
            'start_date': payload.get('startDate'),
            'period_days': payload.get('periodInDays'),
            'timestamp': datetime.utcnow().isoformat(),
            'pillar_analytics': self._process_pillar_stats(payload.get('pillarCompletionStats', [])),
            'change_events': self._process_change_log(payload.get('changeLog', [])),
            'summary': {}
        }
        
        # Calculate summary statistics
        analytics_data['summary'] = self._calculate_summary(analytics_data['pillar_analytics'])
        
        self.processed_events.append(analytics_data)
        return analytics_data
    
    def _process_pillar_stats(self, pillar_stats: List[Dict]) -> Dict[str, Any]:
        """Process pillar completion statistics."""
        pillar_analytics = {}
        
        for pillar in pillar_stats:
            pillar_enum = pillar.get('pillarEnum')
            routines = pillar.get('routineCompletionStats', [])
            
            pillar_data = {
                'total_routines': len(routines),
                'routines_with_data': 0,
                'total_completions': 0,
                'completion_by_period': {'week': {}, 'month': {}},
                'routine_details': []
            }
            
            for routine in routines:
                routine_info = self._process_routine_stats(routine)
                if routine_info['has_completion_data']:
                    pillar_data['routines_with_data'] += 1
                pillar_data['total_completions'] += routine_info['total_completions']
                pillar_data['routine_details'].append(routine_info)
                
                # Aggregate completion by period
                for stat in routine_info['completion_stats']:
                    period_unit = stat['period_unit'].lower()
                    period_no = stat['period_sequence']
                    
                    if period_no not in pillar_data['completion_by_period'][period_unit]:
                        pillar_data['completion_by_period'][period_unit][period_no] = 0
                    
                    pillar_data['completion_by_period'][period_unit][period_no] += stat['completion_rate']
            
            # Calculate engagement rate
            if pillar_data['total_routines'] > 0:
                pillar_data['engagement_rate'] = pillar_data['routines_with_data'] / pillar_data['total_routines']
            else:
                pillar_data['engagement_rate'] = 0
            
            pillar_analytics[pillar_enum] = pillar_data
        
        return pillar_analytics
    
    def _process_routine_stats(self, routine: Dict) -> Dict[str, Any]:
        """Process individual routine completion statistics."""
        completion_stats = routine.get('completionStatistics', [])
        
        routine_info = {
            'routine_id': routine.get('routineUniqueId'),
            'display_name': routine.get('displayName'),
            'schedule_category': routine.get('scheduleCategory'),
            'has_completion_data': len(completion_stats) > 0,
            'total_completions': 0,
            'completion_stats': []
        }
        
        for stat in completion_stats:
            stat_info = {
                'completion_rate': stat.get('completionRate', 0),
                'period_unit': stat.get('completionRatePeriodUnit', ''),
                'period_sequence': stat.get('periodSequenceNo', 0),
                'completion_unit': stat.get('completionUnit', ''),
                'target_total': stat.get('completionTargetTotal', 0),
                'completed_total': stat.get('completedValueTotal', 0)
            }
            routine_info['completion_stats'].append(stat_info)
            routine_info['total_completions'] += stat_info['completion_rate']
        
        return routine_info
    
    def _process_change_log(self, change_log: List[Dict]) -> List[Dict[str, Any]]:
        """Process change log events."""
        processed_changes = []
        
        for change in change_log:
            change_info = {
                'event_type': change.get('eventEnum'),
                'event_date': change.get('eventDate'),
                'target_id': change.get('targetId'),
                'change_target': change.get('changeTarget'),
                'event_details': change.get('eventDetails', {}),
                'changes': []
            }
            
            for detail in change.get('changes', []):
                change_info['changes'].append({
                    'property': detail.get('changedProperty'),
                    'old_value': detail.get('oldValue'),
                    'new_value': detail.get('newValue')
                })
            
            processed_changes.append(change_info)
        
        return processed_changes
    
    def _calculate_summary(self, pillar_analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary statistics across all pillars."""
        summary = {
            'total_pillars': len(pillar_analytics),
            'active_pillars': 0,
            'total_routines': 0,
            'engaged_routines': 0,
            'total_completions': 0,
            'average_engagement_rate': 0,
            'most_active_pillar': None,
            'least_active_pillar': None
        }
        
        max_completions = 0
        min_completions = float('inf')
        total_engagement = 0
        
        for pillar, data in pillar_analytics.items():
            summary['total_routines'] += data['total_routines']
            summary['engaged_routines'] += data['routines_with_data']
            summary['total_completions'] += data['total_completions']
            
            if data['routines_with_data'] > 0:
                summary['active_pillars'] += 1
            
            total_engagement += data['engagement_rate']
            
            # Track most/least active pillars
            if data['total_completions'] > max_completions:
                max_completions = data['total_completions']
                summary['most_active_pillar'] = pillar
            
            if data['total_completions'] < min_completions:
                min_completions = data['total_completions']
                summary['least_active_pillar'] = pillar
        
        # Calculate average engagement rate
        if summary['total_pillars'] > 0:
            summary['average_engagement_rate'] = total_engagement / summary['total_pillars']
        
        # Overall engagement rate
        if summary['total_routines'] > 0:
            summary['overall_engagement_rate'] = summary['engaged_routines'] / summary['total_routines']
        else:
            summary['overall_engagement_rate'] = 0
        
        return summary
    
    def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent processed events."""
        return self.processed_events[-limit:]