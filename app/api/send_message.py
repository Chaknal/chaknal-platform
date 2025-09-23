from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

from database.database import get_session
from app.models.contact import Contact
from app.models.campaign_contact import CampaignContact
from app.models.message import Message
from app.models.duxsoup_user import DuxSoupUser
from app.services.duxwrap_new import DuxSoupWrapper

router = APIRouter()

class SendMessageRequest(BaseModel):
    contact_id: str
    message_text: str
    campaign_id: Optional[str] = None

@router.post("/messages/send", tags=["Messages"])
async def send_message(
    request: SendMessageRequest,
    session: AsyncSession = Depends(get_session)
):
    """Send a message to a contact via DuxSoup"""
    try:
        # Get the contact
        contact_result = await session.execute(
            select(Contact).where(Contact.contact_id == request.contact_id)
        )
        contact = contact_result.scalar_one_or_none()
        
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        # Get the campaign contact to find the assigned user
        campaign_contact_query = select(CampaignContact).where(
            CampaignContact.contact_id == request.contact_id
        )
        
        if request.campaign_id:
            campaign_contact_query = campaign_contact_query.where(
                CampaignContact.campaign_id == request.campaign_id
            )
        
        campaign_contact_result = await session.execute(campaign_contact_query)
        campaign_contacts = campaign_contact_result.scalars().all()
        
        if not campaign_contacts:
            raise HTTPException(status_code=400, detail="No campaign contact found for this contact")
        
        # Use the first campaign contact (they should all have the same assigned user)
        campaign_contact = campaign_contacts[0]
        
        if not campaign_contact.assigned_to:
            raise HTTPException(status_code=400, detail="No assigned user found for this contact")
        
        # Get the user to find their email
        from app.models.user import User
        user_result = await session.execute(
            select(User).where(User.id == campaign_contact.assigned_to)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        
        # Get the DuxSoup user by email
        dux_user_result = await session.execute(
            select(DuxSoupUser).where(DuxSoupUser.email == user.email)
        )
        dux_user = dux_user_result.scalar_one_or_none()
        
        if not dux_user:
            raise HTTPException(status_code=400, detail="DuxSoup user not found")
        
        # Create DuxSoup user configuration
        from app.services.duxwrap_new import DuxSoupUser as DuxSoupUserConfig
        dux_user_config = DuxSoupUserConfig(
            userid=dux_user.dux_soup_user_id,
            apikey=dux_user.dux_soup_auth_key,
            label=f"{dux_user.first_name} {dux_user.last_name}"
        )
        
        # Send the message via DuxSoup
        async with DuxSoupWrapper(dux_user_config) as dux_wrapper:
            result = await dux_wrapper.send_message(
                profile_url=contact.linkedin_url,
                message_text=request.message_text,
                campaign_id=campaign_contact.campaign_id
            )
        
        if not result.success:
            raise HTTPException(status_code=500, detail=f"Failed to send message: {result.error or 'Unknown error'}")
        
        # Store the message in our database
        message = Message(
            message_id=str(uuid.uuid4()),
            campaign_contact_id=campaign_contact.campaign_contact_id,
            direction="sent",
            message_text=request.message_text,
            linkedin_message_id=result.message_id,
            thread_url=result.data.get("thread_url") if result.data else None,
            status="delivered",
            sent_at=datetime.utcnow(),
            received_at=None,
            created_at=datetime.utcnow()
        )
        
        session.add(message)
        
        # Update campaign contact status
        campaign_contact.status = "active"
        campaign_contact.updated_at = datetime.utcnow()
        
        await session.commit()
        
        # Get campaign information
        from app.models.campaign import Campaign
        campaign_result = await session.execute(
            select(Campaign).where(Campaign.campaign_id == campaign_contact.campaign_id)
        )
        campaign = campaign_result.scalar_one_or_none()
        
        return {
            "success": True,
            "message": "Message sent successfully",
            "data": {
                "message_id": str(message.message_id),
                "linkedin_message_id": result.message_id,
                "thread_url": result.data.get("thread_url") if result.data else None,
                "campaign": {
                    "campaign_id": campaign.campaign_id if campaign else None,
                    "campaign_name": campaign.name if campaign else None,
                    "campaign_status": campaign.status if campaign else None,
                    "campaign_description": campaign.description if campaign else None
                } if campaign else None,
                "contact": {
                    "contact_id": contact.contact_id,
                    "contact_name": contact.first_name + " " + contact.last_name if contact.first_name and contact.last_name else "Unknown",
                    "company_name": contact.company_name,
                    "linkedin_url": contact.linkedin_url
                },
                "assigned_user": {
                    "user_id": user.id,
                    "email": user.email,
                    "dux_user_name": f"{dux_user.first_name} {dux_user.last_name}"
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

