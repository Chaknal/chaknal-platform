"""
Authentication endpoints for Chaknal Platform
Handles login, logout, and user context with organization info
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from database.database import get_session
from app.auth.auth_service import AuthService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# Request/Response models
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_context: dict

class UserContextResponse(BaseModel):
    user_id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_superuser: bool
    is_verified: bool
    organization: Optional[dict]
    company: Optional[dict]
    permissions: list

@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Authenticate user and return JWT token with organization context
    """
    try:
        # Authenticate user
        user_context = await AuthService.authenticate_user(
            session, 
            login_data.email, 
            login_data.password
        )
        
        if not user_context:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create JWT token
        access_token = AuthService.create_user_token(user_context)
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_context=user_context
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@router.get("/me", response_model=UserContextResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session)
):
    """
    Get current user context including organization and company info
    """
    try:
        token = credentials.credentials
        user_context = await AuthService.get_user_by_token(session, token)
        
        if not user_context:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        return UserContextResponse(**user_context)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get user context error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/logout")
async def logout():
    """
    Logout endpoint (client should discard token)
    """
    return {"message": "Successfully logged out"}

@router.get("/organization")
async def get_user_organization(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session)
):
    """
    Get user's organization details
    """
    try:
        token = credentials.credentials
        user_context = await AuthService.get_user_by_token(session, token)
        
        if not user_context:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        if not user_context.get("organization"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not associated with any organization"
            )
        
        return {
            "organization": user_context["organization"],
            "company": user_context["company"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get organization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/permissions")
async def get_user_permissions(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session)
):
    """
    Get user's permissions based on role and organization
    """
    try:
        token = credentials.credentials
        user_context = await AuthService.get_user_by_token(session, token)
        
        if not user_context:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        return {
            "permissions": user_context["permissions"],
            "is_superuser": user_context["is_superuser"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get permissions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
