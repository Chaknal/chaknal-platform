"""
DuxSoup Sync API
Pulls DuxSoup status back to PostgreSQL database
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from database.database import get_session
from app.models.campaign import Campaign
from app.models.campaign_contact import CampaignContact
from app.models.contact import Contact
from app.models.message import Message
from app.models.duxsoup_user import DuxSoupUser
from app.services.enhanced_duxwrap import EnhancedDuxWrap

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/sync/status/{campaign_id}", tags=["DuxSoup Sync"])
async def get_campaign_sync_status(
    campaign_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get sync status for a specific campaign"""
    try:
        # Get campaign
        query = select(Campaign).where(Campaign.campaign_id == campaign_id)
        result = await session.execute(query)
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Get DuxSoup user config
        dux_config_query = select(DuxSoupUser).where(DuxSoupUser.user_id == campaign.dux_user_id)
        dux_config_result = await session.execute(dux_config_query)
        dux_user = dux_config_result.scalar_one_or_none()
        
        if not dux_user:
            return {
                "campaign_id": campaign_id,
                "sync_status": "error",
                "error": "DuxSoup user not configured"
            }
        
        # Get campaign contacts
        contacts_query = select(CampaignContact, Contact).join(
            Contact, CampaignContact.contact_id == Contact.id
        ).where(CampaignContact.campaign_id == campaign_id)
        
        contacts_result = await session.execute(contacts_query)
        campaign_contacts = contacts_result.all()
        
        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign.name,
            "sync_status": "active",
            "total_contacts": len(campaign_contacts),
            "dux_user_id": campaign.dux_user_id,
            "last_sync": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sync status: {str(e)}")


@router.post("/sync/campaign/{campaign_id}", tags=["DuxSoup Sync"])
async def sync_campaign_status(
    campaign_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Sync DuxSoup status for a campaign back to database"""
    try:
        # Get campaign
        query = select(Campaign).where(Campaign.campaign_id == campaign_id)
        result = await session.execute(query)
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Get DuxSoup user config
        dux_config_query = select(DuxSoupUser).where(DuxSoupUser.user_id == campaign.dux_user_id)
        dux_config_result = await session.execute(dux_config_query)
        dux_user = dux_config_result.scalar_one_or_none()
        
        if not dux_user:
            raise HTTPException(status_code=404, detail="DuxSoup user not configured")
        
        # Initialize DuxSoup wrapper
        dux = EnhancedDuxWrap(
            api_key=dux_user.api_key,
            user_id=dux_user.dux_user_id
        )
        
        # Get DuxSoup queue status
        queue_status = await _get_dux_queue_status(dux)
        
        # Update campaign status in database
        await _update_campaign_status(campaign, queue_status, session)
        
        return {
            "campaign_id": campaign_id,
            "sync_status": "completed",
            "queue_size": queue_status.get("queue_size", 0),
            "processed_messages": queue_status.get("processed", 0),
            "failed_messages": queue_status.get("failed", 0),
            "last_sync": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error syncing campaign: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to sync campaign: {str(e)}")


@router.get("/sync/queue/{dux_user_id}", tags=["DuxSoup Sync"])
async def get_dux_queue_status(
    dux_user_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get DuxSoup queue status for a user"""
    try:
        # Get DuxSoup user config
        query = select(DuxSoupUser).where(DuxSoupUser.user_id == dux_user_id)
        result = await session.execute(query)
        dux_user = result.scalar_one_or_none()
        
        if not dux_user:
            raise HTTPException(status_code=404, detail="DuxSoup user not found")
        
        # Initialize DuxSoup wrapper
        dux = EnhancedDuxWrap(
            api_key=dux_user.api_key,
            user_id=dux_user.dux_user_id
        )
        
        # Get queue status
        queue_status = await _get_dux_queue_status(dux)
        
        return {
            "dux_user_id": dux_user_id,
            "queue_status": queue_status,
            "last_checked": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting queue status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get queue status: {str(e)}")


@router.post("/sync/bulk", tags=["DuxSoup Sync"])
async def bulk_sync_campaigns(
    campaign_ids: List[str] = Query(..., description="List of campaign IDs to sync"),
    session: AsyncSession = Depends(get_session)
):
    """Bulk sync multiple campaigns"""
    try:
        results = []
        
        for campaign_id in campaign_ids:
            try:
                # Get campaign
                query = select(Campaign).where(Campaign.campaign_id == campaign_id)
                result = await session.execute(query)
                campaign = result.scalar_one_or_none()
                
                if not campaign:
                    results.append({
                        "campaign_id": campaign_id,
                        "status": "error",
                        "error": "Campaign not found"
                    })
                    continue
                
                # Get DuxSoup user config
                dux_config_query = select(DuxSoupUser).where(DuxSoupUser.user_id == campaign.dux_user_id)
                dux_config_result = await session.execute(dux_config_query)
                dux_user = dux_config_result.scalar_one_or_none()
                
                if not dux_user:
                    results.append({
                        "campaign_id": campaign_id,
                        "status": "error",
                        "error": "DuxSoup user not configured"
                    })
                    continue
                
                # Initialize DuxSoup wrapper
                dux = EnhancedDuxWrap(
                    api_key=dux_user.api_key,
                    user_id=dux_user.dux_user_id
                )
                
                # Get queue status
                queue_status = await _get_dux_queue_status(dux)
                
                # Update campaign status
                await _update_campaign_status(campaign, queue_status, session)
                
                results.append({
                    "campaign_id": campaign_id,
                    "status": "success",
                    "queue_size": queue_status.get("queue_size", 0),
                    "processed": queue_status.get("processed", 0)
                })
                
            except Exception as e:
                results.append({
                    "campaign_id": campaign_id,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "bulk_sync_status": "completed",
            "total_campaigns": len(campaign_ids),
            "results": results,
            "last_sync": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in bulk sync: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to bulk sync: {str(e)}")


async def _get_dux_queue_status(dux: EnhancedDuxWrap) -> Dict[str, Any]:
    """
    Get DuxSoup queue status
    
    Args:
        dux: Enhanced DuxSoup wrapper
        
    Returns:
        Queue status dictionary
    """
    
    try:
        # This would use the existing DuxWrap functionality
        # For now, return a placeholder structure
        
        # TODO: Implement actual queue status checking
        # This would involve calling dux.call('size', {}) and dux.call('items', {})
        # and analyzing the results
        
        return {
            "queue_size": 0,
            "processed": 0,
            "failed": 0,
            "pending": 0
        }
        
    except Exception as e:
        logger.error(f"Error getting queue status: {e}")
        return {
            "queue_size": 0,
            "processed": 0,
            "failed": 0,
            "pending": 0,
            "error": str(e)
        }


async def _update_campaign_status(
    campaign: Campaign,
    queue_status: Dict[str, Any],
    session: AsyncSession
):
    """
    Update campaign status based on DuxSoup queue status
    
    Args:
        campaign: Campaign object
        queue_status: Queue status from DuxSoup
        session: Database session
    """
    
    try:
        # Update campaign with sync information
        await session.execute(
            update(Campaign).where(
                Campaign.campaign_id == campaign.campaign_id
            ).values(
                updated_at=datetime.utcnow(),
                settings={
                    **campaign.settings,
                    "last_sync": datetime.utcnow().isoformat(),
                    "queue_status": queue_status
                }
            )
        )
        
        await session.commit()
        
    except Exception as e:
        logger.error(f"Error updating campaign status: {e}")
        await session.rollback()
