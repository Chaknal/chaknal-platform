"""
Complete Database Manager for Dux-Soup LinkedIn Automation Platform

This module provides a comprehensive database interface for storing and processing
Dux-Soup webhook events. It includes all the logic needed to handle different
types of webhook events (messages, visits, actions, robot commands) and manage
campaigns, contacts, and messaging sequences.

DUX-SOUP WEBHOOK EVENT TYPES:
- message: LinkedIn messages sent/received
- visit: Profile visits and interactions  
- action: Connection requests, endorsements, etc.
- rccommand: Robot command status updates

USAGE:
    from complete_database_manager import CompleteDatabaseManager
    
    # Initialize with connection string
    db = CompleteDatabaseManager(connection_string)
    
    # Store webhook event
    event_id = db.store_webhook_event(webhook_data)
    
    # Get campaign statistics
    stats = db.get_campaign_stats(campaign_id)
    
    # Close connections
    db.close()
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
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
    """Dux-Soup event types from webhook data"""
    MESSAGE = "message"
    VISIT = "visit"
    ACTION = "action"
    RCCOMMAND = "rccommand"

class EventStatus(Enum):
    """Event processing status"""
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"

class CampaignStatus(Enum):
    """Campaign status values"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class ContactStatus(Enum):
    """Campaign contact status values"""
    ENROLLED = "enrolled"
    ACCEPTED = "accepted"
    REPLIED = "replied"
    BLACKLISTED = "blacklisted"
    COMPLETED = "completed"

@dataclass
class Contact:
    """LinkedIn contact data model extracted from Dux-Soup webhooks"""
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
    """LinkedIn automation campaign data model"""
    campaign_id: str
    campaign_key: str
    name: str
    dux_user_id: str
    description: Optional[str] = None
    target_title: Optional[str] = None
    intent: Optional[str] = None
    status: str = "active"
    scheduled_start: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    settings: Optional[Dict[str, Any]] = None

@dataclass
class CampaignContact:
    """Campaign-contact association with engagement tracking"""
    campaign_contact_id: str
    campaign_id: str
    campaign_key: str
    contact_id: str
    status: str = "enrolled"
    enrolled_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    blacklisted_at: Optional[datetime] = None
    sequence_step: int = 1
    tags: Optional[List[str]] = None

@dataclass
class Message:
    """LinkedIn message data model for conversation tracking"""
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
    """Raw webhook event data model"""
    event_id: str
    dux_user_id: str
    event_type: str
    event_name: str
    raw_data: Dict[str, Any]
    contact_id: Optional[str] = None
    campaign_id: Optional[str] = None
    processed: bool = False
    created_at: Optional[datetime] = None

