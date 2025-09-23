"""
DuxSoup Queue Model

This model represents the DuxSoup action queue for LinkedIn automation.
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.base import Base
import uuid
from datetime import datetime



class DuxSoupQueue(Base):
    __tablename__ = "duxsoup_queue"

    queue_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dux_user_id = Column(String(100), nullable=False)
    campaign_id = Column(String(36), ForeignKey("campaigns_new.campaign_id"), nullable=True)
    contact_id = Column(String(36), ForeignKey("contacts.contact_id"), nullable=True)
    command = Column(String(50), nullable=False)
    params = Column(JSON, nullable=False)
    force_execution = Column(Boolean, default=False)
    run_after = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), nullable=False, default="queued")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    campaign = relationship("Campaign", back_populates="duxsoup_queue_items")
    contact = relationship("Contact", back_populates="duxsoup_queue_items")

    def __repr__(self):
        return f"<DuxSoupQueue(queue_id={self.queue_id}, command={self.command}, status={self.status})>"
