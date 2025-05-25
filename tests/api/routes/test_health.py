"""Tests for health check endpoint"""

import pytest


class TestHealthEndpoint:
    """Test the health check endpoint"""
    
    def test_health_check_success(self, client):
        """Test that health check returns success"""
        response = client.get('/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'message' in data
        
    def test_health_check_format(self, client):
        """Test health check response format"""
        response = client.get('/')
        data = response.get_json()
        
        # Should match original response
        assert 'Flask is working!' in data['message']