"""
Real Conversation API
Retrieve real conversation history from the database
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from database.database import get_session
from app.models.message import Message
from app.models.contact import Contact
from app.models.campaign_contact import CampaignContact
from app.models.campaign import Campaign

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/real-conversation", tags=["real-conversation"])


@router.get("/sergio-sercio")
async def get_sergio_sercio_conversation(session: AsyncSession = Depends(get_session)):
    """Get the real conversation history between Sergio and Sercio"""
    try:
        # Find Sergio's contact
        sergio_linkedin = "https://www.linkedin.com/in/sergio-campos-97b9b7362/"
        result = await session.execute(
            select(Contact).where(Contact.linkedin_url == sergio_linkedin)
        )
        sergio_contact = result.scalar_one_or_none()
        
        if not sergio_contact:
            return {
                "success": False,
                "error": "Sergio contact not found",
                "data": {"messages": [], "contact": None}
            }
        
        # Find campaign contact relationship
        result = await session.execute(
            select(CampaignContact).where(CampaignContact.contact_id == sergio_contact.contact_id)
        )
        campaign_contact = result.scalar_one_or_none()
        
        if not campaign_contact:
            return {
                "success": False,
                "error": "Campaign contact relationship not found",
                "data": {"messages": [], "contact": sergio_contact}
            }
        
        # Get messages for this conversation
        result = await session.execute(
            select(Message)
            .where(Message.campaign_contact_id == campaign_contact.campaign_contact_id)
            .order_by(Message.created_at)
        )
        messages = result.scalars().all()
        
        # Format messages for frontend
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "id": msg.message_id,
                "sender": "user" if msg.direction == "sent" else "contact",
                "sender_name": "Sercio Campos" if msg.direction == "sent" else "Sergio Campos",
                "content": msg.message_text,
                "timestamp": msg.created_at.isoformat(),
                "sequence_step": "database_history",
                "dux_message_id": msg.linkedin_message_id,
                "status": msg.status,
                "direction": msg.direction
            })
        
        return {
            "success": True,
            "data": {
                "contact": {
                    "contact_id": sergio_contact.contact_id,
                    "name": f"{sergio_contact.first_name} {sergio_contact.last_name}",
                    "linkedin_url": sergio_contact.linkedin_url,
                    "company": sergio_contact.company,
                    "headline": sergio_contact.headline,
                    "email": sergio_contact.email
                },
                "campaign": {
                    "campaign_id": campaign_contact.campaign_id,
                    "campaign_contact_id": campaign_contact.campaign_contact_id
                },
                "messages": formatted_messages,
                "total_messages": len(formatted_messages),
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get Sergio-Sercio conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add-message")
async def add_message_to_conversation(
    message_text: str,
    direction: str = "sent",  # "sent" or "received"
    session: AsyncSession = Depends(get_session)
):
    """Add a new message to the Sergio-Sercio conversation"""
    try:
        # Find Sergio's contact and campaign contact
        sergio_linkedin = "https://www.linkedin.com/in/sergio-campos-97b9b7362/"
        result = await session.execute(
            select(Contact).where(Contact.linkedin_url == sergio_linkedin)
        )
        sergio_contact = result.scalar_one_or_none()
        
        if not sergio_contact:
            raise HTTPException(status_code=404, detail="Sergio contact not found")
        
        result = await session.execute(
            select(CampaignContact).where(CampaignContact.contact_id == sergio_contact.contact_id)
        )
        campaign_contact = result.scalar_one_or_none()
        
        if not campaign_contact:
            raise HTTPException(status_code=404, detail="Campaign contact relationship not found")
        
        # Create new message
        import uuid
        message = Message(
            message_id=str(uuid.uuid4()),
            campaign_contact_id=campaign_contact.campaign_contact_id,
            direction=direction,
            message_text=message_text,
            linkedin_message_id=f"real_{int(datetime.utcnow().timestamp())}",
            status="delivered" if direction == "sent" else "received",
            created_at=datetime.utcnow(),
            campaign_id=campaign_contact.campaign_id
        )
        
        session.add(message)
        await session.commit()
        
        return {
            "success": True,
            "data": {
                "message_id": message.message_id,
                "direction": direction,
                "message_text": message_text,
                "created_at": message.created_at.isoformat(),
                "sender": "Sercio Campos" if direction == "sent" else "Sergio Campos"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to add message: {e}")
        raise HTTPException(status_code=500, detail=str(e))
