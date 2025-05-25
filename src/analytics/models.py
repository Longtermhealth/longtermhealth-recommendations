"""Analytics data models"""

from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class CompletionUnit(Enum):
    REPETITIONS = "REPETITIONS"
    MINUTES = "MINUTES"
    SECONDS = "SECONDS"
    ROUTINE = "ROUTINE"


class PeriodUnit(Enum):
    WEEK = "WEEK"
    MONTH = "MONTH"


class Pillar(Enum):
    MOVEMENT = "MOVEMENT"
    NUTRITION = "NUTRITION"
    SLEEP = "SLEEP"
    MINDFULNESS = "MINDFULNESS"
    SOCIAL = "SOCIAL"
    COGNITION = "COGNITION"
    ENVIRONMENT = "ENVIRONMENT"


@dataclass
class CompletionStatistic:
    """Individual completion statistic from webhook"""
    completion_rate: int
    completion_rate_period_unit: PeriodUnit
    period_sequence_no: int
    completion_unit: CompletionUnit
    completion_target_total: float
    completed_value_total: float
    
    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage"""
        if self.completion_target_total == 0:
            return 0.0
        return (self.completed_value_total / self.completion_target_total) * 100


@dataclass
class PillarCompletion:
    """Pillar completion statistics"""
    pillar: Pillar
    completion_rate: float
    total_routines: int
    completed_routines: int
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate for the pillar"""
        if self.total_routines == 0:
            return 0.0
        return (self.completed_routines / self.total_routines) * 100


@dataclass
class RoutineCompletion:
    """Routine completion data"""
    routine_id: str
    routine_name: str
    pillar: Pillar
    completion_stats: List[CompletionStatistic] = field(default_factory=list)
    schedule_changes: List[Dict] = field(default_factory=list)
    
    @property
    def average_completion_rate(self) -> float:
        """Calculate average completion rate across all periods"""
        if not self.completion_stats:
            return 0.0
        total = sum(stat.completion_percentage for stat in self.completion_stats)
        return total / len(self.completion_stats)
    
    @property
    def trend(self) -> str:
        """Determine completion trend (improving/declining/stable)"""
        if len(self.completion_stats) < 2:
            return "insufficient_data"
        
        recent = self.completion_stats[-3:]  # Last 3 periods
        if len(recent) < 2:
            return "insufficient_data"
            
        # Calculate trend based on recent periods
        first_half_avg = sum(stat.completion_percentage for stat in recent[:len(recent)//2]) / (len(recent)//2)
        second_half_avg = sum(stat.completion_percentage for stat in recent[len(recent)//2:]) / (len(recent) - len(recent)//2)
        
        if second_half_avg > first_half_avg * 1.1:
            return "improving"
        elif second_half_avg < first_half_avg * 0.9:
            return "declining"
        else:
            return "stable"


@dataclass
class UserAnalytics:
    """Complete user analytics snapshot"""
    user_id: str
    timestamp: datetime
    pillar_completions: Dict[str, PillarCompletion]
    routine_completions: Dict[str, RoutineCompletion]
    overall_completion_rate: float
    engagement_score: float
    
    @property
    def struggling_routines(self) -> List[RoutineCompletion]:
        """Identify routines with low completion rates"""
        threshold = 50.0  # 50% completion threshold
        return [
            routine for routine in self.routine_completions.values()
            if routine.average_completion_rate < threshold
        ]
    
    @property
    def successful_routines(self) -> List[RoutineCompletion]:
        """Identify routines with high completion rates"""
        threshold = 80.0  # 80% completion threshold
        return [
            routine for routine in self.routine_completions.values()
            if routine.average_completion_rate >= threshold
        ]
    
    @property
    def pillar_rankings(self) -> List[tuple[str, float]]:
        """Rank pillars by success rate"""
        rankings = [
            (pillar, data.success_rate) 
            for pillar, data in self.pillar_completions.items()
        ]
        return sorted(rankings, key=lambda x: x[1], reverse=True)