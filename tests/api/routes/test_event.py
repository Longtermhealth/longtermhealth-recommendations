"""Tests for event endpoint"""

import pytest
import json
from unittest.mock import patch


class TestEventEndpoint:
    """Test the event endpoint"""
    
    def test_recalculate_action_plan_success(self, client, recalculate_event_payload, 
                                           old_action_plan_response, mock_external_apis):
        """Test RECALCULATE_ACTION_PLAN event"""
        response = client.post('/event', json=recalculate_event_payload)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Should return action plan ID and matches
        assert data['actionPlanUniqueId'] == 'test-plan-123'
        assert 'matches' in data
        assert isinstance(data['matches'], list)
        
        # Should have found matching routines
        assert len(data['matches']) == 2
        assert data['matches'][0]['id'] == 1
        assert data['matches'][0]['name'] == 'Morning Meditation'
        
        # Should calculate health scores
        assert 'healthScores' in data
        assert 'data' in data['healthScores']
        assert data['healthScores']['data']['accountId'] == 494
    
    def test_recalculate_with_string_payload(self, client, mock_external_apis):
        """Test event with string eventPayload (like original)"""
        payload = {
            "eventEnum": "RECALCULATE_ACTION_PLAN",
            "eventPayload": '{"actionPlanUniqueId": "test-plan-123", "accountId": 494, "pillarCompletionStats": []}'
        }
        
        response = client.post('/event', json=payload)
        assert response.status_code == 200
    
    def test_recalculate_with_dict_payload(self, client, mock_external_apis):
        """Test event with dict eventPayload"""
        payload = {
            "eventEnum": "RECALCULATE_ACTION_PLAN",
            "eventPayload": {
                "actionPlanUniqueId": "test-plan-123",
                "accountId": 494,
                "pillarCompletionStats": []
            }
        }
        
        response = client.post('/event', json=payload)
        assert response.status_code == 200
    
    def test_renew_action_plan_success(self, client, renew_event_payload, mock_external_apis):
        """Test RENEW_ACTION_PLAN event"""
        response = client.post('/event', json=renew_event_payload)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Should return new action plan
        assert 'data' in data
        assert 'actionPlanUniqueId' in data['data']
        assert data['data']['accountId'] == 494
        
        # Should have posted to Strapi
        mock_external_apis['strapi']['post_plan'].assert_called_once()
    
    def test_renew_with_schedule_changes(self, client, renew_event_payload, 
                                        old_action_plan_response, mock_external_apis):
        """Test renew applies schedule changes correctly"""
        response = client.post('/event', json=renew_event_payload)
        
        assert response.status_code == 200
        
        # Check that post was called with updated schedule
        post_call_args = mock_external_apis['strapi']['post_plan'].call_args[0][0]
        routines = post_call_args['data']['routines']
        
        # First routine should have updated schedule days
        assert routines[0]['scheduleDays'] == [1, 2, 3, 4, 5]
    
    def test_event_missing_enum(self, client):
        """Test event without eventEnum"""
        response = client.post('/event', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Missing eventEnum' in data['error']
    
    def test_event_invalid_json_payload(self, client):
        """Test event with invalid JSON in eventPayload"""
        payload = {
            "eventEnum": "RECALCULATE_ACTION_PLAN",
            "eventPayload": "invalid json"
        }
        
        response = client.post('/event', json=payload)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Invalid eventPayload JSON' in data['error']
    
    def test_event_unhandled_type(self, client):
        """Test unhandled event type"""
        payload = {
            "eventEnum": "UNKNOWN_EVENT",
            "eventPayload": "{}"
        }
        
        response = client.post('/event', json=payload)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Unhandled event type' in data['error']
    
    def test_event_missing_action_plan_id(self, client):
        """Test recalculate without action plan ID"""
        payload = {
            "eventEnum": "RECALCULATE_ACTION_PLAN",
            "eventPayload": json.dumps({"accountId": 494})
        }
        
        response = client.post('/event', json=payload)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Missing actionPlanUniqueId' in data['error']
    
    def test_event_action_plan_not_found(self, client, mock_external_apis):
        """Test when action plan is not found"""
        mock_external_apis['strapi']['get_plan'].return_value = None
        
        payload = {
            "eventEnum": "RECALCULATE_ACTION_PLAN",
            "eventPayload": json.dumps({
                "actionPlanUniqueId": "non-existent",
                "accountId": 494
            })
        }
        
        response = client.post('/event', json=payload)
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'Action Plan not found' in data['error']