"""Tests for rule service"""

import pytest
from src.rules.rule_service import evaluate_rule, apply_rules


class TestRuleService:
    """Test the basic rule service"""
    
    def test_evaluate_rule_equality(self):
        """Test equality operator"""
        rule = {
            'condition': {
                'field': 'age',
                'operator': '==',
                'value': 30
            }
        }
        
        assert evaluate_rule(rule, {'age': 30}) is True
        assert evaluate_rule(rule, {'age': 31}) is False
        assert evaluate_rule(rule, {}) is False  # Missing field
    
    def test_evaluate_rule_greater_than(self):
        """Test greater than operator"""
        rule = {
            'condition': {
                'field': 'score',
                'operator': '>',
                'value': 50
            }
        }
        
        assert evaluate_rule(rule, {'score': 60}) is True
        assert evaluate_rule(rule, {'score': 50}) is False
        assert evaluate_rule(rule, {'score': 40}) is False
    
    def test_evaluate_rule_less_than(self):
        """Test less than operator"""
        rule = {
            'condition': {
                'field': 'score',
                'operator': '<',
                'value': 50
            }
        }
        
        assert evaluate_rule(rule, {'score': 40}) is True
        assert evaluate_rule(rule, {'score': 50}) is False
        assert evaluate_rule(rule, {'score': 60}) is False
    
    def test_evaluate_rule_greater_equal(self):
        """Test greater than or equal operator"""
        rule = {
            'condition': {
                'field': 'score',
                'operator': '>=',
                'value': 50
            }
        }
        
        assert evaluate_rule(rule, {'score': 60}) is True
        assert evaluate_rule(rule, {'score': 50}) is True
        assert evaluate_rule(rule, {'score': 40}) is False
    
    def test_evaluate_rule_less_equal(self):
        """Test less than or equal operator"""
        rule = {
            'condition': {
                'field': 'score',
                'operator': '<=',
                'value': 50
            }
        }
        
        assert evaluate_rule(rule, {'score': 40}) is True
        assert evaluate_rule(rule, {'score': 50}) is True
        assert evaluate_rule(rule, {'score': 60}) is False
    
    def test_evaluate_rule_unknown_operator(self):
        """Test unknown operator raises error"""
        rule = {
            'condition': {
                'field': 'score',
                'operator': 'unknown',
                'value': 50
            }
        }
        
        with pytest.raises(ValueError) as exc_info:
            evaluate_rule(rule, {'score': 50})
        assert "Unknown operator: unknown" in str(exc_info.value)
    
    def test_apply_rules_basic(self):
        """Test basic rule application"""
        rules = {
            'rules': [
                {
                    'name': 'High Score Rule',
                    'condition': {
                        'field': 'score',
                        'operator': '>',
                        'value': 70
                    },
                    'action': {
                        'field': 'category',
                        'value': 'advanced'
                    }
                }
            ]
        }
        
        user_data = {'score': 80}
        routines = {
            'routine1': {'category': 'advanced', 'name': 'Advanced Routine'},
            'routine2': {'category': 'beginner', 'name': 'Beginner Routine'},
            'routine3': {'category': 'advanced', 'name': 'Another Advanced'}
        }
        
        matched = apply_rules(rules, user_data, routines)
        
        assert len(matched) == 2
        assert 'routine1' in matched
        assert 'routine3' in matched
        assert 'routine2' not in matched
    
    def test_apply_rules_multiple_conditions(self):
        """Test applying multiple rules"""
        rules = {
            'rules': [
                {
                    'name': 'Young User Rule',
                    'condition': {
                        'field': 'age',
                        'operator': '<',
                        'value': 30
                    },
                    'action': {
                        'field': 'target',
                        'value': 'youth'
                    }
                },
                {
                    'name': 'Active User Rule',
                    'condition': {
                        'field': 'activity_level',
                        'operator': '>=',
                        'value': 4
                    },
                    'action': {
                        'field': 'intensity',
                        'value': 'high'
                    }
                }
            ]
        }
        
        user_data = {'age': 25, 'activity_level': 5}
        routines = {
            'routine1': {'target': 'youth', 'intensity': 'low'},
            'routine2': {'target': 'adult', 'intensity': 'high'},
            'routine3': {'target': 'youth', 'intensity': 'high'},
            'routine4': {'target': 'senior', 'intensity': 'low'}
        }
        
        matched = apply_rules(rules, user_data, routines)
        
        # Should match routines that are either for youth OR high intensity
        assert 'routine1' in matched  # youth match
        assert 'routine2' in matched  # high intensity match
        assert 'routine3' in matched  # both match
        assert 'routine4' not in matched  # neither match
    
    def test_apply_rules_no_matches(self):
        """Test when no rules match"""
        rules = {
            'rules': [
                {
                    'name': 'Impossible Rule',
                    'condition': {
                        'field': 'score',
                        'operator': '>',
                        'value': 1000
                    },
                    'action': {
                        'field': 'level',
                        'value': 'impossible'
                    }
                }
            ]
        }
        
        user_data = {'score': 50}
        routines = {
            'routine1': {'level': 'impossible'},
            'routine2': {'level': 'normal'}
        }
        
        matched = apply_rules(rules, user_data, routines)
        assert len(matched) == 0
    
    def test_apply_rules_missing_user_data(self):
        """Test when user data is missing required fields"""
        rules = {
            'rules': [
                {
                    'name': 'Age Rule',
                    'condition': {
                        'field': 'age',
                        'operator': '>',
                        'value': 18
                    },
                    'action': {
                        'field': 'audience',
                        'value': 'adult'
                    }
                }
            ]
        }
        
        user_data = {}  # Missing age field
        routines = {
            'routine1': {'audience': 'adult'},
            'routine2': {'audience': 'child'}
        }
        
        matched = apply_rules(rules, user_data, routines)
        assert len(matched) == 0  # No matches because condition fails