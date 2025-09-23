"""
LinkedIn Automation API Endpoints

This module provides API endpoints for managing LinkedIn automation campaigns
using the DuxSoup wrapper.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime

from database.database import get_session
from app.services.linkedin_automation import linkedin_automation_service
from app.models.campaign import Campaign, CampaignStatus
from app.models.contact import Contact
from app.models.campaign_contact import CampaignContact
from app.models.message import Message
from app.schemas.automation import (
    AutomationStatusResponse,
    CampaignExecutionResponse,
    ContactUploadResponse,
    AutomationSettings
)

router = APIRouter(prefix="/api/automation", tags=["LinkedIn Automation"])


@router.post("/campaigns/{campaign_id}/execute", response_model=CampaignExecutionResponse)
async def execute_campaign_step(
    campaign_id: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session)
):
    """
    Execute the next step of a LinkedIn automation campaign
    
    This endpoint will:
    1. Process contacts that need action
    2. Send connection requests or follow-up messages
    3. Update contact statuses
    4. Log all activities
    """
    try:
        # Execute campaign step
        result = await linkedin_automation_service.execute_campaign_step(campaign_id, session)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return CampaignExecutionResponse(
            success=True,
            campaign_id=campaign_id,
            processed=result["processed"],
            results=result["results"],
            executed_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute campaign: {str(e)}")


@router.get("/campaigns/{campaign_id}/status", response_model=AutomationStatusResponse)
async def get_campaign_automation_status(
    campaign_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get the current automation status of a campaign"""
    try:
        result = await linkedin_automation_service.get_campaign_automation_status(campaign_id, session)
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return AutomationStatusResponse(
            campaign_id=campaign_id,
            campaign_name=result["campaign_name"],
            status=result["status"],
            contact_counts=result["contact_counts"],
            total_contacts=result["total_contacts"],
            recent_activity=result["recent_activity"],
            last_updated=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get automation status: {str(e)}")


@router.post("/campaigns/{campaign_id}/pause")
async def pause_campaign_automation(
    campaign_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Pause a running LinkedIn automation campaign"""
    try:
        result = await linkedin_automation_service.pause_campaign(campaign_id, session)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {"success": True, "message": result["message"]}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to pause campaign: {str(e)}")


@router.post("/campaigns/{campaign_id}/resume")
async def resume_campaign_automation(
    campaign_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Resume a paused LinkedIn automation campaign"""
    try:
        result = await linkedin_automation_service.resume_campaign(campaign_id, session)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {"success": True, "message": result["message"]}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resume campaign: {str(e)}")


@router.post("/campaigns/{campaign_id}/contacts/upload")
async def upload_campaign_contacts(
    campaign_id: str,
    contacts: List[Dict[str, Any]],
    session: AsyncSession = Depends(get_session)
):
    """
    Upload contacts for a campaign
    
    Expected contact format:
    {
        "first_name": "John",
        "last_name": "Doe",
        "company": "Tech Corp",
        "linkedin_url": "https://linkedin.com/in/johndoe",
        "email": "john@techcorp.com",
        "title": "Software Engineer"
    }
    """
    try:
        # Validate campaign exists
        from sqlalchemy import select
        result = await session.execute(
            select(Campaign).where(Campaign.campaign_id == campaign_id)
        )
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        uploaded_contacts = []
        for contact_data in contacts:
            try:
                # Create or get contact
                contact = Contact(
                    first_name=contact_data.get("first_name"),
                    last_name=contact_data.get("last_name"),
                    company=contact_data.get("company"),
                    linkedin_url=contact_data.get("linkedin_url"),
                    email=contact_data.get("email"),
                    headline=contact_data.get("title")
                )
                session.add(contact)
                await session.flush()  # Get the ID
                
                # Create campaign contact relationship
                campaign_contact = CampaignContact(
                    campaign_id=campaign_id,
                    campaign_key=campaign.campaign_key,
                    contact_id=contact.contact_id,
                    status="enrolled"
                )
                session.add(campaign_contact)
                
                uploaded_contacts.append({
                    "contact_id": str(contact.contact_id),
                    "status": "enrolled",
                    "first_name": contact.first_name,
                    "last_name": contact.last_name,
                    "company": contact.company
                })
                
            except Exception as e:
                # Log error but continue with other contacts
                print(f"Error uploading contact {contact_data}: {e}")
                continue
        
        await session.commit()
        
        return ContactUploadResponse(
            success=True,
            campaign_id=campaign_id,
            uploaded_count=len(uploaded_contacts),
            contacts=uploaded_contacts
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to upload contacts: {str(e)}")


@router.get("/campaigns/{campaign_id}/contacts")
async def get_campaign_contacts(
    campaign_id: str,
    status: Optional[str] = Query(None, description="Filter by contact status"),
    limit: int = Query(100, le=1000, description="Maximum number of contacts to return"),
    offset: int = Query(0, ge=0, description="Number of contacts to skip"),
    session: AsyncSession = Depends(get_session)
):
    """Get contacts for a specific campaign"""
    try:
        from sqlalchemy import select
        
        query = select(CampaignContact, Contact).join(Contact).where(
            CampaignContact.campaign_id == campaign_id
        )
        
        if status:
            query = query.where(CampaignContact.status == status)
        
        query = query.offset(offset).limit(limit)
        
        result = await session.execute(query)
        rows = result.fetchall()
        
        contacts = []
        for campaign_contact, contact in rows:
            contacts.append({
                "campaign_contact_id": str(campaign_contact.campaign_contact_id),
                "contact_id": str(contact.contact_id),
                "first_name": contact.first_name,
                "last_name": contact.last_name,
                "company": contact.company,
                "linkedin_url": contact.linkedin_url,
                "email": contact.email,
                "status": campaign_contact.status,
                "enrolled_at": campaign_contact.enrolled_at.isoformat() if campaign_contact.enrolled_at else None,
                "sequence_step": campaign_contact.sequence_step
            })
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "contacts": contacts,
            "total": len(contacts)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get campaign contacts: {str(e)}")


@router.get("/dashboard")
async def get_automation_dashboard(session: AsyncSession = Depends(get_session)):
    """Get overview of all automation campaigns"""
    try:
        from sqlalchemy import select, func
        
        # Get campaign counts by status
        result = await session.execute(
            select(Campaign.status, func.count(Campaign.campaign_id)).group_by(Campaign.status)
        )
        campaign_counts = dict(result.fetchall())
        
        # Get total contacts across all campaigns
        result = await session.execute(
            select(func.count(CampaignContact.contact_id))
        )
        total_contacts = result.scalar() or 0
        
        # Get recent activity
        result = await session.execute(
            select(Message).join(CampaignContact).join(Campaign).order_by(
                Message.created_at.desc()
            ).limit(20)
        )
        recent_messages = result.scalars().all()
        
        # Get active campaigns
        result = await session.execute(
            select(Campaign).where(Campaign.status == CampaignStatus.ACTIVE)
        )
        active_campaigns = result.scalars().all()
        
        return {
            "success": True,
            "overview": {
                "total_campaigns": sum(campaign_counts.values()),
                "active_campaigns": campaign_counts.get(CampaignStatus.ACTIVE.value, 0),
                "paused_campaigns": campaign_counts.get(CampaignStatus.PAUSED.value, 0),
                "completed_campaigns": campaign_counts.get(CampaignStatus.COMPLETED.value, 0),
                "total_contacts": total_contacts
            },
            "recent_activity": [
                {
                    "message_id": str(msg.message_id),
                    "direction": msg.direction,
                    "status": msg.status,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in recent_messages
            ],
            "active_campaigns": [
                {
                    "campaign_id": str(campaign.campaign_id),
                    "name": campaign.name,
                    "status": campaign.status.value,
                    "created_at": campaign.created_at.isoformat()
                }
                for campaign in active_campaigns
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")
