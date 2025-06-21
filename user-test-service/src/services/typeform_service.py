"""
Typeform API Service
Handles fetching form definitions and caching
"""
import json
import os
import requests
from datetime import datetime
from typing import Dict, List, Tuple, Optional

from config.settings import TYPEFORM_API_TOKEN, TYPEFORM_API_BASE, TYPEFORM_ALWAYS_FETCH_LATEST


class TypeformService:
    def __init__(self):
        self.form_definitions_cache = {}
        self.cache_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'cache')
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_and_save_master_form_definition(self, form_id: str, force_refresh: bool = True) -> Optional[Dict]:
        """
        Fetch the complete form definition from Typeform API and save it to a file.
        """
        master_file = os.path.join(self.cache_dir, f"typeform_master_{form_id}.json")
        
        # If not forcing refresh, try to load from file first
        if not force_refresh:
            try:
                with open(master_file, 'r') as f:
                    master_data = json.load(f)
                    print(f"DEBUG: Loaded master form definition from {master_file}")
                    return master_data
            except FileNotFoundError:
                print(f"DEBUG: No saved master form definition found, fetching from API...")
        
        # Fetch from API
        url = f"{TYPEFORM_API_BASE}/forms/{form_id}"
        headers = {
            "Authorization": f"Bearer {TYPEFORM_API_TOKEN}"
        }
        
        try:
            print(f"DEBUG: Fetching latest form definition from Typeform API for form {form_id}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            form_data = response.json()
            print(f"DEBUG: Successfully fetched form definition with {len(form_data.get('fields', []))} fields")
            
            # Save to file for backup/debugging
            with open(master_file, 'w') as f:
                json.dump(form_data, f, indent=2)
                print(f"DEBUG: Saved master form definition to {master_file}")
            
            return form_data
            
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Failed to fetch form definition from Typeform: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            
            # If API fails, try to use cached version as fallback
            try:
                with open(master_file, 'r') as f:
                    master_data = json.load(f)
                    print(f"WARNING: Using cached form definition due to API error")
                    return master_data
            except FileNotFoundError:
                print(f"ERROR: No cached form definition available")
                return None
    
    def extract_all_questions_from_fields(self, fields: List[Dict], is_master: bool = False) -> List[Tuple[str, Dict]]:
        """
        Extract all questions from fields, handling inline_group types.
        Returns a list of (title, field_info) tuples.
        """
        questions = []
        
        for field in fields:
            field_type = field.get('type')
            
            if field_type == 'inline_group':
                # Extract nested fields from inline_group
                nested_fields = field.get('properties', {}).get('fields', [])
                for nested_field in nested_fields:
                    title = nested_field.get('title', '')
                    if title:
                        field_info = {
                            'type': nested_field.get('type'),
                            'choices': nested_field.get('properties', {}).get('choices', []),
                            'allow_multiple_selections': nested_field.get('properties', {}).get('allow_multiple_selections', False)
                        }
                        if is_master:
                            field_info['master_id'] = nested_field.get('id')
                        else:
                            field_info['webhook_id'] = nested_field.get('id')
                        questions.append((title, field_info))
            else:
                # Regular field
                title = field.get('title', '')
                if title:
                    field_info = {
                        'type': field.get('type'),
                        'choices': field.get('properties', {}).get('choices', []),
                        'allow_multiple_selections': field.get('properties', {}).get('allow_multiple_selections', False)
                    }
                    if is_master:
                        field_info['master_id'] = field.get('id')
                    else:
                        field_info['webhook_id'] = field.get('id')
                    questions.append((title, field_info))
        
        return questions
    
    def build_question_reference_map(self, master_form: Dict, webhook_fields: List[Dict]) -> Dict:
        """
        Build a map between question titles and their field IDs/options.
        """
        question_map = {}
        
        # Extract all questions from master form
        if master_form and 'fields' in master_form:
            master_questions = self.extract_all_questions_from_fields(master_form['fields'], is_master=True)
            for title, field_info in master_questions:
                question_map[title] = field_info
        
        # Update with webhook field IDs
        webhook_questions = self.extract_all_questions_from_fields(webhook_fields, is_master=False)
        for title, field_info in webhook_questions:
            if title in question_map:
                # Update existing entry with webhook ID
                question_map[title]['webhook_id'] = field_info.get('webhook_id')
            else:
                # Add new question that only exists in webhook
                question_map[title] = field_info
        
        return question_map