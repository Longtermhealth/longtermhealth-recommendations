"""
Typeform Webhook Handler
Process incoming Typeform webhooks and update ClickUp
"""
import json
import traceback
from typing import Dict, Tuple, Optional

from services.clickup_service import ClickUpService
from services.formatter import ResponseFormatter


class TypeformWebhookHandler:
    def __init__(self):
        self.clickup_service = ClickUpService()
        self.formatter = ResponseFormatter()
    
    def process_webhook(self, data: Dict) -> Tuple[Dict, int]:
        """
        Process Typeform webhook data and update ClickUp.
        Returns (response_dict, status_code)
        """
        try:
            print("\n" + "="*80)
            print("NEW WEBHOOK REQUEST RECEIVED")
            print("="*80)
            
            # Validate webhook data
            if not data:
                print("ERROR: No data received in request")
                return {"status": "error", "message": "No data received"}, 400
            
            print(f"DEBUG: Received Typeform webhook data:")
            print(json.dumps(data, indent=2))
            print("-"*80)
            
            # Extract form response
            form_response = data.get('form_response', {})
            if not form_response:
                print("WARNING: No form_response found in data")
                print(f"Available keys in data: {list(data.keys())}")
            
            # Extract hidden fields
            hidden = form_response.get('hidden', {})
            email, name, surname = self._extract_user_info(data, hidden)
            
            print(f"DEBUG: Extracted user info:")
            print(f"  Email: '{email}'")
            print(f"  Name: '{name}'")
            print(f"  Surname: '{surname}'")
            
            # Check if we have valid values (not masked)
            valid_email = email and email != 'hidden_value'
            valid_name = (name and name != 'hidden_value') or (surname and surname != 'hidden_value')
            
            if not valid_email and not valid_name:
                print("ERROR: No valid email or name found (all values are masked)")
                return self._create_masked_fields_response(hidden), 200
            
            # Format the response
            print("DEBUG: Formatting Typeform response...")
            formatted_feedback = self.formatter.format_typeform_response(data)
            print(f"DEBUG: Formatted feedback:\n{formatted_feedback}")
            print("-"*80)
            
            # Process in ClickUp
            return self._process_clickup_update(email, name, surname, formatted_feedback)
            
        except Exception as e:
            print(f"UNEXPECTED ERROR: {str(e)}")
            print("Full traceback:")
            traceback.print_exc()
            
            return {
                "status": "error",
                "message": f"Internal server error: {str(e)}",
                "typeform_status": "Data received but processing failed",
                "error_details": str(e),
                "action_required": "Check server logs for full error details"
            }, 200  # Always return 200 to prevent Typeform retries
    
    def _extract_user_info(self, data: Dict, hidden: Dict) -> Tuple[str, str, str]:
        """
        Extract user information from webhook data.
        """
        email = hidden.get('email', '')
        name = hidden.get('name', '')
        surname = hidden.get('surname', '')
        
        # Check if values are masked
        if email == 'hidden_value':
            print("WARNING: Hidden fields are masked by Typeform")
            print("DEBUG: Checking for other identifying information...")
            
            # Try to extract from other sources
            respondent_email = data.get('form_response', {}).get('email', '')
            if respondent_email:
                email = respondent_email
                print(f"DEBUG: Found respondent email: {email}")
            
            # Check variables if available
            variables = data.get('form_response', {}).get('variables', [])
            for var in variables:
                if var.get('key') == 'email':
                    email = var.get('text', '')
                elif var.get('key') == 'name':
                    name = var.get('text', '')
                elif var.get('key') == 'surname':
                    surname = var.get('text', '')
        
        return email, name, surname
    
    def _create_masked_fields_response(self, hidden: Dict) -> Dict:
        """
        Create response for masked fields scenario.
        """
        print("DEBUG: This usually means:")
        print("  1. The webhook needs to be reconfigured in Typeform")
        print("  2. Hidden fields need to be properly passed to the form")
        print("  3. Check Typeform webhook settings for 'Include hidden fields'")
        
        return {
            "status": "warning", 
            "message": "Hidden fields are masked - please check Typeform webhook configuration",
            "hidden_fields_received": hidden,
            "instructions": "Make sure 'Include hidden fields' is enabled in Typeform webhook settings",
            "typeform_status": "Data received but could not process due to masked fields"
        }
    
    def _process_clickup_update(self, email: str, name: str, surname: str, 
                               formatted_feedback: str) -> Tuple[Dict, int]:
        """
        Process the ClickUp update logic.
        """
        # Find existing task
        print(f"DEBUG: Searching for ClickUp task with email/name...")
        task_id = self.clickup_service.find_task_by_email_or_name(email, name, surname)
        
        if not task_id:
            # No task found - create a new one
            print(f"WARNING: No existing task found for user")
            print(f"Creating new task for: {name} {surname} ({email})")
            
            task_id = self.clickup_service.create_new_task(email, name, surname, formatted_feedback)
            
            if task_id:
                return self._create_success_response(
                    task_id=task_id,
                    action="created_new_task",
                    message=f"Created new task {task_id} with feedback",
                    email=email,
                    name=name,
                    surname=surname
                ), 200
            else:
                return self._create_failure_response(
                    action="create_new_task_failed",
                    email=email,
                    name=name,
                    surname=surname,
                    formatted_feedback=formatted_feedback
                ), 200
        
        # Found existing task - create subtask
        print(f"DEBUG: Found existing task ID: {task_id}")
        print(f"DEBUG: Creating subtask under task {task_id} with feedback...")
        
        subtask_id = self.clickup_service.create_subtask_with_feedback(
            task_id, formatted_feedback, email, name, surname
        )
        
        if subtask_id:
            return self._create_success_response(
                task_id=task_id,
                subtask_id=subtask_id,
                action="created_subtask_for_existing_user",
                message=f"Successfully created subtask {subtask_id} with feedback",
                email=email,
                name=name,
                surname=surname
            ), 200
        else:
            return self._create_partial_success_response(
                task_id=task_id,
                email=email,
                name=name,
                surname=surname,
                formatted_feedback=formatted_feedback
            ), 200
    
    def _create_success_response(self, **kwargs) -> Dict:
        """Create a success response."""
        response = {
            "status": "success",
            "typeform_status": "Data received successfully",
            "clickup_status": "Updated successfully",
            "user": {
                "email": kwargs.get('email', ''),
                "name": kwargs.get('name', ''),
                "surname": kwargs.get('surname', ''),
                "full_name": f"{kwargs.get('name', '')} {kwargs.get('surname', '')}".strip()
            }
        }
        # Add any additional kwargs to response
        for key, value in kwargs.items():
            if key not in ['email', 'name', 'surname']:
                response[key] = value
        return response
    
    def _create_failure_response(self, **kwargs) -> Dict:
        """Create a failure response."""
        return {
            "status": "warning",
            "message": "Could not find existing task or create new one",
            "typeform_status": "Data received successfully",
            "clickup_status": "Failed to create new task",
            "search_criteria": {
                "email": kwargs.get('email', ''),
                "name": kwargs.get('name', ''),
                "surname": kwargs.get('surname', ''),
                "full_name": f"{kwargs.get('name', '')} {kwargs.get('surname', '')}".strip()
            },
            "feedback_preserved": kwargs.get('formatted_feedback', ''),
            "action_required": "Manually create task and add feedback"
        }
    
    def _create_partial_success_response(self, **kwargs) -> Dict:
        """Create a partial success response."""
        return {
            "status": "partial_success",
            "message": f"Data received but failed to create subtask under ClickUp task {kwargs.get('task_id', '')}",
            "typeform_status": "Data received successfully",
            "clickup_status": "Failed to create subtask - manual intervention required",
            "parent_task_id": kwargs.get('task_id', ''),
            "user": {
                "email": kwargs.get('email', ''),
                "name": kwargs.get('name', ''),
                "surname": kwargs.get('surname', ''),
                "full_name": f"{kwargs.get('name', '')} {kwargs.get('surname', '')}".strip()
            },
            "feedback_preserved": kwargs.get('formatted_feedback', ''),
            "action_required": "Manually create subtask with the keyFeedback in ClickUp"
        }