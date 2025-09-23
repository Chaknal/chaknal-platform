"""
Test script to simulate webhook events for the data collector
"""

import requests
import json
import time
from datetime import datetime

# Webhook collector URL
WEBHOOK_URL = "http://localhost:5000/webhook"

def send_test_webhook(webhook_data):
    """Send a test webhook to the collector"""
    try:
        response = requests.post(WEBHOOK_URL, json=webhook_data)
        print(f"✅ Webhook sent: {response.status_code} - {response.json()}")
        return response.json()
    except Exception as e:
        print(f"❌ Error sending webhook: {e}")
        return None

def test_message_webhook():
    """Test message webhook event"""
    webhook_data = {
        "type": "message",
        "event": "received",
        "profile": "https://www.linkedin.com/in/chris-gullo/",
        "userid": "test_user_123",
        "data": {
            "from": "https://www.linkedin.com/in/chris-gullo/",
            "message": "Hi, thanks for connecting!",
            "timestamp": int(time.time() * 1000)
        },
        "timestamp": int(time.time() * 1000)
    }
    return send_test_webhook(webhook_data)

def test_action_webhook():
    """Test action webhook event"""
    webhook_data = {
        "type": "action",
        "event": "completed",
        "profile": "https://www.linkedin.com/in/sergio-campos/",
        "userid": "test_user_123",
        "data": {
            "action": "connect",
            "status": "success",
            "targeturl": "https://www.linkedin.com/in/sergio-campos/",
            "timestamp": int(time.time() * 1000)
        },
        "timestamp": int(time.time() * 1000)
    }
    return send_test_webhook(webhook_data)

def test_visit_webhook():
    """Test visit webhook event"""
    webhook_data = {
        "type": "visit",
        "event": "completed",
        "profile": "https://www.linkedin.com/in/jane-doe/",
        "userid": "test_user_123",
        "data": {
            "action": "visit",
            "status": "success",
            "targeturl": "https://www.linkedin.com/in/jane-doe/",
            "timestamp": int(time.time() * 1000)
        },
        "timestamp": int(time.time() * 1000)
    }
    return send_test_webhook(webhook_data)

def test_rccommand_webhook():
    """Test robot command webhook event"""
    webhook_data = {
        "type": "rccommand",
        "event": "ready",
        "userid": "test_user_123",
        "data": {
            "command": "ready",
            "status": "online",
            "timestamp": int(time.time() * 1000)
        },
        "timestamp": int(time.time() * 1000)
    }
    return send_test_webhook(webhook_data)

def test_connect_webhook():
    """Test connection webhook event"""
    webhook_data = {
        "type": "connect",
        "event": "accepted",
        "profile": "https://www.linkedin.com/in/alex-smith/",
        "userid": "test_user_123",
        "data": {
            "action": "connect",
            "status": "accepted",
            "targeturl": "https://www.linkedin.com/in/alex-smith/",
            "timestamp": int(time.time() * 1000)
        },
        "timestamp": int(time.time() * 1000)
    }
    return send_test_webhook(webhook_data)

def run_all_tests():
    """Run all test webhooks"""
    print("🧪 Testing Webhook Data Collector")
    print("=" * 50)
    
    tests = [
        ("Message Event", test_message_webhook),
        ("Action Event", test_action_webhook),
        ("Visit Event", test_visit_webhook),
        ("Robot Command Event", test_rccommand_webhook),
        ("Connect Event", test_connect_webhook)
    ]
    
    for test_name, test_func in tests:
        print(f"\n📤 Testing: {test_name}")
        result = test_func()
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("\n📊 Check the analysis report at: http://localhost:5000/analysis")
    print("📋 Check recent events at: http://localhost:5000/events")

if __name__ == "__main__":
    run_all_tests() 