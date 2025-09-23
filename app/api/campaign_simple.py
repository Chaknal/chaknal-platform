from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
import uuid
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)

from database.database import get_session
from app.models.campaign import Campaign, CampaignStatus
from app.models.campaign_contact import CampaignContact
from app.models.contact import Contact
from app.models.message import Message
from app.schemas.campaign import (
    CampaignCreate, 
    CampaignUpdate, 
    CampaignResponse, 
    CampaignListResponse,
    CampaignStatsResponse
)

router = APIRouter()

@router.get("/campaigns", response_model=List[CampaignResponse], tags=["Campaigns"])
async def list_campaigns_simple(
    status: Optional[str] = Query(None, description="Filter by campaign status"),
    dux_user_id: Optional[str] = Query(None, description="Filter by Dux-Soup user ID"),
    limit: int = Query(100, le=1000, description="Maximum number of campaigns to return"),
    offset: int = Query(0, ge=0, description="Number of campaigns to skip"),
    session: AsyncSession = Depends(get_session)
):
    """List all campaigns with simplified query to avoid timeouts"""
    try:
        logger.info(f"Listing campaigns (simple) with filters: status={status}, dux_user_id={dux_user_id}")
        
        # Simple query without complex joins
        query = select(Campaign)
        
        # Apply filters
        if status:
            query = query.where(Campaign.status == status)
        if dux_user_id:
            query = query.where(Campaign.dux_user_id == dux_user_id)
            
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        # Execute with timeout
        result = await asyncio.wait_for(session.execute(query), timeout=15.0)
        campaigns = result.scalars().all()
        
        logger.info(f"Found {len(campaigns)} campaigns")
        
        # Create simple responses without contact counts (to avoid timeout)
        campaign_responses = []
        for c in campaigns:
            campaign_responses.append(CampaignResponse(
                campaign_id=str(c.campaign_id),
                campaign_key=str(c.campaign_key),
                name=c.name,
                description=c.description,
                target_title=c.target_title,
                intent=c.intent,
                status=c.status,
                dux_user_id=c.dux_user_id,
                scheduled_start=c.scheduled_start,
                end_date=c.end_date,
                created_at=c.created_at,
                updated_at=c.updated_at,
                settings=c.settings or {},
                initial_action=c.initial_action,
                follow_up_actions=c.follow_up_actions or [],
                total_contacts=0  # Skip contact count to avoid timeout
            ))
        
        logger.info(f"Returning {len(campaign_responses)} campaign responses")
        return campaign_responses
        
    except asyncio.TimeoutError:
        logger.error("Timeout listing campaigns")
        raise HTTPException(status_code=504, detail="Request timeout - database operation took too long")
    except Exception as e:
        logger.error(f"Error listing campaigns: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve campaigns")

@router.post("/campaigns", response_model=CampaignResponse, tags=["Campaigns"])
async def create_campaign_simple(
    campaign_data: CampaignCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new LinkedIn automation campaign with simplified error handling"""
    try:
        logger.info(f"Creating campaign: {campaign_data.name}")
        
        # Generate campaign key for external access
        campaign_key = str(uuid.uuid4())
        
        # Create campaign
        campaign = Campaign(
            campaign_key=campaign_key,
            name=campaign_data.name,
            description=campaign_data.description,
            target_title=campaign_data.target_title,
            intent=campaign_data.intent,
            status="active",
            dux_user_id=campaign_data.dux_user_id,
            scheduled_start=campaign_data.scheduled_start,
            end_date=campaign_data.end_date,
            settings=campaign_data.settings,
            initial_action=campaign_data.initial_action,
            follow_up_actions=campaign_data.follow_up_actions
        )
        
        session.add(campaign)
        await session.commit()
        await session.refresh(campaign)
        
        logger.info(f"Campaign created successfully: {campaign.campaign_id}")
        
        return CampaignResponse(
            campaign_id=str(campaign.campaign_id),
            campaign_key=str(campaign.campaign_key),
            name=campaign.name,
            description=campaign.description,
            target_title=campaign.target_title,
            intent=campaign.intent,
            status=campaign.status,
            dux_user_id=campaign.dux_user_id,
            scheduled_start=campaign.scheduled_start,
            end_date=campaign.end_date,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            settings=campaign.settings or {},
            initial_action=campaign.initial_action,
            follow_up_actions=campaign.follow_up_actions or [],
            total_contacts=0
        )
        
    except asyncio.TimeoutError:
        logger.error("Timeout creating campaign")
        await session.rollback()
        raise HTTPException(status_code=504, detail="Request timeout - database operation took too long")
    except Exception as e:
        logger.error(f"Error creating campaign: {e}", exc_info=True)
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create campaign: {str(e)}")
