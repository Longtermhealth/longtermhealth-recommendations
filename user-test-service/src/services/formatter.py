"""
Response Formatter Service
Formats Typeform responses into human-readable feedback
"""
from datetime import datetime
from typing import Dict, List, Any

from services.typeform_service import TypeformService
from config.settings import TYPEFORM_ALWAYS_FETCH_LATEST


class ResponseFormatter:
    def __init__(self):
        self.typeform_service = TypeformService()
    
    def format_typeform_response(self, typeform_data: Dict) -> str:
        """
        Convert Typeform webhook data into a human-readable format.
        """
        formatted_response = []
        
        # Extract form information
        form_response = typeform_data.get('form_response', {})
        form_id = form_response.get('form_id', 'Unknown')
        submitted_at = form_response.get('submitted_at', '')
        
        # Format submission time
        if submitted_at:
            try:
                dt = datetime.fromisoformat(submitted_at.replace('Z', '+00:00'))
                formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
            except:
                formatted_time = submitted_at
        else:
            formatted_time = 'Unknown'
        
        formatted_response.append(f"Form Submission Details:")
        formatted_response.append(f"- Form ID: {form_id}")
        formatted_response.append(f"- Submitted at: {formatted_time}")
        formatted_response.append("")
        
        # Extract hidden fields
        hidden = form_response.get('hidden', {})
        account_id = hidden.get('accountid', '')
        email = hidden.get('email', '')
        name = hidden.get('name', '')
        surname = hidden.get('surname', '')
        
        if account_id:
            formatted_response.append(f"Account ID: {account_id}")
        if email:
            formatted_response.append(f"Email: {email}")
        if name or surname:
            formatted_response.append(f"Name: {name} {surname}")
        if hidden:
            formatted_response.append("")
        
        # Get master form definition
        master_form = self.typeform_service.get_and_save_master_form_definition(
            form_id, 
            force_refresh=TYPEFORM_ALWAYS_FETCH_LATEST
        )
        
        # Get webhook fields
        definition = form_response.get('definition', {})
        webhook_fields = definition.get('fields', [])
        
        # Build question reference map
        question_map = self.typeform_service.build_question_reference_map(master_form, webhook_fields)
        print(f"DEBUG: Built question map with {len(question_map)} total questions")
        
        # Create a mapping of field IDs to answers
        answer_map = {}
        answers = form_response.get('answers', [])
        print(f"DEBUG: Found {len(answers)} answers in response")
        
        for answer in answers:
            field = answer.get('field', {})
            field_id = field.get('id')
            if field_id:
                answer_map[field_id] = answer
        
        # Process all questions from master form
        formatted_response.append("Survey Responses:")
        formatted_response.append("-" * 40)
        
        # Build ordered list of all questions
        all_questions = []
        
        # Use the order from master form if available
        if master_form and 'fields' in master_form:
            # Extract questions in the order they appear in master form
            master_questions = self.typeform_service.extract_all_questions_from_fields(
                master_form['fields'], 
                is_master=True
            )
            for title, _ in master_questions:
                if title in question_map:
                    all_questions.append((title, question_map[title]))
        else:
            # Fallback to webhook order
            for title, info in question_map.items():
                all_questions.append((title, info))
        
        # Process each question
        for i, (title, question_info) in enumerate(all_questions, 1):
            field_id = question_info.get('webhook_id') or question_info.get('master_id')
            field_type = question_info.get('type', 'unknown')
            
            # Start with question number and title
            formatted_response.append(f"\nQ{i}: {title}")
            
            # Check if we have an answer for this question
            if field_id and field_id in answer_map:
                answer = answer_map[field_id]
                answer_type = answer.get('type', field_type)
                
                # Debug multiselect answers specifically
                if answer_type == 'choices':
                    print(f"DEBUG Q{i}: Multiselect answer found - {answer.get('choices', {}).get('labels', [])}")
                
                # Format the answer based on type
                value = self._format_answer_value(answer, answer_type)
            else:
                # No answer provided for this question
                value = '-'
            
            formatted_response.append(f"Answer: {value}")
        
        # Add calculated metrics if available
        calculated = form_response.get('calculated', {})
        if calculated:
            score = calculated.get('score', {})
            if score:
                formatted_response.append("")
                formatted_response.append("-" * 40)
                formatted_response.append(f"Total Score: {score}")
        
        return '\n'.join(formatted_response)
    
    def _format_answer_value(self, answer: Dict, answer_type: str) -> str:
        """
        Format answer value based on its type.
        """
        if answer_type == 'text':
            value = answer.get('text', '-')
        elif answer_type == 'number':
            value = str(answer.get('number', '-'))
        elif answer_type == 'boolean':
            value = 'Yes' if answer.get('boolean', False) else 'No'
        elif answer_type == 'choice':
            choice = answer.get('choice', {})
            value = choice.get('label', '-')
        elif answer_type == 'choices':
            choices = answer.get('choices', {})
            labels = choices.get('labels', [])
            value = ', '.join(labels) if labels else '-'
        elif answer_type == 'email':
            value = answer.get('email', '-')
        elif answer_type == 'url':
            value = answer.get('url', '-')
        elif answer_type == 'file_url':
            value = answer.get('file_url', '-')
        elif answer_type == 'date':
            value = answer.get('date', '-')
        elif answer_type == 'phone_number':
            value = answer.get('phone_number', '-')
        elif answer_type == 'rating':
            value = str(answer.get('rating', '-'))
        elif answer_type == 'opinion_scale':
            value = str(answer.get('opinion_scale', '-'))
        elif answer_type == 'nps':
            value = str(answer.get('nps', '-'))
        else:
            # Generic handling for unknown types
            value = str(answer.get(answer_type, '-'))
        
        # Handle empty values
        if value == '' or value == 'None':
            value = '-'
        
        return value