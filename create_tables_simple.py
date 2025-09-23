#!/usr/bin/env python3
"""
Script to create database tables without foreign key constraints
"""
import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Set the database URL
DATABASE_URL = 'postgresql+asyncpg://chaknaladmin:Chaknal2024!@chaknal-db-server.postgres.database.azure.com/chaknal_platform'

async def create_tables_simple():
    """Create all database tables without foreign key constraints"""
    try:
        print(f"Connecting to database: {DATABASE_URL}")
        
        # Create engine
        engine = create_async_engine(DATABASE_URL, echo=True)
        
        # Create tables one by one without foreign keys
        tables_sql = [
            """
            CREATE TABLE IF NOT EXISTS organization (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR UNIQUE NOT NULL,
                created_at TIMESTAMP WITHOUT TIME ZONE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS company (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR,
                domain VARCHAR UNIQUE NOT NULL,
                logo_url VARCHAR,
                created_at TIMESTAMP WITHOUT TIME ZONE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS campaigns_new (
                campaign_id VARCHAR(36) PRIMARY KEY,
                campaign_key VARCHAR(36) NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                target_title VARCHAR(255),
                intent TEXT NOT NULL,
                status VARCHAR(50),
                dux_user_id VARCHAR(100) NOT NULL DEFAULT 'default_user',
                scheduled_start TIMESTAMP WITH TIME ZONE,
                end_date TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE,
                updated_at TIMESTAMP WITH TIME ZONE,
                settings JSON,
                dux_campaign_id VARCHAR(100),
                force_override BOOLEAN,
                run_after TIMESTAMP WITH TIME ZONE,
                daily_limits JSON,
                automation_settings JSON,
                initial_action VARCHAR(50),
                initial_message TEXT,
                initial_subject VARCHAR(255),
                follow_up_actions JSON,
                delay_days INTEGER,
                random_delay BOOLEAN,
                follow_up_action_1 VARCHAR(50),
                follow_up_message_1 TEXT,
                follow_up_subject_1 VARCHAR(255),
                follow_up_delay_1 INTEGER,
                follow_up_action_2 VARCHAR(50),
                follow_up_message_2 TEXT,
                follow_up_subject_2 VARCHAR(255),
                follow_up_delay_2 INTEGER,
                follow_up_action_3 VARCHAR(50),
                follow_up_message_3 TEXT,
                follow_up_subject_3 VARCHAR(255),
                follow_up_delay_3 INTEGER
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS "user" (
                id VARCHAR(36) PRIMARY KEY,
                email VARCHAR UNIQUE NOT NULL,
                hashed_password VARCHAR(1024) NOT NULL,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                phone VARCHAR(20),
                bio VARCHAR(500),
                linkedin_url VARCHAR(500),
                timezone VARCHAR(50),
                role VARCHAR(20),
                is_active VARCHAR,
                is_superuser VARCHAR,
                is_verified VARCHAR,
                is_agency BOOLEAN,
                agency_company_id VARCHAR(36),
                organization_id VARCHAR(36),
                company_id VARCHAR(36),
                created_at TIMESTAMP WITHOUT TIME ZONE,
                updated_at TIMESTAMP WITHOUT TIME ZONE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS contacts (
                contact_id VARCHAR(36) PRIMARY KEY,
                email VARCHAR,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                company VARCHAR(255),
                title VARCHAR(255),
                linkedin_url VARCHAR(500),
                phone VARCHAR(20),
                location VARCHAR(255),
                notes TEXT,
                tags JSON,
                created_at TIMESTAMP WITHOUT TIME ZONE,
                updated_at TIMESTAMP WITHOUT TIME ZONE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS webhook_events (
                event_id VARCHAR(36) PRIMARY KEY,
                dux_user_id VARCHAR(100) NOT NULL,
                event_type VARCHAR(50) NOT NULL,
                event_name VARCHAR(50) NOT NULL,
                contact_id VARCHAR(36),
                campaign_id VARCHAR(36),
                raw_data JSON NOT NULL,
                processed BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE
            )
            """
        ]
        
        async with engine.begin() as conn:
            for sql in tables_sql:
                print(f"Executing: {sql[:50]}...")
                await conn.execute(text(sql))
        
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
    success = asyncio.run(create_tables_simple())
    sys.exit(0 if success else 1)
