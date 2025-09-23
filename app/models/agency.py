"""
Agency Models for Multi-Client Management
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from database.base import Base
import uuid
from datetime import datetime


class AgencyClient(Base):
    """Association table linking agency users to client companies"""
    __tablename__ = "agency_client"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agency_user_id = Column(String(36), ForeignKey("user.id"), nullable=False)
    client_company_id = Column(String(36), ForeignKey("company.id"), nullable=False)
    access_level = Column(String(20), default="full")  # full, read_only, limited
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    agency_user = relationship("User", foreign_keys=[agency_user_id])
    client_company = relationship("Company", foreign_keys=[client_company_id])


class AgencyInvitation(Base):
    """Invitations for agency users to manage client accounts"""
    __tablename__ = "agency_invitation"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agency_user_id = Column(String(36), ForeignKey("user.id"), nullable=False)
    client_company_id = Column(String(36), ForeignKey("company.id"), nullable=False)
    invited_by_user_id = Column(String(36), ForeignKey("user.id"), nullable=False)
    access_level = Column(String(20), default="full")
    status = Column(String(20), default="pending")  # pending, accepted, declined, expired
    invitation_token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)
    
    # Relationships
    agency_user = relationship("User", foreign_keys=[agency_user_id])
    client_company = relationship("Company")
    invited_by = relationship("User", foreign_keys=[invited_by_user_id])


class AgencyActivityLog(Base):
    """Log of agency activities across client accounts"""
    __tablename__ = "agency_activity_log"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agency_user_id = Column(String(36), ForeignKey("user.id"), nullable=False)
    client_company_id = Column(String(36), ForeignKey("company.id"), nullable=False)
    activity_type = Column(String(50), nullable=False)  # campaign_created, settings_changed, etc.
    activity_description = Column(Text, nullable=False)
    activity_metadata = Column(Text, nullable=True)  # JSON string for additional data
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agency_user = relationship("User", foreign_keys=[agency_user_id])
    client_company = relationship("Company", foreign_keys=[client_company_id])
