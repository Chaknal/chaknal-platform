#!/usr/bin/env python3
"""
DuxSoup Campaign Monitor
Monitor the progress of your LinkedIn outreach campaign in real-time.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the duxwrap directory to the Python path
duxwrap_path = os.path.join(os.path.dirname(os.getcwd()), 'duxwrap-master')
sys.path.insert(0, duxwrap_path)

try:
    from duxwrap.duxwrap import DuxWrap
    
    # Configuration
    DUXSOUP_API_KEY = 'e96sH0Qehcqk8LWsyNjJpr9OL9qzasXR'
    DUXSOUP_USER_ID = '117833704731893145427'
    
    # Campaign contacts
    CAMPAIGN_CONTACTS = [
        {'name': 'Chris Gullo', 'url': 'https://www.linkedin.com/in/chgullo/'},
        {'name': 'Sergio Campos', 'url': 'https://www.linkedin.com/in/sergio-campos-97b9b7362/'},
        {'name': 'Ava Shoraka', 'url': 'https://www.linkedin.com/in/avashoraka/'}
    ]
    
    def get_contact_name_from_message(message_text, url):
        """Extract contact name from message content or URL"""
        for contact in CAMPAIGN_CONTACTS:
            if contact['name'] in message_text or contact['url'] == url:
                return contact['name']
        return 'Unknown'
    
    def get_message_step(message_text):
        """Determine which step of the sequence this message is"""
        if 'Thanks for connecting' in message_text:
            return 'Step 1 (Initial)'
        elif 'follow up' in message_text.lower():
            return 'Step 2 (Follow-up)'
        elif 'final follow-up' in message_text.lower():
            return 'Step 3 (Final)'
        else:
            return 'Unknown'
    
    def format_timestamp(timestamp_str):
        """Format timestamp for display"""
        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return timestamp_str
    
    async def monitor_campaign():
        print('👀 DuxSoup Campaign Monitor')
        print('=' * 50)
        print(f'🔍 Monitoring campaign for user: {DUXSOUP_USER_ID}')
        print(f'⏰ Started monitoring at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print()
        
        # Initialize DuxWrap
        dux = DuxWrap(DUXSOUP_API_KEY, DUXSOUP_USER_ID)
        
        # Get initial queue status
        queue_size = dux.call('size', {})
        queue_items = dux.call('items', {})
        
        print(f'📊 Queue Status:')
        print(f'   Total items: {queue_size["result"]}')
        print(f'   Items available: {len(queue_items)}')
        print()
        
        if len(queue_items) == 0:
            print('❌ No items in queue. Campaign may be complete or not started.')
            return
        
        # Analyze campaign messages
        campaign_messages = []
        wait_commands = []
        
        for item in queue_items:
            if item.get('command') == 'message':
                # Extract contact info
                profile_url = item.get('params', {}).get('profile', '')
                message_text = item.get('params', {}).get('messagetext', '')
                contact_name = get_contact_name_from_message(message_text, profile_url)
                step = get_message_step(message_text)
                
                campaign_messages.append({
                    'id': item['messageid'],
                    'contact': contact_name,
                    'step': step,
                    'url': profile_url,
                    'message': message_text,
                    'when': item['when']
                })
            elif item.get('command') == 'wait':
                wait_commands.append({
                    'id': item['messageid'],
                    'duration': item.get('params', {}).get('duration', 0),
                    'when': item['when']
                })
        
        print(f'📋 Campaign Analysis:')
        print('-' * 30)
        print(f'   Messages: {len(campaign_messages)}')
        print(f'   Wait commands: {len(wait_commands)}')
        print()
        
        # Group messages by contact
        contacts_status = {}
        for msg in campaign_messages:
            contact = msg['contact']
            if contact not in contacts_status:
                contacts_status[contact] = []
            contacts_status[contact].append(msg)
        
        print(f'👥 Contact Sequences:')
        print('-' * 30)
        for contact, messages in contacts_status.items():
            print(f'\\n{contact}:')
            for msg in sorted(messages, key=lambda x: x['when']):
                print(f'   📨 {msg["step"]}')
                print(f'      🆔 {msg["id"]}')
                print(f'      ⏰ {format_timestamp(msg["when"])}')
                print(f'      💬 {msg["message"][:50]}...')
        
        # Show wait commands
        if wait_commands:
            print(f'\\n⏰ Wait Commands:')
            print('-' * 20)
            for wait in wait_commands:
                hours = wait['duration'] / 3600
                print(f'   🕐 {hours} hours - {format_timestamp(wait["when"])}')
        
        # Calculate timeline
        print(f'\\n📅 Expected Timeline:')
        print('-' * 25)
        print('Today: Initial messages (Step 1)')
        print('Tomorrow: Follow-up messages (Step 2)')
        print('Wednesday: Final messages (Step 3)')
        
        print(f'\\n🎯 Campaign Status:')
        print('-' * 20)
        if len(campaign_messages) == 9:  # 3 contacts × 3 messages
            print('✅ Complete 3-message sequence queued for all contacts')
        else:
            print(f'⚠️ Expected 9 messages, found {len(campaign_messages)}')
        
        print('✅ DuxSoup will process messages automatically')
        print('✅ Natural delays prevent LinkedIn detection')
        print('✅ Check DuxSoup dashboard for real-time progress')
        
        print(f'\\n📱 Next Steps:')
        print('-' * 15)
        print('1. Check your DuxSoup dashboard')
        print('2. Monitor message send status')
        print('3. Track responses and engagement')
        print('4. Campaign will run automatically over 3 days')
    
    if __name__ == "__main__":
        asyncio.run(monitor_campaign())
        
except ImportError as e:
    print(f'❌ Import Error: {e}')
    print('Make sure the duxwrap-master directory is in the parent directory')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()