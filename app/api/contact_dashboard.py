from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import uuid

from database.database import get_session
from app.models.contact import Contact
from app.models.campaign import Campaign
from app.models.campaign_contact import CampaignContact
from app.models.message import Message
from app.models.company import Company

router = APIRouter(prefix="/api/contact-dashboard", tags=["Contact Dashboard"])

# =============================================================================
# SCHEMAS
# =============================================================================

class ContactAnalytics(BaseModel):
    """Contact analytics summary"""
    total_contacts: int
    total_companies: int
    contacts_with_email: int
    contacts_with_phone: int
    contacts_with_linkedin: int
    average_lead_score: float
    top_industries: List[Dict[str, Any]]
    top_companies: List[Dict[str, Any]]
    top_locations: List[Dict[str, Any]]
    lead_score_distribution: List[Dict[str, Any]]
    growth_trend: List[Dict[str, Any]]

class ContactActivity(BaseModel):
    """Contact activity summary"""
    total_messages_sent: int
    total_connection_requests: int
    total_profile_visits: int
    total_replies: int
    total_acceptances: int
    activity_timeline: List[Dict[str, Any]]
    top_performing_contacts: List[Dict[str, Any]]

class ContactSegment(BaseModel):
    """Contact segmentation data"""
    segment_name: str
    criteria: Dict[str, Any]
    contact_count: int
    average_lead_score: float
    engagement_rate: float
    contacts: List[Dict[str, Any]]

class ContactExportRequest(BaseModel):
    """Contact export request"""
    format: str = Field(default="csv", description="Export format: csv, json, xlsx")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filter criteria")
    fields: List[str] = Field(default_factory=lambda: ["first_name", "last_name", "company", "email", "linkedin_url"])
    include_analytics: bool = Field(default=False, description="Include analytics data")

class ContactBulkAction(BaseModel):
    """Bulk action request"""
    action: str = Field(..., description="Action to perform: tag, untag, delete, export, enrich")
    contact_ids: List[str] = Field(..., description="Contact IDs to act on")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Action parameters")

class ContactTagRequest(BaseModel):
    """Contact tagging request"""
    contact_ids: List[str] = Field(..., description="Contact IDs to tag")
    tags: List[str] = Field(..., description="Tags to add")
    action: str = Field(default="add", description="Action: add, remove, replace")

class ContactNoteRequest(BaseModel):
    """Contact note request"""
    contact_id: str = Field(..., description="Contact ID")
    note: str = Field(..., description="Note content")
    note_type: str = Field(default="general", description="Note type: general, call, meeting, follow_up")

# =============================================================================
# DASHBOARD OVERVIEW
# =============================================================================

@router.get("/overview", response_model=Dict[str, Any])
async def get_dashboard_overview(
    session: AsyncSession = Depends(get_session)
):
    """Get comprehensive dashboard overview"""
    try:
        # Get basic counts
        contact_count = await _get_contact_count(session)
        company_count = await _get_company_count(session)
        campaign_count = await _get_campaign_count(session)
        
        # Get recent activity
        recent_contacts = await _get_recent_contacts(session, limit=5)
        recent_activity = await _get_recent_activity(session, limit=10)
        
        # Get quick stats
        quick_stats = await _get_quick_stats(session)
        
        return {
            "summary": {
                "total_contacts": contact_count,
                "total_companies": company_count,
                "total_campaigns": campaign_count,
                "last_updated": datetime.utcnow()
            },
            "recent_contacts": recent_contacts,
            "recent_activity": recent_activity,
            "quick_stats": quick_stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard overview: {str(e)}"
        )

@router.get("/analytics", response_model=ContactAnalytics)
async def get_contact_analytics(
    date_from: Optional[datetime] = Query(None, description="Start date for analytics"),
    date_to: Optional[datetime] = Query(None, description="End date for analytics"),
    session: AsyncSession = Depends(get_session)
):
    """Get detailed contact analytics"""
    try:
        # Set default date range if not provided
        if not date_from:
            date_from = datetime.utcnow() - timedelta(days=30)
        if not date_to:
            date_to = datetime.utcnow()
        
        # Get basic counts
        total_contacts = await _get_contact_count(session)
        total_companies = await _get_company_count(session)
        
        # Get contact information availability
        contacts_with_email = await _get_contacts_with_field(session, "email")
        contacts_with_phone = await _get_contacts_with_field(session, "phone")
        contacts_with_linkedin = await _get_contacts_with_field(session, "linkedin_url")
        
        # Get lead score analytics
        average_lead_score = await _get_average_lead_score(session)
        lead_score_distribution = await _get_lead_score_distribution(session)
        
        # Get top categories
        top_industries = await _get_top_categories(session, "industry", limit=10)
        top_companies = await _get_top_categories(session, "company", limit=10)
        top_locations = await _get_top_categories(session, "location", limit=10)
        
        # Get growth trend
        growth_trend = await _get_growth_trend(session, date_from, date_to)
        
        return ContactAnalytics(
            total_contacts=total_contacts,
            total_companies=total_companies,
            contacts_with_email=contacts_with_email,
            contacts_with_phone=contacts_with_phone,
            contacts_with_linkedin=contacts_with_linkedin,
            average_lead_score=average_lead_score,
            top_industries=top_industries,
            top_companies=top_companies,
            top_locations=top_locations,
            lead_score_distribution=lead_score_distribution,
            growth_trend=growth_trend
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get contact analytics: {str(e)}"
        )

