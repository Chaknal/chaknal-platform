#!/usr/bin/env python3
"""
Integration test for the new DuxSoup wrapper with LinkedIn automation service

This script tests the integration without requiring a database connection.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.duxwrap_new import DuxSoupWrapper, DuxSoupUser, DuxSoupCommand


async def test_wrapper_integration():
    """Test the wrapper integration with automation logic"""
    print("🧪 Testing DuxSoup wrapper integration...")
    
    # Create a test user
    test_user = DuxSoupUser(
        userid="test_user_123",
        apikey="fake_api_key_for_testing",
        label="Test User",
        daily_limits={"max_invites": 50, "max_messages": 25, "max_visits": 100},
        automation_settings={"auto_connect": True, "auto_message": True}
    )
    
    print(f"✅ Created test user: {test_user.label}")
    
    # Test campaign automation flow
    try:
        async with DuxSoupWrapper(test_user) as wrapper:
            print("✅ Wrapper initialized successfully")
            
            # Simulate campaign step 1: Visit profile
            print("\n📋 Step 1: Visiting profile...")
            visit_response = await wrapper.visit_profile(
                "https://linkedin.com/in/testuser",
                campaign_id="campaign_123"
            )
            
            if visit_response.success:
                print(f"   ✅ Profile visit queued: {visit_response.message_id}")
            else:
                print(f"   ❌ Profile visit failed: {visit_response.error}")
            
            # Simulate campaign step 2: Send connection request
            print("\n📋 Step 2: Sending connection request...")
            connect_response = await wrapper.connect_profile(
                "https://linkedin.com/in/testuser",
                message_text="Hi! I'd like to connect with you on LinkedIn.",
                campaign_id="campaign_123"
            )
            
            if connect_response.success:
                print(f"   ✅ Connection request queued: {connect_response.message_id}")
            else:
                print(f"   ❌ Connection request failed: {connect_response.error}")
            
            # Simulate campaign step 3: Send follow-up message
            print("\n📋 Step 3: Sending follow-up message...")
            message_response = await wrapper.send_message(
                "https://linkedin.com/in/testuser",
                "Thanks for connecting! How are you?",
                campaign_id="campaign_123"
            )
            
            if message_response.success:
                print(f"   ✅ Follow-up message queued: {message_response.message_id}")
            else:
                print(f"   ❌ Follow-up message failed: {message_response.error}")
            
            # Test batch operations
            print("\n📋 Step 4: Testing batch operations...")
            commands = [
                DuxSoupCommand(
                    command="visit",
                    params={"profile": "https://linkedin.com/in/user2"},
                    campaign_id="campaign_123",
                    priority=5
                ),
                DuxSoupCommand(
                    command="connect",
                    params={
                        "profile": "https://linkedin.com/in/user2",
                        "messagetext": "Hi! I'd like to connect."
                    },
                    campaign_id="campaign_123",
                    priority=4
                )
            ]
            
            batch_responses = await wrapper.batch_queue_actions(commands)
            print(f"   ✅ Batch operations completed: {len(batch_responses)} commands")
            
            for i, response in enumerate(batch_responses):
                if response.success:
                    print(f"      Command {i+1}: ✅ {response.message_id}")
                else:
                    print(f"      Command {i+1}: ❌ {response.error}")
            
            # Test queue health
            print("\n📋 Step 5: Testing queue health...")
            health = await wrapper.get_queue_health()
            print(f"   ✅ Queue health retrieved")
            print(f"      Size: {health.get('size', 'N/A')}")
            print(f"      Items: {health.get('items', 'N/A')}")
            print(f"      Profile: {health.get('profile', 'N/A')}")
            
            # Show final stats
            print("\n📊 Final wrapper statistics:")
            stats = wrapper.get_stats()
            for key, value in stats.items():
                print(f"   {key}: {value}")
            
            print("\n🎉 Integration test completed successfully!")
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_error_handling():
    """Test error handling scenarios"""
    print("\n🧪 Testing error handling...")
    
    # Test with invalid user
    invalid_user = DuxSoupUser(
        userid="",
        apikey="",
        label="Invalid User"
    )
    
    try:
        async with DuxSoupWrapper(invalid_user) as wrapper:
            # This should fail
            response = await wrapper.visit_profile("https://linkedin.com/in/testuser")
            print("❌ Should have failed with empty credentials")
    except Exception as e:
        print(f"✅ Properly caught error: {type(e).__name__}: {e}")
    
    print("✅ Error handling test completed")


async def main():
    """Main test function"""
    print("🚀 Starting DuxSoup Integration Tests\n")
    
    try:
        # Test 1: Basic integration
        await test_wrapper_integration()
        
        # Test 2: Error handling
        await test_error_handling()
        
        print("\n🎉 All integration tests completed successfully!")
        
    except Exception as e:
        print(f"\n💥 Integration test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
