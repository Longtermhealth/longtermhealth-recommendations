"""Tests for display order filtering logic"""

import pytest
from src.scheduling.filter_service import (
    filter_routines_by_display_order,
    map_movement_orders,
    get_order
)


class TestDisplayOrderFilter:
    """Test display order filtering functionality"""
    
    def test_get_order_thresholds(self):
        """Test score to order mapping"""
        # Test exact thresholds
        assert get_order(0) == 1
        assert get_order(16) == 1
        assert get_order(16.1) == 2
        assert get_order(32) == 2
        assert get_order(32.1) == 3
        assert get_order(48) == 3
        assert get_order(48.1) == 4
        assert get_order(64) == 4
        assert get_order(64.1) == 5
        assert get_order(100) == 5
    
    def test_map_movement_orders(self):
        """Test movement order mapping from answers"""
        answers = {
            'Wie schätzt du deine Beweglichkeit ein?': 3,
            'Wie oft in der Woche treibst du eine Cardio-Sportart?': 5,
            'Wie schätzt du deine Kraft ein?': 2
        }
        
        result = map_movement_orders(answers)
        
        assert result['order_mobility'] == 3
        assert result['order_cardio'] == 5
        assert result['order_strength'] == 2
    
    def test_map_movement_orders_defaults(self):
        """Test movement order mapping with missing/invalid values"""
        # Missing values should default to 3
        assert map_movement_orders({})['order_mobility'] == 3
        assert map_movement_orders({})['order_cardio'] == 3
        assert map_movement_orders({})['order_strength'] == 3
        
        # Invalid values should default to 3
        answers = {
            'Wie schätzt du deine Beweglichkeit ein?': 'invalid',
            'Wie oft in der Woche treibst du eine Cardio-Sportart?': None,
            'Wie schätzt du deine Kraft ein?': []
        }
        result = map_movement_orders(answers)
        assert result['order_mobility'] == 3
        assert result['order_cardio'] == 3
        assert result['order_strength'] == 3
    
    def test_filter_routines_by_display_order_movement(self):
        """Test filtering movement routines by display order"""
        routines = [
            {
                'id': 1,
                'attributes': {
                    'pillar': {'pillarEnum': 'MOVEMENT'},
                    'movementType': 'cardio',
                    'displayForOrder': '3,4,5'
                }
            },
            {
                'id': 2,
                'attributes': {
                    'pillar': {'pillarEnum': 'MOVEMENT'},
                    'movementType': 'strength',
                    'displayForOrder': '1,2'
                }
            },
            {
                'id': 3,
                'attributes': {
                    'pillar': {'pillarEnum': 'MOVEMENT'},
                    'movementType': 'mobility',
                    'displayForOrder': '3'
                }
            }
        ]
        
        answers = {
            'Wie oft in der Woche treibst du eine Cardio-Sportart?': 5,  # order 5
            'Wie schätzt du deine Kraft ein?': 2,  # order 2
            'Wie schätzt du deine Beweglichkeit ein?': 3  # order 3
        }
        
        health_scores = {}
        
        result = filter_routines_by_display_order(routines, answers, health_scores)
        
        # Check routine 1 (cardio, order 5, allowed in 3,4,5)
        routine_1 = next(r for r in result if r['id'] == 1)
        assert routine_1['attributes'].get('rule_status') != 'excluded'
        
        # Check routine 2 (strength, order 2, allowed in 1,2)
        routine_2 = next(r for r in result if r['id'] == 2)
        assert routine_2['attributes'].get('rule_status') != 'excluded'
        
        # Check routine 3 (mobility, order 3, allowed in 3)
        routine_3 = next(r for r in result if r['id'] == 3)
        assert routine_3['attributes'].get('rule_status') != 'excluded'
    
    def test_filter_routines_by_display_order_exclusion(self):
        """Test routines are excluded when order doesn't match"""
        routines = [
            {
                'id': 1,
                'attributes': {
                    'pillar': {'pillarEnum': 'MOVEMENT'},
                    'movementType': 'cardio',
                    'displayForOrder': '1,2'  # Only for low orders
                }
            }
        ]
        
        answers = {
            'Wie oft in der Woche treibst du eine Cardio-Sportart?': 5  # order 5
        }
        
        result = filter_routines_by_display_order(routines, answers, {})
        
        routine = result[0]
        assert routine['attributes']['rule_status'] == 'excluded'
        assert routine['attributes']['score_rules'] == 0
        assert 'not in allowed orders' in routine['attributes']['score_rules_explanation']
    
    def test_filter_routines_by_display_order_non_movement(self):
        """Test filtering non-movement routines by health scores"""
        routines = [
            {
                'id': 1,
                'attributes': {
                    'pillar': {'pillarEnum': 'NUTRITION'},
                    'displayForOrder': '1,2'
                }
            },
            {
                'id': 2,
                'attributes': {
                    'pillar': {'pillarEnum': 'SLEEP'},
                    'displayForOrder': '3,4,5'
                }
            }
        ]
        
        health_scores = {
            'NUTRITION': 25,  # Will be order 2 (16 < 25 <= 32)
            'SLEEP': 70      # Will be order 5 (> 64)
        }
        
        result = filter_routines_by_display_order(routines, {}, health_scores)
        
        # Nutrition routine should be allowed (order 2 in allowed 1,2)
        routine_1 = next(r for r in result if r['id'] == 1)
        assert routine_1['attributes'].get('rule_status') != 'excluded'
        
        # Sleep routine should be allowed (order 5 in allowed 3,4,5)
        routine_2 = next(r for r in result if r['id'] == 2)
        assert routine_2['attributes'].get('rule_status') != 'excluded'
    
    def test_filter_routines_by_display_order_missing_score(self):
        """Test behavior when health score is missing"""
        routines = [
            {
                'id': 1,
                'attributes': {
                    'pillar': {'pillarEnum': 'UNKNOWN_PILLAR'},
                    'displayForOrder': '3',
                    'order': 2  # Fallback order
                }
            }
        ]
        
        health_scores = {}  # No score for UNKNOWN_PILLAR
        
        result = filter_routines_by_display_order(routines, {}, health_scores)
        
        # Should use fallback order from routine attributes
        routine = result[0]
        # Order 2 is not in allowed orders "3", so should be excluded
        assert routine['attributes']['rule_status'] == 'excluded'
    
    def test_filter_routines_by_display_order_empty(self):
        """Test routines without displayForOrder are not filtered"""
        routines = [
            {
                'id': 1,
                'attributes': {
                    'pillar': {'pillarEnum': 'MOVEMENT'},
                    'movementType': 'cardio',
                    'displayForOrder': ''  # Empty string
                }
            },
            {
                'id': 2,
                'attributes': {
                    'pillar': {'pillarEnum': 'MOVEMENT'},
                    'movementType': 'strength'
                    # No displayForOrder field
                }
            }
        ]
        
        result = filter_routines_by_display_order(routines, {}, {})
        
        # Both should remain unfiltered
        for routine in result:
            assert routine['attributes'].get('rule_status') != 'excluded'
    
    def test_filter_routines_by_display_order_invalid_format(self):
        """Test handling of invalid displayForOrder format"""
        routines = [
            {
                'id': 1,
                'attributes': {
                    'pillar': {'pillarEnum': 'MOVEMENT'},
                    'displayForOrder': 'invalid,format,abc'  # Non-numeric values
                }
            }
        ]
        
        result = filter_routines_by_display_order(routines, {}, {})
        
        # Should handle gracefully, likely by skipping
        assert len(result) == 1  # Routine still in results
    
    def test_movement_type_defaults(self):
        """Test movement type defaults to mobility"""
        routines = [
            {
                'id': 1,
                'attributes': {
                    'pillar': {'pillarEnum': 'MOVEMENT'},
                    # No movementType specified
                    'displayForOrder': '3'
                }
            }
        ]
        
        answers = {
            'Wie schätzt du deine Beweglichkeit ein?': 3  # mobility order 3
        }
        
        result = filter_routines_by_display_order(routines, answers, {})
        
        # Should use mobility order by default
        routine = result[0]
        assert routine['attributes'].get('rule_status') != 'excluded'