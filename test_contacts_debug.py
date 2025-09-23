#!/usr/bin/env python3
"""
Debug script to test contacts API and identify timezone issues
"""

import asyncio
import sys
sys.path.append('.')
from database.database import engine
from sqlalchemy import text
from datetime import datetime, timezone

async def debug_contacts():
    try:
        async with engine.begin() as conn:
            print('🔍 Debugging contacts table...')
            
            # Check contact data types and values
            result = await conn.execute(text('''
                SELECT 
                    contact_id, 
                    first_name, 
                    last_name, 
                    created_at, 
                    updated_at,
                    pg_typeof(created_at) as created_at_type,
                    pg_typeof(updated_at) as updated_at_type
                FROM contacts 
                LIMIT 3;
            '''))
            
            contacts = result.fetchall()
            print(f'Found {len(contacts)} contacts')
            
            for contact in contacts:
                print(f'Contact: {contact[0]}')
                print(f'  Name: {contact[1]} {contact[2]}')
                print(f'  Created: {contact[3]} (type: {contact[4]})')
                print(f'  Updated: {contact[5]} (type: {contact[6]})')
                print()
            
            # Check campaign_contacts data
            result = await conn.execute(text('''
                SELECT 
                    campaign_contact_id,
                    contact_id,
                    campaign_id,
                    created_at,
                    updated_at,
                    pg_typeof(created_at) as created_at_type,
                    pg_typeof(updated_at) as updated_at_type
                FROM campaign_contacts 
                LIMIT 3;
            '''))
            
            campaign_contacts = result.fetchall()
            print(f'Found {len(campaign_contacts)} campaign contacts')
            
            for cc in campaign_contacts:
                print(f'Campaign Contact: {cc[0]}')
                print(f'  Contact ID: {cc[1]}')
                print(f'  Campaign ID: {cc[2]}')
                print(f'  Created: {cc[3]} (type: {cc[4]})')
                print(f'  Updated: {cc[5]} (type: {cc[6]})')
                print()
                
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    asyncio.run(debug_contacts())
