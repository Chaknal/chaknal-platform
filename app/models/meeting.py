from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base
import uuid
from datetime import datetime


class Meeting(Base):
    __tablename__ = "meetings"

    meeting_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_contact_id = Column(String(36), ForeignKey("campaign_contacts.campaign_contact_id"), nullable=False)
    contact_id = Column(String(36), ForeignKey("contacts.contact_id"), nullable=False)
    campaign_id = Column(String(36), ForeignKey("campaigns_new.campaign_id"), nullable=True)
    
    # Meeting Details
    meeting_type = Column(String(50), nullable=True, comment="call, demo, discovery, presentation, etc.")
    meeting_status = Column(String(50), nullable=False, default="scheduled", comment="scheduled, confirmed, completed, cancelled, no_show, rescheduled")
    scheduled_date = Column(DateTime, nullable=True, comment="When the meeting is scheduled")
    actual_date = Column(DateTime, nullable=True, comment="When the meeting actually happened")
    duration_minutes = Column(Integer, nullable=True, comment="Planned or actual meeting duration")
    meeting_link = Column(String(500), nullable=True, comment="Zoom, Teams, or other meeting link")
    
    # Booking Details
    booked_by = Column(String(36), ForeignKey("user.id"), nullable=True, comment="User who marked it as booked")
    booking_source = Column(String(50), nullable=True, default="manual_entry", comment="message_reply, manual_entry, calendar_sync")
    booking_message_id = Column(String(36), ForeignKey("messages.message_id"), nullable=True, comment="Which message led to booking")
    booking_notes = Column(Text, nullable=True, comment="Notes about how the meeting was booked")
    
    # Meeting Outcome
    outcome = Column(String(50), nullable=True, comment="interested, not_interested, follow_up, closed_won, closed_lost, no_decision")
    outcome_notes = Column(Text, nullable=True, comment="Detailed notes about meeting outcome")
    next_action = Column(String(100), nullable=True, comment="What needs to happen next")
    follow_up_date = Column(DateTime, nullable=True, comment="When to follow up")
    deal_value = Column(String(20), nullable=True, comment="Potential or actual deal value")
    
    # Contact Information at Time of Meeting
    contact_title_at_meeting = Column(String(255), nullable=True, comment="Contact's title when meeting was booked")
    contact_company_at_meeting = Column(String(255), nullable=True, comment="Contact's company when meeting was booked")
    
    # Meeting Preparation
    agenda = Column(Text, nullable=True, comment="Meeting agenda or talking points")
    attendees = Column(Text, nullable=True, comment="JSON array of attendees")
    preparation_notes = Column(Text, nullable=True, comment="Notes for meeting preparation")
    
    # Tracking
    reminder_sent = Column(Boolean, default=False, comment="Whether reminder was sent")
    calendar_invite_sent = Column(Boolean, default=False, comment="Whether calendar invite was sent")
    confirmation_received = Column(Boolean, default=False, comment="Whether contact confirmed attendance")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign_contact = relationship("CampaignContact", foreign_keys=[campaign_contact_id])
    contact = relationship("Contact", foreign_keys=[contact_id])
    campaign = relationship("Campaign", foreign_keys=[campaign_id])
    booked_by_user = relationship("User", foreign_keys=[booked_by])
    booking_message = relationship("Message", foreign_keys=[booking_message_id])

    def __repr__(self):
        return f"<Meeting(meeting_id={self.meeting_id}, contact={self.contact_id}, status={self.meeting_status}, date={self.scheduled_date})>"

    def to_dict(self):
        """Convert meeting to dictionary for API responses"""
        return {
            "meeting_id": self.meeting_id,
            "campaign_contact_id": self.campaign_contact_id,
            "contact_id": self.contact_id,
            "campaign_id": self.campaign_id,
            "meeting_type": self.meeting_type,
            "meeting_status": self.meeting_status,
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else None,
            "actual_date": self.actual_date.isoformat() if self.actual_date else None,
            "duration_minutes": self.duration_minutes,
            "meeting_link": self.meeting_link,
            "booked_by": self.booked_by,
            "booking_source": self.booking_source,
            "booking_message_id": self.booking_message_id,
            "booking_notes": self.booking_notes,
            "outcome": self.outcome,
            "outcome_notes": self.outcome_notes,
            "next_action": self.next_action,
            "follow_up_date": self.follow_up_date.isoformat() if self.follow_up_date else None,
            "deal_value": self.deal_value,
            "contact_title_at_meeting": self.contact_title_at_meeting,
            "contact_company_at_meeting": self.contact_company_at_meeting,
            "agenda": self.agenda,
            "attendees": self.attendees,
            "preparation_notes": self.preparation_notes,
            "reminder_sent": self.reminder_sent,
            "calendar_invite_sent": self.calendar_invite_sent,
            "confirmation_received": self.confirmation_received,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
