"""Event route handler"""

import json
import logging
from flask import Blueprint, jsonify, request, current_app

from src.services.action_plan.action_plan_service import ActionPlanService
from src.services.health.health_score_service import HealthScoreService
from src.utils.strapi_api import strapi_get_health_scores, strapi_get_old_action_plan

event_bp = Blueprint('event', __name__)
logger = logging.getLogger(__name__)


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


@event_bp.route('/event', methods=['POST'])
def event():
    """Handle event webhooks"""
    host = request.host
    logger.info(f"Received event webhook on host: {host}")

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

    return jsonify(result), 200