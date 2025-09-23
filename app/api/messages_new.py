"""
Messages API Router - Rebuilt from scratch
Simple, clean implementation of message endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter()

# Pydantic models
class MessageCreate(BaseModel):
    contact_id: str
    campaign_id: Optional[str] = None
    subject: str
    content: str
    message_type: str = "email"  # email, linkedin, sms
    scheduled_at: Optional[datetime] = None

class MessageResponse(BaseModel):
    id: str
    contact_id: str
    campaign_id: Optional[str] = None
    subject: str
    content: str
    message_type: str
    status: str = "pending"  # pending, sent, delivered, failed
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

# In-memory storage for now
messages_db = []

@router.get("/messages/", response_model=List[MessageResponse])
async def get_messages():
    """Get all messages"""
    return messages_db

@router.post("/messages/", response_model=MessageResponse)
async def create_message(message: MessageCreate):
    """Create a new message"""
    message_id = str(uuid.uuid4())
    now = datetime.now()
    
    new_message = MessageResponse(
        id=message_id,
        contact_id=message.contact_id,
        campaign_id=message.campaign_id,
        subject=message.subject,
        content=message.content,
        message_type=message.message_type,
        status="pending",
        scheduled_at=message.scheduled_at,
        sent_at=None,
        created_at=now,
        updated_at=now
    )
    
    messages_db.append(new_message)
    return new_message

@router.get("/messages/{message_id}", response_model=MessageResponse)
async def get_message(message_id: str):
    """Get a specific message by ID"""
    for message in messages_db:
        if message.id == message_id:
            return message
    
    raise HTTPException(status_code=404, detail="Message not found")

@router.put("/messages/{message_id}", response_model=MessageResponse)
async def update_message(message_id: str, message: MessageCreate):
    """Update a message"""
    for i, existing_message in enumerate(messages_db):
        if existing_message.id == message_id:
            updated_message = MessageResponse(
                id=message_id,
                contact_id=message.contact_id,
                campaign_id=message.campaign_id,
                subject=message.subject,
                content=message.content,
                message_type=message.message_type,
                status=existing_message.status,
                scheduled_at=message.scheduled_at,
                sent_at=existing_message.sent_at,
                created_at=existing_message.created_at,
                updated_at=datetime.now()
            )
            messages_db[i] = updated_message
            return updated_message
    
    raise HTTPException(status_code=404, detail="Message not found")

@router.delete("/messages/{message_id}")
async def delete_message(message_id: str):
    """Delete a message"""
    for i, message in enumerate(messages_db):
        if message.id == message_id:
            del messages_db[i]
            return {"message": "Message deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Message not found")

@router.post("/send-message")
async def send_message(message_id: str):
    """Send a message immediately"""
    for i, message in enumerate(messages_db):
        if message.id == message_id:
            if message.status == "sent":
                raise HTTPException(status_code=400, detail="Message already sent")
            
            # Simulate sending
            messages_db[i].status = "sent"
            messages_db[i].sent_at = datetime.now()
            messages_db[i].updated_at = datetime.now()
            
            return {
                "message_id": message_id,
                "status": "sent",
                "sent_at": messages_db[i].sent_at
            }
    
    raise HTTPException(status_code=404, detail="Message not found")

@router.get("/message-monitor")
async def get_message_monitor():
    """Get message monitoring data"""
    total_messages = len(messages_db)
    pending_messages = len([m for m in messages_db if m.status == "pending"])
    sent_messages = len([m for m in messages_db if m.status == "sent"])
    failed_messages = len([m for m in messages_db if m.status == "failed"])
    
    return {
        "total_messages": total_messages,
        "pending_messages": pending_messages,
        "sent_messages": sent_messages,
        "failed_messages": failed_messages,
        "success_rate": (sent_messages / total_messages * 100) if total_messages > 0 else 0
    }
