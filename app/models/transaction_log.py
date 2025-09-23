"""
Transaction log model for storing all platform activities.
"""

from sqlalchemy import Column, String, DateTime, Text, JSON, Boolean, Integer
from sqlalchemy.orm import relationship
from database.base import Base
import uuid
from app.utils.sqlalchemy_types import UTCDateTime


class TransactionLog(Base):
    """Model for storing transaction logs."""
    
    __tablename__ = "transaction_logs"
    
    transaction_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_type = Column(String(100), nullable=False, index=True)
    transaction_time = Column(UTCDateTime, nullable=False, index=True)
    user_id = Column(String(36), nullable=True, index=True)
    entity_id = Column(String(36), nullable=True, index=True)
    entity_type = Column(String(50), nullable=True, index=True)
    description = Column(Text, nullable=True)
    transaction_metadata = Column(JSON, nullable=True)
    success = Column(Boolean, default=True, index=True)
    error_message = Column(Text, nullable=True)
    
    # Additional fields for better querying
    campaign_id = Column(String(36), nullable=True, index=True)
    contact_id = Column(String(36), nullable=True, index=True)
    dux_user_id = Column(String(100), nullable=True, index=True)
    
    def __repr__(self):
        return f"<TransactionLog(id={self.transaction_id}, type={self.transaction_type}, time={self.transaction_time})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "transaction_id": self.transaction_id,
            "transaction_type": self.transaction_type,
            "transaction_time": self.transaction_time.isoformat() if self.transaction_time else None,
            "user_id": self.user_id,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "description": self.description,
            "metadata": self.transaction_metadata or {},
            "success": self.success,
            "error_message": self.error_message,
            "campaign_id": self.campaign_id,
            "contact_id": self.contact_id,
            "dux_user_id": self.dux_user_id
        }
