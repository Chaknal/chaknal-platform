#!/usr/bin/env python3
"""
Test the logging system for contact import debugging
"""

import requests
import json
import time

# Production API base URL
BASE_URL = "https://chaknal-backend-container.azurewebsites.net"

def test_logging_system():
    """Test the logging system"""
    print("🧪 Testing Contact Import Logging System...")
    
    try:
        # Test 1: Check if logging endpoints are available
        print("\n1️⃣ Testing logging endpoints...")
        response = requests.get(f"{BASE_URL}/api/logs/import/test")
        if response.status_code == 200:
            print("✅ Logging endpoints are working!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Logging endpoints failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
        
        # Test 2: Get import logs
        print("\n2️⃣ Getting import logs...")
        response = requests.get(f"{BASE_URL}/api/logs/import")
        if response.status_code == 200:
            logs = response.json()
            print(f"✅ Retrieved {len(logs.get('logs', []))} log entries")
            for log in logs.get('logs', [])[-3:]:  # Show last 3 logs
                print(f"   📝 {log['timestamp']} | {log['level']} | {log['operation']} | {log['message']}")
        else:
            print(f"❌ Failed to get logs: {response.status_code}")
        
        # Test 3: Get import statistics
        print("\n3️⃣ Getting import statistics...")
        response = requests.get(f"{BASE_URL}/api/logs/import/stats")
        if response.status_code == 200:
            stats = response.json()
            print("✅ Import statistics:")
            print(f"   📊 Total operations: {stats['stats']['total_operations']}")
            print(f"   📈 Operations by type: {stats['stats']['operations_by_type']}")
            print(f"   📊 Operations by level: {stats['stats']['operations_by_level']}")
        else:
            print(f"❌ Failed to get stats: {response.status_code}")
        
        # Test 4: Test contact import with logging
        print("\n4️⃣ Testing contact import with logging...")
        response = requests.get(f"{BASE_URL}/api/test-import-logging")
        if response.status_code == 200:
            print("✅ Contact import logging test successful!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Contact import logging test failed: {response.status_code}")
        
        print("\n🎉 Logging system test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing logging system: {str(e)}")
        return False

def monitor_import_logs():
    """Monitor import logs in real-time"""
    print("📊 Monitoring import logs...")
    print("Press Ctrl+C to stop monitoring\n")
    
    try:
        while True:
            response = requests.get(f"{BASE_URL}/api/logs/import?limit=5")
            if response.status_code == 200:
                logs = response.json()
                recent_logs = logs.get('logs', [])
                
                if recent_logs:
                    print(f"\n📝 Recent logs ({len(recent_logs)} entries):")
                    for log in recent_logs:
                        print(f"   {log['timestamp']} | {log['level']} | {log['operation']} | {log['message']}")
                else:
                    print("📝 No recent logs")
            
            time.sleep(5)  # Check every 5 seconds
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped")

if __name__ == "__main__":
    print("🚀 Contact Import Logging System Test")
    print("=" * 50)
    
    # Test the logging system
    if test_logging_system():
        print("\n" + "=" * 50)
        print("📊 Logging system is ready for debugging!")
        print("You can now:")
        print("1. Try importing contacts through the frontend")
        print("2. Check logs at: https://chaknal-backend-container.azurewebsites.net/api/logs/import")
        print("3. Monitor logs in real-time")
        
        # Ask if user wants to monitor logs
        try:
            monitor = input("\nWould you like to monitor logs in real-time? (y/n): ").lower().strip()
            if monitor == 'y':
                monitor_import_logs()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
    else:
        print("\n❌ Logging system test failed!")
        print("Check the backend deployment and try again.")
