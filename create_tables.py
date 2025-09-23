#!/usr/bin/env python3
"""
Script to manually create database tables for Chaknal Platform
"""
import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from database.base import Base

# Set the database URL from environment or use the Azure one
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://chaknaladmin:Chaknal2024!@chaknal-db-server.postgres.database.azure.com/chaknal_platform')

async def create_tables():
    """Create all database tables"""
    try:
        print(f"Connecting to database: {DATABASE_URL}")
        
        # Create engine
        engine = create_async_engine(DATABASE_URL, echo=True)
        
        # Import all models to ensure they're registered
        print("Importing models...")
        from app.models.user import User, Organization
        from app.models.company import Company
        from app.models.campaign import Campaign
        from app.models.contact import Contact
        from app.models.campaign_contact import CampaignContact
        from app.models.message import Message
        from app.models.webhook_event import WebhookEvent
        from app.models.duxsoup_user import DuxSoupUser
        from app.models.duxsoup_user_settings import DuxSoupUserSettings
        from app.models.agency import AgencyClient, AgencyInvitation, AgencyActivityLog
        from app.models.meeting import Meeting
        
        # Create all tables
        print("Creating tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database tables created successfully!")
        
        # Close engine
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(create_tables())
    sys.exit(0 if success else 1)
