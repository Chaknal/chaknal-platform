"""
Company and Organization Management API

This module provides comprehensive management of companies and organizations
in the multi-tenant Chaknal Platform.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, and_, or_
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from pydantic import BaseModel, Field, validator

from database.database import get_session
from app.models.company import Company
from app.models.user import User, Organization
from app.models.tenant_aware import TenantContext, require_tenant_context
from app.middleware.tenant_middleware import get_current_tenant_context

router = APIRouter(prefix="/api/companies", tags=["Company Management"])

# =============================================================================
# SCHEMAS
# =============================================================================

class CompanyCreate(BaseModel):
    """Company creation request"""
    name: str = Field(..., min_length=1, max_length=255, description="Company name")
    domain: str = Field(..., min_length=1, max_length=255, description="Company domain")
    industry: Optional[str] = Field(None, max_length=255, description="Company industry")
    size: Optional[str] = Field(None, max_length=100, description="Company size (e.g., 1-10, 11-50, 51-200, 200+)")
    location: Optional[str] = Field(None, max_length=255, description="Company location")
    website: Optional[str] = Field(None, max_length=500, description="Company website")
    description: Optional[str] = Field(None, max_length=1000, description="Company description")
    parent_company_id: Optional[str] = Field(None, description="Parent company ID for subsidiaries")
    organization_id: Optional[str] = Field(None, description="Organization ID for enterprise grouping")

class CompanyUpdate(BaseModel):
    """Company update request"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    industry: Optional[str] = Field(None, max_length=255)
    size: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None, max_length=1000)
    parent_company_id: Optional[str] = Field(None)
    organization_id: Optional[str] = Field(None)

class CompanyResponse(BaseModel):
    """Company response model"""
    id: str
    name: str
    domain: str
    industry: Optional[str]
    size: Optional[str]
    location: Optional[str]
    website: Optional[str]
    description: Optional[str]
    parent_company_id: Optional[str]
    organization_id: Optional[str]
    user_count: int
    contact_count: int
    campaign_count: int
    created_at: datetime
    updated_at: datetime

class CompanyListResponse(BaseModel):
    """Company list response with pagination"""
    companies: List[CompanyResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

class OrganizationCreate(BaseModel):
    """Organization creation request"""
    name: str = Field(..., min_length=1, max_length=255, description="Organization name")
    description: Optional[str] = Field(None, max_length=1000, description="Organization description")
    industry: Optional[str] = Field(None, max_length=255, description="Primary industry")
    website: Optional[str] = Field(None, max_length=500, description="Organization website")
    parent_organization_id: Optional[str] = Field(None, description="Parent organization ID")

class OrganizationResponse(BaseModel):
    """Organization response model"""
    id: str
    name: str
    description: Optional[str]
    industry: Optional[str]
    website: Optional[str]
    parent_organization_id: Optional[str]
    company_count: int
    user_count: int
    created_at: datetime

class CompanyHierarchy(BaseModel):
    """Company hierarchy structure"""
    company: CompanyResponse
    subsidiaries: List['CompanyHierarchy']
    parent: Optional['CompanyHierarchy']

class CompanyStats(BaseModel):
    """Company statistics"""
    total_users: int
    total_contacts: int
    total_campaigns: int
    total_messages_sent: int
    total_connections_made: int
    average_lead_score: float
    monthly_growth: float
    top_performing_users: List[Dict[str, Any]]

# =============================================================================
# COMPANY MANAGEMENT
# =============================================================================

@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    tenant_context: TenantContext = Depends(require_tenant_context),
    session: AsyncSession = Depends(get_session)
):
    """Create a new company"""
    try:
        # Check if user has permission to create companies
        if tenant_context.organization_id:
            # User is in an organization - can create companies in that org
            if company_data.organization_id and company_data.organization_id != tenant_context.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Can only create companies in your organization"
                )
        else:
            # User is not in an organization - can only create companies for themselves
            if company_data.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot assign organization without proper permissions"
                )
        
        # Check if domain already exists
        result = await session.execute(
            select(Company).where(Company.domain == company_data.domain)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company with this domain already exists"
            )
        
        # Create company
        company = Company(
            id=str(uuid.uuid4()),
            name=company_data.name,
            domain=company_data.domain,
            # Add additional fields when you extend the Company model
        )
        
        session.add(company)
        await session.commit()
        await session.refresh(company)
        
        # Return company with basic stats
        return CompanyResponse(
            id=company.id,
            name=company.name,
            domain=company.domain,
            industry=company.industry if hasattr(company, 'industry') else None,
            size=company.size if hasattr(company, 'size') else None,
            location=company.location if hasattr(company, 'location') else None,
            website=company.website if hasattr(company, 'website') else None,
            description=company.description if hasattr(company, 'description') else None,
            parent_company_id=company.parent_company_id if hasattr(company, 'parent_company_id') else None,
            organization_id=company.organization_id if hasattr(company, 'organization_id') else None,
            user_count=0,
            contact_count=0,
            campaign_count=0,
            created_at=company.created_at if hasattr(company, 'created_at') else datetime.utcnow(),
            updated_at=company.updated_at if hasattr(company, 'updated_at') else datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create company: {str(e)}"
        )

