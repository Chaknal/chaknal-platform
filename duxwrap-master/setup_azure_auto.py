#!/usr/bin/env python3
"""
Automated Azure Database Setup for Chaknal
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Azure PostgreSQL Connection Details
AZURE_CONFIG = {
    'host': 'chaknal1.postgres.database.azure.com',
    'port': 5432,
    'database': 'outreach_db',
    'user': 'chakadmin',
    'password': '!1Nicoamir'
}

def test_connection():
    """Test database connection"""
    try:
        conn = psycopg2.connect(**AZURE_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        logger.info(f"✅ Connected to PostgreSQL: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        return False

def create_tables():
    """Create all database tables"""
    try:
        conn = psycopg2.connect(**AZURE_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create campaigns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id SERIAL PRIMARY KEY,
                campaign_id VARCHAR(255) UNIQUE NOT NULL,
                title VARCHAR(500) NOT NULL,
                description TEXT,
                status VARCHAR(50) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                dux_user_id VARCHAR(255),
                tags JSONB,
                settings JSONB
            );
        """)
        logger.info("✅ Created campaigns table")
        
        # Create contacts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id SERIAL PRIMARY KEY,
                contact_id VARCHAR(255) UNIQUE NOT NULL,
                linkedin_url VARCHAR(500) UNIQUE,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                headline VARCHAR(500),
                company VARCHAR(200),
                location VARCHAR(200),
                industry VARCHAR(200),
                profile_picture_url VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                dux_user_id VARCHAR(255),
                tags JSONB,
                notes TEXT
            );
        """)
        logger.info("✅ Created contacts table")
        
        # Create campaign_contacts junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS campaign_contacts (
                id SERIAL PRIMARY KEY,
                campaign_id INTEGER REFERENCES campaigns(id),
                contact_id INTEGER REFERENCES contacts(id),
                status VARCHAR(50) DEFAULT 'pending',
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_contacted TIMESTAMP,
                sequence_step INTEGER DEFAULT 1,
                tags JSONB,
                notes TEXT,
                UNIQUE(campaign_id, contact_id)
            );
        """)
        logger.info("✅ Created campaign_contacts table")
        
        # Create sequences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sequences (
                id SERIAL PRIMARY KEY,
                sequence_id VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                steps JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                dux_user_id VARCHAR(255),
                is_active BOOLEAN DEFAULT true
            );
        """)
        logger.info("✅ Created sequences table")
        
        # Create messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                message_id VARCHAR(255) UNIQUE NOT NULL,
                campaign_id INTEGER REFERENCES campaigns(id),
                contact_id INTEGER REFERENCES contacts(id),
                message_type VARCHAR(50) NOT NULL,
                direction VARCHAR(20) NOT NULL,
                content TEXT NOT NULL,
                sent_at TIMESTAMP,
                received_at TIMESTAMP,
                status VARCHAR(50) DEFAULT 'sent',
                thread_url VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                dux_user_id VARCHAR(255),
                metadata JSONB
            );
        """)
        logger.info("✅ Created messages table")
        
        # Create actions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS actions (
                id SERIAL PRIMARY KEY,
                action_id VARCHAR(255) UNIQUE NOT NULL,
                campaign_id INTEGER REFERENCES campaigns(id),
                contact_id INTEGER REFERENCES contacts(id),
                action_type VARCHAR(50) NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                executed_at TIMESTAMP,
                result JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                dux_user_id VARCHAR(255),
                metadata JSONB
            );
        """)
        logger.info("✅ Created actions table")
        
        # Create webhook_events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS webhook_events (
                id SERIAL PRIMARY KEY,
                event_id VARCHAR(255) UNIQUE NOT NULL,
                dux_user_id VARCHAR(255) NOT NULL,
                event_type VARCHAR(100) NOT NULL,
                event_name VARCHAR(100) NOT NULL,
                contact_id VARCHAR(255),
                campaign_id VARCHAR(255),
                raw_data JSONB NOT NULL,
                processed BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP
            );
        """)
        logger.info("✅ Created webhook_events table")
        
        # Create campaign_stats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS campaign_stats (
                id SERIAL PRIMARY KEY,
                campaign_id INTEGER REFERENCES campaigns(id),
                date DATE NOT NULL,
                total_contacts INTEGER DEFAULT 0,
                messages_sent INTEGER DEFAULT 0,
                messages_received INTEGER DEFAULT 0,
                connections_made INTEGER DEFAULT 0,
                responses_received INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(campaign_id, date)
            );
        """)
        logger.info("✅ Created campaign_stats table")
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_webhook_events_created_at ON webhook_events(created_at);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_webhook_events_event_type ON webhook_events(event_type);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_linkedin_url ON contacts(linkedin_url);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_contact_id ON messages(contact_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaign_contacts_status ON campaign_contacts(status);")
        
        logger.info("✅ Created database indexes")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 CHAKNAL - AZURE DATABASE SETUP")
    print("=" * 60)
    print()
    
    # Test connection
    print("🔧 Testing database connection...")
    if not test_connection():
        print("❌ Failed to connect to database. Please check your credentials.")
        sys.exit(1)
    
    # Create tables
    print("🔧 Creating database tables...")
    if not create_tables():
        print("❌ Failed to create tables.")
        sys.exit(1)
    
    print()
    print("✅ AZURE DATABASE SETUP COMPLETE!")
    print("=" * 60)
    print("📊 Database: outreach_db")
    print("🏠 Host: outreach-platform-pg.postgres.database.azure.com")
    print("👤 User: postgres")
    print("🔗 Connection string saved to .env file")
    print()
    print("🚀 Next steps:")
    print("1. Start the webhook data collector with Azure integration")
    print("2. Configure webhook URL")
    print("3. Begin collecting LinkedIn automation data")
    print("=" * 60)

if __name__ == "__main__":
    main() 