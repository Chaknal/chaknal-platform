"""
LinkedIn Automation Service v2

This service integrates the working DuxSoup wrapper with the existing campaign system
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


class LinkedInAutomationServiceV2:
    """
    Enhanced service for managing LinkedIn automation campaigns using the working DuxSoup wrapper
    """
    
    def __init__(self):
        self.active_campaigns: Dict[str, Any] = {}
        self.dux_wrappers: Dict[str, DuxSoupWrapper] = {}
        self._lock = asyncio.Lock()
    
    async def get_dux_wrapper(self, dux_user_id: str, session: AsyncSession) -> Optional[DuxSoupWrapper]:
        """Get or create a DuxSoup wrapper for a user"""
        async with self._lock:
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
            
            # Create wrapper with working DuxSoup user config
            dux_user_config = DuxSoupUserConfig(
                userid=dux_user.dux_soup_user_id,
                apikey=dux_user.dux_soup_auth_key,
                label=f"{dux_user.first_name} {dux_user.last_name}",
                daily_limits={
                    "max_invites": dux_user.daily_invite_limit or 100,
                    "max_messages": dux_user.daily_message_limit or 50,
                    "max_visits": dux_user.daily_visit_limit or 200
                },
                automation_settings={
                    "auto_connect": dux_user.auto_connect or True,
                    "auto_message": dux_user.auto_message or True,
                    "auto_endorse": dux_user.auto_endorse or False,
                    "auto_follow": dux_user.auto_follow or False
                },
                rate_limit_delay=1.0  # Conservative rate limiting
            )
            
            # Create and initialize wrapper
            wrapper = DuxSoupWrapper(dux_user_config)
            await wrapper.__aenter__()
            self.dux_wrappers[dux_user_id] = wrapper
            
            logger.info(f"Created DuxSoup wrapper for user: {dux_user_id}")
            return wrapper
    
    async def execute_campaign_step(self, campaign_id: str, session: AsyncSession) -> Dict[str, Any]:
        """Execute the next step of a campaign using the working wrapper"""
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
                    CampaignContact.status.in_(["enrolled", "pending", "ready"])
                ).limit(5)  # Process in batches
            )
            contacts = result.scalars().all()
            
            if not contacts:
                return {"success": False, "error": "No contacts ready for action"}
            
            results = []
            for contact in contacts:
                try:
                    # Get contact details
                    result = await session.execute(
                        select(Contact).where(Contact.contact_id == contact.contact_id)
                    )
                    contact_details = result.scalar_one()
                    
                    if not contact_details or not contact_details.linkedin_url:
                        results.append({
                            "contact_id": str(contact.contact_id),
                            "success": False,
                            "error": "No LinkedIn URL available"
                        })
                        continue
                    
                    # Execute appropriate action based on contact status
                    if contact.status == "enrolled":
                        action_result = await self._execute_contact_action(
                            wrapper, contact, campaign, "connect", session
                        )
                    elif contact.status == "pending":
                        action_result = await self._execute_contact_action(
                            wrapper, contact, campaign, "message", session
                        )
                    elif contact.status == "ready":
                        action_result = await self._execute_contact_action(
                            wrapper, contact, campaign, "visit", session
                        )
                    else:
                        action_result = {
                            "contact_id": str(contact.contact_id),
                            "success": False,
                            "error": f"Unknown status: {contact.status}"
                        }
                    
                    results.append(action_result)
                    
                    # Rate limiting between actions
                    await asyncio.sleep(1.0)
                    
                except Exception as e:
                    logger.error(f"Error processing contact {contact.contact_id}: {e}")
                    results.append({
                        "contact_id": str(contact.contact_id),
                        "success": False,
                        "error": str(e)
                    })
            
            # Commit all changes
            await session.commit()
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "processed_contacts": len(contacts),
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
        action_type: str,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Execute a specific action on a contact using the working DuxSoup wrapper"""
        try:
            # Get contact details
            result = await session.execute(
                select(Contact).where(Contact.contact_id == contact.contact_id)
            )
            contact_details = result.scalar_one()
            
            if not contact_details or not contact_details.linkedin_url:
                return {
                    "contact_id": str(contact.contact_id),
                    "success": False,
                    "error": "No LinkedIn URL available"
                }
            
            if action_type == "connect":
                # Send connection request using working wrapper
                response = await wrapper.connect_profile(
                    contact_details.linkedin_url,
                    message_text=self._get_connection_message(campaign, contact_details),
                    campaign_id=str(campaign.campaign_id)
                )
                
                if response.success:
                    # Update contact status
                    await session.execute(
                        update(CampaignContact).where(
                            CampaignContact.campaign_contact_id == contact.campaign_contact_id
                        ).values(
                            status="connection_sent",
                            last_action=datetime.utcnow(),
                            action_result="success",
                            dux_profile_id=response.message_id
                        )
                    )
                    
                    # Log message
                    message = Message(
                        contact_id=contact.contact_id,
                        campaign_id=campaign.campaign_id,
                        message_type="connection_request",
                        content=self._get_connection_message(campaign, contact_details),
                        status="sent",
                        dux_message_id=response.message_id,
                        created_at=datetime.utcnow()
                    )
                    session.add(message)
                    
                    return {
                        "contact_id": str(contact.contact_id),
                        "success": True,
                        "action": "connection_request_sent",
                        "message_id": response.message_id
                    }
                else:
                    return {
                        "contact_id": str(contact.contact_id),
                        "success": False,
                        "error": response.error
                    }
                    
            elif action_type == "message":
                # Send follow-up message using working wrapper
                response = await wrapper.send_message(
                    contact_details.linkedin_url,
                    self._get_followup_message(campaign, contact_details),
                    campaign_id=str(campaign.campaign_id)
                )
                
                if response.success:
                    # Update contact status
                    await session.execute(
                        update(CampaignContact).where(
                            CampaignContact.campaign_contact_id == contact.campaign_contact_id
                        ).values(
                            status="message_sent",
                            last_action=datetime.utcnow(),
                            action_result="success",
                            dux_profile_id=response.message_id
                        )
                    )
                    
                    # Log message
                    message = Message(
                        contact_id=contact.contact_id,
                        campaign_id=campaign.campaign_id,
                        message_type="followup_message",
                        content=self._get_followup_message(campaign, contact_details),
                        status="sent",
                        dux_message_id=response.message_id,
                        created_at=datetime.utcnow()
                    )
                    session.add(message)
                    
                    return {
                        "contact_id": str(contact.contact_id),
                        "success": True,
                        "action": "followup_message_sent",
                        "message_id": response.message_id
                    }
                else:
                    return {
                        "contact_id": str(contact.contact_id),
                        "success": False,
                        "error": response.error
                    }
                    
            elif action_type == "visit":
                # Visit profile using working wrapper
                response = await wrapper.visit_profile(
                    contact_details.linkedin_url,
                    campaign_id=str(campaign.campaign_id)
                )
                
                if response.success:
                    # Update contact status
                    await session.execute(
                        update(CampaignContact).where(
                            CampaignContact.campaign_contact_id == contact.campaign_contact_id
                        ).values(
                            status="profile_visited",
                            last_action=datetime.utcnow(),
                            action_result="success",
                            dux_profile_id=response.message_id
                        )
                    )
                    
                    return {
                        "contact_id": str(contact.contact_id),
                        "success": True,
                        "action": "profile_visited",
                        "message_id": response.message_id
                    }
                else:
                    return {
                        "contact_id": str(contact.contact_id),
                        "success": False,
                        "error": response.error
                    }
                    
            elif action_type == "enroll":
                # Enroll profile using working wrapper
                response = await wrapper.enroll_profile(
                    contact_details.linkedin_url,
                    campaign_id=str(campaign.campaign_id)
                )
                
                if response.success:
                    # Update contact status
                    await session.execute(
                        update(CampaignContact).where(
                            CampaignContact.campaign_contact_id == contact.campaign_contact_id
                        ).values(
                            status="enrolled",
                            last_action=datetime.utcnow(),
                            action_result="success",
                            dux_profile_id=response.message_id
                        )
                    )
                    
                    return {
                        "contact_id": str(contact.contact_id),
                        "success": True,
                        "action": "profile_enrolled",
                        "message_id": response.message_id
                    }
                else:
                    return {
                        "contact_id": str(contact.contact_id),
                        "success": False,
                        "error": response.error
                    }
                    
            else:
                return {
                    "contact_id": str(contact.contact_id),
                    "success": False,
                    "error": f"Unknown action type: {action_type}"
                }
                
        except Exception as e:
            logger.error(f"Error executing contact action: {e}")
            return {
                "contact_id": str(contact.contact_id),
                "success": False,
                "error": str(e)
            }
    
    async def batch_queue_actions(
        self, 
        campaign_id: str, 
        actions: List[Dict[str, Any]], 
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Queue multiple LinkedIn actions in batch using the working wrapper"""
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
            
            # Create DuxSoup commands
            commands = []
            for action in actions:
                command = DuxSoupCommand(
                    command=action["command"],
                    params=action["params"],
                    campaign_id=str(campaign.campaign_id),
                    force=action.get("force", False)
                )
                commands.append(command)
            
            # Execute batch actions
            responses = await wrapper.batch_queue_actions(commands)
            
            # Process results
            results = []
            for i, response in enumerate(responses):
                action = actions[i]
                if response.success:
                    results.append({
                        "action": action,
                        "success": True,
                        "message_id": response.message_id
                    })
                else:
                    results.append({
                        "action": action,
                        "success": False,
                        "error": response.error
                    })
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "total_actions": len(actions),
                "successful_actions": sum(1 for r in results if r["success"]),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error in batch queue actions: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_queue_status(self, dux_user_id: str, session: AsyncSession) -> Dict[str, Any]:
        """Get the current queue status for a DuxSoup user"""
        try:
            wrapper = await self.get_dux_wrapper(dux_user_id, session)
            if not wrapper:
                return {"success": False, "error": "DuxSoup user not configured"}
            
            # Get queue health
            health = await wrapper.get_queue_health()
            
            return {
                "success": True,
                "dux_user_id": dux_user_id,
                "queue_health": health,
                "wrapper_stats": wrapper.get_stats()
            }
            
        except Exception as e:
            logger.error(f"Error getting queue status: {e}")
            return {"success": False, "error": str(e)}
    
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
            
            # Get queue status if DuxSoup user is configured
            queue_status = None
            if campaign.dux_user_id:
                queue_status = await self.get_queue_status(campaign.dux_user_id, session)
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "campaign_name": campaign.name,
                "status": campaign.status,
                "contact_counts": status_counts,
                "total_contacts": len(contacts),
                "recent_activity": [
                    {
                        "message_id": str(msg.message_id),
                        "message_type": msg.message_type,
                        "status": msg.status,
                        "created_at": msg.created_at.isoformat()
                    }
                    for msg in recent_messages
                ],
                "queue_status": queue_status
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
                    status="paused",
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
                    status="active",
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
linkedin_automation_service_v2 = LinkedInAutomationServiceV2()
