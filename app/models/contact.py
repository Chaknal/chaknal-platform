from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean
from sqlalchemy.orm import relationship
from database.base import Base
import uuid
from datetime import datetime, timezone
from sqlalchemy import JSON
from app.utils.sqlalchemy_types import ContactTimestamp


class Contact(Base):
    __tablename__ = "contacts"

    contact_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    linkedin_id = Column(String(100), nullable=True, unique=True)
    linkedin_url = Column(String(500), nullable=True, unique=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    headline = Column(String(500), nullable=True)
    company = Column(String(255), nullable=True)
    company_url = Column(String(500), nullable=True)
    location = Column(String(255), nullable=True)
    industry = Column(String(255), nullable=True)
    connection_degree = Column(Integer, nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    profile_data = Column(JSON, nullable=True)
    created_at = Column(ContactTimestamp, nullable=False)
    updated_at = Column(ContactTimestamp, nullable=False)
    
    # Data source tracking fields
    data_source = Column(String(50), nullable=True)  # duxsoup, zoominfo, apollo, custom
    source_id = Column(String(100), nullable=True)  # Original ID from source
    import_batch_id = Column(String(100), nullable=True)  # Batch import identifier
    data_quality_score = Column(Integer, nullable=True)  # 1-100 quality score
    
    # Standardized fields for better compatibility
    full_name = Column(String(255), nullable=True)
    job_title = Column(String(255), nullable=True)
    company_name = Column(String(255), nullable=True)
    company_size = Column(String(100), nullable=True)
    company_website = Column(String(500), nullable=True)
    connection_count = Column(Integer, nullable=True)
    
    # DuxSoup-specific fields
    profile_id = Column(String(100), nullable=True)
    degree_level = Column(Integer, default=0)
    connection_status = Column(String(50), default="not_connected")
    connection_request_sent = Column(DateTime(timezone=True), nullable=True)
    connection_accepted = Column(DateTime(timezone=True), nullable=True)
    last_message_sent = Column(DateTime(timezone=True), nullable=True)
    message_count = Column(Integer, default=0)
    
    # Additional DuxSoup fields
    scan_time = Column(DateTime(timezone=True), nullable=True)
    sales_profile_url = Column(String(500), nullable=True)
    public_profile_url = Column(String(500), nullable=True)
    recruiter_profile_url = Column(String(500), nullable=True)
    middle_name = Column(String(100), nullable=True)
    company_id = Column(String(100), nullable=True)
    can_send_email = Column(Boolean, default=False)
    can_send_inmail = Column(Boolean, default=False)
    can_send_connection = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)

    # Relationships
    campaign_contacts = relationship("CampaignContact", back_populates="contact", cascade="all, delete-orphan")
    webhook_events = relationship("WebhookEvent", back_populates="contact")
    duxsoup_queue_items = relationship("DuxSoupQueue", back_populates="contact")
    duxsoup_execution_logs = relationship("DuxSoupExecutionLog", back_populates="contact")

    def __repr__(self):
        return f"<Contact(contact_id={self.contact_id}, name={self.first_name} {self.last_name}, company={self.company})>"
