"""
Automation API Schemas

Pydantic models for LinkedIn automation API responses and requests.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class CampaignExecutionResponse(BaseModel):
    """Response for campaign execution"""
    success: bool = Field(..., description="Whether the execution was successful")
    campaign_id: str = Field(..., description="Campaign ID that was executed")
    processed: int = Field(..., description="Number of contacts processed")
    results: List[Dict[str, Any]] = Field(..., description="Results for each contact")
    executed_at: datetime = Field(..., description="When the execution was performed")


class AutomationStatusResponse(BaseModel):
    """Response for campaign automation status"""
    campaign_id: str = Field(..., description="Campaign ID")
    campaign_name: str = Field(..., description="Campaign name")
    status: str = Field(..., description="Current campaign status")
    contact_counts: Dict[str, int] = Field(..., description="Contact counts by status")
    total_contacts: int = Field(..., description="Total number of contacts")
    recent_activity: List[Dict[str, Any]] = Field(..., description="Recent automation activity")
    last_updated: datetime = Field(..., description="When status was last updated")


class ContactUploadResponse(BaseModel):
    """Response for contact upload"""
    success: bool = Field(..., description="Whether the upload was successful")
    campaign_id: str = Field(..., description="Campaign ID where contacts were uploaded")
    uploaded_count: int = Field(..., description="Number of contacts successfully uploaded")
    contacts: List[Dict[str, Any]] = Field(..., description="Details of uploaded contacts")


class AutomationSettings(BaseModel):
    """Settings for LinkedIn automation"""
    message_templates: List[str] = Field(..., description="Message templates for outreach")
    followup_templates: List[str] = Field(..., description="Follow-up message templates")
    max_connections_per_day: int = Field(50, description="Maximum connections per day")
    delay_between_messages: int = Field(24, description="Hours between messages")
    auto_followup: bool = Field(True, description="Whether to send automatic follow-ups")
    connection_message_enabled: bool = Field(True, description="Whether to send connection messages")


class ContactUploadRequest(BaseModel):
    """Request for uploading contacts"""
    first_name: str = Field(..., description="Contact first name")
    last_name: str = Field(..., description="Contact last name")
    company: Optional[str] = Field(None, description="Company name")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    email: Optional[str] = Field(None, description="Email address")
    title: Optional[str] = Field(None, description="Job title")
    location: Optional[str] = Field(None, description="Location")
    industry: Optional[str] = Field(None, description="Industry")


class CampaignAutomationRequest(BaseModel):
    """Request for campaign automation actions"""
    action: str = Field(..., description="Action to perform (execute, pause, resume)")
    settings: Optional[AutomationSettings] = Field(None, description="Automation settings")


class AutomationDashboardResponse(BaseModel):
    """Response for automation dashboard"""
    success: bool = Field(..., description="Whether the request was successful")
    overview: Dict[str, Any] = Field(..., description="Overview statistics")
    recent_activity: List[Dict[str, Any]] = Field(..., description="Recent automation activity")
    active_campaigns: List[Dict[str, Any]] = Field(..., description="Currently active campaigns")
