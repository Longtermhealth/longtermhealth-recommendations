"""
Configuration settings for User Test Service
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ClickUp Configuration
CLICKUP_API_KEY = os.getenv('CLICKUP_API_KEY')
CLICKUP_LIST_ID = os.getenv('CLICKUP_LIST_ID')
KEY_FEEDBACK_FIELD_ID = os.getenv('KEY_FEEDBACK_FIELD_ID')
EMAIL_FIELD_ID = os.getenv('EMAIL_FIELD_ID', 'bb63a362-e97c-4b77-8f04-254b6437aef7')

# Typeform Configuration
TYPEFORM_API_TOKEN = os.getenv('TYPEFORM_API_TOKEN')
TYPEFORM_API_BASE = 'https://api.typeform.com'
TYPEFORM_ALWAYS_FETCH_LATEST = os.getenv('TYPEFORM_ALWAYS_FETCH_LATEST', 'true').lower() == 'true'

# Flask Configuration
PORT = int(os.getenv('USER_TEST_SERVICE_PORT', '5001'))
DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
HOST = os.getenv('USER_TEST_SERVICE_HOST', '0.0.0.0')

# Service Configuration
SERVICE_NAME = 'User Test Service'
SERVICE_VERSION = '1.0.0'