@router.get("/", response_model=CompanyListResponse)
async def list_companies(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Companies per page"),
    search: Optional[str] = Query(None, description="Search by name or domain"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    size: Optional[str] = Query(None, description="Filter by company size"),
    organization_id: Optional[str] = Query(None, description="Filter by organization"),
    tenant_context: TenantContext = Depends(require_tenant_context),
    session: AsyncSession = Depends(get_session)
):
    """List companies based on user permissions"""
    try:
        # Build query based on user permissions
        query = select(Company)
        
        # Apply tenant filtering
        if tenant_context.organization_id:
            # User can see companies in their organization
            if organization_id and organization_id != tenant_context.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot access companies outside your organization"
                )
            # Filter by organization
            query = query.where(Company.organization_id == tenant_context.organization_id)
        else:
            # User can only see their own company
            query = query.where(Company.id == tenant_context.company_id)
        
        # Apply search filters
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Company.name.ilike(search_term),
                    Company.domain.ilike(search_term)
                )
            )
        
        if industry:
            query = query.where(Company.industry == industry)
        
        if size:
            query = query.where(Company.size == size)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await session.execute(query)
        companies = result.scalars().all()
        
        # Convert to response models with stats
        company_responses = []
        for company in companies:
            # Get company stats
            stats = await _get_company_stats(session, company.id)
            
            company_responses.append(CompanyResponse(
                id=company.id,
                name=company.name,
                domain=company.domain,
                industry=company.industry if hasattr(company, 'industry') else None,
                size=company.size if hasattr(company, 'size') else None,
                location=company.location if hasattr(company, 'location') else None,
                website=company.website if hasattr(company, 'website') else None,
                description=company.description if hasattr(company, 'description') else None,
                parent_company_id=company.parent_company_id if hasattr(company, 'parent_company_id') else None,
                organization_id=company.organization_id if hasattr(company, 'organization_id') else None,
                user_count=stats.get('user_count', 0),
                contact_count=stats.get('contact_count', 0),
                campaign_count=stats.get('campaign_count', 0),
                created_at=company.created_at if hasattr(company, 'created_at') else datetime.utcnow(),
                updated_at=company.updated_at if hasattr(company, 'updated_at') else datetime.utcnow()
            ))
        
        total_pages = (total + per_page - 1) // per_page
        
        return CompanyListResponse(
            companies=company_responses,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list companies: {str(e)}"
        )

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: str,
    tenant_context: TenantContext = Depends(require_tenant_context),
    session: AsyncSession = Depends(get_session)
):
    """Get company by ID"""
    try:
        # Check access permissions
        if not await _can_access_company(session, tenant_context, company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to company data"
            )
        
        # Get company
        result = await session.execute(
            select(Company).where(Company.id == company_id)
        )
        company = result.scalar_one_or_none()
        
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # Get company stats
        stats = await _get_company_stats(session, company_id)
        
        return CompanyResponse(
            id=company.id,
            name=company.name,
            domain=company.domain,
            industry=company.industry if hasattr(company, 'industry') else None,
            size=company.size if hasattr(company, 'size') else None,
            location=company.location if hasattr(company, 'location') else None,
            website=company.website if hasattr(company, 'website') else None,
            description=company.description if hasattr(company, 'description') else None,
            parent_company_id=company.parent_company_id if hasattr(company, 'parent_company_id') else None,
            organization_id=company.organization_id if hasattr(company, 'organization_id') else None,
            user_count=stats.get('user_count', 0),
            contact_count=stats.get('contact_count', 0),
            campaign_count=stats.get('campaign_count', 0),
            created_at=company.created_at if hasattr(company, 'created_at') else datetime.utcnow(),
            updated_at=company.updated_at if hasattr(company, 'updated_at') else datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get company: {str(e)}"
        )

