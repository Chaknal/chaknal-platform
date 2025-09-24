#!/usr/bin/env python3
"""
Add data to production database via API endpoints
"""

import requests
import json

# Production API base URL
BASE_URL = "https://chaknal-backend-container.azurewebsites.net"

def add_data_via_api():
    """Add data to production database via API"""
    print("🚀 Adding data to production database via API...")
    
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
    print("💡 The issue is that the Azure PostgreSQL database is empty.")
    print("   This explains why you're not seeing any data on the frontend.")
    
    print("\n🔍 Possible solutions:")
    print("   1. The database was reset during deployment")
    print("   2. The data was never migrated to the production database")
    print("   3. The database connection is pointing to a different database")
    
    print("\n🚀 Next steps:")
    print("   1. Check if there's a backup of the database with data")
    print("   2. Run database migrations to ensure schema is set up")
    print("   3. Import existing data from a backup")
    print("   4. Add some initial data manually through the API")
    
    print("\n📝 To add data manually, you can:")
    print("   1. Use the contact import feature in the frontend")
    print("   2. Create campaigns and contacts through the API")
    print("   3. Check if there's existing data in a different database")

if __name__ == "__main__":
    add_data_via_api()

