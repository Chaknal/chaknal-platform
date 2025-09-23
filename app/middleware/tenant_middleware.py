"""
Tenant Middleware

This middleware automatically enforces tenant boundaries and sets
tenant context for all requests based on the authenticated user.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.company import Company
from app.models.tenant_aware import TenantContext, set_current_tenant_context, clear_current_tenant_context
from database.database import get_session

logger = logging.getLogger(__name__)


class TenantMiddleware:
    """
    Middleware to enforce tenant boundaries
    
    This middleware:
    1. Extracts user information from the request
    2. Sets tenant context based on user's company/organization
    3. Ensures all subsequent operations are tenant-scoped
    4. Prevents cross-tenant data access
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Skip tenant context for public endpoints
            if self._is_public_endpoint(request.url.path):
                await self.app(scope, receive, send)
                return
            
            try:
                # Set tenant context based on authenticated user
                await self._set_tenant_context(request)
                
                # Process the request
                await self.app(scope, receive, send)
                
            except HTTPException:
                # Re-raise HTTP exceptions
                raise
            except Exception as e:
                logger.error(f"Tenant middleware error: {e}")
                # Return error response
                response = JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"detail": "Internal server error"}
                )
                await response(scope, receive, send)
            finally:
                # Always clear tenant context
                clear_current_tenant_context()
        else:
            await self.app(scope, receive, send)
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public (no tenant context needed)"""
        public_paths = [
            "/",
            "/health",
            "/docs",
            "/openapi.json",
            "/auth/login",
            "/auth/google/login",
            "/auth/google/callback",
            "/static/",
            "/api/status"
        ]
        
        return any(path.startswith(public_path) for public_path in public_paths)
    
    async def _set_tenant_context(self, request: Request):
        """Set tenant context based on authenticated user"""
        try:
            # Get user from request (implement based on your auth system)
            user = await self._get_authenticated_user(request)
            
            if not user:
                # No authenticated user, skip tenant context
                return
            
            # Create tenant context
            tenant_context = TenantContext(
                company_id=user.company_id,
                organization_id=user.organization_id,
                user_id=user.id
            )
            
            # Set tenant context
            set_current_tenant_context(tenant_context)
            
            logger.info(f"Set tenant context: company={user.company_id}, org={user.organization_id}")
            
        except Exception as e:
            logger.error(f"Failed to set tenant context: {e}")
            # Don't fail the request, just log the error
            pass
    
    async def _get_authenticated_user(self, request: Request) -> Optional[User]:
        """Get authenticated user from request"""
        try:
            # This is a placeholder - implement based on your authentication system
            # You might get the user from JWT token, session, etc.
            
            # Example: Extract user ID from JWT token
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            # For now, return None - implement actual user extraction
            # user_id = extract_user_id_from_jwt(auth_header.split(" ")[1])
            # user = await get_user_by_id(user_id)
            # return user
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get authenticated user: {e}")
            return None


async def get_tenant_context_from_request(request: Request) -> Optional[TenantContext]:
    """
    Get tenant context from request (for use in route handlers)
    
    This allows route handlers to access tenant context without
    going through the middleware.
    """
    try:
        # Get user from request
        user = await get_authenticated_user_from_request(request)
        
        if not user:
            return None
        
        return TenantContext(
            company_id=user.company_id,
            organization_id=user.organization_id,
            user_id=user.id
        )
        
    except Exception as e:
        logger.error(f"Failed to get tenant context from request: {e}")
        return None


async def get_authenticated_user_from_request(request: Request) -> Optional[User]:
    """
    Get authenticated user from request
    
    This is a placeholder function - implement based on your
    authentication system.
    """
    try:
        # Extract user from request based on your auth system
        # This might involve:
        # 1. JWT token validation
        # 2. Session lookup
        # 3. API key validation
        # 4. OAuth token validation
        
        # For now, return None
        return None
        
    except Exception as e:
        logger.error(f"Failed to get authenticated user from request: {e}")
        return None


def require_tenant_context():
    """
    Dependency to require tenant context in route handlers
    
    Usage:
    @app.get("/protected")
    async def protected_endpoint(
        tenant_context: TenantContext = Depends(require_tenant_context)
    ):
        # This endpoint requires tenant context
        pass
    """
    async def dependency(request: Request):
        tenant_context = await get_tenant_context_from_request(request)
        if not tenant_context:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant context required"
            )
        return tenant_context
    
    return dependency


def require_company_access(company_id: str):
    """
    Dependency to require access to specific company data
    
    Usage:
    @app.get("/company/{company_id}/data")
    async def get_company_data(
        company_id: str,
        tenant_context: TenantContext = Depends(require_tenant_context),
        _: bool = Depends(require_company_access(company_id))
    ):
        # This endpoint requires access to specific company
        pass
    """
    async def dependency(tenant_context: TenantContext = Depends(require_tenant_context)):
        if tenant_context.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to company data"
            )
        return True
    
    return dependency


def require_organization_access(organization_id: str):
    """
    Dependency to require access to organization data
    
    Usage:
    @app.get("/organization/{organization_id}/data")
    async def get_organization_data(
        organization_id: str,
        tenant_context: TenantContext = Depends(require_tenant_context),
        _: bool = Depends(require_organization_access(organization_id))
    ):
        # This endpoint requires access to organization data
        pass
    """
    async def dependency(tenant_context: TenantContext = Depends(require_tenant_context)):
        if tenant_context.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to organization data"
            )
        return True
    
    return dependency


def require_role(required_role: str):
    """
    Dependency to require specific user role
    
    Usage:
    @app.get("/admin-only")
    async def admin_endpoint(
        tenant_context: TenantContext = Depends(require_tenant_context),
        _: bool = Depends(require_role("admin"))
    ):
        # This endpoint requires admin role
        pass
    """
    async def dependency(tenant_context: TenantContext = Depends(require_tenant_context)):
        # Get user to check role
        user = await get_user_by_id(tenant_context.user_id)
        if not user or user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        return True
    
    return dependency


async def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by ID"""
    try:
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Failed to get user by ID: {e}")
        return None


# Tenant context dependency for route handlers
async def get_current_tenant_context() -> Optional[TenantContext]:
    """
    Get current tenant context
    
    This can be used as a dependency in route handlers to access
    the current tenant context.
    """
    from app.models.tenant_aware import get_current_tenant_context as get_context
    return get_context()