@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: str,
    company_data: CompanyUpdate,
    tenant_context: TenantContext = Depends(require_tenant_context),
    session: AsyncSession = Depends(get_session)
):
    """Update company"""
    try:
        # Check access permissions
        if not await _can_access_company(session, tenant_context, company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to company data"
            )
        
        # Get company
        result = await session.execute(
            select(Company).where(Company.id == company_id)
        )
        company = result.scalar_one_or_none()
        
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # Update company fields
        update_data = {}
        for field, value in company_data.dict(exclude_unset=True).items():
            if hasattr(company, field):
                setattr(company, field, value)
        
        # Update timestamp
        if hasattr(company, 'updated_at'):
            company.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(company)
        
        # Get updated stats
        stats = await _get_company_stats(session, company_id)
        
        return CompanyResponse(
            id=company.id,
            name=company.name,
            domain=company.domain,
            industry=company.industry if hasattr(company, 'industry') else None,
            size=company.size if hasattr(company, 'size') else None,
            location=company.location if hasattr(company, 'location') else None,
            website=company.website if hasattr(company, 'website') else None,
            description=company.description if hasattr(company, 'description') else None,
            parent_company_id=company.parent_company_id if hasattr(company, 'parent_company_id') else None,
            organization_id=company.organization_id if hasattr(company, 'organization_id') else None,
            user_count=stats.get('user_count', 0),
            contact_count=stats.get('contact_count', 0),
            campaign_count=stats.get('campaign_count', 0),
            created_at=company.created_at if hasattr(company, 'created_at') else datetime.utcnow(),
            updated_at=company.updated_at if hasattr(company, 'updated_at') else datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update company: {str(e)}"
        )

# =============================================================================
# ORGANIZATION MANAGEMENT
# =============================================================================

@router.post("/organizations", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_data: OrganizationCreate,
    tenant_context: TenantContext = Depends(require_tenant_context),
    session: AsyncSession = Depends(get_session)
):
    """Create a new organization"""
    try:
        # Only admins can create organizations
        if not await _is_admin(session, tenant_context.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can create organizations"
            )
        
        # Create organization
        organization = Organization(
            id=str(uuid.uuid4()),
            name=org_data.name,
            # Add additional fields when you extend the Organization model
        )
        
        session.add(organization)
        await session.commit()
        await session.refresh(organization)
        
        return OrganizationResponse(
            id=organization.id,
            name=organization.name,
            description=organization.description if hasattr(organization, 'description') else None,
            industry=organization.industry if hasattr(organization, 'industry') else None,
            website=organization.website if hasattr(organization, 'website') else None,
            parent_organization_id=organization.parent_organization_id if hasattr(organization, 'parent_organization_id') else None,
            company_count=0,
            user_count=0,
            created_at=organization.created_at if hasattr(organization, 'created_at') else datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create organization: {str(e)}"
        )

@router.get("/organizations", response_model=List[OrganizationResponse])
async def list_organizations(
    tenant_context: TenantContext = Depends(require_tenant_context),
    session: AsyncSession = Depends(get_session)
):
    """List organizations user has access to"""
    try:
        query = select(Organization)
        
        # Apply access filtering
        if tenant_context.organization_id:
            # User can see their organization
            query = query.where(Organization.id == tenant_context.organization_id)
        else:
            # User not in organization - can't see any
            return []
        
        result = await session.execute(query)
        organizations = result.scalars().all()
        
        # Convert to response models with stats
        org_responses = []
        for org in organizations:
            stats = await _get_organization_stats(session, org.id)
            
            org_responses.append(OrganizationResponse(
                id=org.id,
                name=org.name,
                description=org.description if hasattr(org, 'description') else None,
                industry=org.industry if hasattr(org, 'industry') else None,
                website=org.website if hasattr(org, 'website') else None,
                parent_organization_id=org.parent_organization_id if hasattr(org, 'parent_organization_id') else None,
                company_count=stats.get('company_count', 0),
                user_count=stats.get('user_count', 0),
                created_at=org.created_at if hasattr(org, 'created_at') else datetime.utcnow()
            ))
        
        return org_responses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list organizations: {str(e)}"
        )

# =============================================================================
# COMPANY HIERARCHY & RELATIONSHIPS
# =============================================================================

@router.get("/{company_id}/hierarchy", response_model=CompanyHierarchy)
async def get_company_hierarchy(
    company_id: str,
    tenant_context: TenantContext = Depends(require_tenant_context),
    session: AsyncSession = Depends(get_session)
):
    """Get company hierarchy (parent, subsidiaries)"""
    try:
        # Check access permissions
        if not await _can_access_company(session, tenant_context, company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to company data"
            )
        
        # Get company hierarchy
        hierarchy = await _build_company_hierarchy(session, company_id)
        return hierarchy
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get company hierarchy: {str(e)}"
        )

