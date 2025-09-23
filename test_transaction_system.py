#!/usr/bin/env python3
"""
Test script for the new transaction logging system.
"""

import asyncio
import sys
sys.path.append('.')
from database.database import get_session
from app.services.transaction_service import TransactionService
from app.utils.transaction_tracker import TransactionType

async def test_transaction_system():
    try:
        print('🧪 Testing transaction logging system...')
        
        # Get database session
        session_gen = get_session()
        session = await session_gen.__anext__()
        
        # Create transaction service
        transaction_service = TransactionService(session)
        
        # Test 1: Log a simple transaction
        print('\n1. Testing basic transaction logging...')
        transaction = await transaction_service.log_transaction(
            transaction_type=TransactionType.SYSTEM_STARTUP,
            user_id="test-user-123",
            entity_id="test-entity-456",
            entity_type="system",
            description="Testing transaction logging system",
            metadata={"test": True, "version": "1.0"},
            success=True
        )
        print(f'✅ Created transaction: {transaction.transaction_id}')
        
        # Test 2: Log LinkedIn activity
        print('\n2. Testing LinkedIn activity logging...')
        linkedin_transaction = await transaction_service.log_linkedin_activity(
            activity_type="profile_viewed",
            contact_id="test-contact-789",
            user_id="test-user-123",
            campaign_id="test-campaign-101",
            linkedin_profile_url="https://linkedin.com/in/test-profile",
            description="Viewed profile during campaign",
            metadata={"profile_views": 1, "campaign_step": 1},
            success=True
        )
        print(f'✅ Created LinkedIn transaction: {linkedin_transaction.transaction_id}')
        
        # Test 3: Log message activity
        print('\n3. Testing message activity logging...')
        message_transaction = await transaction_service.log_message_activity(
            message_id="test-message-202",
            activity_type="sent",
            user_id="test-user-123",
            contact_id="test-contact-789",
            campaign_id="test-campaign-101",
            message_content="Hello! This is a test message.",
            description="Sent initial message to contact",
            metadata={"message_type": "initial", "sequence_step": 1},
            success=True
        )
        print(f'✅ Created message transaction: {message_transaction.transaction_id}')
        
        # Test 4: Get transaction history
        print('\n4. Testing transaction history retrieval...')
        history = await transaction_service.get_transaction_history(limit=10)
        print(f'✅ Retrieved {len(history)} transactions from history')
        
        for tx in history:
            print(f'  - {tx.transaction_type}: {tx.description} ({tx.transaction_time})')
        
        # Test 5: Get activity stats
        print('\n5. Testing activity statistics...')
        stats = await transaction_service.get_activity_stats(hours=1)
        print(f'✅ Activity stats: {stats}')
        
        await session.close()
        print('\n🎉 Transaction system test completed successfully!')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_transaction_system())
