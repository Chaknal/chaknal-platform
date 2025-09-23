"""
Agency API Endpoints for Multi-Client Management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from pydantic import BaseModel
from database.database import get_session
from app.auth.dependencies import get_current_user
from app.services.agency_service import AgencyService
from app.models.agency import AgencyClient
from app.models.user import User
from app.models.company import Company
from sqlalchemy import select
import uuid


router = APIRouter(prefix="/api/agency", tags=["agency"])


# Pydantic models
class ClientAddRequest(BaseModel):
    client_company_id: str
    access_level: str = "full"


class ReadOnlyUserRequest(BaseModel):
    client_company_id: str
    email: str
    first_name: str
    last_name: str


class ClientSwitchResponse(BaseModel):
    success: bool
    client_data: Dict[str, Any]
    message: str


# Agency endpoints
@router.get("/clients")
async def get_agency_clients(
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get all clients managed by the current agency user"""
    if not current_user.get("is_agency"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Agency access required."
        )
    
    try:
        clients = await AgencyService.get_agency_clients(session, current_user["user_id"])
        return {
            "success": True,
            "clients": clients,
            "total_clients": len(clients)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving clients: {str(e)}"
        )


@router.post("/clients/add")
async def add_client_to_agency(
    request: ClientAddRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Add a client company to the agency user's managed clients"""
    if not current_user.get("is_agency"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Agency access required."
        )
    
    try:
        result = await AgencyService.add_client_to_agency(
            session,
            current_user["user_id"],
            request.client_company_id,
            request.access_level
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding client: {str(e)}"
        )


@router.delete("/clients/{client_company_id}")
async def remove_client_from_agency(
    client_company_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Remove a client company from the agency user's managed clients"""
    if not current_user.get("is_agency"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Agency access required."
        )
    
    try:
        result = await AgencyService.remove_client_from_agency(
            session,
            current_user["user_id"],
            client_company_id
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing client: {str(e)}"
        )


@router.post("/switch-client/{client_company_id}")
async def switch_client_context(
    client_company_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Switch to a different client context for agency users"""
    if not current_user.get("is_agency"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Agency access required."
        )
    
    try:
        # Verify the agency user has access to this client
        agency_client_query = select(AgencyClient).where(
            AgencyClient.agency_user_id == current_user["user_id"],
            AgencyClient.client_company_id == client_company_id,
            AgencyClient.is_active == True
        )
        result = await session.execute(agency_client_query)
        agency_client = result.scalar_one_or_none()
        
        if not agency_client:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You don't have permission to access this client."
            )
        
        # Get client company data
        company_query = select(Company).where(Company.id == client_company_id)
        company_result = await session.execute(company_query)
        client_company = company_result.scalar_one_or_none()
        
        if not client_company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client company not found."
            )
        
        # Get client statistics
        stats = await AgencyService._get_client_stats(session, client_company_id)
        
        client_data = {
            "id": client_company.id,
            "name": client_company.name,
            "domain": client_company.domain,
            "access_level": agency_client.access_level,
            "stats": stats
        }
        
        return ClientSwitchResponse(
            success=True,
            client_data=client_data,
            message="Client context switched successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error switching client context: {str(e)}"
        )


@router.get("/overview")
async def get_agency_overview(
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get overview statistics for the agency user"""
    if not current_user.get("is_agency"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Agency access required."
        )
    
    try:
        overview = await AgencyService.get_agency_overview(session, current_user["user_id"])
        return {
            "success": True,
            "overview": overview
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving agency overview: {str(e)}"
        )


@router.post("/create-read-only-user")
async def create_read_only_user(
    request: ReadOnlyUserRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Create a read-only user for a client"""
    if not current_user.get("is_agency"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Agency access required."
        )
    
    try:
        # Verify the agency user has access to this client
        agency_client_query = select(AgencyClient).where(
            AgencyClient.agency_user_id == current_user["user_id"],
            AgencyClient.client_company_id == request.client_company_id,
            AgencyClient.is_active == True
        )
        result = await session.execute(agency_client_query)
        agency_client = result.scalar_one_or_none()
        
        if not agency_client:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You don't have permission to create users for this client."
            )
        
        result = await AgencyService.create_read_only_user(
            session,
            current_user["user_id"],
            request.client_company_id,
            request.email,
            request.first_name,
            request.last_name
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "user_id": result["user_id"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating read-only user: {str(e)}"
        )


@router.get("/available-companies")
async def get_available_companies(
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get all companies that can be added as clients (excluding agency's own company)"""
    if not current_user.get("is_agency"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Agency access required."
        )
    
    try:
        # Get all companies except the agency's own company
        companies_query = select(Company).where(
            Company.id != current_user.get("agency_company_id")
        )
        result = await session.execute(companies_query)
        companies = result.scalars().all()
        
        # Get already managed clients
        managed_clients = await AgencyService.get_agency_clients(session, current_user["user_id"])
        managed_client_ids = {client["id"] for client in managed_clients}
        
        available_companies = [
            {
                "id": company.id,
                "name": company.name,
                "domain": company.domain,
                "is_managed": company.id in managed_client_ids
            }
            for company in companies
        ]
        
        return {
            "success": True,
            "companies": available_companies
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving available companies: {str(e)}"
        )
