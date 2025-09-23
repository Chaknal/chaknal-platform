#!/usr/bin/env python3
"""
Send Message to Chris Gullo and Monitor Responses

This script demonstrates:
1. Sending a message to Chris Gullo
2. Monitoring for responses via webhook
3. Checking message status and history
"""

import json
import time
import requests
from datetime import datetime, timedelta
from duxwrap.enhanced_duxwrap import EnhancedDuxWrap
from duxwrap.linkedin_messaging_manager import (
    LinkedInMessagingManager, LinkedInProfile, MessageType, DegreeLevel, ConnectionStatus
)

# Configuration - using real Dux-Soup credentials
USERID = "117833704731893145427"
APIKEY = "e96sH0Qehcqk8LWsyNjJpr9OL9qzasXR"

# Sergio Campos's profile URL
SERGIO_PROFILE_URL = "https://www.linkedin.com/in/sergio-campos-97b9b7362/"

def send_message_to_sergio():
    """Send a message to Sergio Campos and monitor for responses"""
    
    print("📨 Sending Message to Sergio Campos")
    print("=" * 50)
    
    # Initialize the enhanced Dux-Soup wrapper
    print("🔧 Initializing Dux-Soup wrapper...")
    from duxwrap.enhanced_duxwrap import DuxUser
    dux_user = DuxUser(userid=USERID, apikey=APIKEY)
    dux_wrapper = EnhancedDuxWrap(dux_user)
    
    # Initialize LinkedIn messaging manager
    messaging_manager = LinkedInMessagingManager(dux_wrapper)
    
    # Create Sergio Campos's profile in the messaging manager
    print(f"\n👤 Setting up Sergio Campos's profile...")
    sergio_profile = LinkedInProfile(
        profile_url=SERGIO_PROFILE_URL,
        first_name="Sergio",
        last_name="Campos",
        company="LinkedIn",
        title="Software Engineer",
        degree_level=DegreeLevel.FIRST,  # Assuming 1st degree connection
        connection_status=ConnectionStatus.CONNECTED,  # Assuming connected
        can_send_email=False,  # 1st degree can't use email
        can_send_inmail=False,  # 1st degree can't use InMail
        can_send_connection=False  # 1st degree can't send connection requests
    )
    
    messaging_manager.add_profile(sergio_profile)
    print(f"   ✅ Added Sergio Campos to messaging manager")
    print(f"      - Degree: {sergio_profile.degree_level.value}°")
    print(f"      - Status: {sergio_profile.connection_status.value}")
    print(f"      - Can send direct message: ✅")
    
    # Check if we can send a message to Sergio
    print(f"\n🔍 Checking messaging capabilities...")
    can_send = messaging_manager.can_send_message(SERGIO_PROFILE_URL, MessageType.FOLLOW_UP)
    
    if can_send["can_send"]:
        print(f"   ✅ Can send follow-up message to Sergio")
        print(f"      - Reason: {can_send['reason']}")
    else:
        print(f"   ❌ Cannot send message to Sergio")
        print(f"      - Reason: {can_send['reason']}")
        print(f"      - Restrictions: {', '.join(can_send['restrictions'])}")
        return
    
    # Prepare the message
    message_data = {
        "message": "Hey Sergio nice to meet you did you go to Aragon?"
    }
    
    # Send the message
    print(f"\n📤 Sending message to Sergio...")
    send_result = messaging_manager.send_message(
        profile_url=SERGIO_PROFILE_URL,
        message_type=MessageType.FOLLOW_UP,
        message_data=message_data,
        sequence_id="manual_sergio_message"
    )
    
    if send_result["success"]:
        print(f"   ✅ Message sent successfully!")
        print(f"      - Message ID: {send_result.get('message_id', 'N/A')}")
        print(f"      - Sent at: {send_result['sent_at']}")
        print(f"      - Message type: {send_result['message_type']}")
        
        # Store the message details for later reference
        message_details = {
            "profile_url": SERGIO_PROFILE_URL,
            "message_id": send_result.get('message_id'),
            "sent_at": send_result['sent_at'],
            "message_type": send_result['message_type'],
            "message_content": message_data["message"],
            "linkedin_response": send_result.get('linkedin_response', {})
        }
        
        # Save message details to file
        with open('sergio_message_details.json', 'w') as f:
            json.dump(message_details, f, indent=2)
        print(f"   💾 Message details saved to sergio_message_details.json")
        
    else:
        print(f"   ❌ Failed to send message")
        print(f"      - Full response: {send_result}")
        return
    
    # Monitor for responses
    print(f"\n👂 Monitoring for responses...")
    print(f"   📡 Webhook URL: http://localhost:5000/webhook")
    print(f"   📊 Check stats: http://localhost:5000/stats")
    print(f"   ⏰ Monitoring for the next 60 seconds...")
    
    # Check webhook server stats to see if there are any recent events
    try:
        stats_response = requests.get("http://localhost:5000/stats", timeout=5)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"\n📊 Current webhook server stats:")
            print(f"   - Total webhooks received: {stats.get('total_webhooks', 0)}")
            print(f"   - Last webhook: {stats.get('last_webhook', 'None')}")
            print(f"   - Server uptime: {stats.get('uptime', 'Unknown')}")
    except Exception as e:
        print(f"   ⚠️ Could not fetch webhook stats: {e}")
    
    # Wait and check for responses
    start_time = datetime.now()
    check_interval = 10  # Check every 10 seconds
    
    while (datetime.now() - start_time).total_seconds() < 60:
        time.sleep(check_interval)
        
        # Check webhook server for new events
        try:
            stats_response = requests.get("http://localhost:5000/stats", timeout=5)
            if stats_response.status_code == 200:
                stats = stats_response.json()
                recent_webhooks = stats.get('recent_webhooks', [])
                
                # Look for messages from Sergio
                sergio_messages = [
                    webhook for webhook in recent_webhooks
                    if webhook.get('profile') == SERGIO_PROFILE_URL and 
                    webhook.get('event_type') == 'message'
                ]
                
                if sergio_messages:
                    print(f"\n📨 Found {len(sergio_messages)} message(s) from Sergio!")
                    for msg in sergio_messages:
                        print(f"   📝 Message received at: {msg.get('timestamp')}")
                        print(f"   📄 Content: {msg.get('message', 'No content')[:100]}...")
                        
                        # Save the response
                        response_details = {
                            "profile_url": SERGIO_PROFILE_URL,
                            "received_at": msg.get('timestamp'),
                            "message_content": msg.get('message', ''),
                            "webhook_data": msg
                        }
                        
                        with open('sergio_response.json', 'w') as f:
                            json.dump(response_details, f, indent=2)
                        print(f"   💾 Response saved to sergio_response.json")
                        
                        return  # Found a response, exit monitoring
                
                print(f"   ⏳ No new messages from Sergio yet... ({int((datetime.now() - start_time).total_seconds())}s elapsed)")
                
        except Exception as e:
            print(f"   ⚠️ Error checking webhook stats: {e}")
    
    print(f"\n⏰ Monitoring period ended. No responses received from Chris.")
    print(f"   💡 You can continue monitoring by checking the webhook server manually:")
    print(f"      - Stats: http://localhost:5000/stats")
    print(f"      - Health: http://localhost:5000/health")
    
    # Show message status from messaging manager
    print(f"\n📋 Message Status Summary:")
    message_statuses = [
        status for status in messaging_manager.message_statuses
        if status.profile_url == CHRIS_PROFILE_URL
    ]
    
    if message_statuses:
        for status in message_statuses:
            print(f"   - {status.message_type.value}: {status.status}")
            if status.sent_at:
                print(f"     Sent at: {status.sent_at}")
            if status.error_message:
                print(f"     Error: {status.error_message}")
    else:
        print(f"   - No message statuses found for Chris")
    
    # Generate messaging report
    print(f"\n📊 Messaging Report:")
    report = messaging_manager.get_messaging_report()
    print(f"   - Total profiles: {report['total_profiles']}")
    print(f"   - Total messages sent: {report['messaging_stats']['total_messages_sent']}")
    print(f"   - Message type breakdown: {report['messaging_stats']['message_type_breakdown']}")

