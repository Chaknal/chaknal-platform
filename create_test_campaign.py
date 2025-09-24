#!/usr/bin/env python3
"""
Create a test campaign via API to populate the database
"""

import requests
import json

# Production API base URL
BASE_URL = "https://chaknal-backend-container.azurewebsites.net"

def create_test_campaign():
    """Create a test campaign via API"""
    print("🚀 Creating test campaign via API...")
    
    # Test campaign data
    campaign_data = {
        "title": "Test LinkedIn Campaign",
        "name": "Test LinkedIn Campaign",
        "target_title": "Sales Manager",
        "intent": "Lead Generation",
        "initial_action": "inmail",
        "initial_message": "Hi {first_name}, I'd like to connect with you.",
        "initial_subject": "Connection Request",
        "follow_up_actions": ["message", "message"],
        "delay_days": 3,
        "random_delay": True,
        "status": "active"
    }
    
    try:
        # Create campaign
        response = requests.post(
            f"{BASE_URL}/api/campaigns/",
            json=campaign_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Campaign created successfully!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Failed to create campaign: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating campaign: {str(e)}")
        return False

def create_test_contact():
    """Create a test contact via API"""
    print("🚀 Creating test contact via API...")
    
    # Test contact data
    contact_data = {
        "first_name": "John",
        "last_name": "Smith",
        "email": "john.smith@example.com",
        "company_name": "Example Corp",
        "job_title": "Sales Manager",
        "linkedin_url": "https://linkedin.com/in/johnsmith"
    }
    
    try:
        # Create contact
        response = requests.post(
            f"{BASE_URL}/api/contacts/",
            json=contact_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Contact created successfully!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Failed to create contact: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating contact: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎯 Adding test data to production database...")
    
    # Create test contact first
    contact_success = create_test_contact()
    
    # Create test campaign
    campaign_success = create_test_campaign()
    
    if contact_success and campaign_success:
        print("\n🎉 Test data added successfully!")
        print("You should now see data on the frontend.")
    else:
        print("\n❌ Failed to add test data.")
        print("The database might need to be set up with proper schema first.")
