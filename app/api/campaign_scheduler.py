from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime
import uuid

from database.database import get_session
from app.services.campaign_scheduler import CampaignScheduler
from app.models.campaign import Campaign

router = APIRouter()

@router.get("/campaigns/{campaign_id}/schedule/status", tags=["Campaign Scheduler"])
async def get_campaign_schedule_status(
    campaign_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get the current schedule status of a campaign"""
    try:
        is_active = await CampaignScheduler.is_campaign_active(campaign_id, session)
        
        # Get campaign details
        query = select(Campaign).where(Campaign.campaign_id == uuid.UUID(campaign_id))
        result = await session.execute(query)
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        return {
            "campaign_id": campaign_id,
            "is_active": is_active,
            "status": campaign.status,
            "scheduled_start": campaign.scheduled_start,
            "end_date": campaign.end_date,
            "can_send_messages": is_active
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get schedule status: {str(e)}")

@router.get("/campaigns/{campaign_id}/schedule/ready-contacts", tags=["Campaign Scheduler"])
async def get_contacts_ready_for_message(
    campaign_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get contacts that are ready to receive their next message"""
    try:
        ready_contacts = await CampaignScheduler.get_contacts_ready_for_message(campaign_id, session)
        
        return {
            "campaign_id": campaign_id,
            "ready_contacts": ready_contacts,
            "count": len(ready_contacts)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get ready contacts: {str(e)}")

@router.post("/campaigns/{campaign_id}/schedule/start", tags=["Campaign Scheduler"])
async def start_campaign(
    campaign_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Manually start a campaign"""
    try:
        success = await CampaignScheduler.start_campaign(campaign_id, session)
        
        if success:
            return {"message": "Campaign started successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to start campaign")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start campaign: {str(e)}")

@router.post("/campaigns/{campaign_id}/schedule/end", tags=["Campaign Scheduler"])
async def end_campaign(
    campaign_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Manually end a campaign"""
    try:
        success = await CampaignScheduler.end_campaign(campaign_id, session)
        
        if success:
            return {"message": "Campaign ended successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to end campaign")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end campaign: {str(e)}")

@router.get("/campaigns/schedule/auto-start", tags=["Campaign Scheduler"])
async def get_campaigns_to_start(
    session: AsyncSession = Depends(get_session)
):
    """Get campaigns that should be started automatically"""
    try:
        campaigns = await CampaignScheduler.get_campaigns_to_start(session)
        
        return {
            "campaigns_to_start": [
                {
                    "campaign_id": str(c.campaign_id),
                    "name": c.name,
                    "scheduled_start": c.scheduled_start,
                    "end_date": c.end_date
                }
                for c in campaigns
            ],
            "count": len(campaigns)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get campaigns to start: {str(e)}")

@router.get("/campaigns/schedule/auto-end", tags=["Campaign Scheduler"])
async def get_campaigns_to_end(
    session: AsyncSession = Depends(get_session)
):
    """Get campaigns that should be ended automatically"""
    try:
        campaigns = await CampaignScheduler.get_campaigns_to_end(session)
        
        return {
            "campaigns_to_end": [
                {
                    "campaign_id": str(c.campaign_id),
                    "name": c.name,
                    "scheduled_start": c.scheduled_start,
                    "end_date": c.end_date
                }
                for c in campaigns
            ],
            "count": len(campaigns)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get campaigns to end: {str(e)}")

@router.post("/campaigns/schedule/auto-process", tags=["Campaign Scheduler"])
async def auto_process_campaigns(
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session)
):
    """Automatically process campaigns (start/end based on dates)"""
    try:
        # Get campaigns to start
        campaigns_to_start = await CampaignScheduler.get_campaigns_to_start(session)
        
        # Get campaigns to end
        campaigns_to_end = await CampaignScheduler.get_campaigns_to_end(session)
        
        # Start campaigns in background
        for campaign in campaigns_to_start:
            background_tasks.add_task(
                CampaignScheduler.start_campaign,
                str(campaign.campaign_id),
                session
            )
        
        # End campaigns in background
        for campaign in campaigns_to_end:
            background_tasks.add_task(
                CampaignScheduler.end_campaign,
                str(campaign.campaign_id),
                session
            )
        
        return {
            "message": "Campaign processing started",
            "campaigns_started": len(campaigns_to_start),
            "campaigns_ended": len(campaigns_to_end)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process campaigns: {str(e)}")

@router.get("/campaigns/{campaign_id}/schedule/next-message-time/{contact_id}", tags=["Campaign Scheduler"])
async def get_next_message_time(
    campaign_id: str,
    contact_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get when the next message should be sent to a specific contact"""
    try:
        next_time = await CampaignScheduler.get_next_message_time(campaign_id, contact_id, session)
        
        if next_time:
            return {
                "campaign_id": campaign_id,
                "contact_id": contact_id,
                "next_message_time": next_time,
                "can_send_now": next_time <= datetime.utcnow()
            }
        else:
            return {
                "campaign_id": campaign_id,
                "contact_id": contact_id,
                "next_message_time": None,
                "can_send_now": False,
                "reason": "Campaign ended or no more messages scheduled"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get next message time: {str(e)}")
