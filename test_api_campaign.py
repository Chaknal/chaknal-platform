#!/usr/bin/env python3
"""
Test Campaign API Directly
==========================

This script tests the campaign creation API endpoint directly
to see what's causing the "Failed to create campaign" error.
"""

import requests
import json

def test_campaign_api():
    """Test the campaign creation API"""
    
    print("🧪 Testing Campaign API")
    print("=" * 40)
    
    # API endpoint
    api_url = "https://chaknal-backend-1758294239.azurewebsites.net/api/campaigns"
    
    # Test campaign data
    campaign_data = {
        "name": "API Test Campaign",
        "description": "Testing campaign creation via API",
        "target_title": "Software Engineer",
        "intent": "Testing the API endpoint",
        "dux_user_id": "test_user_123",
        "initial_action": "message",
        "initial_message": "Hello! This is a test message.",
        "delay_days": 3,
        "random_delay": True
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        print("🔗 Making API request...")
        print(f"URL: {api_url}")
        print(f"Data: {json.dumps(campaign_data, indent=2)}")
        
        response = requests.post(
            api_url, 
            json=campaign_data, 
            headers=headers,
            timeout=30
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Campaign created successfully!")
            print(f"📋 Campaign ID: {result.get('campaign_id')}")
            print(f"📋 Campaign Name: {result.get('name')}")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📋 Error Details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"📋 Raw Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_campaign_api()
    if success:
        print("\n✅ SUCCESS: API can create campaigns")
    else:
        print("\n❌ FAILED: API campaign creation failed")
        print("\n🤔 This might be the same error the frontend is encountering!")
