"""
Campaigns API Router - Rebuilt from scratch
Simple, clean implementation of campaign endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter()

# Pydantic models
class CampaignCreate(BaseModel):
    title: str
    description: Optional[str] = None
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class CampaignResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    status: str = "active"

# In-memory storage for now (we'll connect to database later)
campaigns_db = []

@router.get("/campaigns/", response_model=List[CampaignResponse])
async def get_campaigns():
    """Get all campaigns"""
    return campaigns_db

@router.post("/campaigns/", response_model=CampaignResponse)
async def create_campaign(campaign: CampaignCreate):
    """Create a new campaign"""
    campaign_id = str(uuid.uuid4())
    now = datetime.now()
    
    new_campaign = CampaignResponse(
        id=campaign_id,
        title=campaign.title,
        description=campaign.description,
        industry=campaign.industry,
        target_audience=campaign.target_audience,
        start_date=campaign.start_date,
        end_date=campaign.end_date,
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
