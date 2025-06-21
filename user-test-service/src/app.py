"""
User Test Service - Typeform to ClickUp Integration
"""
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

from config.settings import PORT, DEBUG, HOST, SERVICE_NAME, SERVICE_VERSION
from webhooks.typeform_handler import TypeformWebhookHandler

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize webhook handler
webhook_handler = TypeformWebhookHandler()


@app.before_request
def log_request_info():
    """Log all incoming requests for debugging"""
    if DEBUG:
        print(f"\n{'='*60}")
        print(f"INCOMING REQUEST: {request.method} {request.path}")
        print(f"From: {request.remote_addr}")
        print(f"Headers: {dict(request.headers)}")
        if request.method == 'POST':
            print(f"Content-Type: {request.content_type}")
            if request.json:
                print(f"JSON Data: {json.dumps(request.json, indent=2)}")
            elif request.data:
                print(f"Raw Data: {request.data}")
            elif request.form:
                print(f"Form Data: {dict(request.form)}")
        print(f"{'='*60}")


@app.route('/')
def home():
    """Service information endpoint"""
    print("\nDEBUG: Home page accessed")
    return jsonify({
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "status": "running",
        "message": "Typeform Feedback Webhook Server is running!",
        "endpoints": {
            "/": "This page",
            "/health": "GET - Health check endpoint",
            "/survey": "POST - Typeform webhook endpoint",
            "/webhook/typeform": "POST - Alternative webhook endpoint"
        },
        "server_time": datetime.now().isoformat()
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/survey', methods=['POST'])
@app.route('/webhook/typeform', methods=['POST'])
def handle_typeform_webhook():
    """
    Handle incoming Typeform webhook and update ClickUp task with feedback.
    """
    data = request.json
    response, status_code = webhook_handler.process_webhook(data)
    return jsonify(response), status_code


if __name__ == '__main__':
    print("\n" + "="*80)
    print(f"{SERVICE_NAME} v{SERVICE_VERSION}")
    print("="*80)
    print(f"Starting server...")
    print(f"Webhook URL will be: https://<your-domain>/user-test/survey")
    print("-"*80)
    print("Available endpoints:")
    print("  GET  / - Service information")
    print("  GET  /health - Health check")
    print("  POST /survey - Typeform webhook endpoint")
    print("  POST /webhook/typeform - Alternative webhook endpoint")
    print("-"*80)
    print(f"Server starting on http://{HOST}:{PORT}")
    print("Press CTRL+C to stop")
    print("="*80 + "\n")
    
    app.run(host=HOST, port=PORT, debug=DEBUG)