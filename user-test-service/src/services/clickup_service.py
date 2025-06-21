"""
ClickUp API Service
Handles all ClickUp API interactions
"""
import requests
from datetime import datetime
from typing import Optional, Dict, List
import time

from config.settings import (
    CLICKUP_API_KEY, 
    CLICKUP_LIST_ID, 
    KEY_FEEDBACK_FIELD_ID,
    EMAIL_FIELD_ID
)


class ClickUpService:
    def __init__(self):
        self.headers = {
            'Authorization': CLICKUP_API_KEY,
            'Content-Type': 'application/json'
        }
        self.base_url = 'https://api.clickup.com/api/v2'
    
    def find_task_by_email_or_name(self, email: str, name: str, surname: str) -> Optional[str]:
        """
        Find a ClickUp task by searching for email in mail field or full name in task name.
        """
        print(f"\nDEBUG: find_task_by_email_or_name called")
        print(f"  Email: '{email}'")
        print(f"  Name: '{name}'")
        print(f"  Surname: '{surname}'")
        
        # Get all tasks in the list
        url = f"{self.base_url}/list/{CLICKUP_LIST_ID}/task"
        print(f"DEBUG: ClickUp API URL: {url}")
        
        params = {
            "page": 0,
            "order_by": "created",
            "reverse": True,
            "subtasks": True,
            "include_closed": True
        }
        
        try:
            print("DEBUG: Making request to ClickUp API...")
            response = requests.get(url, headers=self.headers, params=params)
            print(f"DEBUG: Response status code: {response.status_code}")
            
            if response.status_code == 200:
                tasks = response.json().get('tasks', [])
                print(f"DEBUG: Found {len(tasks)} tasks in list")
                
                # Create full name for comparison
                full_name = f"{name} {surname}".strip()
                
                # Search for task with matching email or name
                for i, task in enumerate(tasks):
                    task_name = task.get('name', '')
                    task_id = task.get('id', '')
                    print(f"DEBUG: Checking task {i+1}/{len(tasks)}: ID={task_id}, Name='{task_name}'")
                    
                    # First priority: Check email in mail field
                    custom_fields = task.get('custom_fields', [])
                    print(f"DEBUG: Task has {len(custom_fields)} custom fields")
                    
                    for field in custom_fields:
                        field_name = field.get('name', 'Unknown')
                        field_id = field.get('id', '')
                        field_value = field.get('value')
                        
                        # Check if this is the mail field
                        if field_id == EMAIL_FIELD_ID or field_name.lower() == 'mail':
                            print(f"DEBUG: Found mail field with value: '{field_value}'")
                            if field_value and email and field_value.lower() == email.lower():
                                print(f"DEBUG: Email match found! Email: {email}")
                                return task_id
                    
                    # Second priority: Check full name in task name
                    if full_name and full_name.lower() in task_name.lower():
                        print(f"DEBUG: Name match found! Full name: {full_name} in task name: {task_name}")
                        return task_id
                    
                    # Also check if surname and name (reversed order) matches
                    reversed_name = f"{surname} {name}".strip()
                    if reversed_name and reversed_name.lower() in task_name.lower():
                        print(f"DEBUG: Name match found (reversed)! Full name: {reversed_name} in task name: {task_name}")
                        return task_id
                
                print(f"WARNING: No task found matching:")
                print(f"  Email: {email}")
                print(f"  Full name: {full_name}")
                print("DEBUG: Searched all tasks without finding a match")
                return None
            else:
                print(f"ERROR: Failed to get tasks from ClickUp")
                print(f"Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"ERROR: Exception while finding task: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_new_task(self, email: str, name: str, surname: str, feedback_text: str) -> Optional[str]:
        """
        Create a new ClickUp task for the user with their feedback.
        Returns task ID if successful, None otherwise.
        """
        full_name = f"{name} {surname}" if name and surname else email or "Unknown User"
        
        task_data = {
            'name': full_name,
            'description': f"User created from Typeform survey response",
            'custom_fields': []
        }
        
        # Add email field if provided
        if email:
            task_data['custom_fields'].append({
                'id': EMAIL_FIELD_ID,
                'value': email
            })
        
        # Add feedback
        task_data['custom_fields'].append({
            'id': KEY_FEEDBACK_FIELD_ID,
            'value': feedback_text
        })
        
        create_url = f'{self.base_url}/list/{CLICKUP_LIST_ID}/task'
        
        try:
            response = requests.post(create_url, headers=self.headers, json=task_data)
            response.raise_for_status()
            new_task = response.json()
            print(f"SUCCESS: Created new task: {new_task['id']} for {full_name}")
            return new_task['id']
        except Exception as e:
            print(f"ERROR: Failed to create new task: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
    
    def create_subtask_with_feedback(self, parent_task_id: str, feedback_text: str, 
                                   email: str, name: str, surname: str) -> Optional[str]:
        """
        Create a subtask under an existing task with the feedback.
        Returns subtask ID if successful, None otherwise.
        """
        # Create a timestamp for the subtask name
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        subtask_name = f"Survey Response - {timestamp}"
        
        subtask_data = {
            'name': subtask_name,
            'parent': parent_task_id,
            'custom_fields': []
        }
        
        # Add feedback to the subtask
        subtask_data['custom_fields'].append({
            'id': KEY_FEEDBACK_FIELD_ID,
            'value': feedback_text
        })
        
        create_url = f'{self.base_url}/list/{CLICKUP_LIST_ID}/task'
        
        try:
            response = requests.post(create_url, headers=self.headers, json=subtask_data)
            response.raise_for_status()
            new_subtask = response.json()
            print(f"SUCCESS: Created subtask: {new_subtask['id']} under parent task {parent_task_id}")
            return new_subtask['id']
        except Exception as e:
            print(f"ERROR: Failed to create subtask: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
    
    def update_custom_field(self, task_id: str, field_id: str, value: str, 
                          retries: int = 3, backoff_factor: int = 2) -> bool:
        """
        Update a custom field in a ClickUp task.
        """
        print(f"\nDEBUG: update_custom_field called")
        print(f"  Task ID: {task_id}")
        print(f"  Field ID: {field_id}")
        print(f"  Value length: {len(value)} characters")
        print(f"  First 200 chars of value: {value[:200]}...")
        
        url = f"{self.base_url}/task/{task_id}/field/{field_id}"
        print(f"DEBUG: Update URL: {url}")
        
        payload = {
            "value": value
        }
        
        for attempt in range(retries):
            try:
                print(f"DEBUG: Attempt {attempt + 1}/{retries} to update field...")
                response = requests.post(url, json=payload, headers=self.headers)
                print(f"DEBUG: Response status code: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"SUCCESS: Updated ClickUp task {task_id} with feedback")
                    print(f"DEBUG: Response: {response.text}")
                    return True
                elif response.status_code == 504:
                    print(f"WARNING: Attempt {attempt + 1} failed with status code 504. Retrying...")
                else:
                    print(f"ERROR: Failed to update ClickUp task")
                    print(f"  Status code: {response.status_code}")
                    print(f"  Response: {response.content}")
                    if attempt == retries - 1:
                        print("ERROR: All retry attempts exhausted")
                        return False
            except requests.exceptions.RequestException as e:
                print(f"ERROR: Request failed with exception: {e}")
                if attempt == retries - 1:
                    print("ERROR: All retry attempts exhausted")
                    return False
            
            if attempt < retries - 1:
                wait_time = backoff_factor ** attempt
                print(f"DEBUG: Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
        
        print("ERROR: Should not reach here - all retries exhausted")
        return False