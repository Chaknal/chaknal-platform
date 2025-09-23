from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
from passlib.context import CryptContext

from database.database import get_session
from app.models.user import User, Organization
from app.models.company import Company
from app.models.duxsoup_user import DuxSoupUser
from app.auth.jwt_handler import get_password_hash, verify_password
from app.auth.dependencies import get_current_user

# =============================================================================
# SCHEMAS (Defined first to avoid forward reference issues)
# =============================================================================

class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    is_verified: bool
    role: str
    company_name: Optional[str]
    company_domain: Optional[str]
    phone: Optional[str]
    bio: Optional[str]
    linkedin_url: Optional[str]
    timezone: Optional[str]
    created_at: datetime
    updated_at: datetime

class UserListResponse(BaseModel):
    """User list response with pagination"""
    users: List[UserResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

router = APIRouter(prefix="/api/users", tags=["User Management"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# =============================================================================
# SCHEMAS
# =============================================================================

class UserRegistration(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    confirm_password: str
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    company_name: Optional[str] = Field(None, max_length=255)
    company_domain: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    role: str = Field(default="user", description="User role: user, admin, manager")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class UserProfile(BaseModel):
    """User profile update request"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    company_name: Optional[str] = Field(None, max_length=255)
    company_domain: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=1000)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    timezone: Optional[str] = Field(None, max_length=50)


class PasswordChange(BaseModel):
    """Password change request"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_new_password: str
    
    @validator('confirm_new_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('New passwords do not match')
        return v

class UserStats(BaseModel):
    """User statistics"""
    total_campaigns: int
    total_contacts: int
    total_messages_sent: int
    connection_requests_sent: int
    profile_visits: int
    last_activity: Optional[datetime]

# =============================================================================
# USER REGISTRATION & MANAGEMENT
# =============================================================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegistration,
    session: AsyncSession = Depends(get_session)
):
    """Register a new user"""
    try:
        # Check if user already exists
        result = await session.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Skip company creation for now to avoid async issues
        company_id = None
        
        # Create user
        user = User(
            id=str(uuid.uuid4()),
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            company_id=company_id,
            is_active=True,
            is_verified=False,
            role=user_data.role
        )
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        # Create DuxSoup user if needed
        if user_data.role in ["admin", "manager"]:
            await _create_duxsoup_user(session, user)
        
        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            role=user.role,
            company_name=user.company.name if user.company else None,
            company_domain=user.company.domain if user.company else None,
            phone=user.phone,
            bio=user.bio if hasattr(user, 'bio') else None,
            linkedin_url=user.linkedin_url if hasattr(user, 'linkedin_url') else None,
            timezone=user.timezone if hasattr(user, 'timezone') else None,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user: {str(e)}"
        )

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get current user's profile"""
    try:
        result = await session.execute(
            select(User).where(User.id == current_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            role=user.role,
            company_name=user.company.name if user.company else None,
            company_domain=user.company.domain if user.company else None,
            phone=user.phone,
            bio=user.bio if hasattr(user, 'bio') else None,
            linkedin_url=user.linkedin_url if hasattr(user, 'linkedin_url') else None,
            timezone=user.timezone if hasattr(user, 'timezone') else None,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    profile_data: UserProfile,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Update current user's profile"""
    try:
        # Get or create company if company info is provided
        company_id = None
        if profile_data.company_name or profile_data.company_domain:
            company_id = await _get_or_create_company(
                session, profile_data.company_name, profile_data.company_domain
            )
        
        # Update user
        update_data = {
            "first_name": profile_data.first_name,
            "last_name": profile_data.last_name,
            "phone": profile_data.phone,
            "company_id": company_id,
            "updated_at": datetime.utcnow()
        }
        
        # Add optional fields if they exist in the model
        if hasattr(User, 'bio') and profile_data.bio is not None:
            update_data["bio"] = profile_data.bio
        if hasattr(User, 'linkedin_url') and profile_data.linkedin_url is not None:
            update_data["linkedin_url"] = profile_data.linkedin_url
        if hasattr(User, 'timezone') and profile_data.timezone is not None:
            update_data["timezone"] = profile_data.timezone
        
        await session.execute(
            update(User)
            .where(User.id == current_user.id)
            .values(**update_data)
        )
        await session.commit()
        
        # Get updated user
        result = await session.execute(
            select(User).where(User.id == current_user.id)
        )
        user = result.scalar_one_or_none()
        
        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            role=user.role,
            company_name=user.company.name if user.company else None,
            company_domain=user.company.domain if user.company else None,
            phone=user.phone,
            bio=user.bio if hasattr(user, 'bio') else None,
            linkedin_url=user.linkedin_url if hasattr(user, 'linkedin_url') else None,
            timezone=user.timezone if hasattr(user, 'timezone') else None,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Change user password"""
    try:
        # Verify current password
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        await session.execute(
            update(User)
            .where(User.id == current_user.id)
            .values(
                hashed_password=get_password_hash(password_data.new_password),
                updated_at=datetime.utcnow()
            )
        )
        await session.commit()
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )

# =============================================================================
# USER ADMINISTRATION (Admin Only)
# =============================================================================

@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Users per page"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    role: Optional[str] = Query(None, description="Filter by role"),
    company_id: Optional[str] = Query(None, description="Filter by company"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """List all users (admin only)"""
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    try:
        # Build query
        query = select(User)
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                (User.first_name.ilike(search_term)) |
                (User.last_name.ilike(search_term)) |
                (User.email.ilike(search_term))
            )
        
        if role:
            query = query.where(User.role == role)
        
        if company_id:
            query = query.where(User.company_id == company_id)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await session.execute(query)
        users = result.scalars().all()
        
        # Convert to response models
        user_responses = []
        for user in users:
            user_responses.append(UserResponse(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_active=user.is_active,
                is_verified=user.is_verified,
                role=user.role,
                company_name=user.company.name if user.company else None,
                company_domain=user.company.domain if user.company else None,
                phone=user.phone,
                bio=user.bio if hasattr(user, 'bio') else None,
                linkedin_url=user.linkedin_url if hasattr(user, 'linkedin_url') else None,
                timezone=user.timezone if hasattr(user, 'timezone') else None,
                created_at=user.created_at,
                updated_at=user.updated_at
            ))
        
        total_pages = (total + per_page - 1) // per_page
        
        return UserListResponse(
            users=user_responses,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list users: {str(e)}"
        )

@router.put("/{user_id}/status")
async def update_user_status(
    user_id: str,
    is_active: bool,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Update user status (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        # Update user status
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                is_active=is_active,
                updated_at=datetime.utcnow()
            )
        )
        await session.commit()
        
        return {"message": f"User status updated to {'active' if is_active else 'inactive'}"}
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user status: {str(e)}"
        )

@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get user statistics"""
    try:
        # Get campaign count
        from app.models.campaign import Campaign
        campaign_result = await session.execute(
            select(func.count(Campaign.campaign_id))
            .where(Campaign.dux_user_id == current_user.id)
        )
        total_campaigns = campaign_result.scalar() or 0
        
        # Get contact count
        from app.models.contact import Contact
        contact_result = await session.execute(
            select(func.count(Contact.contact_id))
        )
        total_contacts = contact_result.scalar() or 0
        
        # Get message count
        from app.models.message import Message
        message_result = await session.execute(
            select(func.count(Message.message_id))
            .where(Message.user_id == current_user.id)
        )
        total_messages_sent = message_result.scalar() or 0
        
        # Placeholder for other stats (implement based on your data model)
        connection_requests_sent = 0
        profile_visits = 0
        last_activity = current_user.updated_at
        
        return UserStats(
            total_campaigns=total_campaigns,
            total_contacts=total_contacts,
            total_messages_sent=total_messages_sent,
            connection_requests_sent=connection_requests_sent,
            profile_visits=profile_visits,
            last_activity=last_activity
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user stats: {str(e)}"
        )

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def _get_or_create_company(
    session: AsyncSession, 
    company_name: Optional[str], 
    company_domain: Optional[str]
) -> Optional[str]:
    """Get or create company based on name/domain"""
    if not company_name and not company_domain:
        return None
    
    try:
        # Try to find existing company
        if company_domain:
            result = await session.execute(
                select(Company).where(Company.domain == company_domain)
            )
            company = result.scalar_one_or_none()
            if company:
                return company.id
        
        if company_name:
            result = await session.execute(
                select(Company).where(Company.name == company_name)
            )
            company = result.scalar_one_or_none()
            if company:
                return company.id
        
        # Create new company
        company = Company(
            id=str(uuid.uuid4()),
            name=company_name or company_domain,
            domain=company_domain
        )
        session.add(company)
        await session.commit()
        await session.refresh(company)
        
        return company.id
        
    except Exception as e:
        print(f"Error getting/creating company: {e}")
        return None

async def _create_duxsoup_user(session: AsyncSession, user: User) -> None:
    """Create DuxSoup user for admin/manager users"""
    try:
        # Check if DuxSoup user already exists
        result = await session.execute(
            select(DuxSoupUser).where(DuxSoupUser.user_id == user.id)
        )
        if result.scalar_one_or_none():
            return
        
        # Create placeholder DuxSoup user
        dux_user = DuxSoupUser(
            id=str(uuid.uuid4()),
            dux_soup_user_id=f"user_{user.id[:8]}",
            dux_soup_auth_key="",  # Will be set when user connects DuxSoup
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            user_id=user.id
        )
        
        session.add(dux_user)
        await session.commit()
        
    except Exception as e:
        print(f"Error creating DuxSoup user: {e}")

# Placeholder for authentication dependency
async def get_current_user() -> User:
    """Get current authenticated user - implement based on your auth system"""
    # This should be implemented based on your JWT authentication
    # For now, returning a mock user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required"
    )
