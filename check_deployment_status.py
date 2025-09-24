#!/usr/bin/env python3
"""
Check deployment status and test endpoints
"""

import requests
import time
import json

# Production URLs
BACKEND_URL = "https://chaknal-backend-container.azurewebsites.net"
FRONTEND_URL = "https://chaknal-frontend.azurestaticapps.net"

def check_backend_health():
    """Check if backend is healthy"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Health: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Backend Health: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend Health: Error - {str(e)}")
        return False

def check_campaign_creation():
    """Test campaign creation"""
    try:
        test_data = {
            "title": "Deployment Test Campaign",
            "name": "Deployment Test Campaign",
            "target_title": "Sales Manager",
            "intent": "Lead Generation"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/campaigns/",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Campaign Creation: Working (ID: {data.get('id', 'unknown')})")
            return True
        else:
            print(f"❌ Campaign Creation: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Campaign Creation: Error - {str(e)}")
        return False

def check_logging_endpoints():
    """Check if logging endpoints are available"""
    endpoints = [
        "/api/logs/import/test",
        "/api/test-simple-import",
        "/api/test-import-logging"
    ]
    
    available_endpoints = []
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=5)
            if response.status_code == 200:
                available_endpoints.append(endpoint)
                print(f"✅ {endpoint}: Available")
            else:
                print(f"❌ {endpoint}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {str(e)}")
    
    return available_endpoints

def check_frontend():
    """Check if frontend is accessible"""
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        if response.status_code == 200:
            print("✅ Frontend: Accessible")
            return True
        else:
            print(f"❌ Frontend: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend: Error - {str(e)}")
        return False

def main():
    """Main deployment status check"""
    print("🚀 Chaknal Platform Deployment Status Check")
    print("=" * 50)
    
    # Check backend health
    print("\n1️⃣ Backend Health Check:")
    backend_healthy = check_backend_health()
    
    # Check campaign creation
    print("\n2️⃣ Campaign Creation Test:")
    campaign_working = check_campaign_creation()
    
    # Check logging endpoints
    print("\n3️⃣ Logging Endpoints Check:")
    logging_endpoints = check_logging_endpoints()
    
    # Check frontend
    print("\n4️⃣ Frontend Check:")
    frontend_working = check_frontend()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Deployment Status Summary:")
    print(f"   Backend Health: {'✅' if backend_healthy else '❌'}")
    print(f"   Campaign Creation: {'✅' if campaign_working else '❌'}")
    print(f"   Logging Endpoints: {len(logging_endpoints)}/3 available")
    print(f"   Frontend: {'✅' if frontend_working else '❌'}")
    
    if backend_healthy and campaign_working and frontend_working:
        print("\n🎉 Core functionality is working!")
        if logging_endpoints:
            print("🔍 Logging system is available for debugging!")
        else:
            print("⏳ Logging system is still deploying...")
    else:
        print("\n⏳ Deployment is still in progress...")
        print("Please wait a few more minutes and try again.")

if __name__ == "__main__":
    main()
