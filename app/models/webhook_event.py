from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base
import uuid
from datetime import datetime
from sqlalchemy import JSON


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    event_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dux_user_id = Column(String(100), nullable=False)
    event_type = Column(String(50), nullable=False)  # message, visit, action, rccommand
    event_name = Column(String(50), nullable=False)  # create, received, completed, ready, etc.
    contact_id = Column(String(36), ForeignKey("contacts.contact_id"), nullable=True)
    campaign_id = Column(String(36), ForeignKey("campaigns_new.campaign_id"), nullable=True)
    raw_data = Column(JSON, nullable=False)  # Complete raw webhook payload
    processed = Column(Boolean, nullable=False, default=False)  # Whether event has been processed
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    contact = relationship("Contact", back_populates="webhook_events")
    campaign = relationship("Campaign", back_populates="webhook_events")

    def __repr__(self):
        return f"<WebhookEvent(event_id={self.event_id}, type={self.event_type}, name={self.event_name})>"
