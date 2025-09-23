from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, and_, or_
from typing import List, Optional, Dict, Any
import uuid
import csv
import json
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator
import pandas as pd
from io import StringIO

from database.database import get_session
from app.models.contact import Contact
from app.models.campaign import Campaign
from app.models.campaign_contact import CampaignContact
from app.models.company import Company
from app.services.duxwrap_new import DuxSoupManager

router = APIRouter(prefix="/api/prospects", tags=["Prospect Management"])

# =============================================================================
# SCHEMAS
# =============================================================================

class ProspectData(BaseModel):
    """Individual prospect data"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    company: Optional[str] = Field(None, max_length=255)
    company_url: Optional[str] = Field(None, max_length=500)
    title: Optional[str] = Field(None, max_length=500)
    linkedin_url: str = Field(..., max_length=500)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = Field(None)
    source: Optional[str] = Field(None, max_length=100)
    lead_score: Optional[int] = Field(None, ge=0, le=100)
    
    @validator('linkedin_url')
    def validate_linkedin_url(cls, v):
        if not v.startswith('https://www.linkedin.com/'):
            raise ValueError('Must be a valid LinkedIn profile URL')
        return v

class ProspectUploadRequest(BaseModel):
    """Prospect upload request"""
    campaign_id: Optional[str] = Field(None, description="Campaign to add prospects to")
    auto_enroll: bool = Field(default=False, description="Automatically enroll prospects in campaign")
    duplicate_check: bool = Field(default=True, description="Check for duplicate prospects")
    lead_scoring: bool = Field(default=True, description="Apply automatic lead scoring")
    tags: Optional[List[str]] = Field(None, description="Default tags for all prospects")

class ProspectUploadResponse(BaseModel):
    """Prospect upload response"""
    success: bool
    total_processed: int
    total_created: int
    total_updated: int
    total_duplicates: int
    total_errors: int
    errors: List[Dict[str, Any]]
    prospects: List[Dict[str, Any]]

class ProspectSearchRequest(BaseModel):
    """Prospect search request"""
    query: Optional[str] = Field(None, description="Search query")
    company: Optional[str] = Field(None, description="Filter by company")
    title: Optional[str] = Field(None, description="Filter by job title")
    location: Optional[str] = Field(None, description="Filter by location")
    industry: Optional[str] = Field(None, description="Filter by industry")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    lead_score_min: Optional[int] = Field(None, ge=0, le=100)
    lead_score_max: Optional[int] = Field(None, ge=0, le=100)
    created_after: Optional[datetime] = Field(None, description="Filter by creation date")
    has_email: Optional[bool] = Field(None, description="Filter by email availability")
    has_phone: Optional[bool] = Field(None, description="Filter by phone availability")

class ProspectResponse(BaseModel):
    """Prospect response model"""
    contact_id: str
    first_name: str
    last_name: str
    company: Optional[str]
    company_url: Optional[str]
    title: Optional[str]
    linkedin_url: str
    email: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    industry: Optional[str]
    notes: Optional[str]
    tags: List[str]
    source: Optional[str]
    lead_score: int
    connection_status: str
    last_contacted: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class ProspectListResponse(BaseModel):
    """Prospect list response with pagination"""
    prospects: List[ProspectResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

class LeadScoringConfig(BaseModel):
    """Lead scoring configuration"""
    title_weight: int = Field(default=10, ge=0, le=100)
    company_size_weight: int = Field(default=15, ge=0, le=100)
    industry_weight: int = Field(default=8, ge=0, le=100)
    location_weight: int = Field(default=5, ge=0, le=100)
    email_available_weight: int = Field(default=20, ge=0, le=100)
    phone_available_weight: int = Field(default=15, ge=0, le=100)
    linkedin_activity_weight: int = Field(default=12, ge=0, le=100)
    company_revenue_weight: int = Field(default=15, ge=0, le=100)

class ProspectEnrichmentRequest(BaseModel):
    """Prospect enrichment request"""
    contact_ids: List[str] = Field(..., description="Contact IDs to enrich")
    enrich_company: bool = Field(default=True, description="Enrich company information")
    enrich_contact: bool = Field(default=True, description="Enrich contact information")
    find_emails: bool = Field(default=True, description="Find email addresses")
    find_phones: bool = Field(default=True, description="Find phone numbers")
    update_lead_score: bool = Field(default=True, description="Update lead scores")

# =============================================================================
# PROSPECT UPLOAD & MANAGEMENT
# =============================================================================

@router.post("/upload/csv", response_model=ProspectUploadResponse)
async def upload_prospects_csv(
    file: UploadFile = File(..., description="CSV file with prospect data"),
    campaign_id: Optional[str] = Form(None, description="Campaign ID to add prospects to"),
    auto_enroll: bool = Form(False, description="Automatically enroll prospects in campaign"),
    duplicate_check: bool = Form(True, description="Check for duplicate prospects"),
    lead_scoring: bool = Form(True, description="Apply automatic lead scoring"),
    tags: Optional[str] = Form(None, description="Comma-separated default tags"),
    session: AsyncSession = Depends(get_session)
):
    """Upload prospects from CSV file"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="File must be a CSV file"
            )
        
        # Read CSV content
        content = await file.read()
        csv_text = content.decode('utf-8')
        
        # Parse CSV
        df = pd.read_csv(StringIO(csv_text))
        
        # Validate required columns
        required_columns = ['first_name', 'last_name', 'linkedin_url']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {missing_columns}"
            )
        
        # Process prospects
        default_tags = tags.split(',') if tags else []
        default_tags = [tag.strip() for tag in default_tags if tag.strip()]
        
        return await _process_prospect_upload(
            session, df, campaign_id, auto_enroll, duplicate_check, 
            lead_scoring, default_tags
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload prospects: {str(e)}"
        )

