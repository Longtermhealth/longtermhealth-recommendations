"""
Enhanced Response Formatter Service
Formats Typeform responses with actual question texts and all questions (answered and unanswered)
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional


class EnhancedResponseFormatter:
    def __init__(self):
        self.form_definitions = {}
        self.cache_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'cache')
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def load_form_definition(self, form_id: str) -> Optional[Dict]:
        """Load form definition from cache or file"""
        if form_id in self.form_definitions:
            return self.form_definitions[form_id]
        
        # Try to load from cache directory
        cache_file = os.path.join(self.cache_dir, f"form_definition_{form_id}.json")
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                self.form_definitions[form_id] = json.load(f)
                return self.form_definitions[form_id]
        
        # Try to load from parent directory
        parent_file = os.path.join(os.path.dirname(__file__), '..', '..', f"form_definition_{form_id}.json")
        if os.path.exists(parent_file):
            with open(parent_file, 'r') as f:
                self.form_definitions[form_id] = json.load(f)
                return self.form_definitions[form_id]
        
        return None
    
    def extract_all_questions(self, fields: List[Dict]) -> Dict[str, Dict]:
        """Extract all questions including those in inline groups"""
        questions = {}
        
        for field in fields:
            field_id = field.get('id')
            field_type = field.get('type')
            title = field.get('title', '')
            
            if field_type == 'inline_group':
                # Skip inline group containers - they don't have answers
                # The actual questions are in the regular fields
                continue
            else:
                # Regular field
                questions[field_id] = {
                    'title': title,
                    'type': field_type,
                    'properties': field.get('properties', {})
                }
        
        return questions
    
    def format_typeform_response(self, typeform_data: Dict, form_id: str = None) -> str:
        """
        Convert Typeform webhook data into a human-readable format with all questions.
        """
        formatted_response = []
        
        # Extract form information
        form_response = typeform_data.get('form_response', {})
        if not form_id:
            form_id = form_response.get('form_id', 'YXLWqe3x')  # Default to known form
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
        
        # Load form definition
        form_def = self.load_form_definition(form_id)
        form_title = "Unknown Form"
        all_questions = {}
        
        if form_def:
            form_title = form_def.get('title', 'Unknown Form')
            all_questions = self.extract_all_questions(form_def.get('fields', []))
        
        formatted_response.append(f"Form Submission Details:")
        formatted_response.append(f"- Form: {form_title}")
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
            formatted_response.append(f"Name: {name} {surname}".strip())
        if hidden:
            formatted_response.append("")
        
        # Create answer map
        answer_map = {}
        answers = form_response.get('answers', [])
        
        for answer in answers:
            field = answer.get('field', {})
            field_id = field.get('id')
            if field_id:
                answer_map[field_id] = answer
        
        # Process all questions
        formatted_response.append("Survey Responses:")
        formatted_response.append("-" * 40)
        
        # Use a manual mapping for the specific field IDs we know about
        question_order = [
            'uaybutbJir2L',  # Q1 from inline group
            'GxatWoxGQk5e',  # Q2 from inline group
            'p2KVqyv6AdIH',  # Q3
            '2HyjBoa3hzOC',  # Q4
            'rscDP2KytnHY',  # Q5
            'rwjIStVfI7f2',  # Q6
            'eBkLxdxhgZcr',  # Q7
            'ii0U0Nh3offk',  # Q9
            'VWsMhjFOLEyR',  # Q11
            'LLB2bIYGNrFx',  # Q13
            'sM7XBNskBFX8',  # Q14
            'zmC1hLoL7L3Y',  # Q15
            '7MRGsrn7o8EN',  # Q16
            'lZZrvQbD18Tv',  # Q17
            'mm4fvJ3jUx2U',  # Q18
            'qMv6OT5ye7M3',  # Q20
            'ZudpFtyCyuI2',  # Q21
            'i9ZUOqvsQ3Y1',  # Q22
            'dvyIAkxKQR3V',  # Q24
            'CyrtCSUV1c7X',  # Q25
            'cptvFO3zfR5L',  # Q26
            'p6hc1bPzAEGV',  # Q27
            'WZTrrYmNEz2C',  # Q28
            'kN6moX1N5t0K',  # Q29
        ]
        
        # Manual question mapping for inline group questions
        manual_questions = {
            'uaybutbJir2L': "Hast du das Gefühl die App kann dir helfen positive Veränderungen in deinem Leben zu machen?",
            'GxatWoxGQk5e': "Warum/Warum nicht?"
        }
        
        q_num = 1
        for field_id in question_order:
            # Get question info
            if field_id in all_questions:
                question_info = all_questions[field_id]
                title = question_info['title']
                field_type = question_info['type']
            elif field_id in manual_questions:
                title = manual_questions[field_id]
                field_type = answer_map.get(field_id, {}).get('field', {}).get('type', 'unknown')
            else:
                # Skip if we don't have question info
                continue
            
            formatted_response.append(f"\nQ{q_num}: {title}")
            
            # Check if we have an answer
            if field_id in answer_map:
                answer = answer_map[field_id]
                answer_type = answer.get('type', field_type)
                value = self._format_answer_value(answer, answer_type)
            else:
                value = '[Not answered]'
            
            formatted_response.append(f"Answer: {value}")
            q_num += 1
        
        # Add calculated metrics if available
        calculated = form_response.get('calculated', {})
        if calculated:
            score = calculated.get('score', 0)
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
            # For numeric types in answer object directly
            if 'number' in answer:
                value = str(answer.get('number', '-'))
            else:
                # Generic handling for unknown types
                value = str(answer.get(answer_type, '-'))
        
        # Handle empty values
        if value == '' or value == 'None':
            value = '-'
        
        return value