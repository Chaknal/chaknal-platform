#!/usr/bin/env python3
"""
Script to run database migrations for Chaknal Platform
"""
import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from database.base import Base
from config.settings import settings

async def create_tables():
    """Create all database tables"""
    try:
        print(f"Connecting to database: {settings.DATABASE_URL}")
        
        # Create engine
        engine = create_async_engine(settings.DATABASE_URL, echo=True)
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database tables created successfully!")
        
        # Close engine
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(create_tables())
    sys.exit(0 if success else 1)
