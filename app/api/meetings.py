"""
Meetings API
Manage meeting bookings, scheduling, and outcomes
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_, or_
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid
import logging

from database.database import get_session
from app.models.meeting import Meeting
from app.models.contact import Contact
from app.models.campaign_contact import CampaignContact
from app.models.message import Message
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/meetings", tags=["meetings"])


class BookMeetingRequest(BaseModel):
    contact_linkedin_url: str
    meeting_type: str = "call"
    scheduled_date: Optional[str] = None  # ISO datetime string
    duration_minutes: int = 30
    agenda: Optional[str] = None
    booking_notes: Optional[str] = None
    booking_message_id: Optional[str] = None


class UpdateMeetingRequest(BaseModel):
    meeting_status: Optional[str] = None
    actual_date: Optional[str] = None
    outcome: Optional[str] = None
    outcome_notes: Optional[str] = None
    next_action: Optional[str] = None
    follow_up_date: Optional[str] = None
    deal_value: Optional[str] = None


@router.post("/book")
async def book_meeting(
    request: BookMeetingRequest,
    session: AsyncSession = Depends(get_session)
):
    """Book a meeting with a contact"""
    try:
        # Find contact by LinkedIn URL
        result = await session.execute(
            select(Contact).where(Contact.linkedin_url == request.contact_linkedin_url)
        )
        contact = result.scalar_one_or_none()
        
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        # Find campaign contact relationship
        cc_result = await session.execute(
            select(CampaignContact).where(CampaignContact.contact_id == contact.contact_id)
        )
        campaign_contact = cc_result.scalar_one_or_none()
        
        if not campaign_contact:
            raise HTTPException(status_code=404, detail="Campaign contact relationship not found")
        
        # Create meeting record
        meeting = Meeting(
            meeting_id=str(uuid.uuid4()),
            campaign_contact_id=campaign_contact.campaign_contact_id,
            contact_id=contact.contact_id,
            campaign_id=campaign_contact.campaign_id,
            meeting_type=request.meeting_type,
            meeting_status="scheduled",
            scheduled_date=datetime.fromisoformat(request.scheduled_date.replace('Z', '+00:00')) if request.scheduled_date else None,
            duration_minutes=request.duration_minutes,
            booking_source="manual_entry",
            booking_message_id=request.booking_message_id,
            booking_notes=request.booking_notes,
            agenda=request.agenda,
            contact_title_at_meeting=contact.headline,
            contact_company_at_meeting=contact.company,
            created_at=datetime.utcnow()
        )
        
        session.add(meeting)
        await session.commit()
        
        return {
            "success": True,
            "data": meeting.to_dict(),
            "message": f"Meeting booked with {contact.first_name} {contact.last_name}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to book meeting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contact/{contact_linkedin_url}")
async def get_contact_meetings(
    contact_linkedin_url: str,
    session: AsyncSession = Depends(get_session)
):
    """Get all meetings for a specific contact"""
    try:
        # Find contact
        result = await session.execute(
            select(Contact).where(Contact.linkedin_url == contact_linkedin_url)
        )
        contact = result.scalar_one_or_none()
        
        if not contact:
            return {"success": True, "data": {"meetings": [], "contact": None}}
        
        # Get meetings for this contact
        meetings_result = await session.execute(
            select(Meeting)
            .where(Meeting.contact_id == contact.contact_id)
            .order_by(desc(Meeting.scheduled_date))
        )
        meetings = meetings_result.scalars().all()
        
        return {
            "success": True,
            "data": {
                "contact": {
                    "contact_id": contact.contact_id,
                    "name": f"{contact.first_name} {contact.last_name}",
                    "linkedin_url": contact.linkedin_url,
                    "company": contact.company,
                    "title": contact.headline
                },
                "meetings": [meeting.to_dict() for meeting in meetings],
                "total_meetings": len(meetings)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get meetings for contact: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{meeting_id}")
async def update_meeting(
    meeting_id: str,
    request: UpdateMeetingRequest,
    session: AsyncSession = Depends(get_session)
):
    """Update meeting details and outcome"""
    try:
        # Find meeting
        result = await session.execute(
            select(Meeting).where(Meeting.meeting_id == meeting_id)
        )
        meeting = result.scalar_one_or_none()
        
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        # Update fields
        if request.meeting_status:
            meeting.meeting_status = request.meeting_status
        if request.actual_date:
            meeting.actual_date = datetime.fromisoformat(request.actual_date.replace('Z', '+00:00'))
        if request.outcome:
            meeting.outcome = request.outcome
        if request.outcome_notes:
            meeting.outcome_notes = request.outcome_notes
        if request.next_action:
            meeting.next_action = request.next_action
        if request.follow_up_date:
            meeting.follow_up_date = datetime.fromisoformat(request.follow_up_date.replace('Z', '+00:00'))
        if request.deal_value:
            meeting.deal_value = request.deal_value
        
        meeting.updated_at = datetime.utcnow()
        
        await session.commit()
        
        return {
            "success": True,
            "data": meeting.to_dict(),
            "message": "Meeting updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to update meeting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_meetings_dashboard(
    days_ahead: int = Query(7, description="Days ahead to look for meetings"),
    session: AsyncSession = Depends(get_session)
):
    """Get meetings dashboard with upcoming and recent meetings"""
    try:
        now = datetime.utcnow()
        future_date = now + timedelta(days=days_ahead)
        past_date = now - timedelta(days=7)
        
        # Get upcoming meetings
        upcoming_result = await session.execute(
            select(Meeting, Contact)
            .join(Contact, Meeting.contact_id == Contact.contact_id)
            .where(
                and_(
                    Meeting.scheduled_date >= now,
                    Meeting.scheduled_date <= future_date,
                    Meeting.meeting_status.in_(["scheduled", "confirmed"])
                )
            )
            .order_by(Meeting.scheduled_date)
        )
        upcoming_meetings = upcoming_result.all()
        
        # Get recent completed meetings
        recent_result = await session.execute(
            select(Meeting, Contact)
            .join(Contact, Meeting.contact_id == Contact.contact_id)
            .where(
                and_(
                    Meeting.actual_date >= past_date,
                    Meeting.meeting_status == "completed"
                )
            )
            .order_by(desc(Meeting.actual_date))
            .limit(10)
        )
        recent_meetings = recent_result.all()
        
        # Get stats
        stats_result = await session.execute(
            select(Meeting).where(Meeting.created_at >= past_date)
        )
        all_recent = stats_result.scalars().all()
        
        stats = {
            "total_meetings_7d": len(all_recent),
            "completed_meetings_7d": len([m for m in all_recent if m.meeting_status == "completed"]),
            "scheduled_meetings": len(upcoming_meetings),
            "conversion_rate": len([m for m in all_recent if m.outcome in ["interested", "closed_won"]]) / max(len(all_recent), 1) * 100
        }
        
        # Format upcoming meetings
        formatted_upcoming = []
        for meeting, contact in upcoming_meetings:
            formatted_upcoming.append({
                **meeting.to_dict(),
                "contact_name": f"{contact.first_name} {contact.last_name}",
                "contact_company": contact.company,
                "contact_linkedin": contact.linkedin_url
            })
        
        # Format recent meetings
        formatted_recent = []
        for meeting, contact in recent_meetings:
            formatted_recent.append({
                **meeting.to_dict(),
                "contact_name": f"{contact.first_name} {contact.last_name}",
                "contact_company": contact.company,
                "contact_linkedin": contact.linkedin_url
            })
        
        return {
            "success": True,
            "data": {
                "stats": stats,
                "upcoming_meetings": formatted_upcoming,
                "recent_meetings": formatted_recent,
                "last_updated": now.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get meetings dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_all_meetings(
    status: Optional[str] = Query(None, description="Filter by meeting status"),
    days_range: int = Query(30, description="Days range for meetings"),
    session: AsyncSession = Depends(get_session)
):
    """Get all meetings with optional filtering"""
    try:
        now = datetime.utcnow()
        start_date = now - timedelta(days=days_range)
        end_date = now + timedelta(days=days_range)
        
        # Build query
        query = select(Meeting, Contact).join(Contact, Meeting.contact_id == Contact.contact_id)
        
        # Add filters
        conditions = [
            or_(
                and_(Meeting.scheduled_date >= start_date, Meeting.scheduled_date <= end_date),
                and_(Meeting.actual_date >= start_date, Meeting.actual_date <= end_date)
            )
        ]
        
        if status:
            conditions.append(Meeting.meeting_status == status)
        
        query = query.where(and_(*conditions)).order_by(desc(Meeting.scheduled_date))
        
        result = await session.execute(query)
        meetings_with_contacts = result.all()
        
        # Format response
        formatted_meetings = []
        for meeting, contact in meetings_with_contacts:
            formatted_meetings.append({
                **meeting.to_dict(),
                "contact_name": f"{contact.first_name} {contact.last_name}",
                "contact_company": contact.company,
                "contact_linkedin": contact.linkedin_url
            })
        
        return {
            "success": True,
            "data": {
                "meetings": formatted_meetings,
                "total_count": len(formatted_meetings),
                "filters": {
                    "status": status,
                    "days_range": days_range
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get meetings: {e}")
        raise HTTPException(status_code=500, detail=str(e))
