#!/usr/bin/env python3
"""
Chaknal Platform Monitoring Script
Monitors the health and performance of the deployed platform
"""

import requests
import time
import json
from datetime import datetime
import sys

# Configuration
BACKEND_URL = "https://chaknal-backend-container.azurewebsites.net"
FRONTEND_URL = "https://agreeable-bush-01890e00f.1.azurestaticapps.net"

def test_backend_health():
    """Test backend health endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Health: {data.get('status', 'unknown')}")
            print(f"   Database: {data.get('services', {}).get('database', 'unknown')}")
            return True
        else:
            print(f"❌ Backend Health: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend Health: Error - {e}")
        return False

def test_backend_api():
    """Test backend API endpoints"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/duxsoup-users/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend API: {len(data)} DuxSoup users found")
            return True
        else:
            print(f"❌ Backend API: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend API: Error - {e}")
        return False

def test_cors_configuration():
    """Test CORS configuration"""
    try:
        headers = {
            'Origin': FRONTEND_URL,
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'authorization,content-type'
        }
        response = requests.options(f"{BACKEND_URL}/api/duxsoup-users/", headers=headers, timeout=10)
        
        cors_headers = {
            'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
            'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
            'access-control-allow-headers': response.headers.get('access-control-allow-headers'),
            'access-control-allow-credentials': response.headers.get('access-control-allow-credentials')
        }
        
        print(f"✅ CORS Headers: {cors_headers}")
        return True
    except Exception as e:
        print(f"❌ CORS Test: Error - {e}")
        return False

def test_frontend_accessibility():
    """Test frontend accessibility"""
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        if response.status_code == 200:
            print(f"✅ Frontend: Accessible (HTTP {response.status_code})")
            return True
        else:
            print(f"❌ Frontend: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend: Error - {e}")
        return False

def test_api_documentation():
    """Test API documentation accessibility"""
    try:
        response = requests.get(f"{BACKEND_URL}/docs", timeout=10)
        if response.status_code == 200:
            print(f"✅ API Docs: Accessible (HTTP {response.status_code})")
            return True
        else:
            print(f"❌ API Docs: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Docs: Error - {e}")
        return False

def performance_test():
    """Test API response times"""
    endpoints = [
        "/health",
        "/api/duxsoup-users/",
        "/api/version",
        "/api/auth/status"
    ]
    
    print("\n📊 Performance Test:")
    for endpoint in endpoints:
        try:
            start_time = time.time()
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            if response.status_code == 200:
                print(f"   ✅ {endpoint}: {response_time:.2f}ms")
            else:
                print(f"   ❌ {endpoint}: HTTP {response.status_code} ({response_time:.2f}ms)")
        except Exception as e:
            print(f"   ❌ {endpoint}: Error - {e}")

def main():
    """Main monitoring function"""
    print("🔍 Chaknal Platform Monitoring")
    print("=" * 50)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Run all tests
    tests = [
        ("Backend Health", test_backend_health),
        ("Backend API", test_backend_api),
        ("CORS Configuration", test_cors_configuration),
        ("Frontend Accessibility", test_frontend_accessibility),
        ("API Documentation", test_api_documentation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}:")
        if test_func():
            passed += 1
    
    # Performance test
    performance_test()
    
    # Summary
    print(f"\n📋 Test Summary:")
    print(f"   Passed: {passed}/{total}")
    print(f"   Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed! Platform is healthy.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
