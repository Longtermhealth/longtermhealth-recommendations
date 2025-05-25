"""Tests for complex rule evaluation in filter service"""

import pytest
from src.scheduling.filter_service import (
    evaluate_condition, evaluate_conditions, evaluate_rule,
    check_dynamic_field, filter_inclusions
)


class TestFilterServiceRules:
    """Test the complex rule evaluation logic"""
    
    def test_evaluate_condition_operators(self):
        """Test all condition operators"""
        # Greater than
        assert evaluate_condition(10, '>', 5) is True
        assert evaluate_condition(5, '>', 10) is False
        
        # Greater than or equal
        assert evaluate_condition(10, '>=', 10) is True
        assert evaluate_condition(10, '>=', 5) is True
        assert evaluate_condition(5, '>=', 10) is False
        
        # Less than
        assert evaluate_condition(5, '<', 10) is True
        assert evaluate_condition(10, '<', 5) is False
        
        # Less than or equal
        assert evaluate_condition(10, '<=', 10) is True
        assert evaluate_condition(5, '<=', 10) is True
        assert evaluate_condition(10, '<=', 5) is False
        
        # Equality
        assert evaluate_condition(10, '==', 10) is True
        assert evaluate_condition(10, '==', 5) is False
        assert evaluate_condition('test', '==', 'test') is True
        
        # Inequality
        assert evaluate_condition(10, '!=', 5) is True
        assert evaluate_condition(10, '!=', 10) is False
        
        # Includes (list)
        assert evaluate_condition(['a', 'b', 'c'], 'includes', 'b') is True
        assert evaluate_condition(['a', 'b', 'c'], 'includes', 'd') is False
        
        # Includes (string)
        assert evaluate_condition('hello world', 'includes', 'world') is True
        assert evaluate_condition('hello world', 'includes', 'foo') is False
    
    def test_evaluate_condition_type_errors(self):
        """Test type error handling"""
        # Type mismatch should return False, not raise
        assert evaluate_condition('10', '>', 5) is False
        assert evaluate_condition(None, '>', 5) is False
        assert evaluate_condition(10, 'unknown_op', 5) is False
    
    def test_evaluate_conditions_and_logic(self):
        """Test AND logic for multiple conditions"""
        conditions = [
            {'field': 'age', 'operator': '>', 'value': 18},
            {'field': 'score', 'operator': '>=', 'value': 50}
        ]
        
        # Both conditions true
        pillar_data = {'age': 25, 'score': 60}
        assert evaluate_conditions(conditions, 'and', pillar_data, {}) is True
        
        # One condition false
        pillar_data = {'age': 25, 'score': 40}
        assert evaluate_conditions(conditions, 'and', pillar_data, {}) is False
        
        # Both conditions false
        pillar_data = {'age': 15, 'score': 40}
        assert evaluate_conditions(conditions, 'and', pillar_data, {}) is False
    
    def test_evaluate_conditions_or_logic(self):
        """Test OR logic for multiple conditions"""
        conditions = [
            {'field': 'age', 'operator': '>', 'value': 18},
            {'field': 'score', 'operator': '>=', 'value': 50}
        ]
        
        # Both conditions true
        pillar_data = {'age': 25, 'score': 60}
        assert evaluate_conditions(conditions, 'or', pillar_data, {}) is True
        
        # One condition true
        pillar_data = {'age': 25, 'score': 40}
        assert evaluate_conditions(conditions, 'or', pillar_data, {}) is True
        
        # Both conditions false
        pillar_data = {'age': 15, 'score': 40}
        assert evaluate_conditions(conditions, 'or', pillar_data, {}) is False
    
    def test_evaluate_conditions_cross_pillar_lookup(self):
        """Test looking up values across pillars"""
        conditions = [
            {'field': 'global_setting', 'operator': '==', 'value': 'active'}
        ]
        
        # Value not in pillar_data but in user_data
        pillar_data = {}
        user_data = {
            'GENERAL': {'global_setting': 'active'},
            'OTHER': {'some_field': 'value'}
        }
        
        assert evaluate_conditions(conditions, 'and', pillar_data, user_data) is True
    
    def test_check_dynamic_field(self):
        """Test dynamic field access with dot notation"""
        # Simple field
        attributes = {'name': 'test'}
        assert check_dynamic_field(attributes, 'name') == 'test'
        
        # Nested field
        attributes = {'tags': {'primary': 'health'}}
        assert check_dynamic_field(attributes, 'tags.primary') == 'health'
        
        # Deep nesting
        attributes = {'level1': {'level2': {'level3': 'value'}}}
        assert check_dynamic_field(attributes, 'level1.level2.level3') == 'value'
        
        # List handling
        attributes = {'items': [{'name': 'item1'}, {'name': 'item2'}]}
        result = check_dynamic_field(attributes, 'items.name')
        assert result == ['item1', 'item2']
        
        # Missing field
        assert check_dynamic_field(attributes, 'nonexistent') is None
        assert check_dynamic_field(None, 'any') is None
    
    def test_evaluate_rule_simple(self):
        """Test simple rule evaluation"""
        rule = {
            'condition': {
                'field': 'age',
                'operator': '>',
                'value': 18
            }
        }
        
        assert evaluate_rule(rule, {'age': 25}, {}) is True
        assert evaluate_rule(rule, {'age': 15}, {}) is False
    
    def test_evaluate_rule_complex(self):
        """Test complex rule with conditions object"""
        rule = {
            'conditions': {
                'logic': 'and',
                'rules': [
                    {'field': 'age', 'operator': '>', 'value': 18},
                    {'field': 'active', 'operator': '==', 'value': True}
                ]
            }
        }
        
        assert evaluate_rule(rule, {'age': 25, 'active': True}, {}) is True
        assert evaluate_rule(rule, {'age': 25, 'active': False}, {}) is False
        assert evaluate_rule(rule, {'age': 15, 'active': True}, {}) is False
    
    def test_filter_inclusions_weight_scoring(self):
        """Test routine scoring with weights"""
        routines = [
            {
                'id': 1,
                'attributes': {
                    'name': 'Routine 1',
                    'tags': ['cardio', 'beginner'],
                    'pillar': {'pillarEnum': 'MOVEMENT'}
                }
            },
            {
                'id': 2,
                'attributes': {
                    'name': 'Routine 2',
                    'tags': ['strength', 'advanced'],
                    'pillar': {'pillarEnum': 'MOVEMENT'}
                }
            },
            {
                'id': 3,
                'attributes': {
                    'name': 'Routine 3',
                    'tags': ['cardio', 'advanced'],
                    'pillar': {'pillarEnum': 'MOVEMENT'}
                }
            }
        ]
        
        rules = [
            {
                'name': 'Cardio Preference',
                'conditions': {
                    'logic': 'and',
                    'rules': [
                        {'field': 'prefers_cardio', 'operator': '==', 'value': True}
                    ]
                },
                'action': {
                    'field': 'tags',
                    'value': 'cardio',
                    'weight': 3
                }
            },
            {
                'name': 'Advanced Level',
                'conditions': {
                    'logic': 'and', 
                    'rules': [
                        {'field': 'fitness_level', 'operator': '>=', 'value': 4}
                    ]
                },
                'action': {
                    'field': 'tags',
                    'value': 'advanced',
                    'weight': 2
                }
            }
        ]
        
        pillar_data = {'prefers_cardio': True, 'fitness_level': 5}
        user_data = {}
        
        result = filter_inclusions(
            pillar_data, 'MOVEMENT', rules, routines, user_data, set()
        )
        
        # Check scores
        routine_1 = next(r for r in result if r['id'] == 1)
        routine_2 = next(r for r in result if r['id'] == 2)
        routine_3 = next(r for r in result if r['id'] == 3)
        
        assert routine_1.get('score_rules') == 3  # cardio only
        assert routine_2.get('score_rules') == 2  # advanced only
        assert routine_3.get('score_rules') == 5  # cardio + advanced
        
        # Check explanations
        assert 'Cardio Preference' in routine_3.get('score_rules_explanation', '')
        assert 'Advanced Level' in routine_3.get('score_rules_explanation', '')
    
    def test_filter_inclusions_excluded_routines(self):
        """Test that excluded routines are skipped"""
        routines = [
            {
                'id': 1,
                'attributes': {
                    'name': 'Routine 1',
                    'tags': ['cardio'],
                    'pillar': {'pillarEnum': 'MOVEMENT'},
                    'rule_status': 'excluded'  # Already excluded
                }
            },
            {
                'id': 2,
                'attributes': {
                    'name': 'Routine 2',
                    'tags': ['cardio'],
                    'pillar': {'pillarEnum': 'MOVEMENT'}
                }
            }
        ]
        
        rules = [
            {
                'name': 'Cardio Rule',
                'condition': {'field': 'likes_cardio', 'operator': '==', 'value': True},
                'action': {'field': 'tags', 'value': 'cardio', 'weight': 1}
            }
        ]
        
        pillar_data = {'likes_cardio': True}
        result = filter_inclusions(pillar_data, 'MOVEMENT', rules, routines, {}, set())
        
        # Routine 1 should remain excluded
        routine_1 = next(r for r in result if r['id'] == 1)
        assert routine_1['attributes'].get('rule_status') == 'excluded'
        assert routine_1.get('score_rules', 0) == 0
        
        # Routine 2 should be included
        routine_2 = next(r for r in result if r['id'] == 2)
        assert routine_2.get('rule_status') == 'included'
        assert routine_2.get('score_rules') == 1
    
    def test_filter_inclusions_multiple_actions(self):
        """Test rules with multiple actions"""
        routines = [
            {
                'id': 1,
                'attributes': {
                    'name': 'Routine 1',
                    'intensity': 'high',
                    'duration': 30,
                    'pillar': {'pillarEnum': 'MOVEMENT'}
                }
            }
        ]
        
        rules = [
            {
                'name': 'Advanced User',
                'condition': {'field': 'level', 'operator': '>', 'value': 3},
                'actions': [
                    {'field': 'intensity', 'value': 'high', 'weight': 2},
                    {'field': 'duration', 'value': 30, 'weight': 1}
                ]
            }
        ]
        
        pillar_data = {'level': 5}
        result = filter_inclusions(pillar_data, 'MOVEMENT', rules, routines, {}, set())
        
        routine = result[0]
        # Should get points for both matching actions
        assert routine.get('score_rules') == 3  # 2 + 1