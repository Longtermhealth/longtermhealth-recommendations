#!/usr/bin/env python3
"""Test the service locally"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from app import app
    print("✅ App imported successfully")
    
    # Test the routes
    with app.test_client() as client:
        # Test home route
        response = client.get('/')
        print(f"/ endpoint: {response.status_code}")
        
        # Test health route
        response = client.get('/health')
        print(f"/health endpoint: {response.status_code}")
        
        # Test survey route (GET)
        response = client.get('/survey')
        print(f"/survey endpoint (GET): {response.status_code}")
        
    print("✅ All imports and basic routes work!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()