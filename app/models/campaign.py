from sqlalchemy import Column, String, DateTime, Text, Enum, JSON, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship
from database.base import Base
import uuid
from datetime import datetime, timezone
import enum



# Campaign status as string to match DuxSoup expectations
# DuxSoup uses string-based status values
CAMPAIGN_STATUS_CHOICES = [
    "draft",
    "active", 
    "paused",
    "completed",
    "archived"
]

# Campaign status enum for type safety
class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Campaign(Base):
    __tablename__ = "campaigns_new"

    campaign_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_key = Column(String(36), nullable=False, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    target_title = Column(String(255), nullable=True)
    intent = Column(Text, nullable=False)
    status = Column(String(50), default="active")
    dux_user_id = Column(String(100), nullable=False)
    scheduled_start = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    settings = Column(JSON, nullable=True)
    
    # DuxSoup-specific fields
    dux_campaign_id = Column(String(100), nullable=True)
    force_override = Column(Boolean, default=False)
    run_after = Column(DateTime(timezone=True), nullable=True)
    daily_limits = Column(JSON, nullable=True)
    automation_settings = Column(JSON, nullable=True)
    
    # New DuxSoup workflow fields
    initial_action = Column(String(50), nullable=True, default="inmail")
    initial_message = Column(Text, nullable=True)
    initial_subject = Column(String(255), nullable=True)
    follow_up_actions = Column(JSON, nullable=True)  # Array of follow-up action objects
    delay_days = Column(Integer, nullable=True, default=1)
    random_delay = Column(Boolean, nullable=True, default=True)
    
    # Follow-up action fields
    follow_up_action_1 = Column(String(50), nullable=True, default='message')
    follow_up_message_1 = Column(Text, nullable=True)
    follow_up_subject_1 = Column(String(255), nullable=True)
    follow_up_delay_1 = Column(Integer, nullable=True, default=3)
    follow_up_action_2 = Column(String(50), nullable=True, default='message')
    follow_up_message_2 = Column(Text, nullable=True)
    follow_up_subject_2 = Column(String(255), nullable=True)
    follow_up_delay_2 = Column(Integer, nullable=True, default=7)
    follow_up_action_3 = Column(String(50), nullable=True, default='message')
    follow_up_message_3 = Column(Text, nullable=True)
    follow_up_subject_3 = Column(String(255), nullable=True)
    follow_up_delay_3 = Column(Integer, nullable=True, default=14)

    # Relationships
    campaign_contacts = relationship("CampaignContact", back_populates="campaign", cascade="all, delete-orphan")
    webhook_events = relationship("WebhookEvent", back_populates="campaign")
    duxsoup_queue_items = relationship("DuxSoupQueue", back_populates="campaign")
    duxsoup_execution_logs = relationship("DuxSoupExecutionLog", back_populates="campaign")

    def __repr__(self):
        return f"<Campaign(campaign_id={self.campaign_id}, name={self.name}, status={self.status})>"
