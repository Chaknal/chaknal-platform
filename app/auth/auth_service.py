"""
Authentication Service for Chaknal Platform
Handles user login, JWT tokens, and organization context
"""

from jose import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User, Organization
from app.models.company import Company
from app.services.company_service import CompanyService
from app.auth.jwt_handler import verify_password, create_access_token
from config.settings import settings

class AuthService:
    """Service for handling authentication and user context"""
    
    @staticmethod
    async def authenticate_user(session: AsyncSession, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user and return user context with organization info
        """
        try:
            # Find user by email
            user_query = select(User).where(User.email == email)
            result = await session.execute(user_query)
            user = result.scalar_one_or_none()
            
            if not user:
                return None
                
            # Verify password
            if not verify_password(password, user.hashed_password):
                return None
                
            # Check if user is active
            if not user.is_active:
                return None
                
            # Fetch organization and company info
            org_query = select(Organization).where(Organization.id == user.organization_id)
            org_result = await session.execute(org_query)
            organization = org_result.scalar_one_or_none()
            
            company_query = select(Company).where(Company.id == user.company_id)
            company_result = await session.execute(company_query)
            company = company_result.scalar_one_or_none()
            
            # If user doesn't have company/organization, auto-associate them
            if not company or not organization:
                try:
                    association_result = await CompanyService.associate_user_with_company(
                        session, user.email, user.id
                    )
                    # Refresh user data after association
                    user.company_id = association_result["company"]["id"]
                    user.organization_id = association_result["organization"]["id"]
                    
                    # Update organization and company variables
                    organization = await session.get(Organization, association_result["organization"]["id"])
                    company = await session.get(Company, association_result["company"]["id"])
                    
                    print(f"✅ Auto-associated user {user.email} with company {company.name}")
                except Exception as e:
                    print(f"⚠️ Could not auto-associate user: {e}")
            
            # Build user context
            user_context = {
                "user_id": user.id,
                "email": user.email,
                "first_name": getattr(user, 'first_name', None),
                "last_name": getattr(user, 'last_name', None),
                "is_superuser": user.is_superuser,
                "is_verified": user.is_verified,
                "organization": {
                    "id": organization.id if organization else None,
                    "name": organization.name if organization else None
                } if organization else None,
                "company": {
                    "id": company.id if company else None,
                    "name": company.name if company else None,
                    "domain": company.domain if company else None
                } if company else None,
                "permissions": AuthService._get_user_permissions(user, organization)
            }
            
            return user_context
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    @staticmethod
    def _get_user_permissions(user: User, organization: Optional[Organization]) -> list:
        """
        Get user permissions based on role and organization
        """
        permissions = ["user:read"]
        
        if user.is_superuser:
            permissions.extend([
                "user:write", "user:delete",
                "campaign:read", "campaign:write", "campaign:delete",
                "contact:read", "contact:write", "contact:delete",
                "organization:read", "organization:write", "organization:delete",
                "company:read", "company:write", "company:delete"
            ])
        else:
            # Regular user permissions
            permissions.extend([
                "campaign:read", "campaign:write",
                "contact:read", "contact:write",
                "message:read", "message:write"
            ])
            
            # Organization-specific permissions
            if organization:
                permissions.extend([
                    "organization:read",
                    "company:read"
                ])
        
        return permissions
    
    @staticmethod
    async def get_user_by_token(session: AsyncSession, token: str) -> Optional[Dict[str, Any]]:
        """
        Get user context from JWT token
        """
        try:
            # Decode JWT token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            
            if not user_id:
                return None
                
            # Fetch current user data
            user_query = select(User).where(User.id == user_id)
            result = await session.execute(user_query)
            user = result.scalar_one_or_none()
            
            if not user or not user.is_active:
                return None
                
            # Fetch organization and company info
            org_query = select(Organization).where(Organization.id == user.organization_id)
            org_result = await session.execute(org_query)
            organization = org_result.scalar_one_or_none()
            
            company_query = select(Company).where(Company.id == user.company_id)
            company_result = await session.execute(company_query)
            company = company_result.scalar_one_or_none()
            
            # Return user context
            return {
                "user_id": user.id,
                "email": user.email,
                "first_name": getattr(user, 'first_name', None),
                "last_name": getattr(user, 'last_name', None),
                "is_superuser": user.is_superuser,
                "is_verified": user.is_verified,
                "organization": {
                    "id": organization.id if organization else None,
                    "name": organization.name if organization else None
                } if organization else None,
                "company": {
                    "id": company.id if company else None,
                    "name": company.name if company else None,
                    "domain": company.domain if company else None
                } if company else None,
                "permissions": AuthService._get_user_permissions(user, organization)
            }
            
        except jwt.ExpiredSignatureError:
            print("Token expired")
            return None
        except jwt.JWTError:
            print("Invalid token")
            return None
        except Exception as e:
            print(f"Token validation error: {e}")
            return None
    
    @staticmethod
    def create_user_token(user_context: Dict[str, Any]) -> str:
        """
        Create JWT token for authenticated user
        """
        # Prepare token data
        token_data = {
            "sub": user_context["user_id"],
            "email": user_context["email"],
            "org_id": user_context["organization"]["id"] if user_context["organization"] else None,
            "company_id": user_context["company"]["id"] if user_context["company"] else None,
            "permissions": user_context["permissions"],
            "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        
        # Create token
        token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return token
