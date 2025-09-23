from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.campaign import CampaignStatus


class CampaignCreate(BaseModel):
    """Schema for creating a new campaign"""
    name: str = Field(..., min_length=1, max_length=255, description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    target_title: Optional[str] = Field(None, max_length=255, description="Target job titles")
    intent: str = Field(..., min_length=1, description="Campaign intent/goals")
    dux_user_id: str = Field("default_user", min_length=1, max_length=100, description="Dux-Soup user ID")
    scheduled_start: Optional[datetime] = Field(None, description="When campaign should start")
    end_date: Optional[datetime] = Field(None, description="When campaign should end")
    settings: Optional[Dict[str, Any]] = Field(None, description="Flexible campaign settings")
    
    # New DuxSoup workflow fields
    initial_action: str = Field("inmail", description="Initial action: inmail, connection_request, message, email, view_profile")
    initial_message: Optional[str] = Field(None, description="Initial message content")
    initial_subject: Optional[str] = Field(None, description="Subject line for inmail/email")
    follow_up_actions: Optional[list] = Field(None, description="Array of follow-up actions")
    delay_days: int = Field(1, ge=1, le=99, description="Delay between actions in days")
    random_delay: bool = Field(True, description="Add random time variation")
    
    # Follow-up action fields
    follow_up_action_1: Optional[str] = Field('message', description="Type of first follow-up action")
    follow_up_message_1: Optional[str] = Field(None, description="First follow-up message")
    follow_up_subject_1: Optional[str] = Field(None, description="Subject line for first follow-up InMail")
    follow_up_delay_1: int = Field(3, ge=1, le=30, description="Delay for first follow-up in days")
    follow_up_action_2: Optional[str] = Field('message', description="Type of second follow-up action")
    follow_up_message_2: Optional[str] = Field(None, description="Second follow-up message")
    follow_up_subject_2: Optional[str] = Field(None, description="Subject line for second follow-up InMail")
    follow_up_delay_2: int = Field(7, ge=1, le=30, description="Delay for second follow-up in days")
    follow_up_action_3: Optional[str] = Field('message', description="Type of third follow-up action")
    follow_up_message_3: Optional[str] = Field(None, description="Third follow-up message")
    follow_up_subject_3: Optional[str] = Field(None, description="Subject line for third follow-up InMail")
    follow_up_delay_3: int = Field(14, ge=1, le=30, description="Delay for third follow-up in days")

    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and values.get('scheduled_start'):
            if v <= values['scheduled_start']:
                raise ValueError('End date must be after start date')
        return v


class CampaignUpdate(BaseModel):
    """Schema for updating an existing campaign"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    target_title: Optional[str] = Field(None, max_length=255)
    intent: Optional[str] = Field(None, min_length=1)
    status: Optional[CampaignStatus] = None
    scheduled_start: Optional[datetime] = None
    end_date: Optional[datetime] = None
    settings: Optional[Dict[str, Any]] = None
    
    # New DuxSoup workflow fields
    initial_action: Optional[str] = None
    initial_message: Optional[str] = None
    initial_subject: Optional[str] = None
    follow_up_actions: Optional[list] = None
    delay_days: Optional[int] = Field(None, ge=1, le=99)
    random_delay: Optional[bool] = None
    
    # Follow-up action fields
    follow_up_action_1: Optional[str] = None
    follow_up_message_1: Optional[str] = None
    follow_up_subject_1: Optional[str] = None
    follow_up_delay_1: Optional[int] = Field(None, ge=1, le=30)
    follow_up_action_2: Optional[str] = None
    follow_up_message_2: Optional[str] = None
    follow_up_subject_2: Optional[str] = None
    follow_up_delay_2: Optional[int] = Field(None, ge=1, le=30)
    follow_up_action_3: Optional[str] = None
    follow_up_message_3: Optional[str] = None
    follow_up_subject_3: Optional[str] = None
    follow_up_delay_3: Optional[int] = Field(None, ge=1, le=30)

    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and values.get('scheduled_start'):
            if v <= values['scheduled_start']:
                raise ValueError('End date must be after start date')
        return v


class CampaignResponse(BaseModel):
    """Schema for campaign response (full details)"""
    campaign_id: str = Field(..., description="Unique campaign identifier")
    campaign_key: str = Field(..., description="External campaign key for API access")
    name: str = Field(..., description="Campaign name")
    description: Optional[str] = None
    target_title: Optional[str] = None
    intent: str = Field(..., description="Campaign intent")
    status: str = Field(..., description="Campaign status")
    dux_user_id: str = Field(..., description="Dux-Soup user ID")
    scheduled_start: Optional[datetime] = None
    end_date: Optional[datetime] = None
    settings: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(..., description="Campaign creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # New DuxSoup workflow fields
    initial_action: str = Field(..., description="Initial action")
    initial_message: Optional[str] = None
    initial_subject: Optional[str] = None
    follow_up_actions: Optional[list] = None
    delay_days: int = Field(..., description="Delay between actions in days")
    random_delay: bool = Field(..., description="Random time variation enabled")
    
    # Follow-up action fields
    follow_up_action_1: Optional[str] = Field('message', description="Type of first follow-up action")
    follow_up_message_1: Optional[str] = None
    follow_up_subject_1: Optional[str] = None
    follow_up_delay_1: int = Field(3, description="Delay for first follow-up in days")
    follow_up_action_2: Optional[str] = Field('message', description="Type of second follow-up action")
    follow_up_message_2: Optional[str] = None
    follow_up_subject_2: Optional[str] = None
    follow_up_delay_2: int = Field(7, description="Delay for second follow-up in days")
    follow_up_action_3: Optional[str] = Field('message', description="Type of third follow-up action")
    follow_up_message_3: Optional[str] = None
    follow_up_subject_3: Optional[str] = None
    follow_up_delay_3: int = Field(14, description="Delay for third follow-up in days")
    
    # Contact statistics
    total_contacts: int = Field(0, description="Total number of contacts in campaign")
    accepted_contacts: int = Field(0, description="Number of accepted contacts")
    replied_contacts: int = Field(0, description="Number of contacts who replied")
    acceptance_rate: float = Field(0.0, description="Acceptance rate percentage")
    reply_rate: float = Field(0.0, description="Reply rate percentage")

    class Config:
        from_attributes = True


class CampaignListResponse(BaseModel):
    """Schema for campaign list response (summary)"""
    campaign_id: str = Field(..., description="Unique campaign identifier")
    campaign_key: str = Field(..., description="External campaign key")
    name: str = Field(..., description="Campaign name")
    status: str = Field(..., description="Campaign status")
    intent: str = Field(..., description="Campaign intent")
    dux_user_id: str = Field(..., description="Dux-Soup user ID")
    created_at: datetime = Field(..., description="Campaign creation timestamp")

    class Config:
        from_attributes = True


class CampaignStatsResponse(BaseModel):
    """Schema for campaign statistics response"""
    campaign_id: str = Field(..., description="Unique campaign identifier")
    campaign_name: str = Field(..., description="Campaign name")
    total_contacts: int = Field(..., description="Total number of contacts in campaign")
    contacts_by_status: Dict[str, int] = Field(..., description="Contact count by status")
    total_messages: int = Field(..., description="Total number of messages sent/received")
    created_at: datetime = Field(..., description="Campaign creation timestamp")
    last_updated: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class CampaignStatusUpdate(BaseModel):
    """Schema for updating campaign status"""
    status: CampaignStatus = Field(..., description="New campaign status")


class CampaignFilter(BaseModel):
    """Schema for filtering campaigns"""
    status: Optional[str] = Field(None, description="Filter by campaign status")
    dux_user_id: Optional[str] = Field(None, description="Filter by Dux-Soup user ID")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of campaigns")
    offset: int = Field(0, ge=0, description="Number of campaigns to skip")
