"""
Messages API endpoints for conversation management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional, Dict, Any
from datetime import datetime

from database.database import get_session
from app.models.message import Message
from app.models.campaign_contact import CampaignContact
from app.models.contact import Contact
from app.models.campaign import Campaign
from app.models.user import User
from app.models.duxsoup_user import DuxSoupUser

router = APIRouter()

@router.get("/messages", tags=["Messages"])
async def get_messages(
    contact_id: Optional[str] = Query(None, description="Filter by contact ID"),
    campaign_id: Optional[str] = Query(None, description="Filter by campaign ID"),
    direction: Optional[str] = Query(None, description="Filter by message direction (sent/received)"),
    limit: int = Query(50, le=200, description="Maximum number of messages to return"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    session: AsyncSession = Depends(get_session)
):
    """Get messages with optional filtering"""
    try:
        # Build query
        query = select(Message).join(CampaignContact, Message.campaign_contact_id == CampaignContact.campaign_contact_id)
        
        # Apply filters
        if contact_id:
            query = query.where(CampaignContact.contact_id == contact_id)
        if campaign_id:
            query = query.where(CampaignContact.campaign_id == campaign_id)
        if direction:
            query = query.where(Message.direction == direction)
            
        # Order by creation date (newest first)
        query = query.order_by(desc(Message.created_at))
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        result = await session.execute(query)
        messages = result.scalars().all()
        
        # Get contact and campaign info for each message
        message_data = []
        for msg in messages:
            # Get campaign contact info
            cc_query = select(CampaignContact).where(CampaignContact.campaign_contact_id == msg.campaign_contact_id)
            cc_result = await session.execute(cc_query)
            campaign_contact = cc_result.scalar_one_or_none()
            
            if campaign_contact:
                # Get contact info
                contact_query = select(Contact).where(Contact.contact_id == campaign_contact.contact_id)
                contact_result = await session.execute(contact_query)
                contact = contact_result.scalar_one_or_none()
                
                # Get campaign info
                campaign_query = select(Campaign).where(Campaign.campaign_id == campaign_contact.campaign_id)
                campaign_result = await session.execute(campaign_query)
                campaign = campaign_result.scalar_one_or_none()
                
                message_data.append({
                    "message_id": str(msg.message_id),
                    "direction": msg.direction,
                    "message_text": msg.message_text,
                    "status": msg.status,
                    "sent_at": msg.sent_at.isoformat() if msg.sent_at else None,
                    "received_at": msg.received_at.isoformat() if msg.received_at else None,
                    "created_at": msg.created_at.isoformat(),
                    "linkedin_message_id": msg.linkedin_message_id,
                    "thread_url": msg.thread_url,
                    "contact": {
                        "contact_id": str(contact.contact_id) if contact else None,
                        "full_name": contact.full_name if contact else None,
                        "company_name": contact.company_name if contact else None,
                        "linkedin_url": contact.linkedin_url if contact else None
                    } if contact else None,
                    "campaign": {
                        "campaign_id": str(campaign.campaign_id) if campaign else None,
                        "name": campaign.name if campaign else None
                    } if campaign else None
                })
        
        return {
            "success": True,
            "messages": message_data,
            "total": len(message_data),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")

@router.get("/messages/conversations", tags=["Messages"])
async def get_conversations(
    limit: int = Query(20, le=100, description="Maximum number of conversations to return"),
    offset: int = Query(0, ge=0, description="Number of conversations to skip"),
    session: AsyncSession = Depends(get_session)
):
    """Get conversation threads grouped by contact"""
    try:
        # Get unique contacts with recent messages
        query = select(Contact).join(CampaignContact, Contact.contact_id == CampaignContact.contact_id).join(Message, CampaignContact.campaign_contact_id == Message.campaign_contact_id).distinct()
        
        result = await session.execute(query)
        contacts = result.scalars().all()
        
        conversations = []
        for contact in contacts:
            # Get latest message for this contact
            latest_msg_query = select(Message).join(CampaignContact, Message.campaign_contact_id == CampaignContact.campaign_contact_id).where(CampaignContact.contact_id == contact.contact_id).order_by(desc(Message.created_at)).limit(1)
            
            latest_result = await session.execute(latest_msg_query)
            latest_message = latest_result.scalar_one_or_none()
            
            # Get message count for this contact (deduplicated)
            count_query = select(Message).join(CampaignContact, Message.campaign_contact_id == CampaignContact.campaign_contact_id).where(CampaignContact.contact_id == contact.contact_id)
            count_result = await session.execute(count_query)
            all_messages = count_result.scalars().all()
            
            # Deduplicate messages for count
            seen_messages = set()
            for msg in all_messages:
                timestamp_key = msg.created_at.replace(microsecond=0)
                message_key = (msg.message_text, msg.direction, timestamp_key)
                seen_messages.add(message_key)
            message_count = len(seen_messages)
            
            # Get user assignment and DuxSoup account info
            assigned_user_info = None
            duxsoup_account_info = None
            
            if latest_message:
                # Get campaign contact info for the latest message
                cc_query = select(CampaignContact).where(CampaignContact.campaign_contact_id == latest_message.campaign_contact_id)
                cc_result = await session.execute(cc_query)
                campaign_contact = cc_result.scalar_one_or_none()
                
                if campaign_contact and campaign_contact.assigned_to:
                    # Get assigned user info
                    user_query = select(User).where(User.id == campaign_contact.assigned_to)
                    user_result = await session.execute(user_query)
                    assigned_user = user_result.scalar_one_or_none()
                    
                    if assigned_user:
                        assigned_user_info = {
                            "user_id": str(assigned_user.id),
                            "email": assigned_user.email
                        }
                        
                        # Get DuxSoup account info
                        dux_query = select(DuxSoupUser).where(DuxSoupUser.email == assigned_user.email)
                        dux_result = await session.execute(dux_query)
                        dux_user = dux_result.scalar_one_or_none()
                        
                        if dux_user:
                            duxsoup_account_info = {
                                "dux_user_id": dux_user.dux_soup_user_id,
                                "dux_user_name": f"{dux_user.first_name} {dux_user.last_name}",
                                "email": dux_user.email
                            }
            
            if latest_message:
                conversations.append({
                    "contact_id": str(contact.contact_id),
                    "contact_name": contact.full_name,
                    "company_name": contact.company_name,
                    "linkedin_url": contact.linkedin_url,
                    "latest_message": {
                        "message_id": str(latest_message.message_id),
                        "direction": latest_message.direction,
                        "message_text": latest_message.message_text,
                        "created_at": latest_message.created_at.isoformat()
                    },
                    "message_count": message_count,
                    "assigned_user": assigned_user_info,
                    "duxsoup_account": duxsoup_account_info
                })
        
        # Sort by latest message date
        conversations.sort(key=lambda x: x["latest_message"]["created_at"], reverse=True)
        
        # Apply pagination
        paginated_conversations = conversations[offset:offset + limit]
        
        return {
            "success": True,
            "conversations": paginated_conversations,
            "total": len(conversations),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversations: {str(e)}")

@router.get("/messages/contact/{contact_id}", tags=["Messages"])
async def get_contact_conversation(
    contact_id: str,
    limit: int = Query(50, le=200, description="Maximum number of messages to return"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    session: AsyncSession = Depends(get_session)
):
    """Get full conversation history for a specific contact"""
    try:
        # Get contact info
        contact_query = select(Contact).where(Contact.contact_id == contact_id)
        contact_result = await session.execute(contact_query)
        contact = contact_result.scalar_one_or_none()
        
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        # Get all messages for this contact, but deduplicate by message content and timestamp
        query = select(Message).join(CampaignContact, Message.campaign_contact_id == CampaignContact.campaign_contact_id).where(CampaignContact.contact_id == contact_id).order_by(desc(Message.created_at))
        
        result = await session.execute(query)
        all_messages = result.scalars().all()
        
        # Deduplicate messages by content and timestamp (within 1 second)
        seen_messages = set()
        unique_messages = []
        
        for msg in all_messages:
            # Create a key based on content, direction, and rounded timestamp
            timestamp_key = msg.created_at.replace(microsecond=0)
            message_key = (msg.message_text, msg.direction, timestamp_key)
            
            if message_key not in seen_messages:
                seen_messages.add(message_key)
                unique_messages.append(msg)
        
        # Apply pagination to deduplicated messages
        paginated_messages = unique_messages[offset:offset + limit]
        
        # Format messages with campaign information
        message_data = []
        for msg in paginated_messages:
            # Get campaign contact info for this message
            cc_query = select(CampaignContact).where(CampaignContact.campaign_contact_id == msg.campaign_contact_id)
            cc_result = await session.execute(cc_query)
            campaign_contact = cc_result.scalar_one_or_none()
            
            campaign_info = None
            if campaign_contact:
                # Get campaign info
                campaign_query = select(Campaign).where(Campaign.campaign_id == campaign_contact.campaign_id)
                campaign_result = await session.execute(campaign_query)
                campaign = campaign_result.scalar_one_or_none()
                
                if campaign:
                    campaign_info = {
                        "campaign_id": str(campaign.campaign_id),
                        "campaign_name": campaign.name,
                        "campaign_status": campaign.status,
                        "campaign_description": campaign.description
                    }
            
            message_data.append({
                "message_id": str(msg.message_id),
                "direction": msg.direction,
                "message_text": msg.message_text,
                "status": msg.status,
                "sent_at": msg.sent_at.isoformat() if msg.sent_at else None,
                "received_at": msg.received_at.isoformat() if msg.received_at else None,
                "created_at": msg.created_at.isoformat(),
                "linkedin_message_id": msg.linkedin_message_id,
                "thread_url": msg.thread_url,
                "campaign": campaign_info
            })
        
        return {
            "success": True,
            "contact": {
                "contact_id": str(contact.contact_id),
                "full_name": contact.full_name,
                "company_name": contact.company_name,
                "linkedin_url": contact.linkedin_url
            },
            "messages": message_data,
            "total": len(unique_messages),
            "limit": limit,
            "offset": offset
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get contact conversation: {str(e)}")
