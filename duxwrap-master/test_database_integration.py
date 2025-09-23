"""
Test Database Integration with Real Webhook Data

This script tests the Azure database integration using
real webhook data collected from Dux-Soup.
"""

import json
import os
from datetime import datetime
from azure_database import AzureDatabaseManager, WebhookEvent, EventStatus

def load_webhook_data():
    """Load real webhook data from the collector"""
    webhook_dir = "webhook_data/raw"
    events = []
    
    if not os.path.exists(webhook_dir):
        print(f"❌ Webhook data directory not found: {webhook_dir}")
        return events
    
    for filename in os.listdir(webhook_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(webhook_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    webhook_data = json.load(f)
                    events.append(webhook_data)
                print(f"✅ Loaded: {filename}")
            except Exception as e:
                print(f"❌ Error loading {filename}: {e}")
    
    return events

def test_database_integration():
    """Test the database integration with real data"""
    print("🧪 Testing Database Integration")
    print("=" * 50)
    
    # Initialize database manager
    db_manager = AzureDatabaseManager()
    
    # Load real webhook data
    webhook_events = load_webhook_data()
    
    if not webhook_events:
        print("❌ No webhook data found to test")
        return
    
    print(f"📊 Found {len(webhook_events)} webhook events to test")
    print()
    
    # Test storing each event
    success_count = 0
    for i, webhook_data in enumerate(webhook_events, 1):
        print(f"📥 Testing event {i}/{len(webhook_events)}: {webhook_data.get('type', 'unknown')}.{webhook_data.get('event', 'unknown')}")
        
        # Add event_id if not present
        if 'event_id' not in webhook_data:
            webhook_data['event_id'] = f"test_event_{i}"
        
        # Test storing the event
        success = db_manager.store_webhook_event(webhook_data)
        
        if success:
            success_count += 1
            print(f"   ✅ Stored successfully")
        else:
            print(f"   ❌ Failed to store")
        
        print()
    
    # Test statistics
    print("📈 Testing Statistics")
    print("-" * 30)
    stats = db_manager.get_event_statistics()
    print(f"Total events: {stats.get('total_events', 0)}")
    print(f"Event types: {stats.get('event_types', {})}")
    
    # Test recent events
    print("\n🕒 Testing Recent Events")
    print("-" * 30)
    recent_events = db_manager.get_recent_events(hours=24)
    print(f"Recent events (24h): {len(recent_events)}")
    
    # Test events by type
    print("\n📋 Testing Events by Type")
    print("-" * 30)
    for event_type in ['message', 'action', 'connect', 'visit', 'rccommand']:
        events = db_manager.get_events_by_type(event_type, limit=5)
        print(f"{event_type}: {len(events)} events")
    
    print("\n" + "=" * 50)
    print(f"✅ Database integration test completed!")
    print(f"📊 Successfully processed: {success_count}/{len(webhook_events)} events")

def analyze_webhook_structure():
    """Analyze the structure of collected webhook data"""
    print("🔍 Analyzing Webhook Data Structure")
    print("=" * 50)
    
    webhook_events = load_webhook_data()
    
    if not webhook_events:
        print("❌ No webhook data found to analyze")
        return
    
    # Analyze event types
    event_types = {}
    event_names = {}
    profiles = set()
    data_fields = set()
    
    for event in webhook_events:
        event_type = event.get('type', 'unknown')
        event_name = event.get('event', 'unknown')
        profile = event.get('profile')
        data = event.get('data', {})
        
        # Count event types
        event_types[event_type] = event_types.get(event_type, 0) + 1
        event_names[f"{event_type}.{event_name}"] = event_names.get(f"{event_type}.{event_name}", 0) + 1
        
        # Collect profiles
        if profile:
            profiles.add(profile)
        
        # Collect data fields
        for field in data.keys():
            data_fields.add(field)
    
    print(f"📊 Event Type Distribution:")
    for event_type, count in event_types.items():
        print(f"   {event_type}: {count}")
    
    print(f"\n📊 Event Name Distribution:")
    for event_name, count in event_names.items():
        print(f"   {event_name}: {count}")
    
    print(f"\n👥 Unique Profiles: {len(profiles)}")
    for profile in sorted(profiles):
        print(f"   {profile}")
    
    print(f"\n📝 Data Fields Found:")
    for field in sorted(data_fields):
        print(f"   {field}")
    
    # Show sample data structure
    print(f"\n📄 Sample Event Structure:")
    sample_event = webhook_events[0]
    print(json.dumps(sample_event, indent=2))

if __name__ == "__main__":
    print("🚀 Dux-Soup Database Integration Test")
    print("=" * 50)
    
    # First analyze the data structure
    analyze_webhook_structure()
    
    print("\n" + "=" * 50)
    
    # Then test the database integration
    test_database_integration() 