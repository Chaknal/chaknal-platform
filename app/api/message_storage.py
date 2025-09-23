"""
Message Storage API
Store and retrieve conversation history in the database
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
import logging
from pydantic import BaseModel

from database.database import get_session
from app.models.message import Message
from app.models.contact import Contact

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/message-storage", tags=["message-storage"])


async def store_outbound_message(
    contact_linkedin_url: str,
    message_text: str,
    dux_message_id: str,
    sender_name: str = "Sercio Campos",
    sender_email: str = "scampos@wallarm.com",
    session: AsyncSession = None
) -> Dict[str, Any]:
    """Store an outbound message in the database"""
    try:
        if not session:
            # This would be called from another function with session
            return {"success": False, "error": "No database session provided"}
        
        # Find or create contact
        result = await session.execute(
            select(Contact).where(Contact.linkedin_url == contact_linkedin_url)
        )
        contact = result.scalar_one_or_none()
        
        if not contact:
            # Create a new contact for Sergio
            contact = Contact(
                contact_id=str(uuid.uuid4()),
                first_name="Sergio",
                last_name="Campos",
                email="sergio.campos@example.com",
                linkedin_url=contact_linkedin_url,
                company="LinkedIn Profile",
                headline="Connection Target",
                phone=None,
                location="Unknown",
                industry="Technology",
                created_at=datetime.utcnow()
            )
            session.add(contact)
            await session.flush()  # Get the contact_id
        
        # Find campaign contact relationship
        from app.models.campaign_contact import CampaignContact
        cc_result = await session.execute(
            select(CampaignContact).where(CampaignContact.contact_id == contact.contact_id)
        )
        campaign_contact = cc_result.scalar_one_or_none()
        
        if not campaign_contact:
            return {"success": False, "error": "Campaign contact relationship not found - message cannot be stored"}
        
        # Create message record
        message = Message(
            message_id=str(uuid.uuid4()),
            campaign_contact_id=campaign_contact.campaign_contact_id,
            direction="sent",
            message_text=message_text,
            linkedin_message_id=dux_message_id,
            thread_url=None,
            status="queued",
            created_at=datetime.utcnow(),
            campaign_id=campaign_contact.campaign_id
        )
        
        session.add(message)
        await session.commit()
        
        return {
            "success": True,
            "data": {
                "message_id": message.message_id,
                "contact_id": contact.contact_id,
                "dux_message_id": dux_message_id,
                "stored_at": message.created_at.isoformat()
            }
        }
        
    except Exception as e:
        if session:
            await session.rollback()
        logger.error(f"Failed to store outbound message: {e}")
        return {"success": False, "error": str(e)}


class StoreMessageRequest(BaseModel):
    contact_linkedin_url: str
    message_text: str
    dux_message_id: str
    sender_name: str = "Sercio Campos"

@router.post("/store-message")
async def store_message_endpoint(
    request: StoreMessageRequest,
    session: AsyncSession = Depends(get_session)
):
    """API endpoint to store a message"""
    result = await store_outbound_message(
        request.contact_linkedin_url, request.message_text, request.dux_message_id, request.sender_name, session=session
    )
    
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=500, detail=result["error"])


@router.get("/conversation/{contact_linkedin_url}")
async def get_conversation_history(
    contact_linkedin_url: str,
    session: AsyncSession = Depends(get_session)
):
    """Get conversation history for a specific LinkedIn profile"""
    try:
        # Find contact by LinkedIn URL
        result = await session.execute(
            select(Contact).where(Contact.linkedin_url == contact_linkedin_url)
        )
        contact = result.scalar_one_or_none()
        
        if not contact:
            return {
                "success": True,
                "data": {
                    "contact": None,
                    "messages": [],
                    "total_messages": 0
                }
            }
        
        # Get messages for this contact
        messages_result = await session.execute(
            select(Message)
            .where(Message.contact_id == contact.contact_id)
            .order_by(Message.created_at)
        )
        messages = messages_result.scalars().all()
        
        # Format response
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "message_id": msg.message_id,
                "direction": msg.direction,
                "message_text": msg.message_text,
                "linkedin_message_id": msg.linkedin_message_id,
                "status": msg.status,
                "created_at": msg.created_at.isoformat(),
                "sender": "Sercio Campos" if msg.direction == "outbound" else "Sergio Campos"
            })
        
        return {
            "success": True,
            "data": {
                "contact": {
                    "contact_id": contact.contact_id,
                    "name": f"{contact.first_name} {contact.last_name}",
                    "linkedin_url": contact.linkedin_url,
                    "company": contact.company_name,
                    "title": contact.title
                },
                "messages": formatted_messages,
                "total_messages": len(formatted_messages)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get conversation for {contact_linkedin_url}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate-incoming")
async def simulate_incoming_message(
    contact_linkedin_url: str = "https://www.linkedin.com/in/sergio-campos-97b9b7362/",
    message_text: str = "Thanks for reaching out Sercio! I'm definitely interested in learning more about Wallarm's solutions. When would be a good time for a call?",
    session: AsyncSession = Depends(get_session)
):
    """Simulate an incoming message from Sergio to Sercio"""
    try:
        # Find or create contact
        result = await session.execute(
            select(Contact).where(Contact.linkedin_url == contact_linkedin_url)
        )
        contact = result.scalar_one_or_none()
        
        if not contact:
            # Create contact for Sergio
            contact = Contact(
                contact_id=str(uuid.uuid4()),
                first_name="Sergio",
                last_name="Campos", 
                email="sergio.campos@example.com",
                linkedin_url=contact_linkedin_url,
                company="LinkedIn Profile",
                headline="Connection Target",
                phone=None,
                location="Unknown",
                industry="Technology",
                created_at=datetime.utcnow()
            )
            session.add(contact)
            await session.flush()
        
        # Find campaign contact relationship
        cc_result = await session.execute(
            select(CampaignContact).where(CampaignContact.contact_id == contact.contact_id)
        )
        campaign_contact = cc_result.scalar_one_or_none()
        
        if not campaign_contact:
            raise HTTPException(status_code=404, detail="Campaign contact relationship not found")
        
        # Create incoming message
        message = Message(
            message_id=str(uuid.uuid4()),
            campaign_contact_id=campaign_contact.campaign_contact_id,
            direction="received",
            message_text=message_text,
            linkedin_message_id=f"linkedin_{int(datetime.utcnow().timestamp())}",
            thread_url=f"https://linkedin.com/messaging/thread/{int(datetime.utcnow().timestamp())}",
            status="received",
            created_at=datetime.utcnow(),
            campaign_id=campaign_contact.campaign_id
        )
        
        session.add(message)
        await session.commit()
        
        return {
            "success": True,
            "data": {
                "message_id": message.message_id,
                "contact_id": contact.contact_id,
                "message_text": message_text,
                "direction": "inbound",
                "created_at": message.created_at.isoformat()
            }
        }
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to simulate incoming message: {e}")
        raise HTTPException(status_code=500, detail=str(e))
