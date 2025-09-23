from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Boolean, JSON, Text
from sqlalchemy.orm import relationship
from database.base import Base
import uuid
from datetime import datetime, timezone



class CampaignContact(Base):
    __tablename__ = "campaign_contacts"

    campaign_contact_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String(36), ForeignKey("campaigns_new.campaign_id"), nullable=False)
    campaign_key = Column(String(36), nullable=False)
    contact_id = Column(String(36), ForeignKey("contacts.contact_id"), nullable=False)
    status = Column(String(50), nullable=False, default="enrolled")
    assigned_to = Column(String(36), ForeignKey("user.id"), nullable=True)  # Team member assignment
    enrolled_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    replied_at = Column(DateTime(timezone=True), nullable=True)
    blacklisted_at = Column(DateTime(timezone=True), nullable=True)
    sequence_step = Column(Integer, nullable=False, default=1)
    tags = Column(Text, nullable=True)  # JSON array as text for SQLite compatibility
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # DuxSoup-specific fields
    dux_profile_id = Column(String(100), nullable=True)
    command_executed = Column(String(50), nullable=True)
    command_params = Column(JSON, nullable=True)
    force_execution = Column(Boolean, default=False)
    run_after = Column(DateTime(timezone=True), nullable=True)
    execution_result = Column(JSON, nullable=True)
    retry_count = Column(Integer, default=0)
    last_retry = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    campaign = relationship("Campaign", back_populates="campaign_contacts")
    contact = relationship("Contact", back_populates="campaign_contacts")
    messages = relationship("Message", back_populates="campaign_contact", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CampaignContact(campaign_contact_id={self.campaign_contact_id}, status={self.status}, step={self.sequence_step})>"
