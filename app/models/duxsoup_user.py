from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base
import uuid
from datetime import datetime


class DuxSoupUser(Base):
    __tablename__ = "duxsoup_user"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dux_soup_user_id = Column(String, nullable=False)
    dux_soup_auth_key = Column(String, nullable=False)
    email = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    user_id = Column(String(36), ForeignKey("user.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")
    settings = relationship("DuxSoupUserSettings", back_populates="duxsoup_user", uselist=False)
    # Note: Campaigns are now linked directly via dux_user_id field
