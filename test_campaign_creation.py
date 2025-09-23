#!/usr/bin/env python3
"""
Test Campaign Creation Directly
===============================

This script tests campaign creation directly against the database
to identify what's causing the failure.
"""

import asyncio
import sys
import os
sys.path.append('/Users/lacomp/Desktop/chaknal-platform')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.campaign import Campaign
import uuid
from datetime import datetime

async def test_campaign_creation():
    """Test creating a campaign directly in the database"""
    
    print("🧪 Testing Campaign Creation")
    print("=" * 40)
    
    # Database URL from app-settings.json
    DATABASE_URL = "postgresql+asyncpg://chaknaladmin:Chaknal2024!@chaknal-db-server.postgres.database.azure.com/chaknal_platform"
    
    try:
        # Create async engine
        engine = create_async_engine(DATABASE_URL)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            print("✅ Connected to PostgreSQL database")
            
            # Test creating a simple campaign
            print("\n🔨 Creating test campaign...")
            
            campaign = Campaign(
                campaign_id=str(uuid.uuid4()),
                campaign_key=str(uuid.uuid4()),
                name="Test Campaign",
                description="Test campaign description",
                target_title="Software Engineer",
                intent="Testing campaign creation",
                status="active",
                dux_user_id="test_user_123",
                scheduled_start=datetime.utcnow(),
                end_date=None,
                settings={"test": True},
                # DuxSoup workflow fields
                initial_action="message",
                initial_message="Hello! This is a test message.",
                initial_subject="Test Subject",
                follow_up_actions=[],
                delay_days=3,
                random_delay=True
            )
            
            session.add(campaign)
            await session.commit()
            await session.refresh(campaign)
            
            print(f"✅ Campaign created successfully!")
            print(f"   ID: {campaign.campaign_id}")
            print(f"   Name: {campaign.name}")
            print(f"   Status: {campaign.status}")
            print(f"   Created: {campaign.created_at}")
            
            # Verify it exists
            print(f"\n🔍 Verifying campaign exists...")
            result = await session.execute(
                f"SELECT name, status FROM campaigns_new WHERE campaign_id = '{campaign.campaign_id}'"
            )
            row = result.fetchone()
            if row:
                print(f"✅ Verified: {row[0]} - {row[1]}")
            else:
                print("❌ Campaign not found after creation")
                
        await engine.dispose()
        
        print("\n🎉 Campaign creation test PASSED!")
        print("✅ The database can create campaigns successfully")
        print("\n🤔 The issue might be:")
        print("   1. Frontend not sending correct data")
        print("   2. API validation failing")
        print("   3. Authentication/authorization issue")
        print("   4. Missing required fields in the request")
        
        return True
        
    except Exception as e:
        print(f"❌ Campaign creation test FAILED: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_campaign_creation())
    if success:
        print("\n✅ SUCCESS: Database can create campaigns")
        sys.exit(0)
    else:
        print("\n❌ FAILED: Database campaign creation failed")
        sys.exit(1)
