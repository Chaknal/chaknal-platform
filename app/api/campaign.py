from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
import uuid
from datetime import datetime
import logging
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)

def timeout_handler(timeout_seconds=15):
    """Decorator to add timeout to async functions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
            except asyncio.TimeoutError:
                logger.error(f"Function {func.__name__} timed out after {timeout_seconds} seconds")
                raise HTTPException(status_code=504, detail="Request timeout - operation took too long")
        return wrapper
    return decorator

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

# =============================================================================
# CAMPAIGN CRUD OPERATIONS
# =============================================================================

@router.post("/campaigns", response_model=CampaignResponse, tags=["Campaigns"])
@timeout_handler(timeout_seconds=20)
async def create_campaign(
    campaign_data: CampaignCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new LinkedIn automation campaign with DuxSoup scheduling"""
    try:
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
            # New DuxSoup workflow fields
            initial_action=campaign_data.initial_action,
            initial_message=campaign_data.initial_message,
            initial_subject=campaign_data.initial_subject,
            follow_up_actions=campaign_data.follow_up_actions,
            delay_days=campaign_data.delay_days,
            random_delay=campaign_data.random_delay
        )
        
        session.add(campaign)
        await session.commit()
        await session.refresh(campaign)
        
        # Schedule DuxSoup sequences if contacts are provided
        if hasattr(campaign_data, 'contacts') and campaign_data.contacts:
            from app.services.enhanced_campaign_service import EnhancedCampaignService
            
            campaign_service = EnhancedCampaignService()
            schedule_result = await campaign_service.create_and_schedule_campaign(
                campaign=campaign,
                contacts=campaign_data.contacts,
                session=session
            )
            
            if not schedule_result["success"]:
                logger.warning(f"Campaign created but scheduling failed: {schedule_result['error']}")
        
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
            settings=campaign.settings,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            # New DuxSoup workflow fields
            initial_action=campaign.initial_action,
            initial_message=campaign.initial_message,
            initial_subject=campaign.initial_subject,
            follow_up_actions=campaign.follow_up_actions,
            delay_days=campaign.delay_days,
            random_delay=campaign.random_delay
        )
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create campaign: {str(e)}")

@router.get("/campaigns", response_model=List[CampaignResponse], tags=["Campaigns"])
@timeout_handler(timeout_seconds=20)
async def list_campaigns(
    status: Optional[str] = Query(None, description="Filter by campaign status"),
    dux_user_id: Optional[str] = Query(None, description="Filter by Dux-Soup user ID"),
    limit: int = Query(100, le=1000, description="Maximum number of campaigns to return"),
    offset: int = Query(0, ge=0, description="Number of campaigns to skip"),
    session: AsyncSession = Depends(get_session)
):
    """List all campaigns with optional filtering"""
    try:
        query = select(Campaign)
        
        # Apply filters
        if status:
            query = query.where(Campaign.status == status)
        if dux_user_id:
            query = query.where(Campaign.dux_user_id == dux_user_id)
            
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        result = await session.execute(query)
        campaigns = result.scalars().all()
        
        # Create simple responses without complex contact counts to avoid timeout
        campaign_responses = []
        for c in campaigns:
            # Skip complex contact counting for now to avoid timeout
            # Just return campaigns with basic info
            total_contacts = 0  # Simplified - no contact count to avoid timeout
            accepted_contacts = 0
            replied_contacts = 0
            acceptance_rate = 0.0
            reply_rate = 0.0
            
            campaign_responses.append(CampaignResponse(
                campaign_id=str(c.campaign_id),
                campaign_key=str(c.campaign_key),
                name=c.name,
                description=c.description,
                target_title=c.target_title,
                intent=c.intent,
                status=str(c.status),
                dux_user_id=c.dux_user_id,
                scheduled_start=c.scheduled_start,
                end_date=c.end_date,
                settings=c.settings,
                created_at=c.created_at,
                updated_at=c.updated_at or c.created_at,  # Use created_at if updated_at is None
                # DuxSoup workflow fields
                initial_action=c.initial_action or "inmail",
                initial_message=c.initial_message,
                initial_subject=c.initial_subject,
                follow_up_actions=c.follow_up_actions or [],
                delay_days=c.delay_days or 1,
                random_delay=c.random_delay if c.random_delay is not None else True,
                # Contact statistics (simplified to avoid timeout)
                total_contacts=total_contacts,
                accepted_contacts=accepted_contacts,
                replied_contacts=replied_contacts,
                acceptance_rate=acceptance_rate,
                reply_rate=reply_rate
            ))
        
        return campaign_responses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list campaigns: {str(e)}")

