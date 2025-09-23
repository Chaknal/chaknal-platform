#!/usr/bin/env python3
"""
Minimal test to isolate the contacts API timezone issue
"""

import asyncio
import sys
sys.path.append('.')
from database.database import get_session
from app.models.contact import Contact
from sqlalchemy import select

async def test_minimal_contacts():
    try:
        session_gen = get_session()
        session = await session_gen.__anext__()
        print('🔍 Testing minimal contacts query...')
        
        # Test 1: Simple contact query without relationships
        query = select(Contact).limit(1)
        result = await session.execute(query)
        contact = result.scalar_one_or_none()
        
        if contact:
            print(f'✅ Found contact: {contact.contact_id}')
            print(f'  Name: {contact.first_name} {contact.last_name}')
            print(f'  Created: {contact.created_at} (tzinfo: {contact.created_at.tzinfo if contact.created_at else None})')
            print(f'  Updated: {contact.updated_at} (tzinfo: {contact.updated_at.tzinfo if contact.updated_at else None})')
        else:
            print('❌ No contacts found')
        
        # Test 2: Query with relationships
        print('\n🔍 Testing with relationships...')
        from sqlalchemy.orm import selectinload
        query = select(Contact).options(selectinload(Contact.campaign_contacts)).limit(1)
        result = await session.execute(query)
        contact_with_rels = result.scalar_one_or_none()
        
        if contact_with_rels:
            print(f'✅ Found contact with relationships: {contact_with_rels.contact_id}')
            print(f'  Campaign contacts: {len(contact_with_rels.campaign_contacts)}')
            for cc in contact_with_rels.campaign_contacts:
                print(f'    CC: {cc.campaign_contact_id} - {cc.created_at} (tzinfo: {cc.created_at.tzinfo if cc.created_at else None})')
        else:
            print('❌ No contacts with relationships found')
            
        await session.close()
            
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_minimal_contacts())
