"""Demo script showing how to use the new analytics functionality"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analytics import AnalyticsService


def demo_analytics():
    """Demonstrate the analytics service functionality"""
    
    # Initialize the service
    analytics_service = AnalyticsService()
    
    # Sample event data (like what you showed in the logs)
    event_data = {
        "actionPlanUniqueId": "1fadcdea-1536-47b8-a39c-5de3ef85fcd1",
        "accountId": 5,
        "startDate": "2025-05-16T00:00:00.000Z",
        "periodInDays": 28,
        "pillarCompletionStats": [
            {
                "pillarEnum": "MOVEMENT",
                "routineCompletionStats": [
                    {
                        "routineUniqueId": 461,
                        "displayName": "Sprung-Ausfallschritte",
                        "scheduleCategory": "WEEKLY_ROUTINE",
                        "completionStatistics": [
                            {
                                "completionRate": 1,
                                "completionRatePeriodUnit": "WEEK",
                                "periodSequenceNo": 2,
                                "completionUnit": "REPETITIONS",
                                "completionTargetTotal": 0,
                                "completedValueTotal": 0
                            }
                        ]
                    },
                    {
                        "routineUniqueId": 64,
                        "displayName": "Hampelmänner",
                        "scheduleCategory": "WEEKLY_ROUTINE",
                        "completionStatistics": []
                    }
                ]
            },
            {
                "pillarEnum": "NUTRITION",
                "routineCompletionStats": [
                    {
                        "routineUniqueId": 124,
                        "displayName": "3 Handvoll Gemüse täglich",
                        "scheduleCategory": "DAILY_ROUTINE",
                        "completionStatistics": [
                            {
                                "completionRate": 1,
                                "completionRatePeriodUnit": "WEEK",
                                "periodSequenceNo": 2,
                                "completionUnit": "ROUTINE",
                                "completionTargetTotal": 0,
                                "completedValueTotal": 0
                            }
                        ]
                    }
                ]
            },
            {
                "pillarEnum": "GRATITUDE",
                "routineCompletionStats": [
                    {
                        "routineUniqueId": 154,
                        "displayName": "Maui-Gewohnheit",
                        "scheduleCategory": "DAILY_ROUTINE",
                        "completionStatistics": [
                            {
                                "completionRate": 3,
                                "completionRatePeriodUnit": "WEEK",
                                "periodSequenceNo": 1,
                                "completionUnit": "SECONDS",
                                "completionTargetTotal": 0,
                                "completedValueTotal": 0
                            },
                            {
                                "completionRate": 4,
                                "completionRatePeriodUnit": "WEEK",
                                "periodSequenceNo": 2,
                                "completionUnit": "SECONDS",
                                "completionTargetTotal": 0,
                                "completedValueTotal": 0
                            },
                            {
                                "completionRate": 7,
                                "completionRatePeriodUnit": "MONTH",
                                "periodSequenceNo": 1,
                                "completionUnit": "SECONDS",
                                "completionTargetTotal": 0,
                                "completedValueTotal": 0
                            }
                        ]
                    }
                ]
            }
        ],
        "changeLog": []
    }
    
    print("=== Analytics Demo ===\n")
    
    # Process the event
    print("1. Processing completion event...")
    result = analytics_service.process_event(event_data)
    
    # Display summary
    print(f"\nAccount ID: {result['account_id']}")
    print(f"Action Plan ID: {result['action_plan_id']}")
    print(f"\nSummary:")
    print(f"  - Total Pillars: {result['summary']['total_pillars']}")
    print(f"  - Active Pillars: {result['summary']['active_pillars']}")
    print(f"  - Total Routines: {result['summary']['total_routines']}")
    print(f"  - Engaged Routines: {result['summary']['engaged_routines']}")
    print(f"  - Overall Engagement Rate: {result['summary']['overall_engagement_rate']:.1%}")
    
    # Display current metrics
    print(f"\nCurrent Metrics:")
    current = result['metrics']['current']
    print(f"  - Engagement Score: {current['engagement_score']:.1f}%")
    print(f"  - Habit Formation Index: {current['habit_formation_index']:.1f}%")
    print(f"  - Completion Velocity: {current['completion_velocity']}")
    
    # Display insights
    print(f"\nExecutive Summary:")
    exec_summary = result['insights']['executive_summary']
    print(f"  Status: {exec_summary['status']}")
    print(f"  Message: {exec_summary['message']}")
    
    # Display top recommendations
    print(f"\nTop Recommendations:")
    for i, rec in enumerate(result['recommendations'][:3], 1):
        print(f"  {i}. [{rec['priority'].upper()}] {rec['recommendation']}")
    
    # Display alerts if any
    if result['alerts']:
        print(f"\nAlerts:")
        for alert in result['alerts']:
            print(f"  - [{alert['severity'].upper()}] {alert['message']}")
            print(f"    Action: {alert['action']}")
    
    # Display pillar insights
    print(f"\nPillar Insights:")
    pillar_summary = result['insights']['pillar_insights']
    
    if pillar_summary['strengths']:
        print("  Strengths:")
        for strength in pillar_summary['strengths'][:2]:
            print(f"    - {strength}")
    
    if pillar_summary['concerns']:
        print("  Concerns:")
        for concern in pillar_summary['concerns'][:2]:
            print(f"    - {concern}")
    
    # Display achievements
    if result['insights']['achievements']:
        print(f"\nAchievements:")
        for achievement in result['insights']['achievements']:
            print(f"  🏆 {achievement['title']}: {achievement['description']}")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    demo_analytics()