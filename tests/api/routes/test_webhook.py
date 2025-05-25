"""Tests for webhook endpoint"""

import pytest
import time
from unittest.mock import patch, call


class TestWebhookEndpoint:
    """Test the webhook endpoint"""
    
    def test_webhook_original_request(self, client, mock_external_apis):
        """Test original webhook request (not follow-up)"""
        with patch('time.sleep'):  # Speed up tests
            response = client.post('/webhook', json={})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'processingTime' in data
        
        # Should trigger scheduler
        mock_external_apis['scheduler'].assert_called_once()
        
        # Should trigger follow-up
        mock_external_apis['typeform']['trigger_followup'].assert_called_once()
    
    def test_webhook_followup_request(self, client, mock_external_apis):
        """Test follow-up webhook request"""
        with patch('time.sleep'):
            response = client.post(
                '/webhook',
                json={},
                headers={'X-Webhook-Followup': 'true'}
            )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'follow-up processed'
        
        # Should trigger scheduler
        mock_external_apis['scheduler'].assert_called_once()
        
        # Should NOT trigger another follow-up
        mock_external_apis['typeform']['trigger_followup'].assert_not_called()
    
    def test_webhook_with_production_host(self, client, production_host, mock_external_apis):
        """Test webhook with production host"""
        with patch('time.sleep'):
            with client.application.test_request_context(
                '/webhook',
                base_url=f'http://{production_host}'
            ):
                response = client.post('/webhook', json={})
        
        assert response.status_code == 200
        
        # Check scheduler was called with correct host
        mock_external_apis['scheduler'].assert_called_once_with(production_host)
    
    def test_webhook_with_dev_host(self, client, dev_host, mock_external_apis):
        """Test webhook with development host"""
        with patch('time.sleep'):
            with client.application.test_request_context(
                '/webhook',
                base_url=f'http://{dev_host}'
            ):
                response = client.post('/webhook', json={})
        
        assert response.status_code == 200
        
        # Check scheduler was called with correct host
        mock_external_apis['scheduler'].assert_called_once_with(dev_host)
    
    def test_webhook_error_handling(self, client, mock_external_apis):
        """Test webhook error handling"""
        # Make scheduler raise an exception
        mock_external_apis['scheduler'].side_effect = Exception("Test error")
        
        with patch('time.sleep'):
            response = client.post('/webhook', json={})
        
        assert response.status_code == 502  # External service error
        data = response.get_json()
        assert 'error' in data
        assert 'Action Plan Creation' in data['error']
    
    def test_webhook_timing(self, client, mock_external_apis):
        """Test webhook timing behavior matches original"""
        start_time = time.time()
        
        with patch('time.sleep') as mock_sleep:
            response = client.post('/webhook', json={})
        
        # Should have two sleep calls: 3 seconds at start, 5 seconds before follow-up
        assert mock_sleep.call_count == 2
        mock_sleep.assert_has_calls([call(3), call(5)])
        
        assert response.status_code == 200