@router.get("/activity", response_model=ContactActivity)
async def get_contact_activity(
    date_from: Optional[datetime] = Query(None, description="Start date for activity"),
    date_to: Optional[datetime] = Query(None, description="End date for activity"),
    session: AsyncSession = Depends(get_session)
):
    """Get contact activity summary"""
    try:
        # Set default date range if not provided
        if not date_from:
            date_from = datetime.utcnow() - timedelta(days=30)
        if not date_to:
            date_to = datetime.utcnow()
        
        # Get activity counts
        total_messages_sent = await _get_message_count(session, date_from, date_to)
        total_connection_requests = await _get_connection_request_count(session, date_from, date_to)
        total_profile_visits = await _get_profile_visit_count(session, date_from, date_to)
        total_replies = await _get_reply_count(session, date_from, date_to)
        total_acceptances = await _get_acceptance_count(session, date_from, date_to)
        
        # Get activity timeline
        activity_timeline = await _get_activity_timeline(session, date_from, date_to)
        
        # Get top performing contacts
        top_performing_contacts = await _get_top_performing_contacts(session, date_from, date_to)
        
        return ContactActivity(
            total_messages_sent=total_messages_sent,
            total_connection_requests=total_connection_requests,
            total_profile_visits=total_profile_visits,
            total_replies=total_replies,
            total_acceptances=total_acceptances,
            activity_timeline=activity_timeline,
            top_performing_contacts=top_performing_contacts
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get contact activity: {str(e)}"
        )

# =============================================================================
# CONTACT SEGMENTATION
# =============================================================================

@router.get("/segments", response_model=List[ContactSegment])
async def get_contact_segments(
    session: AsyncSession = Depends(get_session)
):
    """Get predefined contact segments"""
    try:
        segments = []
        
        # High-value prospects (lead score > 80)
        high_value = await _get_segment_contacts(
            session, 
            "High-Value Prospects", 
            {"lead_score_min": 80},
            limit=50
        )
        segments.append(high_value)
        
        # Decision makers (CEO, Founder, Director, etc.)
        decision_makers = await _get_segment_contacts(
            session,
            "Decision Makers",
            {"titles": ["ceo", "founder", "president", "director", "vp"]},
            limit=50
        )
        segments.append(decision_makers)
        
        # Recent contacts (created in last 7 days)
        recent_contacts = await _get_segment_contacts(
            session,
            "Recent Contacts",
            {"created_after": datetime.utcnow() - timedelta(days=7)},
            limit=50
        )
        segments.append(recent_contacts)
        
        # Engaged contacts (has messages or connections)
        engaged_contacts = await _get_segment_contacts(
            session,
            "Engaged Contacts",
            {"has_activity": True},
            limit=50
        )
        segments.append(engaged_contacts)
        
        # Missing information (no email or phone)
        missing_info = await _get_segment_contacts(
            session,
            "Missing Information",
            {"missing_fields": ["email", "phone"]},
            limit=50
        )
        segments.append(missing_info)
        
        return segments
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get contact segments: {str(e)}"
        )

@router.post("/segments/custom", response_model=ContactSegment)
async def create_custom_segment(
    segment_name: str,
    criteria: Dict[str, Any],
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session)
):
    """Create a custom contact segment"""
    try:
        segment = await _get_segment_contacts(
            session, segment_name, criteria, limit
        )
        return segment
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create custom segment: {str(e)}"
        )

# =============================================================================
# CONTACT MANAGEMENT
# =============================================================================

@router.post("/tags", response_model=Dict[str, Any])
async def manage_contact_tags(
    request: ContactTagRequest,
    session: AsyncSession = Depends(get_session)
):
    """Manage contact tags"""
    try:
        updated_count = 0
        
        for contact_id in request.contact_ids:
            result = await session.execute(
                select(Contact).where(Contact.contact_id == contact_id)
            )
            contact = result.scalar_one_or_none()
            
            if contact:
                if request.action == "add":
                    # Add new tags
                    existing_tags = contact.tags or []
                    new_tags = [tag for tag in request.tags if tag not in existing_tags]
                    contact.tags = existing_tags + new_tags
                    
                elif request.action == "remove":
                    # Remove specified tags
                    existing_tags = contact.tags or []
                    contact.tags = [tag for tag in existing_tags if tag not in request.tags]
                    
                elif request.action == "replace":
                    # Replace all tags
                    contact.tags = request.tags
                
                contact.updated_at = datetime.utcnow()
                updated_count += 1
        
        await session.commit()
        
        return {
            "success": True,
            "message": f"Updated tags for {updated_count} contacts",
            "updated_count": updated_count
        }
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to manage contact tags: {str(e)}"
        )

