#!/usr/bin/env python3
"""
Credential Update Script

This script helps you update your Dux-Soup credentials in the webhook server.
"""

import re
import sys

def update_credentials():
    """Update USERID and APIKEY in start_webhook_server.py"""
    
    print("🔑 Dux-Soup Credential Update")
    print("=" * 40)
    
    # Get credentials from user
    print("\nPlease enter your Dux-Soup credentials:")
    userid = input("USERID: ").strip()
    apikey = input("APIKEY: ").strip()
    
    if not userid or not apikey:
        print("❌ USERID and APIKEY cannot be empty")
        return False
    
    try:
        # Read the file
        with open('start_webhook_server.py', 'r') as f:
            content = f.read()
        
        # Update USERID
        content = re.sub(
            r"USERID = ['\"].*?['\"]",
            f"USERID = '{userid}'",
            content
        )
        
        # Update APIKEY
        content = re.sub(
            r"APIKEY = ['\"].*?['\"]",
            f"APIKEY = '{apikey}'",
            content
        )
        
        # Write back to file
        with open('start_webhook_server.py', 'w') as f:
            f.write(content)
        
        print("✅ Credentials updated successfully!")
        print(f"   USERID: {userid}")
        print(f"   APIKEY: {apikey[:10]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating credentials: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        success = update_credentials()
        if success:
            print("\n🎉 Credentials updated! You can now run the webhook server.")
        else:
            print("\n❌ Failed to update credentials.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1) 