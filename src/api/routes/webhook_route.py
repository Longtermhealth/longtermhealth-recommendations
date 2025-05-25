"""Webhook route handler"""

import time
import logging
from flask import Blueprint, jsonify, request

from src.scheduling.scheduler import main as process_action_plan
from src.utils.typeform_api import trigger_followup
from src.analytics.storage import AnalyticsStorage

webhook_bp = Blueprint('webhook', __name__)
logger = logging.getLogger(__name__)

# Initialize analytics storage
analytics_storage = AnalyticsStorage()


@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    """Handle webhook requests"""
    host = request.host
    logger.info(f"Received webhook on host: {host}")
    
    # Get webhook data
    webhook_data = request.get_json()
    
    # Process analytics if completion data is present
    if webhook_data and 'completionStatistics' in webhook_data:
        try:
            analytics_result = analytics_storage.process_and_store_webhook(webhook_data)
            logger.info(f"Analytics processed: {analytics_result['insights']['summary']}")
        except Exception as e:
            logger.error(f"Error processing analytics: {e}")
    
    # Small delay for processing
    time.sleep(3)
    
    # Check if this is a follow-up webhook
    if request.headers.get("X-Webhook-Followup") == "true":
        logger.info("Follow-up webhook already received")
        process_action_plan(host)
        return jsonify({"status": "follow-up processed"}), 200
    else:
        logger.info('Original webhook received')

    # Process the action plan
    start_time = time.perf_counter()
    logger.info('Start processing action plan')
    
    final_action_plan = process_action_plan(host)
    
    logger.info(f'Action plan processed and posted: {final_action_plan}')
    end_time = time.perf_counter()
    elapsed = end_time - start_time
    logger.info(f"Total time from webhook reception to posting action plan: {elapsed:.2f} seconds")
    
    # Small delay before triggering follow-up
    time.sleep(5)
    trigger_followup(host)

    return jsonify({'status': 'success'}), 200