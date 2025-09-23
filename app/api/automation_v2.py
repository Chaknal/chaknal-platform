"""
Enhanced LinkedIn Automation API v2

This module provides comprehensive API endpoints for LinkedIn automation
using the working DuxSoup wrapper and integrated campaign management.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from database.database import get_db
from app.services.linkedin_automation_v2 import linkedin_automation_service_v2
from app.schemas.automation import (
    CampaignExecutionResponse,
    AutomationStatusResponse,
    ContactUploadResponse,
    AutomationSettings,
    ContactUploadRequest,
    CampaignAutomationRequest,
    AutomationDashboardResponse,
    BatchActionRequest,
    QueueStatusResponse,
    CampaignMetricsResponse
)
from app.models.campaign import Campaign
from app.models.contact import Contact
from app.models.campaign_contact import CampaignContact
from app.models.duxsoup_user import DuxSoupUser
from app.core.logging_config import get_logger, PerformanceLogger

router = APIRouter(prefix="/api/automation/v2", tags=["LinkedIn Automation v2"])
logger = get_logger("app.api.automation_v2")


@router.post("/campaigns/{campaign_id}/execute", response_model=CampaignExecutionResponse)
async def execute_campaign_step(
    campaign_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Execute the next step of a LinkedIn automation campaign"""
    try:
        with PerformanceLogger(f"execute_campaign_step_{campaign_id}"):
            result = await linkedin_automation_service_v2.execute_campaign_step(campaign_id, db)
            
            if result["success"]:
                logger.info(
                    "Campaign step executed successfully",
                    campaign_id=campaign_id,
                    processed_contacts=result.get("processed_contacts", 0),
                    results_count=len(result.get("results", []))
                )
                
                # Add background task for cleanup
                background_tasks.add_task(
                    linkedin_automation_service_v2.cleanup_wrappers
                )
                
                return CampaignExecutionResponse(
                    success=True,
                    campaign_id=campaign_id,
                    message=f"Processed {result.get('processed_contacts', 0)} contacts",
                    details=result
                )
            else:
                logger.error(
                    "Campaign step execution failed",
                    campaign_id=campaign_id,
                    error=result.get("error")
                )
                raise HTTPException(status_code=400, detail=result.get("error"))
                
    except Exception as e:
        logger.error(
            "Error executing campaign step",
            campaign_id=campaign_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaigns/{campaign_id}/batch-actions", response_model=Dict[str, Any])
async def batch_queue_actions(
    campaign_id: str,
    request: BatchActionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Queue multiple LinkedIn actions in batch for a campaign"""
    try:
        with PerformanceLogger(f"batch_queue_actions_{campaign_id}"):
            result = await linkedin_automation_service_v2.batch_queue_actions(
                campaign_id, request.actions, db
            )
            
            if result["success"]:
                logger.info(
                    "Batch actions queued successfully",
                    campaign_id=campaign_id,
                    total_actions=result.get("total_actions", 0),
                    successful_actions=result.get("successful_actions", 0)
                )
                return result
            else:
                logger.error(
                    "Batch actions failed",
                    campaign_id=campaign_id,
                    error=result.get("error")
                )
                raise HTTPException(status_code=400, detail=result.get("error"))
                
    except Exception as e:
        logger.error(
            "Error in batch queue actions",
            campaign_id=campaign_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns/{campaign_id}/status", response_model=AutomationStatusResponse)
async def get_campaign_automation_status(
    campaign_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive automation status for a campaign"""
    try:
        with PerformanceLogger(f"get_campaign_status_{campaign_id}"):
            result = await linkedin_automation_service_v2.get_campaign_automation_status(
                campaign_id, db
            )
            
            if result["success"]:
                return AutomationStatusResponse(
                    success=True,
                    campaign_id=campaign_id,
                    campaign_name=result.get("campaign_name"),
                    status=result.get("status"),
                    contact_counts=result.get("contact_counts", {}),
                    total_contacts=result.get("total_contacts", 0),
                    recent_activity=result.get("recent_activity", []),
                    queue_status=result.get("queue_status")
                )
            else:
                raise HTTPException(status_code=404, detail=result.get("error"))
                
    except Exception as e:
        logger.error(
            "Error getting campaign automation status",
            campaign_id=campaign_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns/{campaign_id}/metrics", response_model=CampaignMetricsResponse)
async def get_campaign_metrics(
    campaign_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed metrics and analytics for a campaign"""
    try:
        with PerformanceLogger(f"get_campaign_metrics_{campaign_id}"):
            # Get campaign details
            from sqlalchemy import select, func
            from app.models.message import Message
            
            # Contact status distribution
            status_query = select(
                CampaignContact.status,
                func.count(CampaignContact.contact_id)
            ).where(
                CampaignContact.campaign_id == campaign_id
            ).group_by(CampaignContact.status)
            
            result = await db.execute(status_query)
            status_distribution = dict(result.fetchall())
            
            # Message statistics
            message_query = select(
                Message.message_type,
                Message.status,
                func.count(Message.message_id)
            ).join(CampaignContact).where(
                CampaignContact.campaign_id == campaign_id
            ).group_by(Message.message_type, Message.status)
            
            result = await db.execute(message_query)
            message_stats = {}
            for msg_type, status, count in result.fetchall():
                if msg_type not in message_stats:
                    message_stats[msg_type] = {}
                message_stats[msg_type][status] = count
            
            # Response rates
            total_sent = sum(
                count for status, count in message_stats.get("connection_request", {}).items()
                if status == "sent"
            )
            total_accepted = sum(
                count for status, count in message_stats.get("connection_request", {}).items()
                if status == "accepted"
            )
            
            response_rate = (total_accepted / total_sent * 100) if total_sent > 0 else 0
            
            return CampaignMetricsResponse(
                success=True,
                campaign_id=campaign_id,
                status_distribution=status_distribution,
                message_statistics=message_stats,
                response_rate=response_rate,
                total_contacts=sum(status_distribution.values()),
                total_messages=sum(
                    sum(counts.values()) for counts in message_stats.values()
                )
            )
            
    except Exception as e:
        logger.error(
            "Error getting campaign metrics",
            campaign_id=campaign_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue/status/{dux_user_id}", response_model=QueueStatusResponse)
async def get_queue_status(
    dux_user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get current queue status for a DuxSoup user"""
    try:
        with PerformanceLogger(f"get_queue_status_{dux_user_id}"):
            result = await linkedin_automation_service_v2.get_queue_status(dux_user_id, db)
            
            if result["success"]:
                return QueueStatusResponse(
                    success=True,
                    dux_user_id=dux_user_id,
                    queue_health=result.get("queue_health", {}),
                    wrapper_stats=result.get("wrapper_stats", {})
                )
            else:
                raise HTTPException(status_code=400, detail=result.get("error"))
                
    except Exception as e:
        logger.error(
            "Error getting queue status",
            dux_user_id=dux_user_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaigns/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Pause a LinkedIn automation campaign"""
    try:
        with PerformanceLogger(f"pause_campaign_{campaign_id}"):
            result = await linkedin_automation_service_v2.pause_campaign(campaign_id, db)
            
            if result["success"]:
                logger.info("Campaign paused successfully", campaign_id=campaign_id)
                return {"success": True, "message": "Campaign paused successfully"}
            else:
                raise HTTPException(status_code=400, detail=result.get("error"))
                
    except Exception as e:
        logger.error(
            "Error pausing campaign",
            campaign_id=campaign_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaigns/{campaign_id}/resume")
async def resume_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Resume a paused LinkedIn automation campaign"""
    try:
        with PerformanceLogger(f"resume_campaign_{campaign_id}"):
            result = await linkedin_automation_service_v2.resume_campaign(campaign_id, db)
            
            if result["success"]:
                logger.info("Campaign resumed successfully", campaign_id=campaign_id)
                return {"success": True, "message": "Campaign resumed successfully"}
            else:
                raise HTTPException(status_code=400, detail=result.get("error"))
                
    except Exception as e:
        logger.error(
            "Error resuming campaign",
            campaign_id=campaign_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard", response_model=AutomationDashboardResponse)
async def get_automation_dashboard(db: AsyncSession = Depends(get_db)):
    """Get comprehensive automation dashboard data"""
    try:
        with PerformanceLogger("get_automation_dashboard"):
            from sqlalchemy import select, func
            from datetime import datetime, timedelta
            
            # Get active campaigns count
            active_campaigns_query = select(func.count(Campaign.campaign_id)).where(
                Campaign.status == "active"
            )
            result = await db.execute(active_campaigns_query)
            active_campaigns = result.scalar()
            
            # Get total contacts
            total_contacts_query = select(func.count(Contact.contact_id))
            result = await db.execute(total_contacts_query)
            total_contacts = result.scalar()
            
            # Get recent activity (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_activity_query = select(Message).where(
                Message.created_at >= yesterday
            ).order_by(Message.created_at.desc()).limit(20)
            
            result = await db.execute(recent_activity_query)
            recent_messages = result.scalars().all()
            
            # Get DuxSoup users
            dux_users_query = select(DuxSoupUser)
            result = await db.execute(dux_users_query)
            dux_users = result.scalars().all()
            
            # Get queue status for all users
            queue_statuses = {}
            for dux_user in dux_users:
                try:
                    status = await linkedin_automation_service_v2.get_queue_status(
                        dux_user.dux_soup_user_id, db
                    )
                    if status["success"]:
                        queue_statuses[dux_user.dux_soup_user_id] = status
                except Exception as e:
                    logger.warning(
                        "Could not get queue status for user",
                        user_id=dux_user.dux_soup_user_id,
                        error=str(e)
                    )
            
            return AutomationDashboardResponse(
                success=True,
                active_campaigns=active_campaigns or 0,
                total_contacts=total_contacts or 0,
                recent_activity=[
                    {
                        "message_id": str(msg.message_id),
                        "message_type": msg.message_type,
                        "status": msg.status,
                        "created_at": msg.created_at.isoformat()
                    }
                    for msg in recent_messages
                ],
                dux_users_count=len(dux_users),
                queue_statuses=queue_statuses
            )
            
    except Exception as e:
        logger.error("Error getting automation dashboard", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/health-check")
async def perform_health_check():
    """Perform comprehensive health check of automation services"""
    try:
        with PerformanceLogger("health_check"):
            # Check if automation service is accessible
            health_status = {
                "automation_service": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "2.0.0"
            }
            
            logger.info("Health check completed successfully")
            return health_status
            
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cleanup")
async def cleanup_automation_services():
    """Clean up all automation services and wrappers"""
    try:
        with PerformanceLogger("cleanup_automation_services"):
            await linkedin_automation_service_v2.cleanup_wrappers()
            
            logger.info("Automation services cleaned up successfully")
            return {"success": True, "message": "Cleanup completed successfully"}
            
    except Exception as e:
        logger.error("Error during cleanup", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
