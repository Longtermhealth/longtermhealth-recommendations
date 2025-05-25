"""End-to-end integration tests comparing refactored vs original behavior"""

import pytest
import json
import time
from unittest.mock import patch, Mock


class TestEndToEndBehavior:
    """Test that refactored app behaves exactly like the original"""
    
    def test_webhook_full_flow(self, client, production_host, mock_external_apis):
        """Test complete webhook flow matches original behavior"""
        # Setup mock to return a realistic action plan
        mock_external_apis['scheduler'].return_value = {
            "data": {
                "actionPlanUniqueId": "new-plan-123",
                "accountId": 494,
                "periodInDays": 28,
                "gender": "MÄNNLICH",
                "totalDailyTimeInMins": 60,
                "routines": [
                    {
                        "routineUniqueId": 1,
                        "displayName": "Morning Meditation",
                        "scheduleDays": [1, 3, 5],
                        "pillar": {"pillarEnum": "STRESS"}
                    }
                ]
            }
        }
        
        # Track timing
        start_time = time.time()
        
        with patch('time.sleep') as mock_sleep:
            with client.application.test_request_context(
                '/webhook',
                base_url=f'http://{production_host}'
            ):
                response = client.post('/webhook', json={})
        
        # Verify response format matches original
        assert response.status_code == 200
        data = response.get_json()
        assert data == {'status': 'success', 'processingTime': pytest.regex(r'\d+\.\d+s')}
        
        # Verify timing behavior
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(3)  # Initial wait
        mock_sleep.assert_any_call(5)  # Before follow-up
        
        # Verify follow-up was triggered
        mock_external_apis['typeform']['trigger_followup'].assert_called_once_with(production_host)
    
    def test_event_recalculate_full_flow(self, client, recalculate_event_payload, 
                                        old_action_plan_response, initial_health_scores,
                                        mock_external_apis):
        """Test complete recalculate event flow"""
        response = client.post('/event', json=recalculate_event_payload)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify response structure matches original
        assert 'actionPlanUniqueId' in data
        assert 'matches' in data
        assert 'healthScores' in data
        
        # Verify matches are found correctly
        assert len(data['matches']) == 2
        match_ids = [m['id'] for m in data['matches']]
        assert 1 in match_ids
        assert 2 in match_ids
        
        # Verify health scores structure
        health_data = data['healthScores']['data']
        assert health_data['accountId'] == 494
        assert 'totalScore' in health_data
        assert 'pillarScores' in health_data
        
        # Verify each pillar score has required fields
        for pillar_score in health_data['pillarScores']:
            assert 'pillar' in pillar_score
            assert 'score' in pillar_score
            assert 'scoreInterpretation' in pillar_score
            assert 'rating' in pillar_score
            assert 'delta' in pillar_score  # Should have delta for updates
    
    def test_event_renew_full_flow(self, client, renew_event_payload, 
                                   old_action_plan_response, mock_external_apis):
        """Test complete renew event flow"""
        # Track what gets posted to Strapi
        posted_data = None
        
        def capture_post(data, account_id, env):
            nonlocal posted_data
            posted_data = data
            return {"success": True}
        
        mock_external_apis['strapi']['post_plan'].side_effect = capture_post
        
        response = client.post('/event', json=renew_event_payload)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify response structure
        assert 'data' in data
        plan_data = data['data']
        assert 'actionPlanUniqueId' in plan_data
        assert 'previousActionPlanUniqueId' in plan_data
        assert plan_data['previousActionPlanUniqueId'] == 'test-plan-123'
        assert plan_data['accountId'] == 494
        
        # Verify posted data
        assert posted_data is not None
        assert posted_data['data']['routines'][0]['scheduleDays'] == [1, 2, 3, 4, 5]
        assert posted_data['data']['gender'] == 'MÄNNLICH'  # Should be uppercase
    
    def test_error_responses_match_original(self, client):
        """Test that error responses match original format"""
        # Test missing JSON
        response = client.post('/event', data='not json', content_type='text/plain')
        assert response.status_code == 400
        assert 'error' in response.get_json()
        
        # Test missing eventEnum
        response = client.post('/event', json={})
        assert response.status_code == 400
        data = response.get_json()
        assert data == {"error": "Missing eventEnum in payload"}
        
        # Test invalid event type
        response = client.post('/event', json={"eventEnum": "INVALID"})
        assert response.status_code == 400
        data = response.get_json()
        assert "Unhandled event type" in data['error']
    
    def test_health_score_calculation_accuracy(self, client, mock_external_apis):
        """Test that health score calculations match original formula exactly"""
        # Create specific test case
        payload = {
            "eventEnum": "RECALCULATE_ACTION_PLAN",
            "eventPayload": json.dumps({
                "actionPlanUniqueId": "test-plan-123",
                "accountId": 494,
                "pillarCompletionStats": [{
                    "pillarEnum": "STRESS",
                    "routineCompletionStats": [{
                        "routineId": 1,
                        "displayName": "Meditation",
                        "completionStatistics": [{
                            "completionRate": 4,
                            "completionRatePeriodUnit": "MONTH",
                            "periodSequenceNo": 1
                        }]
                    }]
                }]
            })
        }
        
        # Set initial score
        mock_external_apis['strapi']['get_scores'].return_value = {"STRESS": 50.0}
        
        response = client.post('/event', json=payload)
        data = response.get_json()
        
        # Extract calculated score
        stress_score = None
        for pillar in data['healthScores']['data']['pillarScores']:
            if pillar['pillar']['pillarEnum'] == 'STRESS':
                stress_score = float(pillar['score'])
                delta = pillar['delta']
        
        # Verify calculation
        assert stress_score is not None
        assert stress_score > 50.0  # Should increase from completions
        assert delta > 0
        
        # Verify exact formula (k=0.025, dampening, etc)
        init_score = 50.0
        completed = 4
        scheduled = 1
        not_completed = 0
        
        dampening = (100 - init_score) / 90.0
        k = 0.025
        import math
        delta_completed = 10 * dampening * (1 - math.exp(-k * completed))
        delta_not = 10 * dampening * (1 - math.exp(-k * not_completed))
        expected_delta = delta_completed - (delta_not / 3.0)
        expected_score = init_score + expected_delta
        
        assert stress_score == pytest.approx(expected_score, rel=0.01)
        assert delta == pytest.approx(expected_delta, rel=0.01)