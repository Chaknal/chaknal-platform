from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
import uuid
from datetime import datetime
from database.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .company import Company


class Organization(Base):
    __tablename__ = "organization"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    users = relationship("User", back_populates="organization")


class User(SQLAlchemyBaseUserTable, Base):
    __tablename__ = "user"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String(length=1024), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    bio = Column(String(500), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    timezone = Column(String(50), nullable=True)
    role = Column(String(20), default="user")  # user, admin, read_only, agency
    is_active = Column(String, default=True)
    is_superuser = Column(String, default=False)
    is_verified = Column(String, default=False)
    is_agency = Column(Boolean, default=False, comment="Is this user an agency user")
    agency_company_id = Column(String(36), ForeignKey("company.id"), nullable=True, comment="Agency's own company ID")
    organization_id = Column(String(36), ForeignKey("organization.id"), nullable=True)
    organization = relationship("Organization", back_populates="users")
    company_id = Column(String(36), ForeignKey("company.id"), nullable=True)
    company = relationship("Company", foreign_keys=[company_id], back_populates="users")
    agency_company = relationship("Company", foreign_keys=[agency_company_id])
    
    # Agency relationships
    managed_clients = relationship("AgencyClient", foreign_keys="AgencyClient.agency_user_id", back_populates="agency_user")
    agency_invitations = relationship("AgencyInvitation", foreign_keys="AgencyInvitation.agency_user_id", back_populates="agency_user")
    agency_activity_logs = relationship("AgencyActivityLog", foreign_keys="AgencyActivityLog.agency_user_id", back_populates="agency_user")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
