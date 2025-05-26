"""Data loader utilities for Strapi routines"""

import os
import json
import logging
from typing import List, Dict, Any, Set
from flask import current_app

logger = logging.getLogger(__name__)


def list_strapi_matches(matching_routines: List[Dict[str, Any]], 
                       strapi_routines_file: str = None) -> List[Dict[str, Any]]:
    """
    For each routine in `matching_routines`, search in the provided Strapi routines file
    for an entry with a matching `cleanedName` attribute. For every match found, print
    and collect its id, name, and order.

    Parameters:
        matching_routines: A list of dictionaries representing routines.
                          Each dictionary is expected to have a "cleanedName" key.
        strapi_routines_file: Path to the JSON file containing all Strapi routines.

    Returns:
        list: A list of dictionaries. Each dictionary represents a matched routine with keys:
              "id", "name", and "order".
    """
    # Use config file if no file specified
    if strapi_routines_file is None:
        try:
            strapi_routines_file = current_app.config.get('STRAPI_ROUTINES_FILE', './data/strapi_all_routines.json')
        except RuntimeError:
            # Not in application context, use default
            strapi_routines_file = './data/strapi_all_routines.json'
    
    if not os.path.exists(strapi_routines_file):
        logger.error(f"Strapi routines file not found: {strapi_routines_file}")
        return []

    try:
        with open(strapi_routines_file, "r", encoding="utf-8") as f:
            strapi_routines = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {strapi_routines_file}: {e}")
        return []

    search_cleaned_names = set()
    for routine in matching_routines:
        cleaned = routine.get("cleanedName")
        if cleaned:
            search_cleaned_names.add(cleaned)
        else:
            display = routine.get("name") or routine.get("displayName")
            if display:
                search_cleaned_names.add(display)

    matches = []
    for entry in strapi_routines:
        attributes = entry.get("attributes", {})
        strapi_cleaned_name = attributes.get("cleanedName")
        if strapi_cleaned_name in search_cleaned_names:
            match = {
                "id": entry.get("id"),
                "name": attributes.get("name"),
                "order": attributes.get("order")
            }
            matches.append(match)
            logger.info("Found match - ID: {id}, Name: {name}, Order: {order}".format(**match))

    return matches


def list_strapi_matches_with_original(matching_routines: List[Dict[str, Any]], 
                                    strapi_routines_file: str = None) -> List[Dict[str, Any]]:
    """
    For each routine in `matching_routines`, search the Strapi routines file for an entry
    with a matching `cleanedName` attribute. For every match found, print and collect its id,
    name, order, and the original routine object.

    Parameters:
        matching_routines: A list of dictionaries representing routines.
                          Each dictionary is expected to have a "cleanedName" key.
        strapi_routines_file: Path to the JSON file containing all Strapi routines.

    Returns:
        list: A list of dictionaries. Each dictionary represents a matched routine with keys:
              "id", "name", "order", and "original" (the full JSON object from Strapi).
    """
    # Use config file if no file specified
    if strapi_routines_file is None:
        try:
            strapi_routines_file = current_app.config.get('STRAPI_ROUTINES_FILE', './data/strapi_all_routines.json')
        except RuntimeError:
            # Not in application context, use default
            strapi_routines_file = './data/strapi_all_routines.json'
    
    if not os.path.exists(strapi_routines_file):
        logger.error(f"Strapi routines file not found: {strapi_routines_file}")
        return []

    try:
        with open(strapi_routines_file, "r", encoding="utf-8") as f:
            strapi_routines = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {strapi_routines_file}: {e}")
        return []

    search_cleaned_names = set()
    for routine in matching_routines:
        cleaned = routine.get("cleanedName")
        if cleaned:
            search_cleaned_names.add(cleaned)
        else:
            display = routine.get("name") or routine.get("displayName")
            if display:
                search_cleaned_names.add(display)

    matches = []
    for entry in strapi_routines:
        attributes = entry.get("attributes", {})
        strapi_cleaned_name = attributes.get("cleanedName")
        if strapi_cleaned_name in search_cleaned_names:
            match = {
                "id": entry.get("id"),
                "name": attributes.get("name"),
                "order": attributes.get("order"),
                "original": entry
            }
            matches.append(match)
            logger.info("Found match - ID: {id}, Name: {name}, Order: {order}".format(**match))

    return matches