from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, JSON, Integer
from sqlalchemy.orm import relationship
from database.base import Base
import uuid
from datetime import datetime



class Message(Base):
    __tablename__ = "messages"

    message_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_contact_id = Column(String(36), ForeignKey("campaign_contacts.campaign_contact_id"), nullable=False)
    direction = Column(String(20), nullable=False)  # 'sent' or 'received'
    message_text = Column(Text, nullable=False)
    linkedin_message_id = Column(String(100), nullable=True)
    thread_url = Column(String(500), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    received_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), nullable=False, default="sent")  # sent, delivered, read, failed
    tags = Column(Text, nullable=True)  # JSON array as text for SQLite compatibility
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # DuxSoup-specific fields
    dux_message_id = Column(String(100), nullable=True)
    command_type = Column(String(50), nullable=True)
    command_params = Column(JSON, nullable=True)
    campaign_id = Column(String(36), ForeignKey("campaigns_new.campaign_id"), nullable=True)
    force_execution = Column(Boolean, default=False)
    execution_result = Column(JSON, nullable=True)
    retry_count = Column(Integer, default=0)
    last_retry = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    campaign_contact = relationship("CampaignContact", back_populates="messages")

    def __repr__(self):
        return f"<Message(message_id={self.message_id}, direction={self.direction}, status={self.status})>"
