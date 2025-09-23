"""
DuxSoup Execution Log Model

This model logs all DuxSoup command executions for monitoring and debugging.
"""

from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.base import Base
import uuid
from datetime import datetime



class DuxSoupExecutionLog(Base):
    __tablename__ = "duxsoup_execution_log"

    log_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dux_user_id = Column(String(100), nullable=False)
    campaign_id = Column(String(36), ForeignKey("campaigns_new.campaign_id"), nullable=True)
    contact_id = Column(String(36), ForeignKey("contacts.contact_id"), nullable=True)
    command = Column(String(50), nullable=False)
    params = Column(JSON, nullable=False)
    execution_start = Column(DateTime(timezone=True), default=datetime.utcnow)
    execution_end = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), nullable=False, default="running")
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    response_time_ms = Column(Integer, nullable=True)

    # Relationships
    campaign = relationship("Campaign", back_populates="duxsoup_execution_logs")
    contact = relationship("Contact", back_populates="duxsoup_execution_logs")

    def __repr__(self):
        return f"<DuxSoupExecutionLog(log_id={self.log_id}, command={self.command}, status={self.status})>"
