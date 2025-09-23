"""
User Registration endpoints for Chaknal Platform
Demonstrates automatic company association based on email domains
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from database.database import get_session
from app.models.user import User
from app.services.company_service import CompanyService
from app.auth.jwt_handler import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

router = APIRouter(prefix="/users", tags=["user management"])

# Request/Response models
class UserRegistrationRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    preferred_org_name: Optional[str] = None

class UserRegistrationResponse(BaseModel):
    user_id: str
    email: str
    message: str
    company: dict
    organization: dict

@router.post("/register", response_model=UserRegistrationResponse)
async def register_user(
    user_data: UserRegistrationRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Register a new user with automatic company association
    """
    try:
        # Check if user already exists
        from sqlalchemy import select
        existing_user_query = select(User).where(User.email == user_data.email)
        result = await session.execute(existing_user_query)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user
        user = User(
            id=str(uuid.uuid4()),
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            is_active="true",
            is_superuser="false",
            is_verified="false"
        )
        
        session.add(user)
        await session.flush()
        
        # Automatically associate user with company based on email domain
        association_result = await CompanyService.associate_user_with_company(
            session, 
            user_data.email, 
            user.id,
            user_data.preferred_org_name
        )
        
        # Commit all changes
        await session.commit()
        
        return UserRegistrationResponse(
            user_id=user.id,
            email=user.email,
            message=f"User registered successfully and associated with {association_result['company']['name']}",
            company=association_result['company'],
            organization=association_result['organization']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        print(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@router.get("/company-info/{email}")
async def get_company_info_by_email(
    email: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get company information for a given email domain
    """
    try:
        company = await CompanyService.get_company_by_user_email(session, email)
        
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No company found for this email domain"
            )
        
        # Get organizations for this company
        organizations = await CompanyService.get_organizations_by_company(session, company.id)
        
        return {
            "company": {
                "id": company.id,
                "name": company.name,
                "domain": company.domain
            },
            "organizations": [
                {
                    "id": org.id,
                    "name": org.name
                } for org in organizations
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get company info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/create-organization")
async def create_organization(
    org_name: str,
    description: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new organization for a company
    """
    try:
        # This would typically require authentication and company context
        # For demo purposes, we'll create a default company
        company = await CompanyService.get_or_create_company_by_domain(
            session, "example.com", "Example Company"
        )
        
        organization = await CompanyService.create_custom_organization(
            session, company.id, org_name, description
        )
        
        await session.commit()
        
        return {
            "message": "Organization created successfully",
            "organization": {
                "id": organization.id,
                "name": organization.name,
                "company_id": organization.company_id
            }
        }
        
    except Exception as e:
        await session.rollback()
        print(f"Create organization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
