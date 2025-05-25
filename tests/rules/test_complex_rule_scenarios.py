"""Tests for complex rule scenarios and edge cases"""

import pytest
from src.scheduling.filter_service import (
    filter_inclusions, ensure_default_fields, delete_filtered_routines,
    evaluate_rule, evaluate_conditions
)


class TestComplexRuleScenarios:
    """Test complex rule scenarios and interactions"""
    
    def test_rule_priority_and_accumulation(self):
        """Test that multiple matching rules accumulate scores"""
        routines = [
            {
                'id': 1,
                'attributes': {
                    'name': 'Ultimate Routine',
                    'difficulty': 'advanced',
                    'duration': 30,
                    'tags': ['cardio', 'strength', 'flexibility'],
                    'pillar': {'pillarEnum': 'MOVEMENT'}
                }
            }
        ]
        
        rules = [
            {
                'name': 'Advanced User',
                'condition': {'field': 'level', 'operator': '>=', 'value': 4},
                'action': {'field': 'difficulty', 'value': 'advanced', 'weight': 5}
            },
            {
                'name': 'Time Available',
                'condition': {'field': 'available_time', 'operator': '>=', 'value': 30},
                'action': {'field': 'duration', 'value': 30, 'weight': 3}
            },
            {
                'name': 'Cardio Focus',
                'condition': {'field': 'goal', 'operator': '==', 'value': 'cardio'},
                'action': {'field': 'tags', 'value': 'cardio', 'weight': 4}
            }
        ]
        
        pillar_data = {
            'level': 5,
            'available_time': 45,
            'goal': 'cardio'
        }
        
        result = filter_inclusions(pillar_data, 'MOVEMENT', rules, routines, {}, set())
        
        routine = result[0]
        # Should accumulate all matching scores: 5 + 3 + 4 = 12
        assert routine.get('score_rules') == 12
        assert routine.get('rule_status') == 'included'
        
        # Check that all rules are mentioned in explanation
        explanation = routine.get('score_rules_explanation', '')
        assert 'Advanced User' in explanation
        assert 'Time Available' in explanation
        assert 'Cardio Focus' in explanation
    
    def test_conflicting_conditions(self):
        """Test behavior with conflicting rule conditions"""
        routines = [
            {
                'id': 1,
                'attributes': {
                    'name': 'Beginner Routine',
                    'level': 'beginner',
                    'pillar': {'pillarEnum': 'MOVEMENT'}
                }
            },
            {
                'id': 2,
                'attributes': {
                    'name': 'Advanced Routine',
                    'level': 'advanced',
                    'pillar': {'pillarEnum': 'MOVEMENT'}
                }
            }
        ]
        
        # User has conflicting preferences
        rules = [
            {
                'name': 'Low Fitness',
                'condition': {'field': 'fitness_score', 'operator': '<', 'value': 30},
                'action': {'field': 'level', 'value': 'beginner', 'weight': 10}
            },
            {
                'name': 'Wants Challenge',
                'condition': {'field': 'prefers_challenge', 'operator': '==', 'value': True},
                'action': {'field': 'level', 'value': 'advanced', 'weight': 5}
            }
        ]
        
        pillar_data = {
            'fitness_score': 20,  # Low fitness
            'prefers_challenge': True  # But wants challenge
        }
        
        result = filter_inclusions(pillar_data, 'MOVEMENT', rules, routines, {}, set())
        
        routine_1 = next(r for r in result if r['id'] == 1)
        routine_2 = next(r for r in result if r['id'] == 2)
        
        # Beginner routine should score higher due to weight
        assert routine_1.get('score_rules') == 10
        assert routine_2.get('score_rules') == 5
    
    def test_nested_conditions_complex_logic(self):
        """Test complex nested conditions with mixed logic"""
        rule = {
            'conditions': {
                'logic': 'or',
                'rules': [
                    {
                        'logic': 'and',
                        'rules': [
                            {'field': 'age', 'operator': '>=', 'value': 18},
                            {'field': 'age', 'operator': '<=', 'value': 65}
                        ]
                    },
                    {
                        'logic': 'and',
                        'rules': [
                            {'field': 'medical_clearance', 'operator': '==', 'value': True},
                            {'field': 'supervised', 'operator': '==', 'value': True}
                        ]
                    }
                ]
            }
        }
        
        # Test case 1: Adult in age range
        assert evaluate_rule(rule, {'age': 30}, {}) is True
        
        # Test case 2: Too young, but has medical clearance and supervision
        pillar_data = {
            'age': 16,
            'medical_clearance': True,
            'supervised': True
        }
        assert evaluate_rule(rule, pillar_data, {}) is True
        
        # Test case 3: Too old and no medical clearance
        assert evaluate_rule(rule, {'age': 70}, {}) is False
    
    def test_ensure_default_fields(self):
        """Test that default fields are properly set"""
        routines = [
            {'id': 1, 'attributes': {}},  # No rule status
            {'id': 2, 'attributes': {}, 'rule_status': 'included'},  # Already has status
            {'id': 3, 'attributes': {}, 'rule_status': 'excluded'},  # Already excluded
            {'id': 4, 'attributes': {'score_rules': 5}}  # Has score but no status
        ]
        
        result = ensure_default_fields(routines)
        
        # Check routine 1 gets defaults
        routine_1 = next(r for r in result if r['id'] == 1)
        assert routine_1['attributes']['rule_status'] == 'no_rule_applied'
        assert routine_1['attributes']['score_rules'] == 1
        assert routine_1['attributes']['score_rules_explanation'] == "No inclusion rule applied"
        
        # Check routines 2 and 3 are unchanged
        routine_2 = next(r for r in result if r['id'] == 2)
        assert routine_2['rule_status'] == 'included'
        
        routine_3 = next(r for r in result if r['id'] == 3)
        assert routine_3['rule_status'] == 'excluded'
        
        # Check routine 4 gets missing fields
        routine_4 = next(r for r in result if r['id'] == 4)
        assert routine_4['attributes']['rule_status'] == 'no_rule_applied'
        assert routine_4['attributes']['score_rules'] == 1  # Reset to default
    
    def test_delete_filtered_routines(self):
        """Test deletion of routines without rule status"""
        routines = [
            {'id': 1, 'rule_status': 'included'},
            {'id': 2, 'rule_status': 'excluded'},
            {'id': 3},  # No status - should be deleted
            {'id': 4, 'rule_status': 'no_rule_applied'},  # Should be deleted
            {'id': 5, 'rule_status': 'included'}
        ]
        
        result = delete_filtered_routines(routines)
        
        # Only included and excluded should remain
        assert len(result) == 3
        assert all(r['id'] in [1, 2, 5] for r in result)
    
    def test_cross_pillar_rule_evaluation(self):
        """Test rules that reference data from other pillars"""
        routines = [
            {
                'id': 1,
                'attributes': {
                    'name': 'Sleep Meditation',
                    'type': 'meditation',
                    'pillar': {'pillarEnum': 'SLEEP'}
                }
            }
        ]
        
        rules = [
            {
                'name': 'Stressed User Needs Meditation',
                'conditions': {
                    'logic': 'and',
                    'rules': [
                        {'field': 'stress_level', 'operator': '>', 'value': 7},
                        {'field': 'sleep_quality', 'operator': '<', 'value': 5}
                    ]
                },
                'action': {'field': 'type', 'value': 'meditation', 'weight': 10}
            }
        ]
        
        # Sleep pillar data
        pillar_data = {'sleep_quality': 3}
        
        # Stress data in different pillar
        user_data = {
            'STRESS': {'stress_level': 8},
            'SLEEP': {'sleep_quality': 3}
        }
        
        result = filter_inclusions(pillar_data, 'SLEEP', rules, routines, user_data, set())
        
        routine = result[0]
        assert routine.get('score_rules') == 10
        assert routine.get('rule_status') == 'included'
    
    def test_rule_with_list_field_matching(self):
        """Test rules matching against list fields"""
        routines = [
            {
                'id': 1,
                'attributes': {
                    'name': 'Multi-benefit Routine',
                    'benefits': ['strength', 'flexibility', 'endurance'],
                    'equipment': ['mat', 'bands'],
                    'pillar': {'pillarEnum': 'MOVEMENT'}
                }
            },
            {
                'id': 2,
                'attributes': {
                    'name': 'Simple Routine',
                    'benefits': ['flexibility'],
                    'equipment': [],
                    'pillar': {'pillarEnum': 'MOVEMENT'}
                }
            }
        ]
        
        rules = [
            {
                'name': 'Wants Strength',
                'condition': {'field': 'goal_benefits', 'operator': 'includes', 'value': 'strength'},
                'action': {'field': 'benefits', 'value': 'strength', 'weight': 5}
            },
            {
                'name': 'Has Equipment',
                'condition': {'field': 'available_equipment', 'operator': 'includes', 'value': 'mat'},
                'action': {'field': 'equipment', 'value': 'mat', 'weight': 3}
            }
        ]
        
        pillar_data = {
            'goal_benefits': ['strength', 'endurance'],
            'available_equipment': ['mat', 'dumbbells']
        }
        
        result = filter_inclusions(pillar_data, 'MOVEMENT', rules, routines, {}, set())
        
        routine_1 = next(r for r in result if r['id'] == 1)
        routine_2 = next(r for r in result if r['id'] == 2)
        
        # Routine 1 matches both rules
        assert routine_1.get('score_rules') == 8  # 5 + 3
        
        # Routine 2 matches neither
        assert routine_2.get('score_rules', 0) == 0
    
    def test_edge_case_empty_rules(self):
        """Test behavior with empty rules"""
        routines = [{'id': 1, 'attributes': {'pillar': {'pillarEnum': 'MOVEMENT'}}}]
        
        # Empty rules list
        result = filter_inclusions({}, 'MOVEMENT', [], routines, {}, set())
        assert len(result) == 1
        assert result[0].get('rule_status') is None
        
        # None rules
        result = filter_inclusions({}, 'MOVEMENT', None, routines, {}, set())
        assert len(result) == 1
    
    def test_edge_case_malformed_rules(self):
        """Test graceful handling of malformed rules"""
        routines = [
            {
                'id': 1,
                'attributes': {
                    'type': 'test',
                    'pillar': {'pillarEnum': 'MOVEMENT'}
                }
            }
        ]
        
        malformed_rules = [
            {},  # Empty rule
            {'name': 'No Condition'},  # Missing condition
            {'condition': {'field': 'test'}},  # Missing operator/value
            {'condition': {'field': 'test', 'operator': '>', 'value': 5}},  # Missing action
        ]
        
        # Should not crash
        result = filter_inclusions({'test': 10}, 'MOVEMENT', malformed_rules, routines, {}, set())
        assert len(result) == 1