class CompleteDatabaseManager:
    """
    Comprehensive database manager for Dux-Soup LinkedIn automation platform.
    
    This class handles all database operations including:
    - Webhook event storage and processing
    - Contact profile management
    - Campaign creation and tracking
    - Message history and conversation tracking
    - Campaign statistics and reporting
    """
    
    def __init__(self, connection_string: str):
        """
        Initialize database connection and ensure tables exist.
        
        Args:
            connection_string: PostgreSQL connection string
        """
        self.connection_string = connection_string
        self.pool = None
        self._init_connection_pool()
        self._create_tables()
        logger.info("✅ CompleteDatabaseManager initialized successfully")
    
    def _init_connection_pool(self):
        """Initialize database connection pool for performance"""
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
        """
        Create all database tables if they don't exist.
        
        This method creates the complete schema including:
        - campaigns: Campaign management
        - contacts: LinkedIn contact profiles
        - campaign_contacts: Campaign-contact relationships
        - messages: Message history
        - webhook_events: Raw webhook data
        - All necessary indexes and constraints
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                # Create campaigns table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS campaigns (
                        campaign_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        campaign_key UUID NOT NULL DEFAULT uuid_generate_v4(),
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        target_title VARCHAR(255),
                        intent TEXT,
                        status VARCHAR(50) DEFAULT 'active',
                        dux_user_id VARCHAR(100) NOT NULL,
                        scheduled_start TIMESTAMP WITH TIME ZONE,
                        end_date TIMESTAMP WITH TIME ZONE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        settings JSONB
                    )
                """)
                
                # Create contacts table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS contacts (
                        contact_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # Create campaign_contacts table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS campaign_contacts (
                        campaign_contact_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        campaign_id UUID REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
                        campaign_key UUID NOT NULL,
                        contact_id UUID REFERENCES contacts(contact_id) ON DELETE CASCADE,
                        status VARCHAR(50) DEFAULT 'enrolled',
                        enrolled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        accepted_at TIMESTAMP WITH TIME ZONE,
                        replied_at TIMESTAMP WITH TIME ZONE,
                        blacklisted_at TIMESTAMP WITH TIME ZONE,
                        sequence_step INTEGER DEFAULT 1,
                        tags TEXT[],
                        UNIQUE(campaign_id, contact_id)
                    )
                """)
                
                # Create messages table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        campaign_contact_id UUID REFERENCES campaign_contacts(campaign_contact_id) ON DELETE CASCADE,
                        direction VARCHAR(20) NOT NULL,
                        message_text TEXT NOT NULL,
                        linkedin_message_id VARCHAR(100),
                        thread_url VARCHAR(500),
                        sent_at TIMESTAMP WITH TIME ZONE,
                        received_at TIMESTAMP WITH TIME ZONE,
                        status VARCHAR(50) DEFAULT 'sent',
                        tags TEXT[],
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # Create webhook_events table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS webhook_events (
                        event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        dux_user_id VARCHAR(100) NOT NULL,
                        event_type VARCHAR(50) NOT NULL,
                        event_name VARCHAR(50) NOT NULL,
                        contact_id UUID REFERENCES contacts(contact_id) ON DELETE SET NULL,
                        campaign_id UUID REFERENCES campaigns(campaign_id) ON DELETE SET NULL,
                        raw_data JSONB NOT NULL,
                        processed BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # Create indexes for performance
                self._create_indexes(cur)
                
                conn.commit()
                logger.info("✅ Database tables created successfully")
                
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            conn.rollback()
            raise
        finally:
            self._return_connection(conn)
    
    def _create_indexes(self, cur):
        """Create all necessary database indexes for performance"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_webhook_events_type ON webhook_events(event_type)",
            "CREATE INDEX IF NOT EXISTS idx_webhook_events_user ON webhook_events(dux_user_id)",
            "CREATE INDEX IF NOT EXISTS idx_webhook_events_created_at ON webhook_events(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_webhook_events_processed ON webhook_events(processed)",
            "CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status)",
            "CREATE INDEX IF NOT EXISTS idx_campaigns_user ON campaigns(dux_user_id)",
            "CREATE INDEX IF NOT EXISTS idx_campaigns_scheduled_start ON campaigns(scheduled_start)",
            "CREATE INDEX IF NOT EXISTS idx_campaigns_campaign_key ON campaigns(campaign_key)",
            "CREATE INDEX IF NOT EXISTS idx_contacts_linkedin_id ON contacts(linkedin_id)",
            "CREATE INDEX IF NOT EXISTS idx_contacts_linkedin_url ON contacts(linkedin_url)",
            "CREATE INDEX IF NOT EXISTS idx_contacts_company ON contacts(company)",
            "CREATE INDEX IF NOT EXISTS idx_campaign_contacts_status ON campaign_contacts(status)",
            "CREATE INDEX IF NOT EXISTS idx_campaign_contacts_campaign_key ON campaign_contacts(campaign_key)",
            "CREATE INDEX IF NOT EXISTS idx_campaign_contacts_contact ON campaign_contacts(contact_id)",
            "CREATE INDEX IF NOT EXISTS idx_messages_direction ON messages(direction)",
            "CREATE INDEX IF NOT EXISTS idx_messages_campaign_contact ON messages(campaign_contact_id)",
            "CREATE INDEX IF NOT EXISTS idx_messages_sent_at ON messages(sent_at)"
        ]
        
        for index_sql in indexes:
            cur.execute(index_sql)
        
        logger.info("✅ Database indexes created successfully")
    
    def store_webhook_event(self, webhook_data: Dict[str, Any]) -> str:
        """
        Store a Dux-Soup webhook event in the database.
        
        This method processes incoming webhook data and:
        1. Extracts contact information from the webhook
        2. Creates or updates contact profiles
        3. Stores the raw webhook data
        4. Links events to contacts and campaigns
        
        Args:
            webhook_data: Raw webhook payload from Dux-Soup
            
        Returns:
            str: The event ID that was stored
            
        Example webhook_data:
        {
            "type": "message",
            "event": "received", 
            "profile": "https://www.linkedin.com/in/john-doe/",
            "userid": "12345",
            "data": {
                "from": "https://www.linkedin.com/in/john-doe/",
                "message": "Hi, thanks for connecting!",
                "timestamp": 1751508398903
            },
            "timestamp": 1751508398903
        }
        """
        conn = self._get_connection()
        try:
            # Generate event ID if not present
            event_id = webhook_data.get('event_id', str(uuid.uuid4()))
            
            # Parse timestamp (convert ms to seconds if needed)
            raw_ts = webhook_data.get('timestamp', datetime.now().timestamp())
            if raw_ts > 1e12:  # If timestamp is in ms
                raw_ts = raw_ts / 1000.0
            timestamp = datetime.fromtimestamp(raw_ts, tz=timezone.utc)
            
            # Extract contact info and create/update contact
            contact_id = None
            if 'data' in webhook_data:
                data = webhook_data['data']
                contact_id = self._process_contact_data(data, webhook_data.get('profile'))
            
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
                logger.info(f"✅ Webhook event stored: {event_id} ({webhook_data.get('type')})")
                return event_id
                
        except Exception as e:
            logger.error(f"❌ Failed to store webhook event: {e}")
            conn.rollback()
            raise
        finally:
            self._return_connection(conn)
    
    def _process_contact_data(self, data: Dict[str, Any], profile_url: Optional[str] = None) -> Optional[str]:
        """
        Process contact data from webhook and create/update contact record.
        
        Args:
            data: Contact data from webhook
            profile_url: LinkedIn profile URL
            
        Returns:
            str: Contact ID (UUID)
        """
        conn = self._get_connection()
        try:
            # Extract LinkedIn ID from profile URL or data
            linkedin_id = self._extract_linkedin_id(data, profile_url)
            if not linkedin_id:
                return None
            
            with conn.cursor() as cur:
                # Check if contact exists
                cur.execute("SELECT contact_id FROM contacts WHERE linkedin_id = %s", (linkedin_id,))
                result = cur.fetchone()
                
                if result:
                    # Update existing contact
                    contact_id = result[0]
                    self._update_contact_profile(contact_id, data, profile_url)
                    return contact_id
                
                # Create new contact
                contact_id = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO contacts 
                    (contact_id, linkedin_id, linkedin_url, first_name, last_name, headline, 
                     company, company_url, location, industry, connection_degree, 
                     email, phone, profile_data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    contact_id,
                    linkedin_id,
                    profile_url,
                    data.get('First Name') or data.get('fromFirstName'),
                    data.get('Last Name') or data.get('fromLastName'),
                    data.get('Title'),
                    data.get('Company'),
                    data.get('CompanyProfile'),
                    data.get('Location'),
                    data.get('Industry'),
                    data.get('Degree'),
                    data.get('Email'),
                    data.get('Phone'),
                    Json(data)
                ))
                
                conn.commit()
                logger.info(f"✅ New contact created: {contact_id} ({data.get('First Name', 'Unknown')} {data.get('Last Name', 'Unknown')})")
                return contact_id
                
        except Exception as e:
            logger.error(f"❌ Failed to process contact data: {e}")
            conn.rollback()
            raise
        finally:
            self._return_connection(conn)
    
    def _extract_linkedin_id(self, data: Dict[str, Any], profile_url: Optional[str] = None) -> Optional[str]:
        """
        Extract LinkedIn ID from webhook data or profile URL.
        
        Args:
            data: Webhook data
            profile_url: LinkedIn profile URL
            
        Returns:
            str: LinkedIn ID or None
        """
        # Try to extract from profile URL first
        if profile_url:
            # Extract ID from URL like: https://www.linkedin.com/in/john-doe/
            if '/in/' in profile_url:
                return profile_url.split('/in/')[-1].split('/')[0]
        
        # Try to extract from data fields
        if 'Profile' in data:
            profile = data['Profile']
            if '/in/' in profile:
                return profile.split('/in/')[-1].split('/')[0]
        
        # Try other possible fields
        for field in ['fromId', 'toId', 'id']:
            if field in data:
                return str(data[field])
        
        return None
    
    def _update_contact_profile(self, contact_id: str, data: Dict[str, Any], profile_url: Optional[str] = None):
        """
        Update existing contact profile with new data from webhook.
        
        Args:
            contact_id: Contact UUID
            data: New profile data
            profile_url: Updated profile URL
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE contacts SET
                        linkedin_url = COALESCE(%s, linkedin_url),
                        first_name = COALESCE(%s, first_name),
                        last_name = COALESCE(%s, last_name),
                        headline = COALESCE(%s, headline),
                        company = COALESCE(%s, company),
                        company_url = COALESCE(%s, company_url),
                        location = COALESCE(%s, location),
                        industry = COALESCE(%s, industry),
                        connection_degree = COALESCE(%s, connection_degree),
                        email = COALESCE(%s, email),
                        phone = COALESCE(%s, phone),
                        profile_data = %s,
                        updated_at = NOW()
                    WHERE contact_id = %s
                """, (
                    profile_url,
                    data.get('First Name') or data.get('fromFirstName'),
                    data.get('Last Name') or data.get('fromLastName'),
                    data.get('Title'),
                    data.get('Company'),
                    data.get('CompanyProfile'),
                    data.get('Location'),
                    data.get('Industry'),
                    data.get('Degree'),
                    data.get('Email'),
                    data.get('Phone'),
                    Json(data),
                    contact_id
                ))
                
                conn.commit()
                logger.info(f"✅ Contact profile updated: {contact_id}")
                
        except Exception as e:
            logger.error(f"❌ Failed to update contact profile: {e}")
            conn.rollback()
            raise
        finally:
            self._return_connection(conn)
    
    def create_campaign(self, name: str, dux_user_id: str, **kwargs) -> str:
        """
        Create a new LinkedIn automation campaign.
        
        Args:
            name: Campaign name
            dux_user_id: Dux-Soup user ID
            **kwargs: Additional campaign parameters
            
        Returns:
            str: Campaign ID (UUID)
        """
        conn = self._get_connection()
        try:
            campaign_id = str(uuid.uuid4())
            campaign_key = str(uuid.uuid4())
            
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO campaigns 
                    (campaign_id, campaign_key, name, dux_user_id, description, 
                     target_title, intent, status, scheduled_start, end_date, settings)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    campaign_id,
                    campaign_key,
                    name,
                    dux_user_id,
                    kwargs.get('description'),
                    kwargs.get('target_title'),
                    kwargs.get('intent'),
                    kwargs.get('status', 'active'),
                    kwargs.get('scheduled_start'),
                    kwargs.get('end_date'),
                    Json(kwargs.get('settings', {}))
                ))
                
                conn.commit()
                logger.info(f"✅ Campaign created: {campaign_id} ({name})")
                return campaign_id
                
        except Exception as e:
            logger.error(f"❌ Failed to create campaign: {e}")
            conn.rollback()
            raise
        finally:
            self._return_connection(conn)
    
    def add_contact_to_campaign(self, campaign_id: str, contact_id: str, **kwargs) -> str:
        """
        Add a contact to a campaign with status tracking.
        
        Args:
            campaign_id: Campaign UUID
            contact_id: Contact UUID
            **kwargs: Additional parameters (status, tags, etc.)
            
        Returns:
            str: Campaign contact ID (UUID)
        """
        conn = self._get_connection()
        try:
            campaign_contact_id = str(uuid.uuid4())
            
            # Get campaign_key for denormalization
            with conn.cursor() as cur:
                cur.execute("SELECT campaign_key FROM campaigns WHERE campaign_id = %s", (campaign_id,))
                result = cur.fetchone()
                if not result:
                    raise ValueError(f"Campaign not found: {campaign_id}")
                campaign_key = result[0]
                
                cur.execute("""
                    INSERT INTO campaign_contacts 
                    (campaign_contact_id, campaign_id, campaign_key, contact_id, 
                     status, sequence_step, tags)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (campaign_id, contact_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    tags = EXCLUDED.tags,
                    updated_at = NOW()
                """, (
                    campaign_contact_id,
                    campaign_id,
                    campaign_key,
                    contact_id,
                    kwargs.get('status', 'enrolled'),
                    kwargs.get('sequence_step', 1),
                    kwargs.get('tags', [])
                ))
                
                conn.commit()
                logger.info(f"✅ Contact added to campaign: {contact_id} -> {campaign_id}")
                return campaign_contact_id
                
        except Exception as e:
            logger.error(f"❌ Failed to add contact to campaign: {e}")
            conn.rollback()
            raise
        finally:
            self._return_connection(conn)
    
    def store_message(self, campaign_contact_id: str, direction: str, message_text: str, **kwargs) -> str:
        """
        Store a LinkedIn message in the database.
        
        Args:
            campaign_contact_id: Campaign contact UUID
            direction: 'sent' or 'received'
            message_text: Message content
            **kwargs: Additional message parameters
            
        Returns:
            str: Message ID (UUID)
        """
        conn = self._get_connection()
        try:
            message_id = str(uuid.uuid4())
            
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO messages 
                    (message_id, campaign_contact_id, direction, message_text,
                     linkedin_message_id, thread_url, sent_at, received_at, status, tags)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    message_id,
                    campaign_contact_id,
                    direction,
                    message_text,
                    kwargs.get('linkedin_message_id'),
                    kwargs.get('thread_url'),
                    kwargs.get('sent_at'),
                    kwargs.get('received_at'),
                    kwargs.get('status', 'sent'),
                    kwargs.get('tags', [])
                ))
                
                conn.commit()
                logger.info(f"✅ Message stored: {message_id} ({direction})")
                return message_id
                
        except Exception as e:
            logger.error(f"❌ Failed to store message: {e}")
            conn.rollback()
            raise
        finally:
            self._return_connection(conn)
    
    def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a campaign.
        
        Args:
            campaign_id: Campaign UUID
            
        Returns:
            Dict containing campaign statistics
        """
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        c.name,
                        c.status,
                        COUNT(cc.contact_id) as total_contacts,
                        COUNT(CASE WHEN cc.status = 'accepted' THEN 1 END) as accepted_count,
                        COUNT(CASE WHEN cc.status = 'replied' THEN 1 END) as replied_count,
                        COUNT(CASE WHEN cc.status = 'blacklisted' THEN 1 END) as blacklisted_count,
                        COUNT(CASE WHEN m.direction = 'sent' THEN 1 END) as messages_sent,
                        COUNT(CASE WHEN m.direction = 'received' THEN 1 END) as messages_received
                    FROM campaigns c
                    LEFT JOIN campaign_contacts cc ON c.campaign_id = cc.campaign_id
                    LEFT JOIN messages m ON cc.campaign_contact_id = m.campaign_contact_id
                    WHERE c.campaign_id = %s
                    GROUP BY c.campaign_id, c.name, c.status
                """, (campaign_id,))
                
                result = cur.fetchone()
                if result:
                    return dict(result)
                else:
                    return {}
                    
        except Exception as e:
            logger.error(f"❌ Failed to get campaign stats: {e}")
            raise
        finally:
            self._return_connection(conn)
    
    def get_active_campaigns(self, dux_user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all active campaigns with contact counts.
        
        Args:
            dux_user_id: Optional filter by Dux-Soup user ID
            
        Returns:
            List of active campaigns with statistics
        """
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
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
                """
                
                params = []
                if dux_user_id:
                    query += " AND c.dux_user_id = %s"
                    params.append(dux_user_id)
                
                query += " ORDER BY c.scheduled_start ASC NULLS FIRST"
                
                cur.execute(query, params)
                return [dict(row) for row in cur.fetchall()]
                
        except Exception as e:
            logger.error(f"❌ Failed to get active campaigns: {e}")
            raise
        finally:
            self._return_connection(conn)
    
    def get_contacts_who_replied(self, campaign_id: str) -> List[Dict[str, Any]]:
        """
        Get all contacts who replied to messages in a campaign.
        
        Args:
            campaign_id: Campaign UUID
            
        Returns:
            List of contacts with reply information
        """
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        c.*,
                        cc.replied_at,
                        cc.sequence_step,
                        m.message_text as last_reply
                    FROM contacts c
                    JOIN campaign_contacts cc ON c.contact_id = cc.contact_id
                    LEFT JOIN messages m ON cc.campaign_contact_id = m.campaign_contact_id
                    WHERE cc.campaign_id = %s 
                    AND cc.status = 'replied'
                    AND m.direction = 'received'
                    ORDER BY cc.replied_at DESC
                """, (campaign_id,))
                
                return [dict(row) for row in cur.fetchall()]
                
        except Exception as e:
            logger.error(f"❌ Failed to get contacts who replied: {e}")
            raise
        finally:
            self._return_connection(conn)
    
    def get_message_history(self, contact_id: str) -> List[Dict[str, Any]]:
        """
        Get complete message history for a contact.
        
        Args:
            contact_id: Contact UUID
            
        Returns:
            List of messages in chronological order
        """
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        m.*,
                        cc.campaign_id,
                        c.name as campaign_name
                    FROM messages m
                    JOIN campaign_contacts cc ON m.campaign_contact_id = cc.campaign_contact_id
                    JOIN campaigns c ON cc.campaign_id = c.campaign_id
                    WHERE cc.contact_id = %s
                    ORDER BY m.created_at ASC
                """, (contact_id,))
                
                return [dict(row) for row in cur.fetchall()]
                
        except Exception as e:
            logger.error(f"❌ Failed to get message history: {e}")
            raise
        finally:
            self._return_connection(conn)
    
    def get_recent_webhook_events(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get recent webhook events with contact information.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of recent webhook events
        """
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        we.*,
                        c.first_name,
                        c.last_name,
                        c.company
                    FROM webhook_events we
                    LEFT JOIN contacts c ON we.contact_id = c.contact_id
                    WHERE we.created_at >= NOW() - INTERVAL '%s hours'
                    ORDER BY we.created_at DESC
                """, (hours,))
                
                return [dict(row) for row in cur.fetchall()]
                
        except Exception as e:
            logger.error(f"❌ Failed to get recent webhook events: {e}")
            raise
        finally:
            self._return_connection(conn)
    
    def close(self):
        """Close all database connections"""
        if self.pool:
            self.pool.closeall()
            logger.info("✅ Database connections closed")

