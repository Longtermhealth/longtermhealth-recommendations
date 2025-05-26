import os
import logging
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    JSON_SORT_KEYS = False
    
    # Logging
    LOG_LEVEL = logging.INFO
    
    # External services
    CLICKUP_API_KEY = os.getenv("CLICKUP_API_KEY")
    CLICKUP_LIST_ID = os.getenv("CLICKUP_LIST_ID")
    SCORES_FIELD_ID = os.getenv("SCORES_FIELD_ID")
    PLOT_FIELD_ID = os.getenv("PLOT_FIELD_ID")
    ANSWERS_FIELD_ID = os.getenv("ANSWERS_FIELD_ID")
    ROUTINES_FIELD_ID = os.getenv("ROUTINES_FIELD_ID")
    ACTIONPLAN_FIELD_ID = os.getenv("ACTIONPLAN_FIELD_ID")
    TYPEFORM_API_KEY = os.getenv("TYPEFORM_API_KEY")
    STRAPI_API_KEY = os.getenv("STRAPI_API_KEY")
    FORM_ID = os.getenv("FORM_ID")
    LINK_SUMMARY_TITLE_FIELD_ID = os.getenv("LINK_SUMMARY_TITLE_FIELD_ID")
    LINK_SUMMARY_SUMMARY_FIELD_ID = os.getenv("LINK_SUMMARY_SUMMARY_FIELD_ID")
    LINK_SUMMARY_OPENAI_API_KEY = os.getenv("LINK_SUMMARY_OPENAI_API_KEY")
    AZURE_BLOB_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
    
    # Data files
    STRAPI_ROUTINES_FILE = "./data/strapi_all_routines.json"  # Default/fallback
    
    # Calculation parameters
    SCORE_UPDATE_K = 0.025
    
    # Performance settings
    ENABLE_CACHING = True
    CACHE_TTL = 300  # 5 minutes
    MAX_WORKERS = 5
    CONNECTION_POOL_SIZE = 10
    REQUEST_TIMEOUT = 30
    
    # Optimization flags
    USE_ASYNC_PROCESSING = True
    USE_RULE_COMPILATION = True
    ENABLE_PERFORMANCE_MONITORING = False


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = logging.DEBUG
    
    # Development specific settings
    PROPAGATE_EXCEPTIONS = True
    STRAPI_ROUTINES_FILE = "./data/environments/dev/strapi_all_routines_dev.json"


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    # Production specific settings
    PROPAGATE_EXCEPTIONS = False
    STRAPI_ROUTINES_FILE = "./data/environments/staging/strapi_all_routines_staging.json"


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    
    # Testing specific settings
    WTF_CSRF_ENABLED = False