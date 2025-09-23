#!/usr/bin/env python3
"""
Test script for the active campaigns endpoint
"""

import requests
import json
from datetime import datetime

def test_active_campaigns_endpoint():
    """Test the active campaigns endpoint"""
    
    # Base URL for the webhook server
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Active Campaigns Endpoint")
    print("=" * 50)
    
    # Test 1: Get active campaigns
    print("📋 Test 1: Getting active campaigns...")
    try:
        response = requests.get(f"{base_url}/campaigns/active")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {data.get('count', 0)} active campaigns")
            
            campaigns = data.get('active_campaigns', [])
            for i, campaign in enumerate(campaigns, 1):
                print(f"\n📊 Campaign {i}:")
                print(f"   Name: {campaign.get('name', 'N/A')}")
                print(f"   Status: {campaign.get('status', 'N/A')}")
                print(f"   Total Contacts: {campaign.get('total_contacts', 0)}")
                print(f"   Accepted: {campaign.get('accepted_count', 0)}")
                print(f"   Replied: {campaign.get('replied_count', 0)}")
                print(f"   Reply Rate: {campaign.get('reply_rate', 0)}%")
                print(f"   Scheduled Start: {campaign.get('scheduled_start', 'Not set')}")
                print(f"   End Date: {campaign.get('end_date', 'Not set')}")
                print(f"   Is Active: {campaign.get('is_active', False)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the webhook server is running on localhost:5000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    # Test 2: Check home endpoint for new endpoint documentation
    print("\n📋 Test 2: Checking endpoint documentation...")
    try:
        response = requests.get(f"{base_url}/")
        
        if response.status_code == 200:
            data = response.json()
            endpoints = data.get('endpoints', {})
            
            if 'active_campaigns' in endpoints:
                print("✅ Active campaigns endpoint is documented")
                print(f"   Documentation: {endpoints['active_campaigns']}")
            else:
                print("❌ Active campaigns endpoint not found in documentation")
        else:
            print(f"❌ Error getting home endpoint: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking documentation: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    test_active_campaigns_endpoint() 