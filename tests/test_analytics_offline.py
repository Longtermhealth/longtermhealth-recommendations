"""Offline testing script for analytics functionality"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analytics import AnalyticsService


def test_analytics_offline():
    """Test analytics processing with offline payload"""
    
    # Load test payload
    payload_path = Path(__file__).parent / "fixtures" / "event_payload_sample.json"
    with open(payload_path, 'r') as f:
        test_payload = json.load(f)
    
    print("=== Offline Analytics Test ===\n")
    print(f"Loading test payload from: {payload_path}")
    print(f"Account ID: {test_payload['accountId']}")
    print(f"Action Plan ID: {test_payload['actionPlanUniqueId']}")
    print(f"Period: {test_payload['periodInDays']} days\n")
    
    # Initialize analytics service
    analytics_service = AnalyticsService()
    
    # Process the payload
    print("Processing analytics...")
    result = analytics_service.process_event(test_payload)
    
    # Display results
    print("\n=== Analytics Results ===\n")
    
    # Summary
    summary = result['summary']
    print("Summary:")
    print(f"  Total Pillars: {summary['total_pillars']}")
    print(f"  Active Pillars: {summary['active_pillars']}")
    print(f"  Total Routines: {summary['total_routines']}")
    print(f"  Engaged Routines: {summary['engaged_routines']}")
    print(f"  Overall Engagement Rate: {summary['overall_engagement_rate']:.1%}")
    print(f"  Most Active Pillar: {summary['most_active_pillar']}")
    print(f"  Least Active Pillar: {summary['least_active_pillar']}")
    
    # Current Metrics
    print("\nCurrent Metrics:")
    current = result['metrics']['current']
    print(f"  Engagement Score: {current['engagement_score']:.1f}%")
    print(f"  Habit Formation Index: {current['habit_formation_index']:.1f}%")
    print(f"  Completion Velocity: {current['completion_velocity']}")
    
    # Executive Summary
    print("\nExecutive Summary:")
    exec_summary = result['insights']['executive_summary']
    print(f"  Status: {exec_summary['status']}")
    print(f"  Message: {exec_summary['message']}")
    
    # Key Metrics
    print("\n  Key Metrics:")
    for metric, value in exec_summary['key_metrics'].items():
        print(f"    {metric.replace('_', ' ').title()}: {value}")
    
    # Recommendations
    print("\nTop Recommendations:")
    for i, rec in enumerate(result['recommendations'][:3], 1):
        print(f"  {i}. [{rec['priority'].upper()}] {rec['recommendation']}")
    
    # Alerts
    if result['alerts']:
        print("\nAlerts:")
        for alert in result['alerts']:
            print(f"  - [{alert['severity'].upper()}] {alert['message']}")
            print(f"    Action: {alert['action']}")
    
    # Pillar Breakdown
    print("\nPillar Performance:")
    pillar_summary = result['insights']['pillar_insights']
    
    if pillar_summary.get('strengths'):
        print("  Strengths:")
        for strength in pillar_summary['strengths'][:3]:
            print(f"    ✓ {strength}")
    
    if pillar_summary.get('concerns'):
        print("\n  Concerns:")
        for concern in pillar_summary['concerns'][:3]:
            print(f"    - {concern}")
    
    # Achievements
    if result['insights']['achievements']:
        print("\nAchievements:")
        for achievement in result['insights']['achievements']:
            print(f"  🏆 {achievement['title']}: {achievement['description']}")
    
    print("\n=== Test Complete ===")
    
    # Save full results to file for inspection
    output_path = Path(__file__).parent / "fixtures" / "analytics_output.json"
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\nFull results saved to: {output_path}")


def test_individual_components():
    """Test individual analytics components"""
    from src.analytics import EventProcessor, MetricsCalculator, TrendAnalyzer, InsightsEngine
    
    print("\n=== Testing Individual Components ===\n")
    
    # Load test payload
    payload_path = Path(__file__).parent / "fixtures" / "event_payload_sample.json"
    with open(payload_path, 'r') as f:
        test_payload = json.load(f)
    
    # Test Event Processor
    print("1. Testing Event Processor...")
    event_processor = EventProcessor()
    analytics_data = event_processor.process_completion_event(test_payload)
    print(f"   - Processed {len(analytics_data['pillar_analytics'])} pillars")
    print(f"   - Total completions: {analytics_data['summary']['total_completions']}")
    
    # Test Metrics Calculator
    print("\n2. Testing Metrics Calculator...")
    metrics_calculator = MetricsCalculator()
    metrics = metrics_calculator.calculate_metrics(analytics_data)
    print(f"   - Engagement Score: {metrics['engagement_metrics']['engagement_score']:.1f}%")
    print(f"   - Pillars with metrics: {len(metrics['pillar_metrics'])}")
    
    # Test Trend Analyzer (needs historical data)
    print("\n3. Testing Trend Analyzer...")
    trend_analyzer = TrendAnalyzer()
    # Create some mock historical data
    historical_metrics = [metrics] * 3  # Duplicate for testing
    trends = trend_analyzer.analyze_trends(historical_metrics)
    print(f"   - Trend status: {trends.get('status', 'analyzed')}")
    
    # Test Insights Engine
    print("\n4. Testing Insights Engine...")
    insights_engine = InsightsEngine()
    # Add summary data to metrics (required by insights engine)
    metrics['summary'] = analytics_data['summary']
    insights = insights_engine.generate_insights(metrics, trends)
    print(f"   - Generated {len(insights['recommendations'])} recommendations")
    print(f"   - Found {len(insights['achievements'])} achievements")
    print(f"   - Created {len(insights['alerts'])} alerts")
    
    print("\n=== Component Tests Complete ===")


if __name__ == "__main__":
    # Run main test
    test_analytics_offline()
    
    # Optionally test components individually
    print("\n" + "="*50)
    test_individual_components()