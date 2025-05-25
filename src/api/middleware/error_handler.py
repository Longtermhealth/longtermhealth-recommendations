import logging
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException


logger = logging.getLogger(__name__)


def register_error_handlers(app: Flask):
    """Register global error handlers for the Flask app"""
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        """Handle HTTP exceptions"""
        logger.error(f"HTTP error: {error}")
        response = {
            "error": error.description,
            "code": error.code
        }
        return jsonify(response), error.code
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error: Exception):
        """Handle all other exceptions"""
        logger.error(f"Unhandled exception: {error}", exc_info=True)
        response = {
            "error": "An unexpected error occurred",
            "type": "InternalServerError"
        }
        return jsonify(response), 500