# =============================================================================
# USAGE EXAMPLES
# =============================================================================

def example_usage():
    """
    Example usage of the CompleteDatabaseManager.
    
    This demonstrates how to use the database manager for common operations.
    """
    
    # Initialize database manager
    connection_string = "postgresql://user:password@host:port/database"
    db = CompleteDatabaseManager(connection_string)
    
    try:
        # Example webhook data from Dux-Soup
        webhook_data = {
            "type": "message",
            "event": "received",
            "profile": "https://www.linkedin.com/in/john-doe/",
            "userid": "12345",
            "data": {
                "from": "https://www.linkedin.com/in/john-doe/",
                "message": "Hi, thanks for connecting!",
                "timestamp": 1751508398903,
                "First Name": "John",
                "Last Name": "Doe",
                "Title": "Chief Information Security Officer",
                "Company": "TechCorp",
                "Location": "San Francisco, CA"
            },
            "timestamp": 1751508398903
        }
        
        # Store webhook event
        event_id = db.store_webhook_event(webhook_data)
        print(f"Stored webhook event: {event_id}")
        
        # Create a campaign
        campaign_id = db.create_campaign(
            name="Q1 Cybersecurity Outreach",
            dux_user_id="12345",
            description="Targeting CISOs for partnership discussions",
            target_title="Chief Information Security Officer"
        )
        print(f"Created campaign: {campaign_id}")
        
        # Get campaign statistics
        stats = db.get_campaign_stats(campaign_id)
        print(f"Campaign stats: {stats}")
        
        # Get active campaigns
        active_campaigns = db.get_active_campaigns()
        print(f"Active campaigns: {len(active_campaigns)}")
        
        # Get recent webhook events
        recent_events = db.get_recent_webhook_events(hours=24)
        print(f"Recent events: {len(recent_events)}")
        
    finally:
        db.close()

if __name__ == "__main__":
    example_usage() 