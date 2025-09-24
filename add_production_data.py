#!/usr/bin/env python3
"""
Add basic data to production database
"""

import requests
import json

# Production API base URL
BASE_URL = "https://chaknal-backend-container.azurewebsites.net"

def add_production_data():
    """Add basic data to production database via API"""
    print("🚀 Adding data to production database...")
    
    # Test if we can reach the API
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Backend is healthy and connected")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot reach backend: {str(e)}")
        return
    
    # Check current data
    print("\n📊 Checking current data...")
    campaigns_response = requests.get(f"{BASE_URL}/api/campaigns/")
    contacts_response = requests.get(f"{BASE_URL}/api/contacts/")
    
    print(f"Campaigns: {len(campaigns_response.json()) if campaigns_response.status_code == 200 else 'Error'}")
    print(f"Contacts: {len(contacts_response.json()) if contacts_response.status_code == 200 else 'Error'}")
    
    if campaigns_response.status_code == 200 and len(campaigns_response.json()) > 0:
        print("✅ Data already exists in production database")
        return
    
    print("\n🔧 Production database appears to be empty")
    print("💡 You may need to:")
    print("   1. Run database migrations on the production database")
    print("   2. Import existing data from a backup")
    print("   3. Check if the database connection is pointing to the right database")
    
    print("\n🔍 To check the database connection, you can:")
    print("   1. Check Azure App Service configuration")
    print("   2. Verify the DATABASE_URL environment variable")
    print("   3. Check if the database has the correct schema")

if __name__ == "__main__":
    add_production_data()
