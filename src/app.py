"""LTH Recommendation Service - Main Application"""

import os
import logging
from flask import Flask

# Import blueprints
from src.api.routes.health_route import health_bp
from src.api.routes.event_route import event_bp
from src.api.routes.webhook_route import webhook_bp
from src.api.routes.analytics_route import analytics_bp
from src.api.routes.analytics_endpoint import analytics_endpoint_bp

# Import utilities
from src.utils.data_loader import list_strapi_matches, list_strapi_matches_with_original

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv('FLASK_ENV') == 'development' else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler('flask_app.log')  # File output
    ]
)

logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.getenv('FLASK_ENV', 'production')
    app.config['DEBUG'] = config_name == 'development'
    
    # Log startup info
    logger.info(f"Starting LTH Recommendation Service in {config_name} mode")
    logger.info(f"Debug mode: {app.config['DEBUG']}")
    
    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(webhook_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(analytics_endpoint_bp)
    logger.info("All blueprints registered successfully")
    
    # Register error handlers
    register_error_handlers(app)
    
    # Add request logging
    @app.before_request
    def log_request_info():
        from flask import request
        logger.info(f"=== Incoming Request ===")
        logger.info(f"Method: {request.method}")
        logger.info(f"URL: {request.url}")
        logger.info(f"Headers: {dict(request.headers)}")
        if request.is_json:
            try:
                logger.info(f"JSON Body: {request.json}")
            except:
                logger.info("JSON Body: <unable to parse>")
        logger.info(f"Remote Addr: {request.remote_addr}")
    
    @app.after_request
    def log_response_info(response):
        logger.info(f"=== Response ===")
        logger.info(f"Status: {response.status}")
        return response
    
    # Log all registered routes
    logger.info("Registered routes:")
    for rule in app.url_map.iter_rules():
        logger.info(f"  {rule.endpoint}: {rule.rule} [{', '.join(rule.methods)}]")
    
    return app


def register_error_handlers(app):
    """Register error handlers for the application"""
    
    @app.errorhandler(400)
    def bad_request(error):
        logger.error(f"Bad request: {error}")
        return {"error": "Bad request"}, 400
    
    @app.errorhandler(404)
    def not_found(error):
        logger.error(f"Not found: {error}")
        return {"error": "Not found"}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return {"error": "Internal server error"}, 500
    
    @app.errorhandler(Exception)
    def unhandled_exception(error):
        logger.exception("Unhandled exception")
        return {"error": "An unexpected error occurred"}, 500


# Create application instance
app = create_app()

# Export utility functions for backward compatibility
__all__ = [
    'app',
    'list_strapi_matches',
    'list_strapi_matches_with_original'
]


if __name__ == "__main__":
    # Run the application
    port = int(os.getenv('PORT', 5003))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
