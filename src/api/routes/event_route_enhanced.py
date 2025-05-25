"""Enhanced event route handler with analytics integration"""

import json
import logging
from flask import Blueprint, jsonify, request, current_app
import asyncio
from concurrent.futures import ThreadPoolExecutor

from src.services.action_plan.action_plan_service import ActionPlanService
from src.services.health.health_score_service import HealthScoreService
from src.analytics import AnalyticsService
from src.utils.strapi_api import strapi_get_health_scores, strapi_get_old_action_plan

event_enhanced_bp = Blueprint('event_enhanced', __name__)
logger = logging.getLogger(__name__)

# Initialize services
analytics_service = AnalyticsService()
executor = ThreadPoolExecutor(max_workers=3)


def process_event_data(event_data):
    """
    Process the entire event data by:
      1. Extracting eventPayload (which may be a dict or a JSON‐encoded string).
      2. Parsing it if necessary.
      3. Computing routine insights.

    Returns:
        tuple: (insights_dict, payload_dict) or (None, None) on JSON parse error.
    """
    raw_payload = event_data.get("eventPayload")

    if isinstance(raw_payload, str):
        try:
            payload = json.loads(raw_payload)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in eventPayload: {raw_payload!r} – {e}")
            return None, None
    elif isinstance(raw_payload, dict):
        payload = raw_payload
    else:
        logger.error(f"Unexpected type for eventPayload: {type(raw_payload).__name__}")
        return None, None

    insights = HealthScoreService.get_insights(payload)
    return insights, payload


def process_analytics_async(payload):
    """Process analytics asynchronously"""
    try:
        analytics_result = analytics_service.process_event(payload)
        logger.info(f"Analytics processed for account {payload.get('accountId')}")
        return analytics_result
    except Exception as e:
        logger.error(f"Error in analytics processing: {e}", exc_info=True)
        return None


@event_enhanced_bp.route('/event/v2', methods=['POST'])
def event_v2():
    """Enhanced event webhook handler with analytics"""
    host = request.host
    logger.info(f"Received event webhook (v2) on host: {host}")

    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400

    insights, payload = process_event_data(data)
    if payload is None:
        return jsonify({"error": "Invalid eventPayload JSON"}), 400

    # Log pretty-printed payload for debugging
    if current_app.debug:
        pretty_payload = json.dumps(payload, indent=4)
        logger.debug(f'Pretty payload: {pretty_payload}')

    # Extract key information
    action_plan_id = payload.get('actionPlanUniqueId', 0)
    account_id = payload.get('accountId', 0)

    # Submit analytics processing asynchronously
    analytics_future = executor.submit(process_analytics_async, payload)

    # Get initial health scores and action plan
    initial_health_scores = strapi_get_health_scores(account_id, host)
    action_plan = strapi_get_old_action_plan(action_plan_id, host)

    # Calculate health score updates
    final_scores = HealthScoreService.calculate_first_month_update(
        account_id=account_id,
        action_plan=action_plan,
        pretty_payload=payload,
        initial_health_scores=initial_health_scores
    )
    logger.info(f"Final Health Scores per Pillar: {final_scores}")

    # Handle different event types
    event_type = data.get('eventEnum')
    if not event_type:
        return jsonify({"error": "Missing eventEnum in payload"}), 400

    if event_type == 'RECALCULATE_ACTION_PLAN':
        result = ActionPlanService.recalculate_action_plan(payload, host)
        logger.info('RECALCULATE_ACTION_PLAN processed')
    elif event_type == 'RENEW_ACTION_PLAN':
        logger.info('RENEW_ACTION_PLAN processing')
        result = ActionPlanService.renew_action_plan(payload, host)
    else:
        result = {"error": f"Unhandled event type: {event_type}"}

    # Try to get analytics result (non-blocking)
    analytics_result = None
    try:
        analytics_result = analytics_future.result(timeout=2)  # 2 second timeout
    except Exception as e:
        logger.warning(f"Analytics processing timeout or error: {e}")

    # Include analytics in response if available
    if analytics_result:
        result['analytics_summary'] = {
            'engagement_score': analytics_result['metrics']['current']['engagement_score'],
            'active_pillars': analytics_result['summary']['active_pillars'],
            'total_completions': analytics_result['summary']['total_completions'],
            'top_recommendation': analytics_result['recommendations'][0] if analytics_result['recommendations'] else None
        }

    return jsonify(result), 200


@event_enhanced_bp.route('/event/v2/analytics-only', methods=['POST'])
def event_analytics_only():
    """Process only analytics for an event (useful for testing)"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400

    insights, payload = process_event_data(data)
    if payload is None:
        return jsonify({"error": "Invalid eventPayload JSON"}), 400

    try:
        # Process analytics synchronously for this endpoint
        analytics_result = analytics_service.process_event(payload)
        
        return jsonify({
            "status": "success",
            "analytics": analytics_result
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing analytics: {e}", exc_info=True)
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500