@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse, tags=["Campaigns"])
async def get_campaign(
    campaign_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get a specific campaign by ID"""
    try:
        query = select(Campaign).where(Campaign.campaign_id == campaign_id)
        result = await session.execute(query)
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
            
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
            settings=campaign.settings,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            # New DuxSoup workflow fields
            initial_action=campaign.initial_action or "inmail",
            initial_message=campaign.initial_message,
            initial_subject=campaign.initial_subject,
            follow_up_actions=campaign.follow_up_actions,
            delay_days=campaign.delay_days or 1,
            random_delay=campaign.random_delay if campaign.random_delay is not None else True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get campaign: {str(e)}")

@router.put("/campaigns/{campaign_id}", response_model=CampaignResponse, tags=["Campaigns"])
async def update_campaign(
    campaign_id: str,
    campaign_data: CampaignUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update an existing campaign"""
    try:
        query = select(Campaign).where(Campaign.campaign_id == campaign_id)
        result = await session.execute(query)
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
            
        # Update fields
        update_data = campaign_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(campaign, field, value)
            
        campaign.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(campaign)
        
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
            settings=campaign.settings,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            # New DuxSoup workflow fields
            initial_action=campaign.initial_action or "inmail",
            initial_message=campaign.initial_message,
            initial_subject=campaign.initial_subject,
            follow_up_actions=campaign.follow_up_actions,
            delay_days=campaign.delay_days or 1,
            random_delay=campaign.random_delay if campaign.random_delay is not None else True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update campaign: {str(e)}")

@router.delete("/campaigns/{campaign_id}", tags=["Campaigns"])
async def delete_campaign(
    campaign_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Delete a campaign and all associated data"""
    try:
        query = select(Campaign).where(Campaign.campaign_id == campaign_id)
        result = await session.execute(query)
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
            
        await session.delete(campaign)
        await session.commit()
        
        return {"message": "Campaign deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete campaign: {str(e)}")

# =============================================================================
# CAMPAIGN STATUS MANAGEMENT
# =============================================================================

@router.patch("/campaigns/{campaign_id}/status", tags=["Campaigns"])
async def update_campaign_status(
    campaign_id: str,
    status: CampaignStatus,
    session: AsyncSession = Depends(get_session)
):
    """Update campaign status (active, paused, completed, archived)"""
    try:
        query = select(Campaign).where(Campaign.campaign_id == campaign_id)
        result = await session.execute(query)
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
            
        campaign.status = status.value if hasattr(status, 'value') else str(status)
        campaign.updated_at = datetime.utcnow()
        
        await session.commit()
        
        return {"message": f"Campaign status updated to {status}"}
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update campaign status: {str(e)}")

# =============================================================================
# CAMPAIGN ANALYTICS & STATISTICS
# =============================================================================

@router.get("/campaigns/{campaign_id}/stats", response_model=CampaignStatsResponse, tags=["Campaigns"])
async def get_campaign_stats(
    campaign_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get comprehensive statistics for a campaign"""
    try:
        # Get campaign
        query = select(Campaign).where(Campaign.campaign_id == campaign_id)
        result = await session.execute(query)
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
            
        # Count contacts
        contacts_query = select(func.count(CampaignContact.contact_id)).where(
            CampaignContact.campaign_id == campaign_id
        )
        result = await session.execute(contacts_query)
        total_contacts = result.scalar()
        
        # Count by status
        status_query = select(
            CampaignContact.status,
            func.count(CampaignContact.contact_id)
        ).where(
            CampaignContact.campaign_id == campaign_id
        ).group_by(CampaignContact.status)
        
        result = await session.execute(status_query)
        status_counts = dict(result.fetchall())
        
        # Count messages
        messages_query = select(func.count(Message.message_id)).join(
            CampaignContact, Message.campaign_contact_id == CampaignContact.campaign_contact_id
        ).where(CampaignContact.campaign_id == campaign_id)
        
        result = await session.execute(messages_query)
        total_messages = result.scalar()
        
        return CampaignStatsResponse(
            campaign_id=str(campaign.campaign_id),
            campaign_name=campaign.name,
            total_contacts=total_contacts or 0,
            contacts_by_status=status_counts,
            total_messages=total_messages or 0,
            created_at=campaign.created_at,
            last_updated=campaign.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get campaign stats: {str(e)}")

# =============================================================================
# CAMPAIGN BY KEY (for external integrations)
# =============================================================================

@router.get("/campaigns/key/{campaign_key}", response_model=CampaignResponse, tags=["Campaigns"])
async def get_campaign_by_key(
    campaign_key: str,
    session: AsyncSession = Depends(get_session)
):
    """Get a campaign by its external campaign key"""
    try:
        query = select(Campaign).where(Campaign.campaign_key == campaign_key)
        result = await session.execute(query)
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
            
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
            settings=campaign.settings,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            # New DuxSoup workflow fields
            initial_action=campaign.initial_action or "inmail",
            initial_message=campaign.initial_message,
            initial_subject=campaign.initial_subject,
            follow_up_actions=campaign.follow_up_actions,
            delay_days=campaign.delay_days or 1,
            random_delay=campaign.random_delay if campaign.random_delay is not None else True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get campaign: {str(e)}")