@router.post("/notes", response_model=Dict[str, Any])
async def add_contact_note(
    request: ContactNoteRequest,
    session: AsyncSession = Depends(get_session)
):
    """Add a note to a contact"""
    try:
        result = await session.execute(
            select(Contact).where(Contact.contact_id == request.contact_id)
        )
        contact = result.scalar_one_or_none()
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        
        # Add note to profile data
        if not contact.profile_data:
            contact.profile_data = {}
        
        if "notes" not in contact.profile_data:
            contact.profile_data["notes"] = []
        
        note_data = {
            "id": str(uuid.uuid4()),
            "content": request.note,
            "type": request.note_type,
            "created_at": datetime.utcnow().isoformat()
        }
        
        contact.profile_data["notes"].append(note_data)
        contact.updated_at = datetime.utcnow()
        
        await session.commit()
        
        return {
            "success": True,
            "message": "Note added successfully",
            "note": note_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add note: {str(e)}"
        )

@router.post("/bulk-actions", response_model=Dict[str, Any])
async def perform_bulk_action(
    request: ContactBulkAction,
    session: AsyncSession = Depends(get_session)
):
    """Perform bulk actions on contacts"""
    try:
        if request.action == "tag":
            # Handle tagging
            tag_request = ContactTagRequest(
                contact_ids=request.contact_ids,
                tags=request.parameters.get("tags", []),
                action=request.parameters.get("action", "add")
            )
            return await manage_contact_tags(tag_request, session)
            
        elif request.action == "delete":
            # Handle deletion
            deleted_count = await _bulk_delete_contacts(session, request.contact_ids)
            return {
                "success": True,
                "message": f"Deleted {deleted_count} contacts",
                "deleted_count": deleted_count
            }
            
        elif request.action == "export":
            # Handle export
            export_data = await _bulk_export_contacts(session, request.contact_ids, request.parameters)
            return {
                "success": True,
                "message": "Export completed",
                "export_data": export_data
            }
            
        elif request.action == "enrich":
            # Handle enrichment
            enriched_count = await _bulk_enrich_contacts(session, request.contact_ids)
            return {
                "success": True,
                "message": f"Enriched {enriched_count} contacts",
                "enriched_count": enriched_count
            }
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown action: {request.action}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform bulk action: {str(e)}"
        )

# =============================================================================
# EXPORT & REPORTING
# =============================================================================

@router.post("/export", response_model=Dict[str, Any])
async def export_contacts(
    request: ContactExportRequest,
    session: AsyncSession = Depends(get_session)
):
    """Export contacts based on criteria"""
    try:
        # Build query based on filters
        query = select(Contact)
        
        if request.filters:
            query = _apply_export_filters(query, request.filters)
        
        # Execute query
        result = await session.execute(query)
        contacts = result.scalars().all()
        
        # Prepare export data
        export_data = []
        for contact in contacts:
            contact_data = {}
            for field in request.fields:
                if field == "tags":
                    contact_data[field] = ", ".join(contact.tags or [])
                elif field == "lead_score":
                    contact_data[field] = contact.profile_data.get("lead_score", 0) if contact.profile_data else 0
                elif hasattr(contact, field):
                    contact_data[field] = getattr(contact, field)
                else:
                    contact_data[field] = None
            
            if request.include_analytics:
                contact_data["analytics"] = await _get_contact_analytics(session, contact.contact_id)
            
            export_data.append(contact_data)
        
        # Format export based on requested format
        if request.format.lower() == "json":
            return {
                "success": True,
                "format": "json",
                "data": export_data,
                "total_contacts": len(export_data)
            }
        elif request.format.lower() == "csv":
            # Return CSV data (frontend can handle conversion)
            return {
                "success": True,
                "format": "csv",
                "data": export_data,
                "total_contacts": len(export_data)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported export format: {request.format}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export contacts: {str(e)}"
        )

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def _get_contact_count(session: AsyncSession) -> int:
    """Get total contact count"""
    result = await session.execute(select(func.count(Contact.contact_id)))
    return result.scalar() or 0

async def _get_company_count(session: AsyncSession) -> int:
    """Get total company count"""
    result = await session.execute(select(func.count(Company.id)))
    return result.scalar() or 0

async def _get_campaign_count(session: AsyncSession) -> int:
    """Get total campaign count"""
    result = await session.execute(select(func.count(Campaign.campaign_id)))
    return result.scalar() or 0

