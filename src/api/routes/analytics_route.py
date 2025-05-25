"""Analytics API routes"""

import logging
from flask import Blueprint, jsonify, request

from src.analytics.storage import AnalyticsStorage

analytics_bp = Blueprint('analytics', __name__)
logger = logging.getLogger(__name__)

# Initialize storage
analytics_storage = AnalyticsStorage()


@analytics_bp.route('/analytics/process', methods=['POST'])
def process_analytics():
    """Process webhook data and return analytics insights"""
    try:
        webhook_data = request.get_json()
        
        if not webhook_data:
            return jsonify({"error": "No data provided"}), 400
        
        # Process and store analytics
        result = analytics_storage.process_and_store_webhook(webhook_data)
        
        logger.info(f"Analytics processed for user {webhook_data.get('userId')}")
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error processing analytics: {e}")
        return jsonify({"error": str(e)}), 500


@analytics_bp.route('/analytics/user/<user_id>', methods=['GET'])
def get_user_analytics(user_id):
    """Get analytics history for a user"""
    try:
        days = request.args.get('days', 30, type=int)
        history = analytics_storage.get_user_analytics_history(user_id, days)
        
        return jsonify({
            "user_id": user_id,
            "days": days,
            "snapshots": len(history),
            "history": history
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving analytics: {e}")
        return jsonify({"error": str(e)}), 500


@analytics_bp.route('/analytics/user/<user_id>/aggregate', methods=['GET'])
def get_aggregated_analytics(user_id):
    """Get aggregated analytics for a user"""
    try:
        period = request.args.get('period', 'week')
        if period not in ['week', 'month', 'quarter']:
            return jsonify({"error": "Invalid period. Use week, month, or quarter"}), 400
        
        aggregated = analytics_storage.get_aggregated_analytics(user_id, period)
        
        return jsonify(aggregated), 200
        
    except Exception as e:
        logger.error(f"Error retrieving aggregated analytics: {e}")
        return jsonify({"error": str(e)}), 500


@analytics_bp.route('/analytics/insights/<user_id>', methods=['GET'])
def get_latest_insights(user_id):
    """Get latest insights for a user"""
    try:
        # Get most recent analytics
        history = analytics_storage.get_user_analytics_history(user_id, days=1)
        
        if not history:
            return jsonify({"error": "No recent analytics available"}), 404
        
        latest = history[-1]
        insights = latest.get('insights', {})
        
        return jsonify({
            "user_id": user_id,
            "timestamp": latest.get('timestamp'),
            "insights": insights
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving insights: {e}")
        return jsonify({"error": str(e)}), 500