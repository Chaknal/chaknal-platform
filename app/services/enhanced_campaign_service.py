"""
Enhanced Campaign Service with Proper DuxSoup Scheduling
Integrates with existing campaign system and frontend
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.campaign import Campaign
from app.models.campaign_contact import CampaignContact
from app.models.contact import Contact
from app.models.duxsoup_user import DuxSoupUser
from app.services.enhanced_duxwrap import EnhancedDuxWrap

logger = logging.getLogger(__name__)


class EnhancedCampaignService:
    """
    Enhanced campaign service that properly schedules DuxSoup sequences
    """
    
    def __init__(self):
        self.rate_limit_delay = 1.0  # 1 second between requests
    
    async def create_and_schedule_campaign(
        self,
        campaign: Campaign,
        contacts: List[Contact],
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Create campaign in database and schedule all DuxSoup sequences
        
        Args:
            campaign: Campaign object from database
            contacts: List of contacts to include in campaign
            session: Database session
            
        Returns:
            Result dictionary with success status and details
        """
        
        try:
            # Get DuxSoup user configuration
            dux_config = await self._get_dux_config(campaign.dux_user_id, session)
            if not dux_config:
                return {
                    "success": False,
                    "error": f"DuxSoup user {campaign.dux_user_id} not configured"
                }
            
            # Initialize enhanced DuxSoup wrapper
            dux = EnhancedDuxWrap(
                api_key=dux_config.api_key,
                user_id=dux_config.user_id
            )
            
            # Schedule campaign sequences
            results = await self._schedule_campaign_sequences(
                dux, campaign, contacts
            )
            
            return {
                "success": True,
                "campaign_id": str(campaign.campaign_id),
                "scheduled_messages": results["total_scheduled"],
                "contacts_processed": len(contacts),
                "details": results["details"]
            }
            
        except Exception as e:
            logger.error(f"Error creating and scheduling campaign: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_dux_config(self, dux_user_id: str, session: AsyncSession) -> Optional[Dict[str, Any]]:
        """Get DuxSoup user configuration from database"""
        try:
            query = select(DuxSoupUser).where(DuxSoupUser.user_id == dux_user_id)
            result = await session.execute(query)
            dux_user = result.scalar_one_or_none()
            
            if dux_user:
                return {
                    "api_key": dux_user.api_key,
                    "user_id": dux_user.dux_user_id
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting DuxSoup config: {e}")
            return None
    
    async def _schedule_campaign_sequences(
        self,
        dux: EnhancedDuxWrap,
        campaign: Campaign,
        contacts: List[Contact]
    ) -> Dict[str, Any]:
        """
        Schedule all campaign sequences in DuxSoup
        
        Args:
            dux: Enhanced DuxSoup wrapper
            campaign: Campaign object
            contacts: List of contacts
            
        Returns:
            Results dictionary
        """
        
        total_scheduled = 0
        details = []
        
        # Calculate schedule times based on campaign settings
        schedule_times = self._calculate_schedule_times(campaign)
        
        for contact in contacts:
            contact_results = []
            
            # Schedule initial action
            initial_result = await self._schedule_initial_action(
                dux, campaign, contact, schedule_times[0]
            )
            if initial_result["success"]:
                total_scheduled += 1
                contact_results.append(initial_result)
            
            # Schedule follow-up actions
            for i, follow_up_action in enumerate(campaign.follow_up_actions or [], 1):
                if i < len(schedule_times):
                    follow_up_result = await self._schedule_follow_up_action(
                        dux, campaign, contact, follow_up_action, schedule_times[i], i
                    )
                    if follow_up_result["success"]:
                        total_scheduled += 1
                        contact_results.append(follow_up_result)
            
            details.append({
                "contact_id": str(contact.contact_id),
                "contact_name": f"{contact.first_name} {contact.last_name}",
                "scheduled_actions": len(contact_results),
                "results": contact_results
            })
        
        return {
            "total_scheduled": total_scheduled,
            "details": details
        }
    
    def _calculate_schedule_times(self, campaign: Campaign) -> List[datetime]:
        """
        Calculate schedule times for campaign actions
        
        Args:
            campaign: Campaign object with scheduling settings
            
        Returns:
            List of datetime objects for each action
        """
        
        start_time = campaign.scheduled_start or datetime.now()
        schedule_times = [start_time]
        
        # Calculate follow-up times based on delay_days
        delay_days = campaign.delay_days or 1
        
        for i in range(1, 4):  # Max 3 follow-ups
            next_time = start_time + timedelta(days=delay_days * i)
            
            # Add random delay if enabled
            if campaign.random_delay:
                import random
                random_hours = random.randint(0, 8)  # 0-8 hours random
                next_time += timedelta(hours=random_hours)
            
            schedule_times.append(next_time)
        
        return schedule_times
    
    async def _schedule_initial_action(
        self,
        dux: EnhancedDuxWrap,
        campaign: Campaign,
        contact: Contact,
        scheduled_time: datetime
    ) -> Dict[str, Any]:
        """
        Schedule the initial action (InMail, connection request, etc.)
        
        Args:
            dux: Enhanced DuxSoup wrapper
            campaign: Campaign object
            contact: Contact object
            scheduled_time: When to execute the action
            
        Returns:
            Result dictionary
        """
        
        try:
            campaign_id = str(campaign.campaign_id)
            profile_url = contact.linkedin_url
            
            if not profile_url:
                return {
                    "success": False,
                    "error": f"No LinkedIn URL for contact {contact.contact_id}"
                }
            
            # Personalize message
            message_text = self._personalize_message(
                campaign.initial_message or "", contact
            )
            
            # Schedule based on action type
            if campaign.initial_action == "inmail":
                subject = self._personalize_message(
                    campaign.initial_subject or "", contact
                )
                
                result = dux.schedule_inmail(
                    profile_url=profile_url,
                    subject=subject,
                    message_text=message_text,
                    campaign_id=campaign_id,
                    scheduled_time=scheduled_time
                )
                
            elif campaign.initial_action == "connection_request":
                result = dux.schedule_connection_request(
                    profile_url=profile_url,
                    message_text=message_text,
                    campaign_id=campaign_id,
                    scheduled_time=scheduled_time
                )
                
            else:  # Default to message
                result = dux.schedule_message(
                    profile_url=profile_url,
                    message_text=message_text,
                    campaign_id=campaign_id,
                    scheduled_time=scheduled_time
                )
            
            return {
                "success": "messageid" in result,
                "action": campaign.initial_action,
                "scheduled_time": scheduled_time.isoformat(),
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _schedule_follow_up_action(
        self,
        dux: EnhancedDuxWrap,
        campaign: Campaign,
        contact: Contact,
        follow_up_action: Dict[str, Any],
        scheduled_time: datetime,
        action_number: int
    ) -> Dict[str, Any]:
        """
        Schedule a follow-up action
        
        Args:
            dux: Enhanced DuxSoup wrapper
            campaign: Campaign object
            contact: Contact object
            follow_up_action: Follow-up action configuration
            scheduled_time: When to execute the action
            action_number: Action number (1, 2, 3, etc.)
            
        Returns:
            Result dictionary
        """
        
        try:
            campaign_id = str(campaign.campaign_id)
            profile_url = contact.linkedin_url
            
            if not profile_url:
                return {
                    "success": False,
                    "error": f"No LinkedIn URL for contact {contact.contact_id}"
                }
            
            # Get action details (these would come from your follow_up_actions array)
            action_type = follow_up_action.get("action", "message")
            message_text = self._personalize_message(
                follow_up_action.get("message", ""), contact
            )
            
            # Schedule based on action type
            if action_type == "inmail":
                subject = self._personalize_message(
                    follow_up_action.get("subject", ""), contact
                )
                
                result = dux.schedule_inmail(
                    profile_url=profile_url,
                    subject=subject,
                    message_text=message_text,
                    campaign_id=campaign_id,
                    scheduled_time=scheduled_time
                )
                
            elif action_type == "connection_request":
                result = dux.schedule_connection_request(
                    profile_url=profile_url,
                    message_text=message_text,
                    campaign_id=campaign_id,
                    scheduled_time=scheduled_time
                )
                
            else:  # Default to message
                result = dux.schedule_message(
                    profile_url=profile_url,
                    message_text=message_text,
                    campaign_id=campaign_id,
                    scheduled_time=scheduled_time
                )
            
            return {
                "success": "messageid" in result,
                "action": action_type,
                "action_number": action_number,
                "scheduled_time": scheduled_time.isoformat(),
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _personalize_message(self, message_template: str, contact: Contact) -> str:
        """
        Personalize message template with contact information
        
        Args:
            message_template: Message template with placeholders
            contact: Contact object
            
        Returns:
            Personalized message
        """
        
        if not message_template:
            return ""
        
        # Replace placeholders with contact information
        personalized = message_template.replace("{first_name}", contact.first_name or "")
        personalized = personalized.replace("{last_name}", contact.last_name or "")
        personalized = personalized.replace("{company}", contact.company or "")
        personalized = personalized.replace("{title}", contact.title or "")
        personalized = personalized.replace("{industry}", contact.industry or "")
        
        return personalized
