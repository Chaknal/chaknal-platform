"""
Authentication dependencies for Chaknal Platform
Provides reusable dependencies for getting current user and organization context
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from database.database import get_session
from app.auth.auth_service import AuthService
from sqlalchemy.ext.asyncio import AsyncSession

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user
    Use this in other endpoints: @app.get("/campaigns", dependencies=[Depends(get_current_user)])
    """
    try:
        token = credentials.credentials
        user_context = await AuthService.get_user_by_token(session, token)
        
        if not user_context:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        return user_context
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get current user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

async def get_current_user_organization(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependency to get current user's organization
    Use this when you need organization context: @app.get("/campaigns", dependencies=[Depends(get_current_user_organization)])
    """
    if not current_user.get("organization"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not associated with any organization"
        )
    
    return current_user["organization"]

async def get_current_user_company(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependency to get current user's company
    Use this when you need company context: @app.get("/company-data", dependencies=[Depends(get_current_user_company)])
    """
    if not current_user.get("company"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not associated with any company"
        )
    
    return current_user["company"]

async def require_permission(
    required_permission: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependency to require specific permission
    Use this for permission-based access: @app.post("/campaigns", dependencies=[Depends(require_permission("campaign:write"))])
    """
    if required_permission not in current_user.get("permissions", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {required_permission} required"
        )
    
    return current_user

async def require_superuser(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependency to require superuser access
    Use this for admin-only endpoints: @app.delete("/users/{user_id}", dependencies=[Depends(require_superuser)])
    """
    if not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser access required"
        )
    
    return current_user

# Example usage in other endpoints:
"""
@app.get("/campaigns")
async def get_campaigns(
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # current_user contains: user_id, email, organization, company, permissions
    user_org_id = current_user["organization"]["id"]
    user_company_id = current_user["company"]["id"]
    
    # Filter campaigns by user's organization/company
    campaigns = await get_campaigns_for_organization(session, user_org_id)
    return campaigns

@app.post("/campaigns")
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: Dict[str, Any] = Depends(require_permission("campaign:write")),
    session: AsyncSession = Depends(get_session)
):
    # User has permission to create campaigns
    # current_user contains full context
    return await create_campaign_for_user(session, campaign_data, current_user)
"""
