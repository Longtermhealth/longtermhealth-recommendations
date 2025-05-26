#scheduling/data_service.py

import json
import os
from typing import Dict, Any, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_json_data(file_path: str) -> List[Dict[str, Any]]:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    absolute_path = os.path.join(script_dir, '..', file_path)

    try:
        with open(absolute_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            logger.info(f"Successfully loaded data from {absolute_path}")
            return data
    except FileNotFoundError:
        logger.error(f"The file {absolute_path} was not found.")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {absolute_path}: {e}")
        return []


def new_load_routines(app_env: str = None) -> Dict[str, Dict[str, Any]]:
    """Load routines based on environment"""
    if app_env == "development":
        return load_json_data('./data/environments/dev/strapi_all_routines_dev.json')
    elif app_env == "production" or app_env == "staging":
        return load_json_data('./data/environments/staging/strapi_all_routines_staging.json')
    else:
        # Fallback to default
        return load_json_data('./data/strapi_all_routines.json')

def new_load_rules() -> Dict[str, Any]:
    return load_json_data('./data/rules.json')
