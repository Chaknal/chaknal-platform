from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from database.base import Base
import uuid
from datetime import datetime


class Company(Base):
    __tablename__ = "company"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=True)
    domain = Column(String, unique=True, nullable=False)
    logo_url = Column(String, nullable=True, comment="URL/path to company logo for white labeling")
    created_at = Column(DateTime, default=datetime.utcnow)
    users = relationship("User", foreign_keys="User.company_id", back_populates="company")
