from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import logging

from app.models.campaign import Campaign
from app.models.campaign_contact import CampaignContact
from app.models.message import Message

logger = logging.getLogger(__name__)

class CampaignScheduler:
    """Service for managing campaign scheduling and sequence execution"""
    
    @staticmethod
    async def is_campaign_active(campaign_id: str, session: AsyncSession) -> bool:
        """Check if a campaign is currently active (within date range)"""
        try:
            query = select(Campaign).where(Campaign.campaign_id == campaign_id)
            result = await session.execute(query)
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                return False
            
            now = datetime.utcnow()
            
            # Check if campaign is within date range
            if campaign.scheduled_start and now < campaign.scheduled_start:
                return False  # Campaign hasn't started yet
            
            if campaign.end_date and now > campaign.end_date:
                return False  # Campaign has ended
            
            # Check if campaign status is active
            return campaign.status == "active"
            
        except Exception as e:
            logger.error(f"Error checking campaign status: {e}")
            return False
    
    @staticmethod
    async def get_campaigns_to_start(session: AsyncSession) -> List[Campaign]:
        """Get campaigns that should start now"""
        try:
            now = datetime.utcnow()
            query = select(Campaign).where(
                and_(
                    Campaign.status == "draft",
                    Campaign.scheduled_start <= now,
                    Campaign.end_date > now
                )
            )
            result = await session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting campaigns to start: {e}")
            return []
    
    @staticmethod
    async def get_campaigns_to_end(session: AsyncSession) -> List[Campaign]:
        """Get campaigns that should end now"""
        try:
            now = datetime.utcnow()
            query = select(Campaign).where(
                and_(
                    Campaign.status == "active",
                    Campaign.end_date <= now
                )
            )
            result = await session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting campaigns to end: {e}")
            return []
    
    @staticmethod
    async def can_send_message(campaign_id: str, contact_id: str, session: AsyncSession) -> bool:
        """Check if a message can be sent to a contact (within campaign date range)"""
        try:
            # Check if campaign is active
            if not await CampaignScheduler.is_campaign_active(campaign_id, session):
                return False
            
            # Get campaign contact relationship
            query = select(CampaignContact).where(
                and_(
                    CampaignContact.campaign_id == campaign_id,
                    CampaignContact.contact_id == contact_id
                )
            )
            result = await session.execute(query)
            campaign_contact = result.scalar_one_or_none()
            
            if not campaign_contact:
                return False
            
            # Check if contact is in a valid status
            valid_statuses = ["pending", "active", "in_progress"]
            return campaign_contact.status in valid_statuses
            
        except Exception as e:
            logger.error(f"Error checking if message can be sent: {e}")
            return False
    
    @staticmethod
    async def get_next_message_time(campaign_id: str, contact_id: str, session: AsyncSession) -> Optional[datetime]:
        """Calculate when the next message should be sent to a contact"""
        try:
            # Get campaign details
            campaign_query = select(Campaign).where(Campaign.campaign_id == campaign_id)
            result = await session.execute(campaign_query)
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                return None
            
            # Get last message sent to this contact
            message_query = select(Message).join(
                CampaignContact, Message.campaign_contact_id == CampaignContact.campaign_contact_id
            ).where(
                and_(
                    CampaignContact.campaign_id == campaign_id,
                    CampaignContact.contact_id == contact_id
                )
            ).order_by(Message.created_at.desc())
            
            result = await session.execute(message_query)
            last_message = result.scalar_one_or_none()
            
            if not last_message:
                # First message - use campaign start date
                return campaign.scheduled_start or datetime.utcnow()
            
            # Calculate next message time based on delay_days
            delay_days = campaign.delay_days or 1
            next_time = last_message.created_at + timedelta(days=delay_days)
            
            # Add random delay if enabled
            if campaign.random_delay:
                import random
                random_hours = random.randint(0, 23)
                random_minutes = random.randint(0, 59)
                next_time += timedelta(hours=random_hours, minutes=random_minutes)
            
            # Ensure next message time is before campaign end date
            if campaign.end_date and next_time > campaign.end_date:
                return None  # Campaign will end before next message
            
            return next_time
            
        except Exception as e:
            logger.error(f"Error calculating next message time: {e}")
            return None
    
    @staticmethod
    async def get_contacts_ready_for_message(campaign_id: str, session: AsyncSession) -> List[Dict[str, Any]]:
        """Get contacts that are ready to receive their next message"""
        try:
            now = datetime.utcnow()
            ready_contacts = []
            
            # Get all active campaign contacts
            query = select(CampaignContact, Contact).join(
                Contact, CampaignContact.contact_id == Contact.contact_id
            ).where(
                and_(
                    CampaignContact.campaign_id == campaign_id,
                    CampaignContact.status.in_(["pending", "active", "in_progress"])
                )
            )
            
            result = await session.execute(query)
            campaign_contacts = result.fetchall()
            
            for campaign_contact, contact in campaign_contacts:
                # Check if contact is ready for next message
                next_message_time = await CampaignScheduler.get_next_message_time(
                    campaign_id, contact.contact_id, session
                )
                
                if next_message_time and next_message_time <= now:
                    ready_contacts.append({
                        "contact_id": contact.contact_id,
                        "campaign_contact_id": campaign_contact.campaign_contact_id,
                        "contact_name": contact.full_name,
                        "contact_email": contact.email,
                        "next_message_time": next_message_time,
                        "status": campaign_contact.status
                    })
            
            return ready_contacts
            
        except Exception as e:
            logger.error(f"Error getting contacts ready for message: {e}")
            return []
    
    @staticmethod
    async def end_campaign(campaign_id: str, session: AsyncSession) -> bool:
        """End a campaign and update all related records"""
        try:
            # Update campaign status
            campaign_query = select(Campaign).where(Campaign.campaign_id == campaign_id)
            result = await session.execute(campaign_query)
            campaign = result.scalar_one_or_none()
            
            if campaign:
                campaign.status = "completed"
                campaign.updated_at = datetime.utcnow()
            
            # Update all campaign contacts to completed status
            contacts_query = select(CampaignContact).where(
                CampaignContact.campaign_id == campaign_id
            )
            result = await session.execute(contacts_query)
            campaign_contacts = result.scalars().all()
            
            for campaign_contact in campaign_contacts:
                if campaign_contact.status in ["pending", "active", "in_progress"]:
                    campaign_contact.status = "completed"
                    campaign_contact.updated_at = datetime.utcnow()
            
            await session.commit()
            logger.info(f"Campaign {campaign_id} ended successfully")
            return True
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error ending campaign {campaign_id}: {e}")
            return False
    
    @staticmethod
    async def start_campaign(campaign_id: str, session: AsyncSession) -> bool:
        """Start a campaign and update status"""
        try:
            campaign_query = select(Campaign).where(Campaign.campaign_id == campaign_id)
            result = await session.execute(campaign_query)
            campaign = result.scalar_one_or_none()
            
            if campaign:
                campaign.status = "active"
                campaign.updated_at = datetime.utcnow()
                await session.commit()
                logger.info(f"Campaign {campaign_id} started successfully")
                return True
            
            return False
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error starting campaign {campaign_id}: {e}")
            return False
