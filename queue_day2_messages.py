#!/usr/bin/env python3
"""
Day 2 Follow-up Messages Script
Run this script tomorrow to queue the follow-up messages for all contacts.
"""

import asyncio
import sys
import os

# Add the duxwrap directory to the Python path
duxwrap_path = os.path.join(os.path.dirname(os.getcwd()), 'duxwrap-master')
sys.path.insert(0, duxwrap_path)

try:
    from duxwrap.duxwrap import DuxWrap
    
    # Configuration
    DUXSOUP_API_KEY = 'e96sH0Qehcqk8LWsyNjJpr9OL9qzasXR'
    DUXSOUP_USER_ID = '117833704731893145427'
    
    # Contacts
    CONTACTS = [
        {
            'name': 'Chris Gullo',
            'url': 'https://www.linkedin.com/in/chgullo/',
            'industry': 'technology'
        },
        {
            'name': 'Sergio Campos', 
            'url': 'https://www.linkedin.com/in/sergio-campos-97b9b7362/',
            'industry': 'business development'
        },
        {
            'name': 'Ava Shoraka',
            'url': 'https://www.linkedin.com/in/avashoraka/',
            'industry': 'marketing'
        }
    ]
    
    # Day 2 message
    MESSAGE_TEMPLATE = "Hi {name}! I hope you're doing well. I wanted to follow up on my previous message about potential collaboration opportunities. Would you be interested in a brief call this week?"
    
    async def queue_day2_messages():
        print('📅 Day 2: Queueing Follow-up Messages')
        print('=' * 50)
        
        # Initialize DuxWrap
        dux = DuxWrap(DUXSOUP_API_KEY, DUXSOUP_USER_ID)
        
        # Queue follow-up messages with staggered delays
        for i, contact in enumerate(CONTACTS):
            message_text = MESSAGE_TEMPLATE.format(
                name=contact['name'], 
                industry=contact['industry']
            )
            
            try:
                # Add a delay before each message (staggered by 30 minutes)
                delay_minutes = i * 30  # 0, 30, 60 minutes
                
                if delay_minutes > 0:
                    # Queue a wait command first
                    wait_result = dux.call('wait', {
                        'params': {
                            'duration': delay_minutes * 60  # Convert to seconds
                        }
                    })
                    print(f'   ⏰ Wait {delay_minutes} minutes queued for {contact["name"]}')
                
                # Then queue the message
                result = dux.call('message', {
                    'params': {
                        'profile': contact['url'],
                        'messagetext': message_text
                    }
                })
                
                print(f'   ✅ {contact["name"]} - Follow-up message queued: {result["messageid"]}')
                if delay_minutes > 0:
                    print(f'      📅 Will be sent after {delay_minutes} minute delay')
                
            except Exception as e:
                print(f'   ❌ {contact["name"]} - Failed: {e}')
        
        # Check queue status
        queue_size = dux.call('size', {})
        print(f'\\n📊 Queue Status:')
        print(f'   Total messages: {queue_size["result"]}')
        
        print(f'\\n✅ Day 2 complete! Follow-up messages queued.')
        print(f'📱 Tomorrow run: python3 queue_day3_messages.py')
    
    if __name__ == "__main__":
        asyncio.run(queue_day2_messages())
        
except ImportError as e:
    print(f'❌ Import Error: {e}')
    print('Make sure the duxwrap-master directory is in the parent directory')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
