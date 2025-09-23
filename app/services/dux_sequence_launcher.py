"""
DuxSoup Sequence Launcher Service

This service handles the integration between our contact assignment system
and DuxSoup API for executing LinkedIn automation sequences.
"""

import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import Campaign
from app.models.campaign_contact import CampaignContact
from app.models.contact import Contact
from app.models.duxsoup_user import DuxSoupUser
from app.models.message import Message
from app.services.duxwrap_new import DuxSoupWrapper, DuxSoupUser as DuxSoupUserConfig, DuxSoupCommandType

logger = logging.getLogger(__name__)


class DuxSequenceLauncher:
    """
    Service for launching LinkedIn automation sequences through DuxSoup
    """
    
    def __init__(self):
        self.rate_limit_delay = 2.0  # 2 seconds between requests
    
    async def get_dux_user_config(self, dux_user_id: str, session: AsyncSession) -> Optional[DuxSoupUserConfig]:
        """
        Get DuxSoup user configuration from database
        
        Args:
            dux_user_id: DuxSoup user ID
            session: Database session
            
        Returns:
            DuxSoupUserConfig or None if not found
        """
        try:
            result = await session.execute(
                select(DuxSoupUser).where(DuxSoupUser.dux_soup_user_id == dux_user_id)
            )
            dux_user = result.scalar_one_or_none()
            
            if not dux_user:
                logger.error(f"DuxSoup user not found: {dux_user_id}")
                return None
            
            # Create DuxSoup user configuration
            return DuxSoupUserConfig(
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
                },
                rate_limit_delay=self.rate_limit_delay
            )
            
        except Exception as e:
            logger.error(f"Error getting DuxSoup user config: {e}")
            return None
    
    async def launch_sequence_for_user(
        self, 
        campaign_id: str, 
        user_id: str, 
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Launch LinkedIn automation sequence for all contacts assigned to a user
        
        Args:
            campaign_id: Campaign ID
            user_id: User ID (team member)
            session: Database session
            
        Returns:
            Dictionary with launch results
        """
        try:
            # Get campaign details
            campaign_result = await session.execute(
                select(Campaign).where(Campaign.campaign_id == campaign_id)
            )
            campaign = campaign_result.scalar_one_or_none()
            
            if not campaign:
                return {"success": False, "error": "Campaign not found"}
            
            # Get DuxSoup user configuration
            dux_config = await self.get_dux_user_config(campaign.dux_user_id, session)
            if not dux_config:
                return {"success": False, "error": "DuxSoup user not configured"}
            
            # Get all contacts assigned to this user
            contacts_result = await session.execute(
                select(CampaignContact, Contact).join(
                    Contact, CampaignContact.contact_id == Contact.contact_id
                ).where(
                    CampaignContact.campaign_id == campaign_id,
                    CampaignContact.assigned_to == user_id,
                    CampaignContact.status == "pending"
                )
            )
            assigned_contacts = contacts_result.all()
            
            if not assigned_contacts:
                return {
                    "success": True,
                    "message": "No pending contacts assigned to this user",
                    "launched_count": 0
                }
            
            # Launch sequence using DuxSoup
            results = await self._execute_sequence_with_dux(
                dux_config, campaign, assigned_contacts, session
            )
            
            return {
                "success": True,
                "message": f"Successfully launched sequence for {results['launched_count']} contacts",
                "launched_count": results["launched_count"],
                "results": results["details"]
            }
            
        except Exception as e:
            logger.error(f"Error launching sequence: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_sequence_with_dux(
        self,
        dux_config: DuxSoupUserConfig,
        campaign: Campaign,
        assigned_contacts: List,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Execute the LinkedIn automation sequence using DuxSoup API
        
        Args:
            dux_config: DuxSoup user configuration
            campaign: Campaign object
            assigned_contacts: List of (CampaignContact, Contact) tuples
            session: Database session
            
        Returns:
            Dictionary with execution results
        """
        launched_count = 0
        results = []
        
        async with DuxSoupWrapper(dux_config) as wrapper:
            # First, ensure the campaign exists in DuxSoup
            campaign_creation_result = await self._ensure_campaign_exists(
                wrapper, campaign
            )
            
            if not campaign_creation_result["success"]:
                logger.warning(f"Campaign creation failed: {campaign_creation_result['error']}")
                # Continue anyway - DuxSoup might handle it gracefully
            
            for cc, contact in assigned_contacts:
                try:
                    # Execute sequence steps for this contact
                    contact_result = await self._execute_contact_sequence(
                        wrapper, campaign, cc, contact, session
                    )
                    
                    if contact_result["success"]:
                        launched_count += 1
                        # Mark contact as completed after successful sequence execution
                        await session.execute(
                            update(CampaignContact).where(
                                CampaignContact.campaign_contact_id == cc.campaign_contact_id
                            ).values(
                                status="completed",
                                updated_at=datetime.utcnow()
                            )
                        )
                    
                    results.append(contact_result)
                    
                    # Rate limiting - wait between contacts
                    await asyncio.sleep(self.rate_limit_delay)
                    
                except Exception as e:
                    logger.error(f"Error processing contact {contact.contact_id}: {e}")
                    results.append({
                        "contact_id": contact.contact_id,
                        "success": False,
                        "error": str(e)
                    })
        
        return {
            "launched_count": launched_count,
            "details": results
        }
    
    async def _ensure_campaign_exists(
        self,
        wrapper: DuxSoupWrapper,
        campaign: Campaign
    ) -> Dict[str, Any]:
        """
        Ensure the campaign exists in DuxSoup before queuing actions
        
        Args:
            wrapper: DuxSoup wrapper instance
            campaign: Campaign object
            
        Returns:
            Dictionary with campaign creation results
        """
        try:
            # First, check if campaign already exists
            campaigns_result = await wrapper.get_campaigns()
            
            if campaigns_result.success and campaigns_result.data:
                # Check if our campaign already exists
                existing_campaigns = campaigns_result.data.get("campaigns", [])
                for existing_campaign in existing_campaigns:
                    if (existing_campaign.get("campaign_id") == campaign.campaign_id or 
                        existing_campaign.get("name") == campaign.name):
                        logger.info(f"Campaign {campaign.name} already exists in DuxSoup")
                        return {"success": True, "message": "Campaign already exists"}
            
            # Create the campaign if it doesn't exist
            logger.info(f"Creating campaign {campaign.name} in DuxSoup")
            campaign_result = await wrapper.create_campaign(
                campaign_name=campaign.name,
                campaign_id=campaign.campaign_id,
                description=campaign.description,
                settings={
                    "initial_action": campaign.initial_action,
                    "initial_message": campaign.initial_message,
                    "follow_up_action_1": campaign.follow_up_action_1,
                    "follow_up_message_1": campaign.follow_up_message_1,
                    "follow_up_delay_1": campaign.follow_up_delay_1,
                    "follow_up_action_2": campaign.follow_up_action_2,
                    "follow_up_message_2": campaign.follow_up_message_2,
                    "follow_up_delay_2": campaign.follow_up_delay_2,
                    "follow_up_action_3": campaign.follow_up_action_3,
                    "follow_up_message_3": campaign.follow_up_message_3,
                    "follow_up_delay_3": campaign.follow_up_delay_3
                }
            )
            
            if campaign_result.success:
                logger.info(f"Successfully created campaign {campaign.name} in DuxSoup")
                return {"success": True, "message": "Campaign created successfully"}
            else:
                logger.error(f"Failed to create campaign {campaign.name}: {campaign_result.error}")
                return {"success": False, "error": campaign_result.error}
                
        except Exception as e:
            logger.error(f"Error ensuring campaign exists: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_contact_sequence(
        self,
        wrapper: DuxSoupWrapper,
        campaign: Campaign,
        cc: CampaignContact,
        contact: Contact,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Execute the complete sequence for a single contact
        
        Args:
            wrapper: DuxSoup wrapper instance
            campaign: Campaign object
            cc: CampaignContact object
            contact: Contact object
            session: Database session
            
        Returns:
            Dictionary with contact execution results
        """
        try:
            if not contact.linkedin_url:
                return {
                    "contact_id": contact.contact_id,
                    "success": False,
                    "error": "No LinkedIn URL available"
                }
            
            # Step 1: Visit profile (if enabled)
            if campaign.initial_action == "visit":
                visit_result = await wrapper.visit_profile(
                    profile_url=contact.linkedin_url,
                    campaign_id=campaign.campaign_id
                )
                if not visit_result.success:
                    logger.warning(f"Visit failed for {contact.contact_id}: {visit_result.error}")
            
            # Step 2: Send connection request
            if campaign.initial_action in ["connect", "visit", "connection_request"]:
                connection_message = self._get_connection_message(campaign, contact)
                
                connect_result = await wrapper.connect_profile(
                    profile_url=contact.linkedin_url,
                    message_text=connection_message,
                    campaign_id=campaign.campaign_id
                )
                
                if connect_result.success:
                    # Update contact status to active
                    await session.execute(
                        update(CampaignContact).where(
                            CampaignContact.campaign_contact_id == cc.campaign_contact_id
                        ).values(
                            status="active",
                            sequence_step=1,
                            dux_profile_id=connect_result.data.get("profile_id"),
                            command_executed="connect",
                            command_params={
                                "profile_url": contact.linkedin_url,
                                "message": connection_message
                            },
                            updated_at=datetime.utcnow()
                        )
                    )
                    
                    # Note: Follow-up messages will be scheduled when connection is accepted via webhook
                    
                    return {
                        "contact_id": contact.contact_id,
                        "success": True,
                        "action": "connect",
                        "message": "Connection request sent successfully"
                    }
                else:
                    return {
                        "contact_id": contact.contact_id,
                        "success": False,
                        "error": f"Connection failed: {connect_result.error}"
                    }
            
            # Step 3: Send initial message (if no connection needed)
            elif campaign.initial_action == "message":
                message_text = campaign.initial_message or "Hello! I'd like to connect with you."
                
                message_result = await wrapper.send_message(
                    profile_url=contact.linkedin_url,
                    message_text=message_text,
                    campaign_id=campaign.campaign_id
                )
                
                if message_result.success:
                    await session.execute(
                        update(CampaignContact).where(
                            CampaignContact.campaign_contact_id == cc.campaign_contact_id
                        ).values(
                            status="active",
                            sequence_step=1,
                            command_executed="message",
                            command_params={
                                "profile_url": contact.linkedin_url,
                                "message": message_text
                            },
                            updated_at=datetime.utcnow()
                        )
                    )
                    
                    return {
                        "contact_id": contact.contact_id,
                        "success": True,
                        "action": "message",
                        "message": "Message sent successfully"
                    }
                else:
                    return {
                        "contact_id": contact.contact_id,
                        "success": False,
                        "error": f"Message failed: {message_result.error}"
                    }
            
            else:
                return {
                    "contact_id": contact.contact_id,
                    "success": False,
                    "error": f"Unknown initial action: {campaign.initial_action}"
                }
                
        except Exception as e:
            logger.error(f"Error executing sequence for contact {contact.contact_id}: {e}")
            return {
                "contact_id": contact.contact_id,
                "success": False,
                "error": str(e)
            }
    
    async def _schedule_follow_up_messages(
        self,
        wrapper: DuxSoupWrapper,
        campaign: Campaign,
        cc: CampaignContact,
        contact: Contact,
        session: AsyncSession
    ):
        """
        Schedule follow-up actions for a contact using the new follow-up action fields
        
        Args:
            wrapper: DuxSoup wrapper instance
            campaign: Campaign object
            cc: CampaignContact object
            contact: Contact object
            session: Database session
        """
        try:
            # Schedule follow-up action 1
            if campaign.follow_up_action_1 and campaign.follow_up_action_1 != 'none':
                delay_days_1 = campaign.follow_up_delay_1 or 3
                run_after_1 = datetime.utcnow() + timedelta(days=delay_days_1)

                await self._schedule_single_follow_up_action(
                    wrapper=wrapper,
                    action_type=campaign.follow_up_action_1,
                    message=campaign.follow_up_message_1,
                    subject=campaign.follow_up_subject_1,
                    contact=contact,
                    campaign_id=campaign.campaign_id,
                    run_after=run_after_1,
                    action_number=1
                )

            # Schedule follow-up action 2
            if campaign.follow_up_action_2 and campaign.follow_up_action_2 != 'none':
                delay_days_2 = campaign.follow_up_delay_2 or 7
                run_after_2 = datetime.utcnow() + timedelta(days=delay_days_2)

                await self._schedule_single_follow_up_action(
                    wrapper=wrapper,
                    action_type=campaign.follow_up_action_2,
                    message=campaign.follow_up_message_2,
                    subject=campaign.follow_up_subject_2,
                    contact=contact,
                    campaign_id=campaign.campaign_id,
                    run_after=run_after_2,
                    action_number=2
                )

            # Schedule follow-up action 3
            if campaign.follow_up_action_3 and campaign.follow_up_action_3 != 'none':
                delay_days_3 = campaign.follow_up_delay_3 or 14
                run_after_3 = datetime.utcnow() + timedelta(days=delay_days_3)

                await self._schedule_single_follow_up_action(
                    wrapper=wrapper,
                    action_type=campaign.follow_up_action_3,
                    message=campaign.follow_up_message_3,
                    subject=campaign.follow_up_subject_3,
                    contact=contact,
                    campaign_id=campaign.campaign_id,
                    run_after=run_after_3,
                    action_number=3
                )

            # Update contact with follow-up info
            await session.execute(
                update(CampaignContact).where(
                    CampaignContact.campaign_contact_id == cc.campaign_contact_id
                ).values(
                    run_after=datetime.utcnow() + timedelta(days=campaign.follow_up_delay_1 or 3),
                    updated_at=datetime.utcnow()
                )
            )
                    
        except Exception as e:
            logger.error(f"Error scheduling follow-up actions for contact {contact.contact_id}: {e}")

    async def _schedule_single_follow_up_action(
        self,
        wrapper: DuxSoupWrapper,
        action_type: str,
        message: str,
        subject: str,
        contact: Contact,
        campaign_id: str,
        run_after: datetime,
        action_number: int
    ):
        """
        Schedule a single follow-up action based on the action type
        
        Args:
            wrapper: DuxSoup wrapper instance
            action_type: Type of action (message, connection_request, inmail, profile_view)
            message: Message content (for message/inmail actions)
            subject: Subject line (for inmail actions)
            contact: Contact object
            campaign_id: Campaign ID
            run_after: When to execute the action
            action_number: Action number for logging
        """
        try:
            if action_type == 'message' and message:
                # Send follow-up message
                personalized_message = self._personalize_message(message, contact)
                await wrapper.queue_action(
                    command=DuxSoupCommandType.MESSAGE.value,
                    params={
                        "profile": contact.linkedin_url,
                        "messagetext": personalized_message
                    },
                    campaign_id=campaign_id,
                    run_after=run_after
                )
                logger.info(f"Scheduled follow-up message {action_number} for contact {contact.contact_id}")

            elif action_type == 'connection_request':
                # Send connection request
                connection_message = message or "Hi, I'd like to connect with you."
                personalized_message = self._personalize_message(connection_message, contact)
                await wrapper.queue_action(
                    command=DuxSoupCommandType.CONNECT.value,
                    params={
                        "profile": contact.linkedin_url,
                        "message": personalized_message
                    },
                    campaign_id=campaign_id,
                    run_after=run_after
                )
                logger.info(f"Scheduled connection request {action_number} for contact {contact.contact_id}")

            elif action_type == 'inmail' and message:
                # Send InMail
                personalized_message = self._personalize_message(message, contact)
                inmail_params = {
                    "profile": contact.linkedin_url,
                    "messagetext": personalized_message
                }
                if subject:
                    inmail_params["subject"] = subject
                
                await wrapper.queue_action(
                    command=DuxSoupCommandType.INMAIL.value,
                    params=inmail_params,
                    campaign_id=campaign_id,
                    run_after=run_after
                )
                logger.info(f"Scheduled InMail {action_number} for contact {contact.contact_id}")

            elif action_type == 'profile_view':
                # View profile
                await wrapper.queue_action(
                    command=DuxSoupCommandType.VIEW_PROFILE.value,
                    params={
                        "profile": contact.linkedin_url
                    },
                    campaign_id=campaign_id,
                    run_after=run_after
                )
                logger.info(f"Scheduled profile view {action_number} for contact {contact.contact_id}")

        except Exception as e:
            logger.error(f"Error scheduling follow-up action {action_number} ({action_type}) for contact {contact.contact_id}: {e}")
    
    def _personalize_message(self, message: str, contact: Contact) -> str:
        """
        Personalize a message with contact information
        
        Args:
            message: Message template
            contact: Contact object
            
        Returns:
            Personalized message
        """
        if not message:
            return message
        
        # Replace placeholders with contact data
        personalized = message
        
        if contact.first_name:
            personalized = personalized.replace("{first_name}", contact.first_name)
        if contact.last_name:
            personalized = personalized.replace("{last_name}", contact.last_name)
        if contact.company_name:
            personalized = personalized.replace("{company}", contact.company_name)
        if contact.job_title:
            personalized = personalized.replace("{title}", contact.job_title)
        if contact.full_name:
            personalized = personalized.replace("{full_name}", contact.full_name)
        
        return personalized
    
    def _get_connection_message(self, campaign: Campaign, contact: Contact) -> str:
        """
        Generate personalized connection message
        
        Args:
            campaign: Campaign object
            contact: Contact object
            
        Returns:
            Personalized connection message
        """
        if campaign.initial_message:
            # Use campaign message as template
            message = campaign.initial_message
            
            # Replace placeholders with contact data (DuxSoup format)
            if contact.first_name:
                message = message.replace("{first_name}", contact.first_name)
                message = message.replace("_FN_", contact.first_name)  # DuxSoup format
            if contact.company_name:
                message = message.replace("{company}", contact.company_name)
                message = message.replace("_CN_", contact.company_name)  # DuxSoup format
            if contact.job_title:
                message = message.replace("{title}", contact.job_title)
                message = message.replace("_TI_", contact.job_title)  # DuxSoup format
            if contact.location:
                message = message.replace("_LO_", contact.location)  # DuxSoup format
            if contact.industry:
                message = message.replace("_IN_", contact.industry)  # DuxSoup format
            
            return message
        
        # Default message
        if contact.first_name:
            return f"Hi {contact.first_name}! I'd like to connect with you."
        else:
            return "Hi! I'd like to connect with you."
    
    async def update_contact_status_from_webhook(
        self,
        campaign_id: str,
        contact_id: str,
        status: str,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Update contact status based on DuxSoup webhook data
        
        Args:
            campaign_id: Campaign ID
            contact_id: Contact ID
            status: New status from DuxSoup
            session: Database session
            
        Returns:
            Dictionary with update results
        """
        try:
            # Find all campaign contacts (handle duplicates)
            result = await session.execute(
                select(CampaignContact).where(
                    CampaignContact.campaign_id == campaign_id,
                    CampaignContact.contact_id == contact_id
                )
            )
            campaign_contacts = result.scalars().all()
            
            if not campaign_contacts:
                return {"success": False, "error": "Campaign contact not found"}
            
            # Update status based on DuxSoup webhook
            update_data = {"updated_at": datetime.utcnow()}
            
            if status == "accepted":
                update_data["status"] = "accepted"
                update_data["accepted_at"] = datetime.utcnow()
                
                logger.info(f"Connection accepted for contact {contact_id}, scheduling follow-up messages")
                # Schedule follow-up messages when connection is accepted
                await self._schedule_follow_up_messages_on_acceptance(
                    campaign_id=campaign_id,
                    contact_id=contact_id,
                    session=session
                )
            elif status == "replied":
                update_data["status"] = "responded"
                update_data["replied_at"] = datetime.utcnow()
            elif status == "declined":
                update_data["status"] = "not_accepted"
                logger.info(f"Connection declined for contact {contact_id}, no follow-up messages will be sent")
            elif status == "blacklisted":
                update_data["status"] = "blacklisted"
                update_data["blacklisted_at"] = datetime.utcnow()
            
            # Update all matching campaign contacts
            for cc in campaign_contacts:
                await session.execute(
                    update(CampaignContact).where(
                        CampaignContact.campaign_contact_id == cc.campaign_contact_id
                    ).values(**update_data)
                )
            
            await session.commit()
            
            return {
                "success": True,
                "message": f"Status updated to {status}",
                "contact_id": contact_id
            }
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating contact status: {e}")
            return {"success": False, "error": str(e)}

    async def _schedule_follow_up_messages_on_acceptance(
        self,
        campaign_id: str,
        contact_id: str,
        session: AsyncSession
    ):
        """
        Schedule follow-up messages when a connection is accepted
        
        Args:
            campaign_id: Campaign ID
            contact_id: Contact ID
            session: Database session
        """
        try:
            # Get campaign and contact details
            from sqlalchemy import select
            from app.models.campaign import Campaign
            from app.models.contact import Contact
            from app.models.campaign_contact import CampaignContact
            
            # Get campaign
            campaign_result = await session.execute(
                select(Campaign).where(Campaign.campaign_id == campaign_id)
            )
            campaign = campaign_result.scalar_one_or_none()
            if not campaign:
                logger.error(f"Campaign {campaign_id} not found for follow-up scheduling")
                return
            
            # Get contact
            contact_result = await session.execute(
                select(Contact).where(Contact.contact_id == contact_id)
            )
            contact = contact_result.scalar_one_or_none()
            if not contact:
                logger.error(f"Contact {contact_id} not found for follow-up scheduling")
                return
            
            # Get campaign contact
            cc_result = await session.execute(
                select(CampaignContact).where(
                    CampaignContact.campaign_id == campaign_id,
                    CampaignContact.contact_id == contact_id
                ).order_by(CampaignContact.created_at.desc()).limit(1)
            )
            cc = cc_result.scalar_one_or_none()
            if not cc:
                logger.error(f"Campaign contact not found for follow-up scheduling")
                return
            
            # Get DuxSoup user configuration
            dux_config = await self.get_dux_user_config(campaign.dux_user_id, session)
            if not dux_config:
                logger.error(f"DuxSoup user not configured for campaign {campaign_id}")
                return
            
            # Schedule follow-up messages using DuxSoup wrapper
            from app.services.duxwrap_new import DuxSoupWrapper
            async with DuxSoupWrapper(dux_config) as wrapper:
                await self._schedule_follow_up_messages(
                    wrapper, campaign, cc, contact, session
                )
                
            logger.info(f"Scheduled follow-up messages for accepted connection: {contact_id}")
            
        except Exception as e:
            logger.error(f"Error scheduling follow-up messages on acceptance: {e}")

    async def handle_message_webhook(
        self,
        campaign_id: str,
        contact_id: str,
        message_content: str,
        message_direction: str,
        linkedin_message_id: str = None,
        thread_url: str = None,
        profile_url: str = None,
        session: AsyncSession = None
    ) -> Dict[str, Any]:
        """
        Handle message webhook from DuxSoup
        
        Args:
            campaign_id: Campaign ID
            contact_id: Contact ID
            message_content: The actual message content
            message_direction: "sent" or "received"
            linkedin_message_id: LinkedIn's message ID
            thread_url: LinkedIn thread URL
            profile_url: LinkedIn profile URL
            session: Database session
            
        Returns:
            Dictionary with message handling results
        """
        try:
            # Find all campaign contacts (handle duplicates)
            result = await session.execute(
                select(CampaignContact).where(
                    CampaignContact.campaign_id == campaign_id,
                    CampaignContact.contact_id == contact_id
                )
            )
            campaign_contacts = result.scalars().all()
            
            if not campaign_contacts:
                return {"success": False, "error": "Campaign contact not found"}
            
            # Create message record for each campaign contact
            message_records = []
            for cc in campaign_contacts:
                # Create new message record
                message = Message(
                    message_id=str(uuid.uuid4()),
                    campaign_contact_id=cc.campaign_contact_id,
                    direction=message_direction,
                    message_text=message_content,
                    linkedin_message_id=linkedin_message_id,
                    thread_url=thread_url,
                    status="delivered" if message_direction == "sent" else "received",
                    sent_at=datetime.utcnow() if message_direction == "sent" else None,
                    received_at=datetime.utcnow() if message_direction == "received" else None,
                    created_at=datetime.utcnow()
                )
                session.add(message)
                message_records.append(message)
                
                # Update contact status based on message direction
                update_data = {"updated_at": datetime.utcnow()}
                
                if message_direction == "received":
                    # Contact replied to our message
                    update_data["status"] = "responded"
                    update_data["replied_at"] = datetime.utcnow()
                elif message_direction == "sent":
                    # We sent a message
                    update_data["status"] = "active"
                
                # Update campaign contact
                await session.execute(
                    update(CampaignContact).where(
                        CampaignContact.campaign_contact_id == cc.campaign_contact_id
                    ).values(**update_data)
                )
            
            await session.commit()
            
            logger.info(f"Processed {message_direction} message for contact {contact_id}: {message_content[:50]}...")
            
            return {
                "success": True,
                "message": f"Message {message_direction} successfully processed",
                "data": {
                    "message_count": len(message_records),
                    "message_direction": message_direction,
                    "contact_id": contact_id,
                    "campaign_id": campaign_id
                }
            }
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error handling message webhook: {e}")
            return {"success": False, "error": str(e)}


# Import asyncio at the top level
import asyncio