@router.get("/{company_id}/stats", response_model=CompanyStats)
async def get_company_statistics(
    company_id: str,
    tenant_context: TenantContext = Depends(require_tenant_context),
    session: AsyncSession = Depends(get_session)
):
    """Get detailed company statistics"""
    try:
        # Check access permissions
        if not await _can_access_company(session, tenant_context, company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to company data"
            )
        
        # Get comprehensive stats
        stats = await _get_comprehensive_company_stats(session, company_id)
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get company statistics: {str(e)}"
        )

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def _can_access_company(session: AsyncSession, tenant_context: TenantContext, company_id: str) -> bool:
    """Check if user can access company data"""
    try:
        # User can always access their own company
        if tenant_context.company_id == company_id:
            return True
        
        # Check if user is admin and company is in same organization
        if tenant_context.organization_id:
            result = await session.execute(
                select(Company).where(
                    and_(
                        Company.id == company_id,
                        Company.organization_id == tenant_context.organization_id
                    )
                )
            )
            company = result.scalar_one_or_none()
            if company and await _is_admin(session, tenant_context.user_id):
                return True
        
        return False
        
    except Exception as e:
        print(f"Error checking company access: {e}")
        return False

async def _is_admin(session: AsyncSession, user_id: str) -> bool:
    """Check if user is admin"""
    try:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        return user and user.role == 'admin'
    except Exception as e:
        print(f"Error checking admin status: {e}")
        return False

async def _get_company_stats(session: AsyncSession, company_id: str) -> Dict[str, Any]:
    """Get basic company statistics"""
    try:
        stats = {}
        
        # User count
        user_result = await session.execute(
            select(func.count(User.id)).where(User.company_id == company_id)
        )
        stats['user_count'] = user_result.scalar() or 0
        
        # Contact count (when you implement tenant-aware contacts)
        stats['contact_count'] = 0
        
        # Campaign count (when you implement tenant-aware campaigns)
        stats['campaign_count'] = 0
        
        return stats
        
    except Exception as e:
        print(f"Error getting company stats: {e}")
        return {'user_count': 0, 'contact_count': 0, 'campaign_count': 0}

async def _get_organization_stats(session: AsyncSession, organization_id: str) -> Dict[str, Any]:
    """Get organization statistics"""
    try:
        stats = {}
        
        # Company count
        company_result = await session.execute(
            select(func.count(Company.id)).where(Company.organization_id == organization_id)
        )
        stats['company_count'] = company_result.scalar() or 0
        
        # User count
        user_result = await session.execute(
            select(func.count(User.id)).where(User.organization_id == organization_id)
        )
        stats['user_count'] = user_result.scalar() or 0
        
        return stats
        
    except Exception as e:
        print(f"Error getting organization stats: {e}")
        return {'company_count': 0, 'user_count': 0}

async def _build_company_hierarchy(session: AsyncSession, company_id: str) -> CompanyHierarchy:
    """Build company hierarchy structure"""
    try:
        # Get company
        result = await session.execute(
            select(Company).where(Company.id == company_id)
        )
        company = result.scalar_one_or_none()
        
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Get subsidiaries
        subsidiaries = []
        if hasattr(company, 'parent_company_id'):
            # This would need to be implemented when you add parent_company_id to Company model
            pass
        
        # Get parent
        parent = None
        if hasattr(company, 'parent_company_id') and company.parent_company_id:
            # This would need to be implemented when you add parent_company_id to Company model
            pass
        
        # Build response
        company_response = CompanyResponse(
            id=company.id,
            name=company.name,
            domain=company.domain,
            industry=company.industry if hasattr(company, 'industry') else None,
            size=company.size if hasattr(company, 'size') else None,
            location=company.location if hasattr(company, 'location') else None,
            website=company.website if hasattr(company, 'website') else None,
            description=company.description if hasattr(company, 'description') else None,
            parent_company_id=company.parent_company_id if hasattr(company, 'parent_company_id') else None,
            organization_id=company.organization_id if hasattr(company, 'organization_id') else None,
            user_count=0,
            contact_count=0,
            campaign_count=0,
            created_at=company.created_at if hasattr(company, 'created_at') else datetime.utcnow(),
            updated_at=company.updated_at if hasattr(company, 'updated_at') else datetime.utcnow()
        )
        
        return CompanyHierarchy(
            company=company_response,
            subsidiaries=subsidiaries,
            parent=parent
        )
        
    except Exception as e:
        print(f"Error building company hierarchy: {e}")
        raise

async def _get_comprehensive_company_stats(session: AsyncSession, company_id: str) -> CompanyStats:
    """Get comprehensive company statistics"""
    try:
        # Basic counts
        basic_stats = await _get_company_stats(session, company_id)
        
        # Additional stats would be implemented here
        # For now, return basic structure
        
        return CompanyStats(
            total_users=basic_stats.get('user_count', 0),
            total_contacts=basic_stats.get('contact_count', 0),
            total_campaigns=basic_stats.get('campaign_count', 0),
            total_messages_sent=0,
            total_connections_made=0,
            average_lead_score=0.0,
            monthly_growth=0.0,
            top_performing_users=[]
        )
        
    except Exception as e:
        print(f"Error getting comprehensive company stats: {e}")
        raise
