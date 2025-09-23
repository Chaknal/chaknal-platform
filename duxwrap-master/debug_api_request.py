import os
import json
import time
import hashlib
import hmac
import base64
import requests
from duxwrap.enhanced_duxwrap import DuxUser, EnhancedDuxWrap, DuxSoupAPIError

# Get credentials
USERID = os.environ.get("DUXSOUP_USERID", "117833704731893145427")
APIKEY = os.environ.get("DUXSOUP_APIKEY", "e96sH0Qehcqk8LWsyNjJpr9OL9qzasXR")

print("\n--- Dux-Soup API Debug ---\n")

# Test 1: Check if we can get profile info (this worked before)
print("=== Test 1: Get Profile Info ===")
try:
    dux_user = DuxUser(userid=USERID, apikey=APIKEY)
    dux = EnhancedDuxWrap(dux_user)
    profile = dux.get_profile()
    print(f"[SUCCESS] Profile: {profile}")
except Exception as e:
    print(f"[ERROR] Get profile failed: {e}")

# Test 2: Check queue size (this worked before)
print("\n=== Test 2: Get Queue Size ===")
try:
    queue_size = dux.get_queue_size()
    print(f"[SUCCESS] Queue size: {queue_size}")
except Exception as e:
    print(f"[ERROR] Get queue size failed: {e}")

# Test 3: Manual API request to see the exact format
print("\n=== Test 3: Manual API Request ===")
try:
    # Create the request data manually
    data = {
        "targeturl": "https://app.dux-soup.com",
        "timestamp": int(time.time() * 1000),
        "userid": USERID,
        "command": "visit",
        "params": {
            "profile": "https://www.linkedin.com/in/chgullo/"
        }
    }
    
    # Create signature
    json_data = json.dumps(data)
    mac = hmac.new(bytes(APIKEY, 'ascii'), digestmod=hashlib.sha1)
    mac.update(bytes(json_data, 'ascii'))
    signature = str(base64.b64encode(mac.digest()), 'ascii')
    
    # Make request
    url = f"https://app.dux-soup.com/xapi/remote/control/{USERID}/queue"
    headers = {
        "Content-Type": "application/json",
        "X-Dux-Signature": signature
    }
    
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    response = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"[ERROR] Manual request failed: {e}")

# Test 4: Try with minimal parameters
print("\n=== Test 4: Minimal Visit Request ===")
try:
    # Try with just the required parameters
    minimal_data = {
        "targeturl": "https://app.dux-soup.com",
        "timestamp": int(time.time() * 1000),
        "userid": USERID,
        "command": "visit",
        "params": {
            "profile": "https://www.linkedin.com/in/chgullo/"
        }
    }
    
    json_data = json.dumps(minimal_data)
    mac = hmac.new(bytes(APIKEY, 'ascii'), digestmod=hashlib.sha1)
    mac.update(bytes(json_data, 'ascii'))
    signature = str(base64.b64encode(mac.digest()), 'ascii')
    
    url = f"https://app.dux-soup.com/xapi/remote/control/{USERID}/queue"
    headers = {
        "Content-Type": "application/json",
        "X-Dux-Signature": signature
    }
    
    response = requests.post(url, json=minimal_data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"[ERROR] Minimal request failed: {e}")

print("\n--- End of Debug ---") 