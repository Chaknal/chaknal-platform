"""
Azure Database Integration for Dux-Soup Webhook Data

This module provides database models and management for storing
Dux-Soup webhook events in Azure PostgreSQL Database.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2.pool import SimpleConnectionPool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventType(Enum):
    """Dux-Soup event types"""
    MESSAGE = "message"
    ACTION = "action"
    CONNECT = "connect"
    VISIT = "visit"
    RCCOMMAND = "rccommand"

class EventStatus(Enum):
    """Event processing status"""
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"

@dataclass
class Contact:
    """LinkedIn contact data model"""
    contact_id: str
    linkedin_id: str
    linkedin_url: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    headline: Optional[str] = None
    company: Optional[str] = None
    company_url: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None
    connection_degree: Optional[int] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    profile_data: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Campaign:
    """Campaign data model"""
    campaign_id: str
    name: str
    dux_user_id: str
    description: Optional[str] = None
    target_title: Optional[str] = None
    intent: Optional[str] = None
    status: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    settings: Optional[Dict[str, Any]] = None

@dataclass
class CampaignContact:
    """Campaign-contact association"""
    campaign_contact_id: str
    campaign_id: str
    contact_id: str
    status: str = "enrolled"  # enrolled, accepted, replied, blacklisted
    enrolled_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    blacklisted_at: Optional[datetime] = None
    sequence_step: int = 1
    tags: Optional[List[str]] = None

@dataclass
class Message:
    """Message data model"""
    message_id: str
    campaign_contact_id: str
    direction: str  # 'sent' or 'received'
    message_text: str
    linkedin_message_id: Optional[str] = None
    thread_url: Optional[str] = None
    sent_at: Optional[datetime] = None
    received_at: Optional[datetime] = None
    status: str = "sent"
    tags: Optional[List[str]] = None
    created_at: Optional[datetime] = None

@dataclass
class WebhookEvent:
    """Webhook event data model"""
    event_id: str
    dux_user_id: str
    event_type: str
    event_name: str
    raw_data: Dict[str, Any]
    contact_id: Optional[str] = None
    campaign_id: Optional[str] = None
    processed: bool = False
    created_at: Optional[datetime] = None

class AzureDatabaseManager:
    """Manages Azure PostgreSQL Database operations"""
    
    def __init__(self, connection_string: str):
        """Initialize database connection"""
        self.connection_string = connection_string
        self.pool = None
        self._init_connection_pool()
        self._create_tables()
    
    def _init_connection_pool(self):
        """Initialize connection pool"""
        try:
            self.pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=self.connection_string
            )
            logger.info("✅ Database connection pool initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize database pool: {e}")
            raise
    
    def _get_connection(self):
        """Get connection from pool"""
        return self.pool.getconn()
    
    def _return_connection(self, conn):
        """Return connection to pool"""
        self.pool.putconn(conn)
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                # Create campaigns table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS campaigns (
                        campaign_id UUID PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        target_title VARCHAR(255),
                        intent TEXT,
                        status VARCHAR(50) DEFAULT 'active',
                        dux_user_id VARCHAR(100) NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW(),
                        settings JSONB
                    )
                """)
                
                # Create contacts table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS contacts (
                        contact_id UUID PRIMARY KEY,
                        linkedin_id VARCHAR(100) UNIQUE,
                        linkedin_url VARCHAR(500),
                        first_name VARCHAR(100),
                        last_name VARCHAR(100),
                        headline VARCHAR(500),
                        company VARCHAR(255),
                        company_url VARCHAR(500),
                        location VARCHAR(255),
                        industry VARCHAR(255),
                        connection_degree INTEGER,
                        email VARCHAR(255),
                        phone VARCHAR(50),
                        profile_data JSONB,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                # Create campaign_contacts table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS campaign_contacts (
                        campaign_contact_id UUID PRIMARY KEY,
                        campaign_id UUID REFERENCES campaigns(campaign_id),
                        contact_id UUID REFERENCES contacts(contact_id),
                        status VARCHAR(50) DEFAULT 'enrolled',
                        enrolled_at TIMESTAMP DEFAULT NOW(),
                        accepted_at TIMESTAMP,
                        replied_at TIMESTAMP,
                        blacklisted_at TIMESTAMP,
                        sequence_step INTEGER DEFAULT 1,
                        tags TEXT[],
                        UNIQUE(campaign_id, contact_id)
                    )
                """)
                
                # Create messages table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        message_id UUID PRIMARY KEY,
                        campaign_contact_id UUID REFERENCES campaign_contacts(campaign_contact_id),
                        direction VARCHAR(20) NOT NULL,
                        message_text TEXT NOT NULL,
                        linkedin_message_id VARCHAR(100),
                        thread_url VARCHAR(500),
                        sent_at TIMESTAMP,
                        received_at TIMESTAMP,
                        status VARCHAR(50) DEFAULT 'sent',
                        tags TEXT[],
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                # Create webhook_events table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS webhook_events (
                        event_id UUID PRIMARY KEY,
                        dux_user_id VARCHAR(100) NOT NULL,
                        event_type VARCHAR(50) NOT NULL,
                        event_name VARCHAR(50) NOT NULL,
                        contact_id UUID REFERENCES contacts(contact_id),
                        campaign_id UUID REFERENCES campaigns(campaign_id),
                        raw_data JSONB NOT NULL,
                        processed BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                # Create indexes for performance
                cur.execute("CREATE INDEX IF NOT EXISTS idx_webhook_events_type ON webhook_events(event_type)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_webhook_events_user ON webhook_events(dux_user_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_campaign_contacts_status ON campaign_contacts(status)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_messages_direction ON messages(direction)")
                
                conn.commit()
                logger.info("✅ Database tables created successfully")
                
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            conn.rollback()
            raise
        finally:
            self._return_connection(conn)
    
    def store_webhook_event(self, webhook_data: Dict[str, Any]) -> str:
        """Store webhook event in database"""
        conn = self._get_connection()
        try:
            # Generate event ID if not present
            event_id = webhook_data.get('event_id', str(uuid.uuid4()))
            
            # Parse timestamp (convert ms to seconds if needed)
            raw_ts = webhook_data.get('timestamp', datetime.now().timestamp())
            if raw_ts > 1e12:  # If timestamp is in ms
                raw_ts = raw_ts / 1000.0
            timestamp = datetime.fromtimestamp(
                raw_ts,
                tz=timezone.utc
            )
            
            # Extract contact info if available
            contact_id = None
            if 'data' in webhook_data:
                data = webhook_data['data']
                if 'fromId' in data:
                    contact_id = self._get_or_create_contact_id(data['fromId'], data)
                elif 'toId' in data:
                    contact_id = self._get_or_create_contact_id(data['toId'], data)
            
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO webhook_events 
                    (event_id, dux_user_id, event_type, event_name, contact_id, raw_data, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (event_id) DO UPDATE SET
                    raw_data = EXCLUDED.raw_data,
                    updated_at = NOW()
                """, (
                    event_id,
                    webhook_data.get('userid', 'unknown'),
                    webhook_data.get('type', 'unknown'),
                    webhook_data.get('event', 'unknown'),
                    contact_id,
                    Json(webhook_data),
                    timestamp
                ))
                
                conn.commit()
                logger.info(f"✅ Webhook event stored: {event_id}")
                return event_id
                
        except Exception as e:
            logger.error(f"❌ Failed to store webhook event: {e}")
            conn.rollback()
            raise
        finally:
            self._return_connection(conn)
    
    def _get_or_create_contact_id(self, linkedin_id: str, profile_data: Dict[str, Any]) -> str:
        """Get existing contact ID or create new contact"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                # Check if contact exists
                cur.execute("SELECT contact_id FROM contacts WHERE linkedin_id = %s", (linkedin_id,))
                result = cur.fetchone()
                
                if result:
                    return result[0]
                
                # Create new contact
                contact_id = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO contacts 
                    (contact_id, linkedin_id, first_name, last_name, headline, company, 
                     company_url, location, industry, profile_data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    contact_id,
                    linkedin_id,
                    profile_data.get('fromFirstName') or profile_data.get('toFirstName'),
                    profile_data.get('fromLastName') or profile_data.get('toLastName'),
                    profile_data.get('headline'),
                    profile_data.get('Company'),
                    profile_data.get('CompanyProfile'),
                    profile_data.get('Location'),
                    profile_data.get('Industry'),
                    Json(profile_data)
                ))
                
                conn.commit()
                logger.info(f"✅ New contact created: {contact_id}")
                return contact_id
                
        except Exception as e:
            logger.error(f"❌ Failed to get/create contact: {e}")
            conn.rollback()
            raise
        finally:
            self._return_connection(conn)
    
    def get_contacts_who_replied(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Get contacts who replied to a campaign"""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT c.*, cc.campaign_id, cc.replied_at
                    FROM contacts c
                    JOIN campaign_contacts cc ON c.contact_id = cc.contact_id
                    WHERE cc.status = 'replied' AND cc.campaign_id = %s
                    ORDER BY cc.replied_at DESC
                """, (campaign_id,))
                
                return cur.fetchall()
                
        except Exception as e:
            logger.error(f"❌ Failed to get contacts who replied: {e}")
            raise
        finally:
            self._return_connection(conn)
    
    def get_message_history(self, contact_id: str) -> List[Dict[str, Any]]:
        """Get message history for a contact"""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT m.*, c.first_name, c.last_name, c.headline
                    FROM messages m
                    JOIN campaign_contacts cc ON m.campaign_contact_id = cc.campaign_contact_id
                    JOIN contacts c ON cc.contact_id = c.contact_id
                    WHERE cc.contact_id = %s
                    ORDER BY m.created_at DESC
                """, (contact_id,))
                
                return cur.fetchall()
                
        except Exception as e:
            logger.error(f"❌ Failed to get message history: {e}")
            raise
        finally:
            self._return_connection(conn)
    
    def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign statistics"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        COUNT(cc.contact_id) as total_contacts,
                        COUNT(CASE WHEN cc.status = 'accepted' THEN 1 END) as accepted,
                        COUNT(CASE WHEN cc.status = 'replied' THEN 1 END) as replied,
                        COUNT(CASE WHEN cc.status = 'blacklisted' THEN 1 END) as blacklisted
                    FROM campaign_contacts cc
                    WHERE cc.campaign_id = %s
                """, (campaign_id,))
                
                result = cur.fetchone()
                if result:
                    total, accepted, replied, blacklisted = result
                    reply_rate = round((replied * 100.0 / total) if total > 0 else 0, 2)
                    
                    return {
                        'total_contacts': total,
                        'accepted': accepted,
                        'replied': replied,
                        'blacklisted': blacklisted,
                        'reply_rate': reply_rate
                    }
                
                return {'total_contacts': 0, 'accepted': 0, 'replied': 0, 'blacklisted': 0, 'reply_rate': 0}
                
        except Exception as e:
            logger.error(f"❌ Failed to get campaign stats: {e}")
            raise
        finally:
            self._return_connection(conn)
    
    def get_active_campaigns(self) -> List[Dict[str, Any]]:
        """Get all active campaigns (between scheduled_start and end_date) using campaign_key (UUID) for joins"""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        c.*, 
                        COALESCE(cnt.total_contacts, 0) as total_contacts,
                        COALESCE(cnt.accepted_count, 0) as accepted_count,
                        COALESCE(cnt.replied_count, 0) as replied_count
                    FROM campaigns c
                    LEFT JOIN (
                        SELECT 
                            campaign_key, 
                            COUNT(contact_id) as total_contacts,
                            COUNT(CASE WHEN status = 'accepted' THEN 1 END) as accepted_count,
                            COUNT(CASE WHEN status = 'replied' THEN 1 END) as replied_count
                        FROM campaign_contacts
                        GROUP BY campaign_key
                    ) cnt ON c.campaign_key = cnt.campaign_key
                    WHERE c.status = 'active'
                    AND (c.scheduled_start IS NULL OR c.scheduled_start <= NOW())
                    AND (c.end_date IS NULL OR c.end_date >= NOW())
                    ORDER BY c.scheduled_start ASC NULLS FIRST;
                """)
                return cur.fetchall()
        except Exception as e:
            self.logger.error(f"❌ Failed to get active campaigns: {e}")
            raise
    
    def close(self):
        """Close database connections"""
        if self.pool:
            self.pool.closeall()
            logger.info("✅ Database connections closed")

# Example usage
if __name__ == "__main__":
    # Connection string format for Azure PostgreSQL
    # "postgresql://username:password@server.postgres.database.azure.com:5432/database"
    
    connection_string = "postgresql://your_username:your_password@your_server.postgres.database.azure.com:5432/your_database"
    
    db_manager = AzureDatabaseManager(connection_string)
    
    # Test webhook data
    test_webhook = {
        "type": "message",
        "event": "received",
        "userid": "test_user_123",
        "timestamp": datetime.now().timestamp() * 1000,
        "data": {
            "fromId": "id.123456789",
            "fromFirstName": "John",
            "fromLastName": "Doe",
            "text": "Hello, thanks for connecting!"
        }
    }
    
    event_id = db_manager.store_webhook_event(test_webhook)
    print(f"Stored webhook event: {event_id}")
    
    db_manager.close() 