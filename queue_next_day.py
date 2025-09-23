#!/usr/bin/env python3
"""
Daily Campaign Queue Script
Run this script daily to queue the next set of messages in the sequence
"""

import sys
import os
from datetime import datetime

# Add the duxwrap directory to the Python path
duxwrap_path = os.path.join(os.path.dirname(os.getcwd()), 'duxwrap-master')
sys.path.insert(0, duxwrap_path)

try:
    from duxwrap.duxwrap import DuxWrap
except ImportError:
    print("❌ Error: Could not import DuxWrap. Make sure duxwrap-master is in the parent directory.")
    sys.exit(1)

def queue_day_messages(day_number):
    """Queue messages for a specific day"""
    
    # Initialize DuxWrap
    api_key = 'e96sH0Qehcqk8LWsyNjJpr9OL9qzasXR'
    user_id = '117833704731893145427'
    
    try:
        dux = DuxWrap(api_key, user_id)
        print(f'✅ Connected to DuxSoup for user: {user_id}')
    except Exception as e:
        print(f'❌ Failed to connect to DuxSoup: {e}')
        return
    
    contacts = [
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
    
    messages = [
        'Hi {name}! Thanks for connecting. I wanted to reach out because I noticed your experience in {industry} and thought we might have some interesting opportunities to discuss.',
        'Hi {name}! I hope you\\'re doing well. I wanted to follow up on my previous message about potential collaboration opportunities. Would you be interested in a brief call this week?',
        'Hi {name}! This is my final follow-up. If you\\'re interested in exploring potential partnerships, I\\'d love to chat. If not, no worries at all - I\\'ll respect your time and won\\'t reach out again.'
    ]
    
    day_names = ['Day 1 (Initial)', 'Day 2 (Follow-up)', 'Day 3 (Final)']
    
    if day_number < 1 or day_number > 3:
        print(f'❌ Invalid day number: {day_number}. Must be 1, 2, or 3.')
        return
    
    print(f'📅 Queuing {day_names[day_number-1]} messages...')
    print('-' * 50)
    
    message_index = day_number - 1
    queued_count = 0
    
    for contact in contacts:
        message_text = messages[message_index].format(name=contact['name'], industry=contact['industry'])
        
        try:
            result = dux.call('message', {
                'params': {
                    'profile': contact['url'],
                    'messagetext': message_text
                }
            })
            print(f'✅ {contact["name"]} - {day_names[day_number-1]} queued: {result["messageid"]}')
            queued_count += 1
        except Exception as e:
            print(f'❌ {contact["name"]} - {day_names[day_number-1]} failed: {e}')
    
    # Check final queue status
    queue_size = dux.call('size', {})
    print(f'\\n📊 Queue Status:')
    print(f'   Messages queued this session: {queued_count}')
    print(f'   Total queue size: {queue_size["result"]}')
    
    print(f'\\n🎯 Campaign Progress:')
    if day_number == 1:
        print('   ✅ Day 1: Initial messages sent')
        print('   🔄 Tomorrow: Run with --day 2 for follow-up messages')
    elif day_number == 2:
        print('   ✅ Day 1: Initial messages sent')
        print('   ✅ Day 2: Follow-up messages sent')
        print('   🔄 Tomorrow: Run with --day 3 for final messages')
    elif day_number == 3:
        print('   ✅ Day 1: Initial messages sent')
        print('   ✅ Day 2: Follow-up messages sent')
        print('   ✅ Day 3: Final messages sent')
        print('   🎉 Campaign sequence complete!')

def main():
    if len(sys.argv) < 2:
        print('📅 Daily Campaign Queue Script')
        print('=' * 40)
        print()
        print('Usage:')
        print('  python3 queue_next_day.py --day 1    # Queue initial messages')
        print('  python3 queue_next_day.py --day 2    # Queue follow-up messages')
        print('  python3 queue_next_day.py --day 3    # Queue final messages')
        print()
        print('Current day:', datetime.now().strftime('%A, %B %d, %Y'))
        return
    
    day_arg = sys.argv[1]
    if day_arg == '--day' and len(sys.argv) > 2:
        try:
            day_number = int(sys.argv[2])
            queue_day_messages(day_number)
        except ValueError:
            print('❌ Invalid day number. Must be 1, 2, or 3.')
    else:
        print('❌ Invalid arguments. Use --day 1, --day 2, or --day 3')

if __name__ == "__main__":
    main()
