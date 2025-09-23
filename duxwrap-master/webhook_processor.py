#!/usr/bin/env python3
"""
Dux-Soup Webhook Processor

Processes incoming Dux-Soup webhook events and populates the database
with structured data for LinkedIn automation campaigns.
"""

import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from dataclasses import dataclass, asdict
import os
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WebhookEvent:
    """Webhook event data structure"""
    event_id: str
    dux_user_id: str
    event_type: str
    event_name: str
    raw_data: Dict[str, Any]
    processed: bool = False
    contact_id: Optional[str] = None
    campaign_id: Optional[str] = None
    created_at: Optional[datetime] = None

@dataclass
class Contact:
    """Contact data structure"""
    contact_id: str
    linkedin_id: Optional[str]
    linkedin_url: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    headline: Optional[str]
    company: Optional[str]
    location: Optional[str]
    industry: Optional[str]
    connection_degree: Optional[int]
    profile_data: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Campaign:
    """Campaign data structure"""
    campaign_id: str
    campaign_key: str
    name: str
    status: str
    dux_user_id: str
    scheduled_start: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    settings: Optional[Dict[str, Any]] = None

@dataclass
class CampaignContact:
    """Campaign-Contact relationship"""
    campaign_contact_id: str
    campaign_id: str
    contact_id: str
    status: str
    sequence_step: int
    enrolled_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None

