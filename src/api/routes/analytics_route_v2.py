"""Enhanced Analytics API routes with comprehensive analytics features"""

import logging
from flask import Blueprint, jsonify, request
from datetime import datetime

from src.analytics import AnalyticsService

analytics_bp_v2 = Blueprint('analytics_v2', __name__)
logger = logging.getLogger(__name__)

# Initialize analytics service
analytics_service = AnalyticsService()


@analytics_bp_v2.route('/api/analytics/process-event', methods=['POST'])
def process_analytics_event():
    """Process completion event and return comprehensive analytics"""
    try:
        event_data = request.get_json()
        
        if not event_data:
            return jsonify({"error": "No event data provided"}), 400
        
        # Validate required fields
        required_fields = ['accountId', 'actionPlanUniqueId', 'pillarCompletionStats']
        missing_fields = [field for field in required_fields if field not in event_data]
        
        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Process the event
        analytics_result = analytics_service.process_event(event_data)
        
        logger.info(f"Analytics processed successfully for account {event_data['accountId']}")
        
        return jsonify(analytics_result), 200
        
    except Exception as e:
        logger.error(f"Error processing analytics event: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@analytics_bp_v2.route('/api/analytics/summary/<int:account_id>', methods=['GET'])
def get_analytics_summary(account_id):
    """Get analytics summary for an account"""
    try:
        # Get query parameters
        days = request.args.get('days', 7, type=int)
        
        # Validate days parameter
        if days < 1 or days > 365:
            return jsonify({"error": "Days must be between 1 and 365"}), 400
        
        # Get analytics summary
        summary = analytics_service.get_analytics_summary(account_id, days)
        
        return jsonify(summary), 200
        
    except Exception as e:
        logger.error(f"Error retrieving analytics summary: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@analytics_bp_v2.route('/api/analytics/pillar/<int:account_id>/<pillar>', methods=['GET'])
def get_pillar_analytics(account_id, pillar):
    """Get detailed analytics for a specific pillar"""
    try:
        # Validate pillar
        valid_pillars = [
            'MOVEMENT', 'NUTRITION', 'STRESS', 'SLEEP', 
            'GRATITUDE', 'SOCIAL_ENGAGEMENT', 'COGNITIVE_ENHANCEMENT'
        ]
        
        if pillar not in valid_pillars:
            return jsonify({
                "error": f"Invalid pillar. Must be one of: {', '.join(valid_pillars)}"
            }), 400
        
        # Get pillar analytics
        pillar_data = analytics_service.get_pillar_analytics(account_id, pillar)
        
        return jsonify(pillar_data), 200
        
    except Exception as e:
        logger.error(f"Error retrieving pillar analytics: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@analytics_bp_v2.route('/api/analytics/insights/<int:account_id>', methods=['GET'])
def get_latest_insights(account_id):
    """Get latest insights and recommendations for an account"""
    try:
        # Get analytics summary which includes insights
        summary = analytics_service.get_analytics_summary(account_id, days=1)
        
        if summary.get('status') == 'no_data':
            return jsonify({
                "error": "No recent analytics data available",
                "account_id": account_id
            }), 404
        
        # Extract insights
        insights = {
            "account_id": account_id,
            "timestamp": datetime.utcnow().isoformat(),
            "executive_summary": summary.get('executive_summary'),
            "recommendations": summary.get('top_recommendations', []),
            "achievements": summary.get('achievements', []),
            "key_trends": summary.get('key_trends', [])
        }
        
        return jsonify(insights), 200
        
    except Exception as e:
        logger.error(f"Error retrieving insights: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@analytics_bp_v2.route('/api/analytics/health', methods=['GET'])
def analytics_health_check():
    """Health check endpoint for analytics service"""
    try:
        return jsonify({
            "status": "healthy",
            "service": "analytics_v2",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0"
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


@analytics_bp_v2.route('/api/analytics/demo', methods=['GET'])
def get_demo_analytics():
    """Get demo analytics data for testing"""
    try:
        # Create a sample event for demonstration
        demo_event = {
            "actionPlanUniqueId": "demo-123",
            "accountId": 999,
            "startDate": "2025-05-01T00:00:00.000Z",
            "periodInDays": 28,
            "pillarCompletionStats": [
                {
                    "pillarEnum": "MOVEMENT",
                    "routineCompletionStats": [
                        {
                            "routineUniqueId": 1,
                            "displayName": "Morning Jog",
                            "scheduleCategory": "DAILY_ROUTINE",
                            "completionStatistics": [
                                {
                                    "completionRate": 0.8,
                                    "completionRatePeriodUnit": "WEEK",
                                    "periodSequenceNo": 1,
                                    "completionUnit": "MINUTES",
                                    "completionTargetTotal": 30,
                                    "completedValueTotal": 24
                                }
                            ]
                        }
                    ]
                },
                {
                    "pillarEnum": "NUTRITION",
                    "routineCompletionStats": [
                        {
                            "routineUniqueId": 2,
                            "displayName": "Healthy Breakfast",
                            "scheduleCategory": "DAILY_ROUTINE",
                            "completionStatistics": [
                                {
                                    "completionRate": 0.9,
                                    "completionRatePeriodUnit": "WEEK",
                                    "periodSequenceNo": 1,
                                    "completionUnit": "ROUTINE",
                                    "completionTargetTotal": 7,
                                    "completedValueTotal": 6
                                }
                            ]
                        }
                    ]
                }
            ],
            "changeLog": []
        }
        
        # Process demo event
        result = analytics_service.process_event(demo_event)
        
        return jsonify({
            "message": "Demo analytics generated successfully",
            "analytics": result
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating demo analytics: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500