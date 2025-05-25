"""Analytics endpoint for processing completion events"""

import json
import logging
from flask import Blueprint, jsonify, request

from src.analytics import AnalyticsService

analytics_endpoint_bp = Blueprint('analytics_endpoint', __name__)
logger = logging.getLogger(__name__)

# Initialize analytics service
analytics_service = AnalyticsService()


@analytics_endpoint_bp.route('/api/analytics/event', methods=['POST'])
def process_analytics_event():
    """Process completion event and return analytics insights"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Extract eventPayload if wrapped
        if 'eventPayload' in data:
            if isinstance(data['eventPayload'], str):
                try:
                    payload = json.loads(data['eventPayload'])
                except json.JSONDecodeError:
                    return jsonify({"error": "Invalid JSON in eventPayload"}), 400
            else:
                payload = data['eventPayload']
        else:
            # Assume the data is the payload itself
            payload = data
        
        # Validate required fields
        required_fields = ['accountId', 'actionPlanUniqueId', 'pillarCompletionStats']
        missing_fields = [field for field in required_fields if field not in payload]
        
        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Process analytics
        logger.info(f"Processing analytics for account {payload.get('accountId')}")
        analytics_result = analytics_service.process_event(payload)
        
        # Create response with key insights
        response = {
            "account_id": analytics_result['account_id'],
            "action_plan_id": analytics_result['action_plan_id'],
            "timestamp": analytics_result['timestamp'],
            "engagement_metrics": {
                "overall_score": analytics_result['metrics']['current']['engagement_score'],
                "active_pillars": f"{analytics_result['summary']['active_pillars']}/{analytics_result['summary']['total_pillars']}",
                "total_routines": analytics_result['summary']['total_routines'],
                "engaged_routines": analytics_result['summary']['engaged_routines'],
                "completion_velocity": analytics_result['metrics']['current']['completion_velocity']
            },
            "executive_summary": analytics_result['insights']['executive_summary'],
            "top_recommendations": analytics_result['recommendations'][:3],
            "alerts": analytics_result['alerts'],
            "pillar_performance": {}
        }
        
        # Add pillar-specific insights
        for pillar, metrics in analytics_result['metrics']['pillar_metrics'].items():
            response['pillar_performance'][pillar] = {
                "completion_score": metrics['completion_score'],
                "engagement_rate": metrics['engagement_rate'],
                "active_routines": f"{metrics['active_routines']}/{metrics['total_routines']}",
                "trend": metrics.get('weekly_trend', 'stable')
            }
        
        logger.info(f"Analytics successfully processed for account {payload.get('accountId')}")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error processing analytics: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@analytics_endpoint_bp.route('/api/analytics/summary/<int:account_id>', methods=['GET'])
def get_account_summary(account_id):
    """Get analytics summary for an account"""
    try:
        days = request.args.get('days', 7, type=int)
        
        summary = analytics_service.get_analytics_summary(account_id, days)
        
        if summary.get('status') == 'no_data':
            return jsonify({
                "error": "No analytics data found",
                "account_id": account_id
            }), 404
        
        return jsonify(summary), 200
        
    except Exception as e:
        logger.error(f"Error retrieving analytics summary: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500