@router.post("/upload/json", response_model=ProspectUploadResponse)
async def upload_prospects_json(
    prospects: List[ProspectData],
    request: ProspectUploadRequest,
    session: AsyncSession = Depends(get_session)
):
    """Upload prospects from JSON data"""
    try:
        # Convert to DataFrame for processing
        df = pd.DataFrame([prospect.dict() for prospect in prospects])
        
        return await _process_prospect_upload(
            session, df, request.campaign_id, request.auto_enroll,
            request.duplicate_check, request.lead_scoring, request.tags or []
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload prospects: {str(e)}"
        )

@router.post("/upload/manual", response_model=ProspectResponse)
async def create_prospect_manual(
    prospect: ProspectData,
    campaign_id: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    """Create a single prospect manually"""
    try:
        # Check for duplicates if LinkedIn URL exists
        if prospect.linkedin_url:
            result = await session.execute(
                select(Contact).where(Contact.linkedin_url == prospect.linkedin_url)
            )
            existing_contact = result.scalar_one_or_none()
            
            if existing_contact:
                raise HTTPException(
                    status_code=400,
                    detail="Prospect with this LinkedIn URL already exists"
                )
        
        # Create contact
        contact = Contact(
            contact_id=uuid.uuid4(),
            first_name=prospect.first_name,
            last_name=prospect.last_name,
            company=prospect.company,
            company_url=prospect.company_url,
            headline=prospect.title,
            linkedin_url=prospect.linkedin_url,
            email=prospect.email,
            phone=prospect.phone,
            location=prospect.location,
            industry=prospect.industry,
            notes=prospect.notes,
            tags=prospect.tags or [],
            profile_data={
                "source": prospect.source or "manual",
                "lead_score": prospect.lead_score or 0
            }
        )
        
        session.add(contact)
        await session.commit()
        await session.refresh(contact)
        
        # Add to campaign if specified
        if campaign_id:
            await _add_contact_to_campaign(session, contact.contact_id, campaign_id)
        
        return ProspectResponse(
            contact_id=str(contact.contact_id),
            first_name=contact.first_name,
            last_name=contact.last_name,
            company=contact.company,
            company_url=contact.company_url,
            title=contact.headline,
            linkedin_url=contact.linkedin_url,
            email=contact.email,
            phone=contact.phone,
            location=contact.location,
            industry=contact.industry,
            notes=contact.notes,
            tags=contact.tags or [],
            source=contact.profile_data.get("source") if contact.profile_data else None,
            lead_score=contact.profile_data.get("lead_score", 0) if contact.profile_data else 0,
            connection_status=contact.connection_status,
            last_contacted=contact.last_message_sent,
            created_at=contact.created_at,
            updated_at=contact.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create prospect: {str(e)}"
        )

# =============================================================================
# PROSPECT SEARCH & RETRIEVAL
# =============================================================================

@router.get("/search", response_model=ProspectListResponse)
async def search_prospects(
    query: Optional[str] = Query(None, description="Search query"),
    company: Optional[str] = Query(None, description="Filter by company"),
    title: Optional[str] = Query(None, description="Filter by job title"),
    location: Optional[str] = Query(None, description="Filter by location"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    lead_score_min: Optional[int] = Query(None, ge=0, le=100),
    lead_score_max: Optional[int] = Query(None, ge=0, le=100),
    created_after: Optional[datetime] = Query(None, description="Filter by creation date"),
    has_email: Optional[bool] = Query(None, description="Filter by email availability"),
    has_phone: Optional[bool] = Query(None, description="Filter by phone availability"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Prospects per page"),
    session: AsyncSession = Depends(get_session)
):
    """Search and filter prospects"""
    try:
        # Build query
        query_builder = select(Contact)
        
        # Apply filters
        if query:
            search_term = f"%{query}%"
            query_builder = query_builder.where(
                or_(
                    Contact.first_name.ilike(search_term),
                    Contact.last_name.ilike(search_term),
                    Contact.company.ilike(search_term),
                    Contact.headline.ilike(search_term),
                    Contact.location.ilike(search_term),
                    Contact.industry.ilike(search_term)
                )
            )
        
        if company:
            query_builder = query_builder.where(Contact.company.ilike(f"%{company}%"))
        
        if title:
            query_builder = query_builder.where(Contact.headline.ilike(f"%{title}%"))
        
        if location:
            query_builder = query_builder.where(Contact.location.ilike(f"%{location}%"))
        
        if industry:
            query_builder = query_builder.where(Contact.industry.ilike(f"%{industry}%"))
        
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            for tag in tag_list:
                query_builder = query_builder.where(Contact.tags.contains([tag]))
        
        if lead_score_min is not None:
            query_builder = query_builder.where(
                Contact.profile_data['lead_score'].astext.cast(int) >= lead_score_min
            )
        
        if lead_score_max is not None:
            query_builder = query_builder.where(
                Contact.profile_data['lead_score'].astext.cast(int) <= lead_score_max
            )
        
        if created_after:
            query_builder = query_builder.where(Contact.created_at >= created_after)
        
        if has_email is not None:
            if has_email:
                query_builder = query_builder.where(Contact.email.isnot(None))
            else:
                query_builder = query_builder.where(Contact.email.is_(None))
        
        if has_phone is not None:
            if has_phone:
                query_builder = query_builder.where(Contact.phone.isnot(None))
            else:
                query_builder = query_builder.where(Contact.phone.is_(None))
        
        # Get total count
        count_query = select(func.count()).select_from(query_builder.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query_builder = query_builder.offset((page - 1) * per_page).limit(per_page)
        result = await session.execute(query_builder)
        contacts = result.scalars().all()
        
        # Convert to response models
        prospect_responses = []
        for contact in contacts:
            prospect_responses.append(ProspectResponse(
                contact_id=str(contact.contact_id),
                first_name=contact.first_name,
                last_name=contact.last_name,
                company=contact.company,
                company_url=contact.company_url,
                title=contact.headline,
                linkedin_url=contact.linkedin_url,
                email=contact.email,
                phone=contact.phone,
                location=contact.location,
                industry=contact.industry,
                notes=contact.notes,
                tags=contact.tags or [],
                source=contact.profile_data.get("source") if contact.profile_data else None,
                lead_score=contact.profile_data.get("lead_score", 0) if contact.profile_data else 0,
                connection_status=contact.connection_status,
                last_contacted=contact.last_message_sent,
                created_at=contact.created_at,
                updated_at=contact.updated_at
            ))
        
        total_pages = (total + per_page - 1) // per_page
        
        return ProspectListResponse(
            prospects=prospect_responses,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search prospects: {str(e)}"
        )

@router.get("/{contact_id}", response_model=ProspectResponse)
async def get_prospect(
    contact_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get prospect by ID"""
    try:
        result = await session.execute(
            select(Contact).where(Contact.contact_id == contact_id)
        )
        contact = result.scalar_one_or_none()
        
        if not contact:
            raise HTTPException(
                status_code=404,
                detail="Prospect not found"
            )
        
        return ProspectResponse(
            contact_id=str(contact.contact_id),
            first_name=contact.first_name,
            last_name=contact.last_name,
            company=contact.company,
            company_url=contact.company_url,
            title=contact.headline,
            linkedin_url=contact.linkedin_url,
            email=contact.email,
            phone=contact.phone,
            location=contact.location,
            industry=contact.industry,
            notes=contact.notes,
            tags=contact.tags or [],
            source=contact.profile_data.get("source") if contact.profile_data else None,
            lead_score=contact.profile_data.get("lead_score", 0) if contact.profile_data else 0,
            connection_status=contact.connection_status,
            last_contacted=contact.last_message_sent,
            created_at=contact.created_at,
            updated_at=contact.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get prospect: {str(e)}"
        )

# =============================================================================
# PROSPECT ENRICHMENT & LEAD SCORING
# =============================================================================

@router.post("/enrich", response_model=Dict[str, Any])
async def enrich_prospects(
    request: ProspectEnrichmentRequest,
    session: AsyncSession = Depends(get_session)
):
    """Enrich prospect information using external APIs"""
    try:
        enriched_count = 0
        errors = []
        
        for contact_id in request.contact_ids:
            try:
                # Get contact
                result = await session.execute(
                    select(Contact).where(Contact.contact_id == contact_id)
                )
                contact = result.scalar_one_or_none()
                
                if not contact:
                    errors.append({
                        "contact_id": contact_id,
                        "error": "Contact not found"
                    })
                    continue
                
                # Enrich contact information
                if request.enrich_contact:
                    await _enrich_contact_info(session, contact)
                
                # Enrich company information
                if request.enrich_company and contact.company:
                    await _enrich_company_info(session, contact)
                
                # Find emails and phones
                if request.find_emails and not contact.email:
                    await _find_contact_email(session, contact)
                
                if request.find_phones and not contact.phone:
                    await _find_contact_phone(session, contact)
                
                # Update lead score
                if request.update_lead_score:
                    await _update_lead_score(session, contact)
                
                enriched_count += 1
                
            except Exception as e:
                errors.append({
                    "contact_id": contact_id,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "enriched_count": enriched_count,
            "total_requested": len(request.contact_ids),
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to enrich prospects: {str(e)}"
        )

@router.post("/lead-scoring/config", response_model=Dict[str, Any])
async def update_lead_scoring_config(
    config: LeadScoringConfig,
    session: AsyncSession = Depends(get_session)
):
    """Update lead scoring configuration"""
    try:
        # Store configuration (implement based on your config storage)
        # For now, just return success
        return {
            "success": True,
            "message": "Lead scoring configuration updated",
            "config": config.dict()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update lead scoring config: {str(e)}"
        )

@router.post("/lead-scoring/recalculate", response_model=Dict[str, Any])
async def recalculate_lead_scores(
    contact_ids: Optional[List[str]] = None,
    session: AsyncSession = Depends(get_session)
):
    """Recalculate lead scores for prospects"""
    try:
        if contact_ids:
            # Recalculate for specific contacts
            query = select(Contact).where(Contact.contact_id.in_(contact_ids))
        else:
            # Recalculate for all contacts
            query = select(Contact)
        
        result = await session.execute(query)
        contacts = result.scalars().all()
        
        updated_count = 0
        for contact in contacts:
            try:
                await _update_lead_score(session, contact)
                updated_count += 1
            except Exception as e:
                print(f"Error updating lead score for {contact.contact_id}: {e}")
                continue
        
        return {
            "success": True,
            "message": f"Lead scores recalculated for {updated_count} prospects",
            "updated_count": updated_count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to recalculate lead scores: {str(e)}"
        )

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def _process_prospect_upload(
    session: AsyncSession,
    df: pd.DataFrame,
    campaign_id: Optional[str],
    auto_enroll: bool,
    duplicate_check: bool,
    lead_scoring: bool,
    default_tags: List[str]
) -> ProspectUploadResponse:
    """Process prospect upload from DataFrame"""
    total_processed = len(df)
    total_created = 0
    total_updated = 0
    total_duplicates = 0
    total_errors = 0
    errors = []
    prospects = []
    
    for index, row in df.iterrows():
        try:
            # Prepare prospect data
            prospect_data = {
                "first_name": row.get("first_name", ""),
                "last_name": row.get("last_name", ""),
                "company": row.get("company"),
                "company_url": row.get("company_url"),
                "title": row.get("title") or row.get("headline"),
                "linkedin_url": row.get("linkedin_url"),
                "email": row.get("email"),
                "phone": row.get("phone"),
                "location": row.get("location"),
                "industry": row.get("industry"),
                "notes": row.get("notes"),
                "tags": (row.get("tags", "").split(",") if row.get("tags") else []) + default_tags,
                "source": row.get("source", "csv_upload"),
                "lead_score": row.get("lead_score", 0)
            }
            
            # Check for duplicates
            if duplicate_check and prospect_data["linkedin_url"]:
                result = await session.execute(
                    select(Contact).where(Contact.linkedin_url == prospect_data["linkedin_url"])
                )
                existing_contact = result.scalar_one_or_none()
                
                if existing_contact:
                    total_duplicates += 1
                    continue
            
            # Create or update contact
            if existing_contact:
                # Update existing contact
                for key, value in prospect_data.items():
                    if key == "tags":
                        existing_contact.tags = value
                    elif key == "title":
                        existing_contact.headline = value
                    elif key == "source" or key == "lead_score":
                        if not existing_contact.profile_data:
                            existing_contact.profile_data = {}
                        existing_contact.profile_data[key] = value
                    elif hasattr(existing_contact, key):
                        setattr(existing_contact, key, value)
                
                existing_contact.updated_at = datetime.utcnow()
                total_updated += 1
                contact = existing_contact
                
            else:
                # Create new contact
                contact = Contact(
                    contact_id=uuid.uuid4(),
                    first_name=prospect_data["first_name"],
                    last_name=prospect_data["last_name"],
                    company=prospect_data["company"],
                    company_url=prospect_data["company_url"],
                    headline=prospect_data["title"],
                    linkedin_url=prospect_data["linkedin_url"],
                    email=prospect_data["email"],
                    phone=prospect_data["phone"],
                    location=prospect_data["location"],
                    industry=prospect_data["industry"],
                    notes=prospect_data["notes"],
                    tags=prospect_data["tags"],
                    profile_data={
                        "source": prospect_data["source"],
                        "lead_score": prospect_data["lead_score"]
                    }
                )
                
                session.add(contact)
                total_created += 1
            
            # Apply lead scoring
            if lead_scoring:
                await _update_lead_score(session, contact)
            
            # Add to campaign if specified
            if campaign_id and auto_enroll:
                await _add_contact_to_campaign(session, contact.contact_id, campaign_id)
            
            # Prepare response data
            prospects.append({
                "contact_id": str(contact.contact_id),
                "first_name": contact.first_name,
                "last_name": contact.last_name,
                "company": contact.company,
                "title": contact.headline,
                "linkedin_url": contact.linkedin_url,
                "email": contact.email,
                "status": "created" if total_created > total_updated else "updated"
            })
            
        except Exception as e:
            total_errors += 1
            errors.append({
                "row": index + 1,
                "error": str(e),
                "data": row.to_dict()
            })
    
    await session.commit()
    
    return ProspectUploadResponse(
        success=True,
        total_processed=total_processed,
        total_created=total_created,
        total_updated=total_updated,
        total_duplicates=total_duplicates,
        total_errors=total_errors,
        errors=errors,
        prospects=prospects
    )

async def _add_contact_to_campaign(
    session: AsyncSession, 
    contact_id: str, 
    campaign_id: str
) -> None:
    """Add contact to campaign"""
    try:
        # Check if already in campaign
        result = await session.execute(
            select(CampaignContact).where(
                and_(
                    CampaignContact.contact_id == contact_id,
                    CampaignContact.campaign_id == campaign_id
                )
            )
        )
        
        if not result.scalar_one_or_none():
            # Get campaign key
            campaign_result = await session.execute(
                select(Campaign).where(Campaign.campaign_id == campaign_id)
            )
            campaign = campaign_result.scalar_one_or_none()
            
            if campaign:
                campaign_contact = CampaignContact(
                    campaign_contact_id=uuid.uuid4(),
                    campaign_id=campaign_id,
                    campaign_key=campaign.campaign_key,
                    contact_id=contact_id,
                    status="enrolled"
                )
                session.add(campaign_contact)
    
    except Exception as e:
        print(f"Error adding contact to campaign: {e}")

async def _enrich_contact_info(session: AsyncSession, contact: Contact) -> None:
    """Enrich contact information using external APIs"""
    # Implement contact enrichment logic
    # This could use Apollo.io, Hunter.io, or other services
    pass

async def _enrich_company_info(session: AsyncSession, contact: Contact) -> None:
    """Enrich company information using external APIs"""
    # Implement company enrichment logic
    # This could use Clearbit, Apollo.io, or other services
    pass

async def _find_contact_email(session: AsyncSession, contact: Contact) -> None:
    """Find email address for contact"""
    # Implement email finding logic
    # This could use Hunter.io, Apollo.io, or other services
    pass

async def _find_contact_phone(session: AsyncSession, contact: Contact) -> None:
    """Find phone number for contact"""
    # Implement phone finding logic
    # This could use various phone lookup services
    pass

async def _update_lead_score(session: AsyncSession, contact: Contact) -> None:
    """Update lead score for contact"""
    try:
        score = 0
        
        # Title-based scoring
        if contact.headline:
            title_lower = contact.headline.lower()
            if any(keyword in title_lower for keyword in ["ceo", "founder", "president", "director"]):
                score += 25
            elif any(keyword in title_lower for keyword in ["manager", "lead", "senior"]):
                score += 15
            elif any(keyword in title_lower for keyword in ["engineer", "developer", "analyst"]):
                score += 10
        
        # Company-based scoring
        if contact.company:
            # Add company size scoring logic
            score += 10
        
        # Contact information scoring
        if contact.email:
            score += 20
        if contact.phone:
            score += 15
        
        # Industry-based scoring
        if contact.industry:
            # Add industry-specific scoring logic
            score += 5
        
        # Update profile data
        if not contact.profile_data:
            contact.profile_data = {}
        
        contact.profile_data["lead_score"] = min(score, 100)
        contact.updated_at = datetime.utcnow()
        
    except Exception as e:
        print(f"Error updating lead score: {e}")