@dataclass
class Message:
    """Message data structure"""
    message_id: str
    campaign_contact_id: str
    direction: str
    message_text: str
    linkedin_message_id: Optional[str]
    thread_url: Optional[str]
    sent_at: Optional[datetime] = None
    received_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class DuxSoupWebhookProcessor:
    """
    Processes Dux-Soup webhook events and populates the database
    """
    
    def __init__(self, database_url: str):
        """
        Initialize the webhook processor
        
        Args:
            database_url: PostgreSQL connection string
        """
        self.database_url = database_url
        self.conn = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.database_url)
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def process_webhook_event(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single webhook event
        
        Args:
            webhook_data: Raw webhook payload from Dux-Soup
            
        Returns:
            Processing result with status and details
        """
        try:
            # Step 1: Store raw webhook event
            event = self._store_webhook_event(webhook_data)
            
            # Step 2: Extract and process contact data
            contact = self._process_contact_data(webhook_data, event)
            
            # Step 3: Extract and process campaign data
            campaign = self._process_campaign_data(webhook_data, event)
            
            # Step 4: Create campaign-contact relationship
            campaign_contact = self._process_campaign_contact(contact, campaign, webhook_data)
            
            # Step 5: Process messages if present
            messages = self._process_messages(webhook_data, campaign_contact)
            
            # Step 6: Mark event as processed
            self._mark_event_processed(event.event_id, contact.contact_id if contact else None, 
                                     campaign.campaign_id if campaign else None)
            
            return {
                "success": True,
                "event_id": event.event_id,
                "contact_id": contact.contact_id if contact else None,
                "campaign_id": campaign.campaign_id if campaign else None,
                "campaign_contact_id": campaign_contact.campaign_contact_id if campaign_contact else None,
                "messages_processed": len(messages)
            }
            
        except Exception as e:
            logger.error(f"Error processing webhook event: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _store_webhook_event(self, webhook_data: Dict[str, Any]) -> WebhookEvent:
        """Store raw webhook event in landing zone"""
        event_id = str(uuid.uuid4())
        dux_user_id = webhook_data.get('userid', 'unknown')
        event_type = webhook_data.get('type', 'unknown')
        event_name = webhook_data.get('name', 'unknown')
        
        event = WebhookEvent(
            event_id=event_id,
            dux_user_id=dux_user_id,
            event_type=event_type,
            event_name=event_name,
            raw_data=webhook_data,
            created_at=datetime.now(timezone.utc)
        )
        
        with self.conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO webhook_events 
                (event_id, dux_user_id, event_type, event_name, raw_data, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                event.event_id,
                event.dux_user_id,
                event.event_type,
                event.event_name,
                Json(event.raw_data),
                event.created_at
            ))
            self.conn.commit()
        
        logger.info(f"Stored webhook event: {event_id}")
        return event
    
    def _process_contact_data(self, webhook_data: Dict[str, Any], event: WebhookEvent) -> Optional[Contact]:
        """Extract and process contact information"""
        # Extract contact data from webhook payload
        contact_data = webhook_data.get('data', {})
        
        # Get LinkedIn profile information
        linkedin_id = contact_data.get('linkedin_id') or contact_data.get('id')
        linkedin_url = contact_data.get('profile') or contact_data.get('profile_url')
        
        if not linkedin_id and not linkedin_url:
            logger.warning("No LinkedIn ID or URL found in webhook data")
            return None
        
        # Check if contact already exists
        existing_contact = self._get_contact_by_linkedin_id(linkedin_id) if linkedin_id else None
        if not existing_contact:
            existing_contact = self._get_contact_by_url(linkedin_url) if linkedin_url else None
        
        if existing_contact:
            # Update existing contact
            return self._update_contact(existing_contact, contact_data)
        else:
            # Create new contact
            return self._create_contact(contact_data, linkedin_id, linkedin_url)
    
    def _get_contact_by_linkedin_id(self, linkedin_id: str) -> Optional[Contact]:
        """Get contact by LinkedIn ID"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM contacts WHERE linkedin_id = %s
            """, (linkedin_id,))
            row = cursor.fetchone()
            return Contact(**dict(row)) if row else None
    
    def _get_contact_by_url(self, linkedin_url: str) -> Optional[Contact]:
        """Get contact by LinkedIn URL"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM contacts WHERE linkedin_url = %s
            """, (linkedin_url,))
            row = cursor.fetchone()
            return Contact(**dict(row)) if row else None
    
    def _create_contact(self, contact_data: Dict[str, Any], linkedin_id: Optional[str], 
                       linkedin_url: Optional[str]) -> Contact:
        """Create new contact record"""
        contact_id = str(uuid.uuid4())
        
        # Extract profile information
        first_name = contact_data.get('first_name') or contact_data.get('firstName')
        last_name = contact_data.get('last_name') or contact_data.get('lastName')
        headline = contact_data.get('headline') or contact_data.get('title')
        company = contact_data.get('company') or contact_data.get('currentCompany')
        location = contact_data.get('location') or contact_data.get('city')
        industry = contact_data.get('industry')
        connection_degree = contact_data.get('connection_degree') or contact_data.get('degree')
        
        contact = Contact(
            contact_id=contact_id,
            linkedin_id=linkedin_id,
            linkedin_url=linkedin_url,
            first_name=first_name,
            last_name=last_name,
            headline=headline,
            company=company,
            location=location,
            industry=industry,
            connection_degree=connection_degree,
            profile_data=contact_data,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        with self.conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO contacts 
                (contact_id, linkedin_id, linkedin_url, first_name, last_name, 
                 headline, company, location, industry, connection_degree, 
                 profile_data, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                contact.contact_id,
                contact.linkedin_id,
                contact.linkedin_url,
                contact.first_name,
                contact.last_name,
                contact.headline,
                contact.company,
                contact.location,
                contact.industry,
                contact.connection_degree,
                Json(contact.profile_data),
                contact.created_at,
                contact.updated_at
            ))
            self.conn.commit()
        
        logger.info(f"Created new contact: {contact_id}")
        return contact
    
    def _update_contact(self, existing_contact: Contact, new_data: Dict[str, Any]) -> Contact:
        """Update existing contact with new data"""
        # Update fields with new data if available
        updated_fields = {}
        
        for field in ['first_name', 'last_name', 'headline', 'company', 'location', 'industry']:
            new_value = new_data.get(field) or new_data.get(field.replace('_', ''))
            if new_value and getattr(existing_contact, field) != new_value:
                setattr(existing_contact, field, new_value)
                updated_fields[field] = new_value
        
        # Update profile_data
        existing_contact.profile_data.update(new_data)
        updated_fields['profile_data'] = existing_contact.profile_data
        
        if updated_fields:
            with self.conn.cursor() as cursor:
                set_clause = ", ".join([f"{k} = %s" for k in updated_fields.keys()])
                values = list(updated_fields.values()) + [existing_contact.contact_id]
                
                cursor.execute(f"""
                    UPDATE contacts 
                    SET {set_clause}, updated_at = NOW()
                    WHERE contact_id = %s
                """, values)
                self.conn.commit()
            
            logger.info(f"Updated contact: {existing_contact.contact_id}")
        
        return existing_contact
    
    def _process_campaign_data(self, webhook_data: Dict[str, Any], event: WebhookEvent) -> Optional[Campaign]:
        """Extract and process campaign information"""
        campaign_id = webhook_data.get('campaignid') or webhook_data.get('campaign_id')
        
        if not campaign_id:
            logger.info("No campaign ID found in webhook data")
            return None
        
        # Check if campaign exists
        existing_campaign = self._get_campaign_by_id(campaign_id)
        
        if existing_campaign:
            return existing_campaign
        else:
            # Create default campaign if it doesn't exist
            return self._create_default_campaign(campaign_id, event.dux_user_id)
    
    def _get_campaign_by_id(self, campaign_id: str) -> Optional[Campaign]:
        """Get campaign by ID"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM campaigns WHERE campaign_id = %s
            """, (campaign_id,))
            row = cursor.fetchone()
            return Campaign(**dict(row)) if row else None
    
    def _create_default_campaign(self, campaign_id: str, dux_user_id: str) -> Campaign:
        """Create default campaign record"""
        campaign_key = str(uuid.uuid4())
        
        campaign = Campaign(
            campaign_id=campaign_id,
            campaign_key=campaign_key,
            name=f"Campaign {campaign_id[:8]}",
            status="active",
            dux_user_id=dux_user_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            settings={}
        )
        
        with self.conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO campaigns 
                (campaign_id, campaign_key, name, status, dux_user_id, 
                 created_at, updated_at, settings)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                campaign.campaign_id,
                campaign.campaign_key,
                campaign.name,
                campaign.status,
                campaign.dux_user_id,
                campaign.created_at,
                campaign.updated_at,
                Json(campaign.settings or {})
            ))
            self.conn.commit()
        
        logger.info(f"Created default campaign: {campaign_id}")
        return campaign
    
    def _process_campaign_contact(self, contact: Optional[Contact], campaign: Optional[Campaign], 
                                 webhook_data: Dict[str, Any]) -> Optional[CampaignContact]:
        """Create or update campaign-contact relationship"""
        if not contact or not campaign:
            return None
        
        # Check if relationship exists
        existing_relationship = self._get_campaign_contact(campaign.campaign_id, contact.contact_id)
        
        if existing_relationship:
            # Update existing relationship
            return self._update_campaign_contact(existing_relationship, webhook_data)
        else:
            # Create new relationship
            return self._create_campaign_contact(campaign.campaign_id, contact.contact_id, webhook_data)
    
    def _get_campaign_contact(self, campaign_id: str, contact_id: str) -> Optional[CampaignContact]:
        """Get campaign-contact relationship"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM campaign_contacts 
                WHERE campaign_id = %s AND contact_id = %s
            """, (campaign_id, contact_id))
            row = cursor.fetchone()
            return CampaignContact(**dict(row)) if row else None
    
    def _create_campaign_contact(self, campaign_id: str, contact_id: str, 
                                webhook_data: Dict[str, Any]) -> CampaignContact:
        """Create new campaign-contact relationship"""
        campaign_contact_id = str(uuid.uuid4())
        
        # Determine initial status based on event type
        event_type = webhook_data.get('type', '')
        event_name = webhook_data.get('name', '')
        
        if event_type == 'message' and event_name == 'received':
            status = 'replied'
        elif event_type == 'action' and 'connect' in event_name.lower():
            status = 'accepted'
        else:
            status = 'enrolled'
        
        campaign_contact = CampaignContact(
            campaign_contact_id=campaign_contact_id,
            campaign_id=campaign_id,
            contact_id=contact_id,
            status=status,
            sequence_step=1,
            enrolled_at=datetime.now(timezone.utc)
        )
        
        with self.conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO campaign_contacts 
                (campaign_contact_id, campaign_id, contact_id, status, 
                 sequence_step, enrolled_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                campaign_contact.campaign_contact_id,
                campaign_contact.campaign_id,
                campaign_contact.contact_id,
                campaign_contact.status,
                campaign_contact.sequence_step,
                campaign_contact.enrolled_at
            ))
            self.conn.commit()
        
        logger.info(f"Created campaign-contact relationship: {campaign_contact_id}")
        return campaign_contact
    
    def _update_campaign_contact(self, existing_relationship: CampaignContact, 
                                webhook_data: Dict[str, Any]) -> CampaignContact:
        """Update existing campaign-contact relationship"""
        event_type = webhook_data.get('type', '')
        event_name = webhook_data.get('name', '')
        
        updates = {}
        
        # Update status based on event
        if event_type == 'message' and event_name == 'received':
            if existing_relationship.status != 'replied':
                updates['status'] = 'replied'
                updates['replied_at'] = datetime.now(timezone.utc)
        elif event_type == 'action' and 'connect' in event_name.lower():
            if existing_relationship.status != 'accepted':
                updates['status'] = 'accepted'
                updates['accepted_at'] = datetime.now(timezone.utc)
        
        if updates:
            with self.conn.cursor() as cursor:
                set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
                values = list(updates.values()) + [existing_relationship.campaign_contact_id]
                
                cursor.execute(f"""
                    UPDATE campaign_contacts 
                    SET {set_clause}
                    WHERE campaign_contact_id = %s
                """, values)
                self.conn.commit()
            
            logger.info(f"Updated campaign-contact relationship: {existing_relationship.campaign_contact_id}")
        
        return existing_relationship
    
    def _process_messages(self, webhook_data: Dict[str, Any], 
                         campaign_contact: Optional[CampaignContact]) -> List[Message]:
        """Process messages from webhook data"""
        messages = []
        
        if not campaign_contact:
            return messages
        
        # Extract message data
        message_data = webhook_data.get('data', {})
        message_text = message_data.get('message') or message_data.get('text')
        
        if not message_text:
            return messages
        
        # Determine message direction
        event_type = webhook_data.get('type', '')
        event_name = webhook_data.get('name', '')
        
        if event_type == 'message' and event_name == 'received':
            direction = 'received'
            received_at = datetime.now(timezone.utc)
            sent_at = None
        else:
            direction = 'sent'
            sent_at = datetime.now(timezone.utc)
            received_at = None
        
        message = Message(
            message_id=str(uuid.uuid4()),
            campaign_contact_id=campaign_contact.campaign_contact_id,
            direction=direction,
            message_text=message_text,
            linkedin_message_id=message_data.get('message_id'),
            thread_url=message_data.get('thread_url'),
            sent_at=sent_at,
            received_at=received_at,
            created_at=datetime.now(timezone.utc)
        )
        
        with self.conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO messages 
                (message_id, campaign_contact_id, direction, message_text,
                 linkedin_message_id, thread_url, sent_at, received_at, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                message.message_id,
                message.campaign_contact_id,
                message.direction,
                message.message_text,
                message.linkedin_message_id,
                message.thread_url,
                message.sent_at,
                message.received_at,
                message.created_at
            ))
            self.conn.commit()
        
        messages.append(message)
        logger.info(f"Processed message: {message.message_id}")
        
        return messages
    
    def _mark_event_processed(self, event_id: str, contact_id: Optional[str], 
                             campaign_id: Optional[str]):
        """Mark webhook event as processed"""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                UPDATE webhook_events 
                SET processed = TRUE, contact_id = %s, campaign_id = %s
                WHERE event_id = %s
            """, (contact_id, campaign_id, event_id))
            self.conn.commit()
        
        logger.info(f"Marked event as processed: {event_id}")


# Flask webhook endpoint handler
def create_webhook_handler(database_url: str):
    """Create Flask webhook handler"""
    app = Flask(__name__)
    processor = DuxSoupWebhookProcessor(database_url)
    
    @app.route('/webhook/dux-soup', methods=['POST'])
    def webhook_endpoint():
        """Handle incoming Dux-Soup webhook events"""
        try:
            # Get webhook data
            webhook_data = request.get_json()
            
            if not webhook_data:
                return jsonify({"error": "No webhook data received"}), 400
            
            # Connect to database
            processor.connect()
            
            # Process the webhook event
            result = processor.process_webhook_event(webhook_data)
            
            # Disconnect from database
            processor.disconnect()
            
            if result["success"]:
                return jsonify(result), 200
            else:
                return jsonify(result), 500
                
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            return jsonify({"error": str(e)}), 500
    
    return app


if __name__ == "__main__":
    # Example usage
    database_url = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/duxwrap")
    
    # Create and run Flask app
    app = create_webhook_handler(database_url)
    app.run(host='0.0.0.0', port=5000, debug=True) 