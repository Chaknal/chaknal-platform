from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from database.database import get_session
from app.models.contact import Contact
from app.models.campaign_contact import CampaignContact
from app.models.user import User
from app.models.campaign import Campaign
from pydantic import BaseModel
from datetime import datetime, timezone
from uuid import uuid4

router = APIRouter()

def make_timezone_aware(dt):
    """Convert datetime to timezone aware if it's naive"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

class ContactResponse(BaseModel):
    """Schema for contact response with campaign and assignment info"""
    contact_id: str
    first_name: str
    last_name: str
    full_name: str
    job_title: Optional[str]
    company_name: Optional[str]
    linkedin_url: Optional[str]
    location: Optional[str]
    industry: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    created_at: datetime
    updated_at: datetime
    # Campaign and assignment info
    campaigns: List[Dict[str, Any]]
    assigned_to: Optional[str]
    assigned_user_email: Optional[str]
    current_status: Optional[str]
    current_campaign_id: Optional[str]
    current_campaign_name: Optional[str]

@router.get("/contacts", response_model=List[ContactResponse], tags=["Contacts"])
async def get_contacts(
    # Filtering parameters
    owner_id: Optional[str] = Query(None, description="Filter by assigned user ID"),
    status: Optional[str] = Query(None, description="Filter by contact status"),
    campaign_id: Optional[str] = Query(None, description="Filter by campaign ID"),
    company_name: Optional[str] = Query(None, description="Filter by company name"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    location: Optional[str] = Query(None, description="Filter by location"),
    # Advanced status filtering
    has_accepted: Optional[bool] = Query(None, description="Filter contacts that have accepted connection"),
    has_replied: Optional[bool] = Query(None, description="Filter contacts that have replied"),
    accepted_only: Optional[bool] = Query(None, description="Filter contacts that accepted but haven't replied"),
    replied_only: Optional[bool] = Query(None, description="Filter contacts that have replied"),
    # Search parameters
    search: Optional[str] = Query(None, description="Search in name, company, job title"),
    # Pagination
    limit: int = Query(50, le=200, description="Number of contacts to return"),
    offset: int = Query(0, ge=0, description="Number of contacts to skip"),
    # Sorting
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    session: AsyncSession = Depends(get_session)
):
    """Get all contacts with filtering and pagination"""
    try:
        # Build base query
        query = select(Contact).options(
            selectinload(Contact.campaign_contacts).selectinload(CampaignContact.campaign)
        )
        
        # Apply filters
        conditions = []
        
        if owner_id:
            # Filter by assigned user
            subquery = select(CampaignContact.contact_id).where(
                CampaignContact.assigned_to == owner_id
            )
            conditions.append(Contact.contact_id.in_(subquery))
        
        if campaign_id:
            # Filter by campaign
            subquery = select(CampaignContact.contact_id).where(
                CampaignContact.campaign_id == campaign_id
            )
            conditions.append(Contact.contact_id.in_(subquery))
        
        if status:
            # Filter by status in campaign contacts
            subquery = select(CampaignContact.contact_id).where(
                CampaignContact.status == status
            )
            conditions.append(Contact.contact_id.in_(subquery))
        
        # Advanced status filtering
        if has_accepted is not None:
            if has_accepted:
                # Contacts that have accepted (accepted_at is not null)
                subquery = select(CampaignContact.contact_id).where(
                    CampaignContact.accepted_at.isnot(None)
                )
            else:
                # Contacts that have not accepted (accepted_at is null)
                subquery = select(CampaignContact.contact_id).where(
                    CampaignContact.accepted_at.is_(None)
                )
            conditions.append(Contact.contact_id.in_(subquery))
        
        if has_replied is not None:
            if has_replied:
                # Contacts that have replied (replied_at is not null)
                subquery = select(CampaignContact.contact_id).where(
                    CampaignContact.replied_at.isnot(None)
                )
            else:
                # Contacts that have not replied (replied_at is null)
                subquery = select(CampaignContact.contact_id).where(
                    CampaignContact.replied_at.is_(None)
                )
            conditions.append(Contact.contact_id.in_(subquery))
        
        if accepted_only:
            # Contacts that accepted but haven't replied
            subquery = select(CampaignContact.contact_id).where(
                and_(
                    CampaignContact.accepted_at.isnot(None),
                    CampaignContact.replied_at.is_(None)
                )
            )
            conditions.append(Contact.contact_id.in_(subquery))
        
        if replied_only:
            # Contacts that have replied
            subquery = select(CampaignContact.contact_id).where(
                CampaignContact.replied_at.isnot(None)
            )
            conditions.append(Contact.contact_id.in_(subquery))
        
        if company_name:
            conditions.append(Contact.company_name.ilike(f"%{company_name}%"))
        
        if industry:
            conditions.append(Contact.industry.ilike(f"%{industry}%"))
        
        if location:
            conditions.append(Contact.location.ilike(f"%{location}%"))
        
        if search:
            search_conditions = [
                Contact.first_name.ilike(f"%{search}%"),
                Contact.last_name.ilike(f"%{search}%"),
                Contact.company_name.ilike(f"%{search}%"),
                Contact.job_title.ilike(f"%{search}%")
            ]
            conditions.append(or_(*search_conditions))
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Apply sorting
        if isinstance(sort_by, str) and hasattr(Contact, sort_by):
            sort_field = getattr(Contact, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_field))
            else:
                query = query.order_by(sort_field)
        else:
            query = query.order_by(desc(Contact.created_at))
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        # Execute query
        result = await session.execute(query)
        contacts = result.scalars().all()
        
        # Build response
        contact_responses = []
        for contact in contacts:
            # Get campaign and assignment info
            campaigns = []
            assigned_to = None
            assigned_user_email = None
            current_status = None
            current_campaign_id = None
            current_campaign_name = None
            
            for cc in contact.campaign_contacts:
                # Get assigned user email if assigned_to exists
                assigned_user_email = None
                if cc.assigned_to:
                    user_result = await session.execute(
                        select(User.email).where(User.id == cc.assigned_to)
                    )
                    user_email = user_result.scalar()
                    assigned_user_email = user_email
                
                campaign_info = {
                    "campaign_id": cc.campaign_id,
                    "campaign_name": cc.campaign.name if cc.campaign else "Unknown Campaign",
                    "status": cc.status,
                    "assigned_to": cc.assigned_to,
                    "assigned_user_email": assigned_user_email,
                    "enrolled_at": make_timezone_aware(cc.enrolled_at),
                    "accepted_at": make_timezone_aware(cc.accepted_at),
                    "replied_at": make_timezone_aware(cc.replied_at),
                    "created_at": make_timezone_aware(cc.created_at)
                }
                campaigns.append(campaign_info)
                
                # Set current assignment info (most recent)
                if not assigned_to:
                    assigned_to = cc.assigned_to
                    assigned_user_email = assigned_user_email
                    current_status = cc.status
                    current_campaign_id = cc.campaign_id
                    current_campaign_name = cc.campaign.name if cc.campaign else "Unknown Campaign"
            
            contact_response = ContactResponse(
                contact_id=contact.contact_id,
                first_name=contact.first_name,
                last_name=contact.last_name,
                full_name=contact.full_name or f"{contact.first_name} {contact.last_name}".strip(),
                job_title=contact.job_title,
                company_name=contact.company_name,
                linkedin_url=contact.linkedin_url,
                location=contact.location,
                industry=contact.industry,
                email=contact.email,
                phone=contact.phone,
                created_at=make_timezone_aware(contact.created_at),
                updated_at=make_timezone_aware(contact.updated_at),
                campaigns=campaigns,
                assigned_to=assigned_to,
                assigned_user_email=assigned_user_email,
                current_status=current_status,
                current_campaign_id=current_campaign_id,
                current_campaign_name=current_campaign_name
            )
            contact_responses.append(contact_response)
        
        return contact_responses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get contacts: {str(e)}")

@router.get("/contacts/stats", tags=["Contacts"])
async def get_contact_stats(
    campaign_id: Optional[str] = Query(None, description="Filter by campaign ID"),
    session: AsyncSession = Depends(get_session)
):
    """Get contact statistics"""
    try:
        # Base query for contacts
        base_query = select(Contact)
        
        if campaign_id:
            # Filter by campaign
            subquery = select(CampaignContact.contact_id).where(
                CampaignContact.campaign_id == campaign_id
            )
            base_query = base_query.where(Contact.contact_id.in_(subquery))
        
        # Get total contacts
        total_result = await session.execute(select(func.count(Contact.contact_id)).select_from(base_query.subquery()))
        total_contacts = total_result.scalar()
        
        # Get status distribution
        status_query = select(
            CampaignContact.status,
            func.count(CampaignContact.contact_id).label('count')
        ).group_by(CampaignContact.status)
        
        if campaign_id:
            status_query = status_query.where(CampaignContact.campaign_id == campaign_id)
        
        status_result = await session.execute(status_query)
        status_distribution = {row.status: row.count for row in status_result}
        
        # Get company distribution
        company_query = select(
            Contact.company_name,
            func.count(Contact.contact_id).label('count')
        ).group_by(Contact.company_name).order_by(desc('count')).limit(10)
        
        if campaign_id:
            subquery = select(CampaignContact.contact_id).where(
                CampaignContact.campaign_id == campaign_id
            )
            company_query = company_query.where(Contact.contact_id.in_(subquery))
        
        company_result = await session.execute(company_query)
        top_companies = [{"company": row.company_name, "count": row.count} for row in company_result]
        
        # Get industry distribution
        industry_query = select(
            Contact.industry,
            func.count(Contact.contact_id).label('count')
        ).group_by(Contact.industry).order_by(desc('count')).limit(10)
        
        if campaign_id:
            subquery = select(CampaignContact.contact_id).where(
                CampaignContact.campaign_id == campaign_id
            )
            industry_query = industry_query.where(Contact.contact_id.in_(subquery))
        
        industry_result = await session.execute(industry_query)
        top_industries = [{"industry": row.industry, "count": row.count} for row in industry_result]
        
        return {
            "total_contacts": total_contacts,
            "status_distribution": status_distribution,
            "top_companies": top_companies,
            "top_industries": top_industries
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get contact stats: {str(e)}")

@router.get("/contacts/filters", tags=["Contacts"])
async def get_contact_filters(
    campaign_id: Optional[str] = Query(None, description="Filter by campaign ID"),
    session: AsyncSession = Depends(get_session)
):
    """Get available filter options for contacts"""
    try:
        # Get unique values for filters
        base_query = select(Contact)
        
        if campaign_id:
            subquery = select(CampaignContact.contact_id).where(
                CampaignContact.campaign_id == campaign_id
            )
            base_query = base_query.where(Contact.contact_id.in_(subquery))
        
        # Get unique companies
        company_result = await session.execute(
            select(Contact.company_name).distinct().where(Contact.company_name.isnot(None))
        )
        companies = [row.company_name for row in company_result if row.company_name]
        
        # Get unique industries
        industry_result = await session.execute(
            select(Contact.industry).distinct().where(Contact.industry.isnot(None))
        )
        industries = [row.industry for row in industry_result if row.industry]
        
        # Get unique locations
        location_result = await session.execute(
            select(Contact.location).distinct().where(Contact.location.isnot(None))
        )
        locations = [row.location for row in location_result if row.location]
        
        # Get unique statuses
        status_result = await session.execute(
            select(CampaignContact.status).distinct()
        )
        statuses = [row.status for row in status_result if row.status]
        
        # Get assigned users
        user_result = await session.execute(
            select(User.id, User.email).distinct()
        )
        users = [{"id": row.id, "email": row.email} for row in user_result]
        
        # Get campaigns
        campaign_result = await session.execute(
            select(Campaign.campaign_id, Campaign.name, Campaign.status).distinct()
        )
        campaigns = [{"id": row.campaign_id, "name": row.name, "status": row.status} for row in campaign_result]
        
        return {
            "companies": sorted(companies),
            "industries": sorted(industries),
            "locations": sorted(locations),
            "statuses": sorted(statuses),
            "users": users,
            "campaigns": campaigns
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get contact filters: {str(e)}")


class BulkEnrollmentRequest(BaseModel):
    """Schema for bulk enrollment request"""
    contact_ids: List[str]
    campaign_id: str
    assigned_to: Optional[str] = None
    status: str = "pending"
    tags: Optional[List[str]] = None


class BulkEnrollmentResponse(BaseModel):
    """Schema for bulk enrollment response"""
    success: bool
    enrolled_count: int
    skipped_count: int
    errors: List[str]
    enrolled_contacts: List[str]
    skipped_contacts: List[str]


@router.post("/contacts/bulk-enroll", response_model=BulkEnrollmentResponse, tags=["Contacts"])
async def bulk_enroll_contacts(
    request: BulkEnrollmentRequest,
    session: AsyncSession = Depends(get_session)
):
    """Bulk enroll contacts into a campaign"""
    try:
        # Verify campaign exists
        campaign_result = await session.execute(
            select(Campaign).where(Campaign.campaign_id == request.campaign_id)
        )
        campaign = campaign_result.scalar_one_or_none()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Verify assigned user exists if provided
        if request.assigned_to:
            user_result = await session.execute(
                select(User).where(User.id == request.assigned_to)
            )
            user = user_result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="Assigned user not found")
        
        enrolled_contacts = []
        skipped_contacts = []
        errors = []
        
        for contact_id in request.contact_ids:
            try:
                # Check if contact exists
                contact_result = await session.execute(
                    select(Contact).where(Contact.contact_id == contact_id)
                )
                contact = contact_result.scalar_one_or_none()
                if not contact:
                    errors.append(f"Contact {contact_id} not found")
                    continue
                
                # Check if already enrolled in this campaign
                existing_enrollment = await session.execute(
                    select(CampaignContact).where(
                        and_(
                            CampaignContact.contact_id == contact_id,
                            CampaignContact.campaign_id == request.campaign_id
                        )
                    )
                )
                if existing_enrollment.scalar_one_or_none():
                    skipped_contacts.append(contact_id)
                    continue
                
                # Create new campaign contact enrollment
                campaign_contact = CampaignContact(
                    campaign_contact_id=str(uuid4()),
                    contact_id=contact_id,
                    campaign_id=request.campaign_id,
                    campaign_key=campaign.campaign_key,
                    status=request.status,
                    assigned_to=request.assigned_to,
                    enrolled_at=datetime.now(timezone.utc),
                    tags=request.tags or [],
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                
                session.add(campaign_contact)
                enrolled_contacts.append(contact_id)
                
            except Exception as e:
                errors.append(f"Failed to enroll contact {contact_id}: {str(e)}")
                continue
        
        # Commit all changes
        await session.commit()
        
        return BulkEnrollmentResponse(
            success=len(errors) == 0,
            enrolled_count=len(enrolled_contacts),
            skipped_count=len(skipped_contacts),
            errors=errors,
            enrolled_contacts=enrolled_contacts,
            skipped_contacts=skipped_contacts
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to bulk enroll contacts: {str(e)}")
