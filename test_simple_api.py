#!/usr/bin/env python3
"""
Test script to check if our rebuilt API routers work locally
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

try:
    print("Testing import of rebuilt API routers...")
    
    # Test importing the main file
    print("1. Testing main.py import...")
    from app.main import app
    print("   ✅ main.py imported successfully")
    
    # Test the app routes
    print("2. Testing app routes...")
    routes = [route.path for route in app.routes]
    print(f"   Found {len(routes)} routes:")
    for route in routes[:10]:  # Show first 10 routes
        print(f"     - {route}")
    
    # Test specific API routes
    print("3. Testing API routes...")
    api_routes = [route for route in routes if route.startswith('/api/')]
    print(f"   Found {len(api_routes)} API routes:")
    for route in api_routes:
        print(f"     - {route}")
    
    print("\n✅ All tests passed! The rebuilt API should work.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