def check_existing_messages():
    """Check if there are any existing messages with Sergio"""
    
    print(f"\n🔍 Checking for existing messages with Sergio...")
    
    # Check if we have any saved message details
    try:
        with open('sergio_message_details.json', 'r') as f:
            message_details = json.load(f)
            print(f"   📄 Found previous message sent to Sergio:")
            print(f"      - Sent at: {message_details['sent_at']}")
            print(f"      - Message ID: {message_details.get('message_id', 'N/A')}")
            print(f"      - Message type: {message_details['message_type']}")
            print(f"      - Content preview: {message_details['message_content'][:100]}...")
    except FileNotFoundError:
        print(f"   📄 No previous message details found")
    
    # Check if we have any responses
    try:
        with open('sergio_response.json', 'r') as f:
            response_details = json.load(f)
            print(f"   📨 Found response from Sergio:")
            print(f"      - Received at: {response_details['received_at']}")
            print(f"      - Content: {response_details['message_content']}")
    except FileNotFoundError:
        print(f"   📨 No responses from Sergio found")
    
    # Check webhook server for any recent activity
    try:
        stats_response = requests.get("http://localhost:5000/stats", timeout=5)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            recent_webhooks = stats.get('recent_webhooks', [])
            
            chris_webhooks = [
                webhook for webhook in recent_webhooks
                if webhook.get('profile') == CHRIS_PROFILE_URL
            ]
            
            if chris_webhooks:
                print(f"   📡 Found {len(chris_webhooks)} webhook events for Chris:")
                for webhook in chris_webhooks:
                    print(f"      - {webhook.get('event_type')} at {webhook.get('timestamp')}")
                    if webhook.get('message'):
                        print(f"        Message: {webhook['message'][:100]}...")
            else:
                print(f"   📡 No webhook events found for Chris")
    except Exception as e:
        print(f"   ⚠️ Could not check webhook server: {e}")

def main():
    """Main function"""
    
    print("🚀 Sergio Campos Messaging Test")
    print("=" * 50)
    
    # First check for existing messages
    check_existing_messages()
    
    # Ask user if they want to send a new message
    print(f"\n❓ Do you want to send a new message to Sergio? (y/n): ", end="")
    try:
        user_input = input().strip().lower()
        if user_input in ['y', 'yes']:
            send_message_to_sergio()
        else:
            print(f"   👋 No new message sent. Exiting...")
    except KeyboardInterrupt:
        print(f"\n   👋 Interrupted by user. Exiting...")
    
    print(f"\n" + "=" * 50)
    print(f"✅ Sergio Campos Messaging Test Complete")
    print(f"=" * 50)

if __name__ == "__main__":
    main() 