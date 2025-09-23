"""
LinkedIn Automation Service

This service integrates the DuxSoup wrapper with the existing campaign system
to provide automated LinkedIn outreach capabilities.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.campaign import Campaign, CampaignStatus
from app.models.contact import Contact
from app.models.campaign_contact import CampaignContact
from app.models.message import Message
from app.models.duxsoup_user import DuxSoupUser
from app.services.duxwrap_new import DuxSoupWrapper, DuxSoupUser as DuxSoupUserConfig, DuxSoupCommand

logger = logging.getLogger(__name__)


class LinkedInAutomationService:
    """
    Service for managing LinkedIn automation campaigns using DuxSoup
    """
    
    def __init__(self):
        self.active_campaigns: Dict[str, Any] = {}
        self.dux_wrappers: Dict[str, DuxSoupWrapper] = {}
    
    async def get_dux_wrapper(self, dux_user_id: str, session: AsyncSession) -> Optional[DuxSoupWrapper]:
        """Get or create a DuxSoup wrapper for a user"""
        if dux_user_id in self.dux_wrappers:
            return self.dux_wrappers[dux_user_id]
        
        # Get user credentials from database
        result = await session.execute(
            select(DuxSoupUser).where(DuxSoupUser.dux_soup_user_id == dux_user_id)
        )
        dux_user = result.scalar_one_or_none()
        
        if not dux_user:
            logger.error(f"DuxSoup user not found: {dux_user_id}")
            return None
        
        # Create wrapper with new DuxSoup user config
        dux_user_config = DuxSoupUserConfig(
            userid=dux_user.dux_soup_user_id,
            apikey=dux_user.dux_soup_auth_key,
            label=f"{dux_user.first_name} {dux_user.last_name}",
            daily_limits={
                "max_invites": 100,
                "max_messages": 50,
                "max_visits": 200
            },
            automation_settings={
                "auto_connect": True,
                "auto_message": True,
                "auto_endorse": False,
                "auto_follow": False
            }
        )
        
        # Create and initialize wrapper
        wrapper = DuxSoupWrapper(dux_user_config)
        await wrapper.__aenter__()
        self.dux_wrappers[dux_user_id] = wrapper
        return wrapper
    
    async def execute_campaign_step(self, campaign_id: str, session: AsyncSession) -> Dict[str, Any]:
        """Execute the next step of a campaign"""
        try:
            # Get campaign
            result = await session.execute(
                select(Campaign).where(Campaign.campaign_id == UUID(campaign_id))
            )
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                return {"success": False, "error": "Campaign not found"}
            
            # Get DuxSoup wrapper
            wrapper = await self.get_dux_wrapper(campaign.dux_user_id, session)
            if not wrapper:
                return {"success": False, "error": "DuxSoup user not configured"}
            
            # Get campaign contacts that need action
            result = await session.execute(
                select(CampaignContact).where(
                    CampaignContact.campaign_id == UUID(campaign_id),
                    CampaignContact.status.in_(["enrolled", "pending"])
                )
            )
            contacts = result.scalars().all()
            
            if not contacts:
                return {"success": False, "error": "No contacts to process"}
            
            # Execute actions based on campaign settings
            results = []
            for contact in contacts[:10]:  # Process max 10 at a time
                try:
                    action_result = await self._execute_contact_action(
                        wrapper, contact, campaign, session
                    )
                    results.append(action_result)
                except Exception as e:
                    logger.error(f"Error processing contact {contact.contact_id}: {e}")
                    results.append({
                        "contact_id": str(contact.contact_id),
                        "success": False,
                        "error": str(e)
                    })
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "processed": len(results),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error executing campaign step: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_contact_action(
        self, 
        wrapper: DuxSoupWrapper, 
        contact: CampaignContact, 
        campaign: Campaign, 
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Execute a specific action for a contact"""
        try:
            # Get contact details
            result = await session.execute(
                select(Contact).where(Contact.contact_id == contact.contact_id)
            )
            contact_details = result.scalar_one_or_none()
            
            if not contact_details:
                return {"contact_id": str(contact.contact_id), "success": False, "error": "Contact not found"}
            
            # Determine action based on campaign settings and contact status
            if contact.status == "enrolled":
                # Send connection request
                if contact_details.linkedin_url:
                    try:
                        response = await wrapper.connect_profile(
                            profile_url=contact_details.linkedin_url,
                            message_text=self._get_connection_message(campaign, contact_details),
                            campaign_id=str(campaign.campaign_id)
                        )
                        
                        if response.success:
                            # Update contact status
                            await session.execute(
                                update(CampaignContact).where(
                                    CampaignContact.campaign_contact_id == contact.campaign_contact_id
                                ).values(
                                    status="pending",
                                    updated_at=datetime.utcnow()
                                )
                            )
                            
                            # Log message
                            message = Message(
                                campaign_contact_id=contact.campaign_contact_id,
                                direction="sent",
                                message_text=response.data.get("message", "Connection request sent") if response.data else "Connection request sent",
                                status="sent",
                                sent_at=datetime.utcnow(),
                                created_at=datetime.utcnow()
                            )
                            session.add(message)
                            
                            await session.commit()
                            
                            return {
                                "contact_id": str(contact.contact_id),
                                "success": True,
                                "action": "connection_request_sent",
                                "message": "Connection request sent successfully"
                            }
                        else:
                            return {
                                "contact_id": str(contact.contact_id),
                                "success": False,
                                "error": response.error or "Failed to send connection request"
                            }
                    except Exception as e:
                        logger.error(f"Error sending connection request: {e}")
                        return {
                            "contact_id": str(contact.contact_id),
                            "success": False,
                            "error": f"Connection request failed: {str(e)}"
                        }
                else:
                    return {
                        "contact_id": str(contact.contact_id),
                        "success": False,
                        "error": "No LinkedIn URL available"
                    }
            
            elif contact.status == "pending":
                # Check if connection was accepted and send follow-up message
                if contact_details.linkedin_url:
                    # For now, we'll assume connection was accepted
                    # In a real implementation, you'd check the actual status
                    try:
                        response = await wrapper.send_message(
                            profile_url=contact_details.linkedin_url,
                            message_text=self._get_followup_message(campaign, contact_details),
                            campaign_id=str(campaign.campaign_id)
                        )
                        
                        if response.success:
                            # Update contact status
                            await session.execute(
                                update(CampaignContact).where(
                                    CampaignContact.campaign_contact_id == contact.campaign_contact_id
                                ).values(
                                    status="messaged",
                                    updated_at=datetime.utcnow()
                                )
                            )
                            
                            # Log message
                            message = Message(
                                campaign_contact_id=contact.campaign_contact_id,
                                direction="sent",
                                message_text=response.data.get("message", "Follow-up message sent") if response.data else "Follow-up message sent",
                                status="sent",
                                sent_at=datetime.utcnow(),
                                created_at=datetime.utcnow()
                            )
                            session.add(message)
                            
                            await session.commit()
                            
                            return {
                                "contact_id": str(contact.contact_id),
                                "success": True,
                                "action": "followup_message_sent",
                                "message": "Follow-up message sent successfully"
                            }
                        else:
                            return {
                                "contact_id": str(contact.contact_id),
                                "success": False,
                                "error": response.error or "Failed to send follow-up message"
                            }
                    except Exception as e:
                        logger.error(f"Error sending follow-up message: {e}")
                        return {
                            "contact_id": str(contact.contact_id),
                            "success": False,
                            "error": f"Follow-up message failed: {str(e)}"
                        }
            
            return {
                "contact_id": str(contact.contact_id),
                "success": False,
                "error": f"Unknown status: {contact.status}"
            }
            
        except Exception as e:
            logger.error(f"Error executing contact action: {e}")
            return {"contact_id": str(contact.contact_id), "success": False, "error": str(e)}
    
    def _get_connection_message(self, campaign: Campaign, contact: Contact) -> str:
        """Get personalized connection message for a contact"""
        if not campaign.settings or "message_templates" not in campaign.settings:
            return "Hi! I'd like to connect with you on LinkedIn."
        
        template = campaign.settings["message_templates"][0]
        
        # Replace placeholders
        message = template.replace("{first_name}", contact.first_name or "there")
        message = message.replace("{company}", contact.company or "your company")
        
        return message
    
    def _get_followup_message(self, campaign: Campaign, contact: Contact) -> str:
        """Get personalized follow-up message for a contact"""
        if not campaign.settings or "followup_templates" not in campaign.settings:
            return "Thanks for connecting! I'd love to learn more about your work."
        
        template = campaign.settings["followup_templates"][0]
        
        # Replace placeholders
        message = template.replace("{first_name}", contact.first_name or "there")
        message = message.replace("{company}", contact.company or "your company")
        
        return message
    
    async def get_campaign_automation_status(self, campaign_id: str, session: AsyncSession) -> Dict[str, Any]:
        """Get the automation status of a campaign"""
        try:
            # Get campaign
            result = await session.execute(
                select(Campaign).where(Campaign.campaign_id == UUID(campaign_id))
            )
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                return {"success": False, "error": "Campaign not found"}
            
            # Get contact counts by status
            result = await session.execute(
                select(CampaignContact.status, CampaignContact.contact_id).where(
                    CampaignContact.campaign_id == UUID(campaign_id)
                )
            )
            contacts = result.fetchall()
            
            status_counts = {}
            for status, _ in contacts:
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Get recent activity
            result = await session.execute(
                select(Message).join(CampaignContact).where(
                    CampaignContact.campaign_id == UUID(campaign_id)
                ).order_by(Message.created_at.desc()).limit(10)
            )
            recent_messages = result.scalars().all()
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "campaign_name": campaign.name,
                "status": campaign.status.value,
                "contact_counts": status_counts,
                "total_contacts": len(contacts),
                "recent_activity": [
                    {
                        "message_id": str(msg.message_id),
                        "direction": msg.direction,
                        "status": msg.status,
                        "created_at": msg.created_at.isoformat()
                    }
                    for msg in recent_messages
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting campaign automation status: {e}")
            return {"success": False, "error": str(e)}
    
    async def pause_campaign(self, campaign_id: str, session: AsyncSession) -> Dict[str, Any]:
        """Pause a campaign automation"""
        try:
            await session.execute(
                update(Campaign).where(
                    Campaign.campaign_id == UUID(campaign_id)
                ).values(
                    status=CampaignStatus.PAUSED,
                    updated_at=datetime.utcnow()
                )
            )
            await session.commit()
            
            return {"success": True, "message": "Campaign paused successfully"}
            
        except Exception as e:
            logger.error(f"Error pausing campaign: {e}")
            return {"success": False, "error": str(e)}
    
    async def resume_campaign(self, campaign_id: str, session: AsyncSession) -> Dict[str, Any]:
        """Resume a paused campaign automation"""
        try:
            await session.execute(
                update(Campaign).where(
                    Campaign.campaign_id == UUID(campaign_id)
                ).values(
                    status=CampaignStatus.ACTIVE,
                    updated_at=datetime.utcnow()
                )
            )
            await session.commit()
            
            return {"success": True, "message": "Campaign resumed successfully"}
            
        except Exception as e:
            logger.error(f"Error resuming campaign: {e}")
            return {"success": False, "error": str(e)}
    
    async def cleanup_wrappers(self):
        """Clean up all DuxSoup wrapper sessions"""
        try:
            for user_id, wrapper in self.dux_wrappers.items():
                try:
                    await wrapper.__aexit__(None, None, None)
                    logger.info(f"Cleaned up wrapper for user: {user_id}")
                except Exception as e:
                    logger.error(f"Error cleaning up wrapper for user {user_id}: {e}")
            
            self.dux_wrappers.clear()
            logger.info("All DuxSoup wrappers cleaned up")
            
        except Exception as e:
            logger.error(f"Error during wrapper cleanup: {e}")


# Global instance
linkedin_automation_service = LinkedInAutomationService()
