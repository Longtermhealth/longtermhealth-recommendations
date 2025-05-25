"""Integration tests for the complete rule processing pipeline"""

import pytest
import json
from unittest.mock import patch, Mock


class TestRuleIntegration:
    """Test complete rule processing workflow"""
    
    @pytest.fixture
    def sample_rules(self):
        """Sample rules configuration"""
        return {
            "inclusion_rules": {
                "MOVEMENT": [
                    {
                        "name": "Beginner Cardio",
                        "conditions": {
                            "logic": "and",
                            "rules": [
                                {"field": "fitness_level", "operator": "<=", "value": 2},
                                {"field": "prefers_cardio", "operator": "==", "value": True}
                            ]
                        },
                        "action": {
                            "field": "tags",
                            "value": "beginner-cardio",
                            "weight": 5
                        }
                    },
                    {
                        "name": "High Intensity",
                        "conditions": {
                            "logic": "and",
                            "rules": [
                                {"field": "fitness_level", "operator": ">=", "value": 4},
                                {"field": "available_time", "operator": ">=", "value": 30}
                            ]
                        },
                        "actions": [
                            {"field": "intensity", "value": "high", "weight": 3},
                            {"field": "duration", "value": 30, "weight": 2}
                        ]
                    }
                ],
                "NUTRITION": [
                    {
                        "name": "Vegan Diet",
                        "condition": {
                            "field": "diet_type",
                            "operator": "==",
                            "value": "vegan"
                        },
                        "action": {
                            "field": "diet_restriction",
                            "value": "vegan",
                            "weight": 10
                        }
                    }
                ],
                "SLEEP": [
                    {
                        "name": "Insomnia Support",
                        "conditions": {
                            "logic": "or",
                            "rules": [
                                {"field": "sleep_quality", "operator": "<", "value": 3},
                                {"field": "sleep_problems", "operator": "includes", "value": "insomnia"}
                            ]
                        },
                        "action": {
                            "field": "focus",
                            "value": "sleep-aid",
                            "weight": 8
                        }
                    }
                ]
            }
        }
    
    @pytest.fixture
    def sample_routines(self):
        """Sample routines data"""
        return [
            {
                "id": 1,
                "attributes": {
                    "name": "Gentle Morning Walk",
                    "pillar": {"pillarEnum": "MOVEMENT", "displayName": "Movement"},
                    "tags": ["beginner-cardio", "low-impact"],
                    "intensity": "low",
                    "duration": 20,
                    "displayForOrder": "1,2,3"
                }
            },
            {
                "id": 2,
                "attributes": {
                    "name": "HIIT Workout",
                    "pillar": {"pillarEnum": "MOVEMENT", "displayName": "Movement"},
                    "tags": ["advanced", "high-intensity"],
                    "intensity": "high",
                    "duration": 30,
                    "displayForOrder": "4,5"
                }
            },
            {
                "id": 3,
                "attributes": {
                    "name": "Vegan Meal Prep",
                    "pillar": {"pillarEnum": "NUTRITION", "displayName": "Nutrition"},
                    "diet_restriction": "vegan",
                    "prep_time": 45,
                    "displayForOrder": "1,2,3,4,5"
                }
            },
            {
                "id": 4,
                "attributes": {
                    "name": "Sleep Meditation",
                    "pillar": {"pillarEnum": "SLEEP", "displayName": "Sleep"},
                    "focus": "sleep-aid",
                    "duration": 15,
                    "displayForOrder": "1,2,3,4,5"
                }
            },
            {
                "id": 5,
                "attributes": {
                    "name": "Power Nap Guide",
                    "pillar": {"pillarEnum": "SLEEP", "displayName": "Sleep"},
                    "focus": "energy",
                    "duration": 20,
                    "displayForOrder": "3,4,5"
                }
            }
        ]
    
    @pytest.fixture
    def user_data_beginner(self):
        """User data for a beginner"""
        return {
            "MOVEMENT": {
                "fitness_level": 1,
                "prefers_cardio": True,
                "available_time": 20
            },
            "NUTRITION": {
                "diet_type": "omnivore"
            },
            "SLEEP": {
                "sleep_quality": 4,
                "sleep_problems": []
            }
        }
    
    @pytest.fixture 
    def user_data_advanced(self):
        """User data for an advanced user"""
        return {
            "MOVEMENT": {
                "fitness_level": 5,
                "prefers_cardio": False,
                "available_time": 45
            },
            "NUTRITION": {
                "diet_type": "vegan"
            },
            "SLEEP": {
                "sleep_quality": 2,
                "sleep_problems": ["insomnia", "restless"]
            }
        }
    
    def test_complete_rule_pipeline_beginner(self, sample_rules, sample_routines, 
                                           user_data_beginner):
        """Test complete pipeline for beginner user"""
        from src.scheduling.filter_service import (
            filter_inclusions, filter_routines_by_display_order,
            ensure_default_fields
        )
        
        # Process each pillar
        processed_routines = sample_routines.copy()
        
        # Apply inclusion rules for each pillar
        for pillar, pillar_data in user_data_beginner.items():
            pillar_rules = sample_rules["inclusion_rules"].get(pillar, [])
            processed_routines = filter_inclusions(
                pillar_data, pillar, pillar_rules, 
                processed_routines, user_data_beginner, set()
            )
        
        # Ensure defaults
        processed_routines = ensure_default_fields(processed_routines)
        
        # Apply display order filtering (mock health scores)
        health_scores = {
            "MOVEMENT": 20,  # Order 2
            "NUTRITION": 50,  # Order 4
            "SLEEP": 65      # Order 5
        }
        
        final_routines = filter_routines_by_display_order(
            processed_routines, 
            {"Wie schätzt du deine Beweglichkeit ein?": 2},
            health_scores
        )
        
        # Verify results
        # Routine 1 (beginner cardio) should be included with high score
        routine_1 = next(r for r in final_routines if r['id'] == 1)
        assert routine_1.get('rule_status') == 'included'
        assert routine_1.get('score_rules') == 5
        assert 'Beginner Cardio' in routine_1.get('score_rules_explanation', '')
        
        # Routine 2 (HIIT) should not match rules and be excluded by display order
        routine_2 = next(r for r in final_routines if r['id'] == 2)
        assert routine_2['attributes']['rule_status'] == 'excluded'
        assert routine_2['attributes']['score_rules'] == 0
        
        # Routine 3 (vegan) should have default status (no rule match)
        routine_3 = next(r for r in final_routines if r['id'] == 3)
        assert routine_3['attributes']['rule_status'] == 'no_rule_applied'
        
        # Sleep routines should have default status
        routine_4 = next(r for r in final_routines if r['id'] == 4)
        assert routine_4['attributes']['rule_status'] == 'no_rule_applied'
    
    def test_complete_rule_pipeline_advanced(self, sample_rules, sample_routines,
                                           user_data_advanced):
        """Test complete pipeline for advanced user"""
        from src.scheduling.filter_service import (
            filter_inclusions, filter_routines_by_display_order,
            ensure_default_fields
        )
        
        processed_routines = sample_routines.copy()
        
        # Apply inclusion rules
        for pillar, pillar_data in user_data_advanced.items():
            pillar_rules = sample_rules["inclusion_rules"].get(pillar, [])
            processed_routines = filter_inclusions(
                pillar_data, pillar, pillar_rules,
                processed_routines, user_data_advanced, set()
            )
        
        processed_routines = ensure_default_fields(processed_routines)
        
        # High fitness scores
        health_scores = {
            "MOVEMENT": 80,  # Order 5
            "NUTRITION": 75,  # Order 5  
            "SLEEP": 30      # Order 2
        }
        
        final_routines = filter_routines_by_display_order(
            processed_routines,
            {"Wie schätzt du deine Kraft ein?": 5},
            health_scores
        )
        
        # Routine 1 (beginner) excluded by display order
        routine_1 = next(r for r in final_routines if r['id'] == 1)
        assert routine_1['attributes']['rule_status'] == 'excluded'
        
        # Routine 2 (HIIT) should be included
        routine_2 = next(r for r in final_routines if r['id'] == 2)
        assert routine_2.get('rule_status') == 'included'
        assert routine_2.get('score_rules') == 5  # 3 + 2 from both actions
        
        # Routine 3 (vegan) should be included
        routine_3 = next(r for r in final_routines if r['id'] == 3)
        assert routine_3.get('rule_status') == 'included'
        assert routine_3.get('score_rules') == 10
        
        # Routine 4 (sleep meditation) should be included
        routine_4 = next(r for r in final_routines if r['id'] == 4)
        assert routine_4.get('rule_status') == 'included'
        assert routine_4.get('score_rules') == 8
    
    def test_rule_accumulation_across_pillars(self):
        """Test that rules accumulate properly within pillars but not across"""
        from src.scheduling.filter_service import filter_inclusions
        
        routines = [
            {
                "id": 1,
                "attributes": {
                    "name": "Universal Routine",
                    "pillar": {"pillarEnum": "MOVEMENT"},
                    "tags": ["cardio", "strength"],
                    "level": "intermediate"
                }
            }
        ]
        
        # Multiple matching rules in same pillar
        movement_rules = [
            {
                "name": "Rule 1",
                "condition": {"field": "test", "operator": "==", "value": True},
                "action": {"field": "tags", "value": "cardio", "weight": 3}
            },
            {
                "name": "Rule 2", 
                "condition": {"field": "test", "operator": "==", "value": True},
                "action": {"field": "tags", "value": "strength", "weight": 2}
            },
            {
                "name": "Rule 3",
                "condition": {"field": "test", "operator": "==", "value": True},
                "action": {"field": "level", "value": "intermediate", "weight": 1}
            }
        ]
        
        result = filter_inclusions(
            {"test": True}, "MOVEMENT", movement_rules, routines, {}, set()
        )
        
        # Should accumulate all matching scores
        assert result[0].get('score_rules') == 6  # 3 + 2 + 1
        
        # Process again with different pillar - should not affect score
        sleep_rules = [{
            "name": "Sleep Rule",
            "condition": {"field": "test", "operator": "==", "value": True},
            "action": {"field": "unrelated", "value": "value", "weight": 10}
        }]
        
        result = filter_inclusions(
            {"test": True}, "SLEEP", sleep_rules, result, {}, set()
        )
        
        # Movement routine score should remain unchanged
        assert result[0].get('score_rules') == 6
    
    def test_excluded_rules_tracking(self):
        """Test that matched rules are tracked in included_rules set"""
        from src.scheduling.filter_service import filter_inclusions, included_rules
        
        # Clear any existing rules
        included_rules.clear()
        
        routines = [{
            "id": 1,
            "attributes": {
                "pillar": {"pillarEnum": "MOVEMENT"},
                "type": "test"
            }
        }]
        
        rules = [{
            "name": "Test Rule",
            "condition": {"field": "match", "operator": "==", "value": True},
            "action": {"field": "type", "value": "test", "weight": 1}
        }]
        
        filter_inclusions({"match": True}, "MOVEMENT", rules, routines, {}, included_rules)
        
        # Check that rule was tracked
        assert len(included_rules) == 1
        assert ("Test Rule", "type: test") in included_rules