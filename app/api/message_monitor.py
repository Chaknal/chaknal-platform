"""
Message Monitor API
Monitor incoming messages from DuxSoup webhooks and display them in real-time
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from database.database import get_session
from app.models.message import Message
from app.models.webhook_event import WebhookEvent
from app.models.contact import Contact
from app.models.campaign_contact import CampaignContact

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/message-monitor", tags=["message-monitor"])


@router.get("/recent-messages")
async def get_recent_messages(
    hours: int = 24,
    limit: int = 50,
    session: AsyncSession = Depends(get_session)
):
    """Get recent messages from the last N hours"""
    try:
        # Calculate time threshold
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        # Get recent messages
        result = await session.execute(
            select(Message)
            .where(Message.created_at >= time_threshold)
            .order_by(desc(Message.created_at))
            .limit(limit)
        )
        messages = result.scalars().all()
        
        # Format messages for frontend
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "message_id": msg.message_id,
                "contact_id": msg.contact_id,
                "campaign_id": msg.campaign_id,
                "direction": msg.direction,
                "message_text": msg.message_text,
                "linkedin_message_id": msg.linkedin_message_id,
                "thread_url": msg.thread_url,
                "status": msg.status,
                "created_at": msg.created_at.isoformat(),
                "updated_at": msg.updated_at.isoformat() if msg.updated_at else None
            })
        
        return {
            "success": True,
            "data": {
                "messages": formatted_messages,
                "total_count": len(formatted_messages),
                "time_range_hours": hours
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get recent messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent-webhooks")
async def get_recent_webhooks(
    hours: int = 24,
    limit: int = 50,
    session: AsyncSession = Depends(get_session)
):
    """Get recent webhook events from the last N hours"""
    try:
        # Calculate time threshold
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        # Get recent webhook events
        result = await session.execute(
            select(WebhookEvent)
            .where(WebhookEvent.created_at >= time_threshold)
            .order_by(desc(WebhookEvent.created_at))
            .limit(limit)
        )
        webhooks = result.scalars().all()
        
        # Format webhooks for frontend
        formatted_webhooks = []
        for webhook in webhooks:
            formatted_webhooks.append({
                "event_id": webhook.event_id,
                "event_type": webhook.event_type,
                "event_name": webhook.event_name,
                "payload": webhook.payload,
                "processed": webhook.processed,
                "contact_id": webhook.contact_id,
                "campaign_id": webhook.campaign_id,
                "created_at": webhook.created_at.isoformat()
            })
        
        return {
            "success": True,
            "data": {
                "webhooks": formatted_webhooks,
                "total_count": len(formatted_webhooks),
                "time_range_hours": hours
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get recent webhooks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversation/{contact_linkedin_url}")
async def get_conversation_by_linkedin_url(
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
                "success": False,
                "error": "Contact not found",
                "data": {"messages": [], "contact": None}
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
                "thread_url": msg.thread_url,
                "status": msg.status,
                "created_at": msg.created_at.isoformat(),
                "sender": "user" if msg.direction == "outbound" else "contact"
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


@router.get("/monitoring-dashboard")
async def get_monitoring_dashboard(session: AsyncSession = Depends(get_session)):
    """Get comprehensive monitoring dashboard data"""
    try:
        # Get recent activity counts
        time_24h = datetime.utcnow() - timedelta(hours=24)
        time_1h = datetime.utcnow() - timedelta(hours=1)
        
        # Count recent messages
        messages_24h_result = await session.execute(
            select(Message).where(Message.created_at >= time_24h)
        )
        messages_24h = len(messages_24h_result.scalars().all())
        
        messages_1h_result = await session.execute(
            select(Message).where(Message.created_at >= time_1h)
        )
        messages_1h = len(messages_1h_result.scalars().all())
        
        # Count recent webhooks
        webhooks_24h_result = await session.execute(
            select(WebhookEvent).where(WebhookEvent.created_at >= time_24h)
        )
        webhooks_24h = len(webhooks_24h_result.scalars().all())
        
        webhooks_1h_result = await session.execute(
            select(WebhookEvent).where(WebhookEvent.created_at >= time_1h)
        )
        webhooks_1h = len(webhooks_1h_result.scalars().all())
        
        # Get recent incoming messages (replies)
        incoming_result = await session.execute(
            select(Message)
            .where(
                Message.direction == "inbound",
                Message.created_at >= time_24h
            )
            .order_by(desc(Message.created_at))
            .limit(10)
        )
        recent_incoming = incoming_result.scalars().all()
        
        formatted_incoming = []
        for msg in recent_incoming:
            # Get contact info
            contact_result = await session.execute(
                select(Contact).where(Contact.contact_id == msg.contact_id)
            )
            contact = contact_result.scalar_one_or_none()
            
            formatted_incoming.append({
                "message_id": msg.message_id,
                "contact_name": f"{contact.first_name} {contact.last_name}" if contact else "Unknown",
                "contact_linkedin": contact.linkedin_url if contact else None,
                "message_text": msg.message_text[:100] + "..." if len(msg.message_text) > 100 else msg.message_text,
                "created_at": msg.created_at.isoformat(),
                "linkedin_message_id": msg.linkedin_message_id
            })
        
        return {
            "success": True,
            "data": {
                "stats": {
                    "messages_24h": messages_24h,
                    "messages_1h": messages_1h,
                    "webhooks_24h": webhooks_24h,
                    "webhooks_1h": webhooks_1h,
                    "incoming_messages_24h": len(formatted_incoming)
                },
                "recent_incoming_messages": formatted_incoming,
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get monitoring dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate-incoming-message")
async def simulate_incoming_message(
    linkedin_url: str = "https://www.linkedin.com/in/sergio-campos-97b9b7362/",
    message_text: str = "Thanks for reaching out Sercio! I'm definitely interested in learning more about Wallarm's API protection solutions.",
    session: AsyncSession = Depends(get_session)
):
    """Simulate an incoming message for testing purposes"""
    try:
        # This simulates what would happen when Sergio replies to Sercio
        webhook_data = {
            "event_type": "message",
            "profile_url": linkedin_url,
            "message_content": message_text,
            "message_direction": "inbound",
            "linkedin_message_id": f"sim_{int(datetime.utcnow().timestamp())}",
            "thread_url": f"https://linkedin.com/messaging/thread/{int(datetime.utcnow().timestamp())}",
            "payload": {
                "action": "MESSAGE",
                "status": "received",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        # Process through webhook handler
        from app.api.contact_assignment import handle_dux_status_update
        result = await handle_dux_status_update(webhook_data, session)
        
        return {
            "success": True,
            "message": "Simulated incoming message processed",
            "data": {
                "simulated_message": message_text,
                "linkedin_url": linkedin_url,
                "webhook_result": result
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to simulate incoming message: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to simulate incoming message"
        }
