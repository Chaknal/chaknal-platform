from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
import uuid

from database.database import get_session
from app.models.campaign_contact import CampaignContact
from app.models.contact import Contact

router = APIRouter()

@router.get("/campaigns/{campaign_id}/contacts", tags=["Campaign Contacts"])
async def get_campaign_contacts(
    campaign_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get all contacts for a specific campaign"""
    try:
        # Get campaign contacts with contact details
        query = select(CampaignContact, Contact).join(
            Contact, CampaignContact.contact_id == Contact.contact_id
        ).where(CampaignContact.campaign_id == uuid.UUID(campaign_id))
        
        result = await session.execute(query)
        campaign_contacts = result.fetchall()
        
        contacts = []
        for campaign_contact, contact in campaign_contacts:
            contacts.append({
                "contact_id": contact.contact_id,
                "campaign_contact_id": campaign_contact.campaign_contact_id,
                "full_name": contact.full_name,
                "email": contact.email,
                "company_name": contact.company_name,
                "job_title": contact.job_title,
                "location": contact.location,
                "status": campaign_contact.status,
                "assigned_to": campaign_contact.assigned_to,
                "data_source": contact.data_source,
                "last_contact": campaign_contact.last_contact,
                "linkedin_url": contact.linkedin_url,
                "created_at": campaign_contact.created_at
            })
        
        return {
            "campaign_id": campaign_id,
            "contacts": contacts,
            "total": len(contacts)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get campaign contacts: {str(e)}")

# Assignment endpoint moved to contact_assignment.py for better organization

@router.delete("/campaigns/{campaign_id}/contacts/{contact_id}", tags=["Campaign Contacts"])
async def remove_contact_from_campaign(
    campaign_id: str,
    contact_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Remove a contact from a campaign"""
    try:
        query = select(CampaignContact).where(
            and_(
                CampaignContact.campaign_id == uuid.UUID(campaign_id),
                CampaignContact.contact_id == contact_id
            )
        )
        result = await session.execute(query)
        campaign_contact = result.scalar_one_or_none()
        
        if not campaign_contact:
            raise HTTPException(status_code=404, detail="Contact not found in campaign")
        
        await session.delete(campaign_contact)
        await session.commit()
        
        return {"message": "Contact removed from campaign successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to remove contact: {str(e)}")

@router.get("/campaigns/{campaign_id}/contacts/stats", tags=["Campaign Contacts"])
async def get_campaign_contact_stats(
    campaign_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get contact statistics for a campaign"""
    try:
        # Get all campaign contacts
        query = select(CampaignContact).where(
            CampaignContact.campaign_id == uuid.UUID(campaign_id)
        )
        result = await session.execute(query)
        campaign_contacts = result.scalars().all()
        
        # Calculate statistics
        total_contacts = len(campaign_contacts)
        status_counts = {}
        assigned_counts = {}
        
        for contact in campaign_contacts:
            # Count by status
            status = contact.status or "unknown"
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by assignment
            assigned_to = contact.assigned_to or "unassigned"
            assigned_counts[assigned_to] = assigned_counts.get(assigned_to, 0) + 1
        
        return {
            "campaign_id": campaign_id,
            "total_contacts": total_contacts,
            "status_breakdown": status_counts,
            "assignment_breakdown": assigned_counts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get contact stats: {str(e)}")