async def _get_contacts_with_field(session: AsyncSession, field: str) -> int:
    """Get count of contacts with a specific field populated"""
    if field == "linkedin_url":
        result = await session.execute(
            select(func.count(Contact.contact_id)).where(Contact.linkedin_url.isnot(None))
        )
    else:
        result = await session.execute(
            select(func.count(Contact.contact_id)).where(getattr(Contact, field).isnot(None))
        )
    return result.scalar() or 0

async def _get_average_lead_score(session: AsyncSession) -> float:
    """Get average lead score"""
    # This is a simplified version - implement based on your data structure
    return 0.0

async def _get_lead_score_distribution(session: AsyncSession) -> List[Dict[str, Any]]:
    """Get lead score distribution"""
    # Implement based on your data structure
    return []

async def _get_top_categories(session: AsyncSession, field: str, limit: int) -> List[Dict[str, Any]]:
    """Get top categories for a field"""
    # Implement based on your data structure
    return []

async def _get_growth_trend(session: AsyncSession, date_from: datetime, date_to: datetime) -> List[Dict[str, Any]]:
    """Get contact growth trend"""
    # Implement based on your data structure
    return []

async def _get_recent_contacts(session: AsyncSession, limit: int) -> List[Dict[str, Any]]:
    """Get recent contacts"""
    result = await session.execute(
        select(Contact)
        .order_by(desc(Contact.created_at))
        .limit(limit)
    )
    contacts = result.scalars().all()
    
    return [
        {
            "contact_id": str(contact.contact_id),
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "company": contact.company,
            "title": contact.headline,
            "created_at": contact.created_at
        }
        for contact in contacts
    ]

async def _get_recent_activity(session: AsyncSession, limit: int) -> List[Dict[str, Any]]:
    """Get recent activity"""
    # Implement based on your activity tracking
    return []

async def _get_quick_stats(session: AsyncSession) -> Dict[str, Any]:
    """Get quick statistics"""
    return {
        "contacts_today": 0,
        "messages_sent_today": 0,
        "new_connections_today": 0,
        "average_response_rate": 0.0
    }

async def _get_message_count(session: AsyncSession, date_from: datetime, date_to: datetime) -> int:
    """Get message count for date range"""
    # Implement based on your message tracking
    return 0

async def _get_connection_request_count(session: AsyncSession, date_from: datetime, date_to: datetime) -> int:
    """Get connection request count for date range"""
    # Implement based on your tracking
    return 0

async def _get_profile_visit_count(session: AsyncSession, date_from: datetime, date_to: datetime) -> int:
    """Get profile visit count for date range"""
    # Implement based on your tracking
    return 0

async def _get_reply_count(session: AsyncSession, date_from: datetime, date_to: datetime) -> int:
    """Get reply count for date range"""
    # Implement based on your tracking
    return 0

async def _get_acceptance_count(session: AsyncSession, date_from: datetime, date_to: datetime) -> int:
    """Get acceptance count for date range"""
    # Implement based on your tracking
    return 0

async def _get_activity_timeline(session: AsyncSession, date_from: datetime, date_to: datetime) -> List[Dict[str, Any]]:
    """Get activity timeline"""
    # Implement based on your activity tracking
    return []

async def _get_top_performing_contacts(session: AsyncSession, date_from: datetime, date_to: datetime) -> List[Dict[str, Any]]:
    """Get top performing contacts"""
    # Implement based on your performance metrics
    return []

async def _get_segment_contacts(
    session: AsyncSession, 
    segment_name: str, 
    criteria: Dict[str, Any], 
    limit: int
) -> ContactSegment:
    """Get contacts for a segment"""
    # Implement segment logic based on criteria
    # This is a placeholder implementation
    return ContactSegment(
        segment_name=segment_name,
        criteria=criteria,
        contact_count=0,
        average_lead_score=0.0,
        engagement_rate=0.0,
        contacts=[]
    )

async def _bulk_delete_contacts(session: AsyncSession, contact_ids: List[str]) -> int:
    """Bulk delete contacts"""
    # Implement bulk deletion
    return 0

async def _bulk_export_contacts(session: AsyncSession, contact_ids: List[str], parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Bulk export contacts"""
    # Implement bulk export
    return {}

async def _bulk_enrich_contacts(session: AsyncSession, contact_ids: List[str]) -> int:
    """Bulk enrich contacts"""
    # Implement bulk enrichment
    return 0

async def _get_contact_analytics(session: AsyncSession, contact_id: str) -> Dict[str, Any]:
    """Get analytics for a specific contact"""
    # Implement contact-specific analytics
    return {}

def _apply_export_filters(query, filters: Dict[str, Any]):
    """Apply filters to export query"""
    # Implement filter logic
    return query
