"""
Campaigns API Router - Rebuilt from scratch
Simple, clean implementation of campaign endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.database import get_session

router = APIRouter()

# Pydantic models
class CampaignCreate(BaseModel):
    title: str
    name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    target_title: Optional[str] = None
    intent: Optional[str] = None
    dux_user_id: Optional[str] = None
    initial_action: Optional[str] = None
    initial_message: Optional[str] = None
    initial_subject: Optional[str] = None
    follow_up_actions: Optional[list] = None
    delay_days: Optional[int] = None
    random_delay: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    scheduled_start: Optional[datetime] = None

class CampaignResponse(BaseModel):
    id: str
    campaign_id: str  # Alias for frontend compatibility
    title: str
    name: Optional[str] = None  # Frontend expects 'name' field
    description: Optional[str] = None
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    target_title: Optional[str] = None  # Frontend expects 'target_title'
    intent: Optional[str] = None  # Frontend expects 'intent'
    dux_user_id: Optional[str] = None  # Frontend expects 'dux_user_id'
    initial_action: Optional[str] = None  # Frontend expects 'initial_action'
    initial_message: Optional[str] = None  # Frontend expects 'initial_message'
    initial_subject: Optional[str] = None  # Frontend expects 'initial_subject'
    follow_up_actions: Optional[list] = None  # Frontend expects 'follow_up_actions'
    delay_days: Optional[int] = None  # Frontend expects 'delay_days'
    random_delay: Optional[bool] = None  # Frontend expects 'random_delay'
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    scheduled_start: Optional[datetime] = None  # Frontend expects 'scheduled_start'
    created_at: datetime
    updated_at: datetime
    status: str = "active"

# Database storage - we'll use the actual database

@router.get("/campaigns/", response_model=List[CampaignResponse])
async def get_campaigns(session: AsyncSession = Depends(get_session)):
    """Get all campaigns from database"""
    from app.models.campaign import Campaign
    result = await session.execute(select(Campaign))
    campaigns = result.scalars().all()
    
    # Convert to response format
    campaign_responses = []
    for campaign in campaigns:
        campaign_responses.append(CampaignResponse(
            id=campaign.id,
            campaign_id=campaign.id,
            title=campaign.title,
            name=getattr(campaign, 'name', campaign.title),
            description=getattr(campaign, 'description', None),
            industry=getattr(campaign, 'industry', None),
            target_audience=getattr(campaign, 'target_audience', None),
            target_title=getattr(campaign, 'target_title', None),
            intent=getattr(campaign, 'intent', None),
            dux_user_id=getattr(campaign, 'dux_user_id', None),
            initial_action=getattr(campaign, 'initial_action', None),
            initial_message=getattr(campaign, 'initial_message', None),
            initial_subject=getattr(campaign, 'initial_subject', None),
            follow_up_actions=getattr(campaign, 'follow_up_actions', None),
            delay_days=getattr(campaign, 'delay_days', None),
            random_delay=getattr(campaign, 'random_delay', None),
            start_date=getattr(campaign, 'start_date', None),
            end_date=getattr(campaign, 'end_date', None),
            scheduled_start=getattr(campaign, 'scheduled_start', None),
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            status=getattr(campaign, 'status', 'active')
        ))
    
    return campaign_responses

@router.post("/campaigns/", response_model=CampaignResponse)
async def create_campaign(campaign: CampaignCreate):
    """Create a new campaign"""
    campaign_id = str(uuid.uuid4())
    now = datetime.now()
    
    # Extract additional fields from the request data
    campaign_dict = campaign.dict() if hasattr(campaign, 'dict') else {}
    
    new_campaign = CampaignResponse(
        id=campaign_id,
        campaign_id=campaign_id,  # Alias for frontend compatibility
        title=campaign.title,
        name=campaign_dict.get('name', campaign.title),  # Use name if provided, otherwise title
        description=campaign.description,
        industry=campaign.industry,
        target_audience=campaign.target_audience,
        target_title=campaign_dict.get('target_title'),
        intent=campaign_dict.get('intent'),
        dux_user_id=campaign_dict.get('dux_user_id'),
        initial_action=campaign_dict.get('initial_action'),
        initial_message=campaign_dict.get('initial_message'),
        initial_subject=campaign_dict.get('initial_subject'),
        follow_up_actions=campaign_dict.get('follow_up_actions'),
        delay_days=campaign_dict.get('delay_days'),
        random_delay=campaign_dict.get('random_delay'),
        start_date=campaign.start_date,
        end_date=campaign.end_date,
        scheduled_start=campaign_dict.get('scheduled_start'),
        created_at=now,
        updated_at=now,
        status="active"
    )
    
    campaigns_db.append(new_campaign)
    return new_campaign

@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: str):
    """Get a specific campaign by ID"""
    for campaign in campaigns_db:
        if campaign.id == campaign_id:
            return campaign
    
    raise HTTPException(status_code=404, detail="Campaign not found")

@router.put("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(campaign_id: str, campaign: CampaignCreate):
    """Update a campaign"""
    for i, existing_campaign in enumerate(campaigns_db):
        if existing_campaign.id == campaign_id:
            updated_campaign = CampaignResponse(
                id=campaign_id,
                title=campaign.title,
                description=campaign.description,
                industry=campaign.industry,
                target_audience=campaign.target_audience,
                start_date=campaign.start_date,
                end_date=campaign.end_date,
                created_at=existing_campaign.created_at,
                updated_at=datetime.now(),
                status=existing_campaign.status
            )
            campaigns_db[i] = updated_campaign
            return updated_campaign
    
    raise HTTPException(status_code=404, detail="Campaign not found")

@router.delete("/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str):
    """Delete a campaign"""
    for i, campaign in enumerate(campaigns_db):
        if campaign.id == campaign_id:
            del campaigns_db[i]
            return {"message": "Campaign deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Campaign not found")

@router.get("/campaigns/{campaign_id}/stats")
async def get_campaign_stats(campaign_id: str):
    """Get campaign statistics"""
    campaign = next((c for c in campaigns_db if c.id == campaign_id), None)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return {
        "campaign_id": campaign_id,
        "total_contacts": 0,  # Will be implemented later
        "messages_sent": 0,
        "responses_received": 0,
        "connection_requests": 0,
        "status": campaign.status
    }
