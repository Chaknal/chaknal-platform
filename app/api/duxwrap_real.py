"""
Real DuxWrap API Endpoints
API endpoints that use the real DuxWrap integration
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import logging

from database.database import get_session
from models.user import User
from models.duxsoup_user import DuxSoupUser
from services.duxwrap_service import get_duxwrap_service, duxwrap_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/duxwrap", tags=["duxwrap"])


class ProfileVisitRequest(BaseModel):
    profile_url: str


class ConnectionRequest(BaseModel):
    profile_url: str
    message: Optional[str] = None


class MessageRequest(BaseModel):
    profile_url: str
    message: str


class WaitRequest(BaseModel):
    duration_minutes: int = 5


class BatchActionRequest(BaseModel):
    actions: List[Dict[str, Any]]


@router.get("/health")
async def get_health_status(db: AsyncSession = Depends(get_session)):
    """Get DuxWrap system health status"""
    try:
        # Get all health status
        all_health = await duxwrap_manager.get_all_health_status()
        stats = duxwrap_manager.get_stats()
        
        return {
            "success": True,
            "data": {
                "overall_stats": stats,
                "services": all_health,
                "timestamp": "2025-09-16T16:00:00Z"
            }
        }
    except Exception as e:
        logger.error(f"Failed to get health status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/{user_id}")
async def get_user_profile(user_id: str, db: AsyncSession = Depends(get_session)):
    """Get DuxSoup user profile"""
    try:
        # Get DuxSoup user from database
        dux_user = db.query(DuxSoupUser).filter(DuxSoupUser.user_id == user_id).first()
        if not dux_user:
            raise HTTPException(status_code=404, detail="DuxSoup user not found")
        
        # Get DuxWrap service
        service = get_duxwrap_service(user_id, dux_user.apikey, dux_user.userid)
        if not service:
            raise HTTPException(status_code=500, detail="DuxWrap service not available")
        
        # Get profile
        profile_result = await service.get_profile()
        
        if profile_result["success"]:
            return {
                "success": True,
                "data": profile_result["data"]
            }
        else:
            raise HTTPException(status_code=400, detail=profile_result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get profile for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue/{user_id}")
async def get_queue_status(user_id: str, db: AsyncSession = Depends(get_session)):
    """Get automation queue status"""
    try:
        # Get DuxSoup user from database
        dux_user = db.query(DuxSoupUser).filter(DuxSoupUser.user_id == user_id).first()
        if not dux_user:
            raise HTTPException(status_code=404, detail="DuxSoup user not found")
        
        # Get DuxWrap service
        service = get_duxwrap_service(user_id, dux_user.apikey, dux_user.userid)
        if not service:
            raise HTTPException(status_code=500, detail="DuxWrap service not available")
        
        # Get queue status
        queue_result = await service.get_queue_status()
        
        if queue_result["success"]:
            return {
                "success": True,
                "data": queue_result["data"]
            }
        else:
            raise HTTPException(status_code=400, detail=queue_result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get queue status for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/visit/{user_id}")
async def visit_profile(user_id: str, request: ProfileVisitRequest, db: AsyncSession = Depends(get_session)):
    """Queue a profile visit"""
    try:
        # Get DuxSoup user from database
        dux_user = db.query(DuxSoupUser).filter(DuxSoupUser.user_id == user_id).first()
        if not dux_user:
            raise HTTPException(status_code=404, detail="DuxSoup user not found")
        
        # Get DuxWrap service
        service = get_duxwrap_service(user_id, dux_user.apikey, dux_user.userid)
        if not service:
            raise HTTPException(status_code=500, detail="DuxWrap service not available")
        
        # Queue visit
        visit_result = await service.visit_profile(request.profile_url)
        
        if visit_result["success"]:
            return {
                "success": True,
                "data": visit_result["data"]
            }
        else:
            raise HTTPException(status_code=400, detail=visit_result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to queue visit for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/connect/{user_id}")
async def send_connection_request(user_id: str, request: ConnectionRequest, db: AsyncSession = Depends(get_session)):
    """Queue a connection request"""
    try:
        # Get DuxSoup user from database
        dux_user = db.query(DuxSoupUser).filter(DuxSoupUser.user_id == user_id).first()
        if not dux_user:
            raise HTTPException(status_code=404, detail="DuxSoup user not found")
        
        # Get DuxWrap service
        service = get_duxwrap_service(user_id, dux_user.apikey, dux_user.userid)
        if not service:
            raise HTTPException(status_code=500, detail="DuxWrap service not available")
        
        # Queue connection
        connect_result = await service.send_connection_request(request.profile_url, request.message)
        
        if connect_result["success"]:
            return {
                "success": True,
                "data": connect_result["data"]
            }
        else:
            raise HTTPException(status_code=400, detail=connect_result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to queue connection for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message/{user_id}")
async def send_message(user_id: str, request: MessageRequest, db: AsyncSession = Depends(get_session)):
    """Queue a direct message"""
    try:
        # Get DuxSoup user from database
        dux_user = db.query(DuxSoupUser).filter(DuxSoupUser.user_id == user_id).first()
        if not dux_user:
            raise HTTPException(status_code=404, detail="DuxSoup user not found")
        
        # Get DuxWrap service
        service = get_duxwrap_service(user_id, dux_user.apikey, dux_user.userid)
        if not service:
            raise HTTPException(status_code=500, detail="DuxWrap service not available")
        
        # Queue message
        message_result = await service.send_message(request.profile_url, request.message)
        
        if message_result["success"]:
            return {
                "success": True,
                "data": message_result["data"]
            }
        else:
            raise HTTPException(status_code=400, detail=message_result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to queue message for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/wait/{user_id}")
async def add_wait(user_id: str, request: WaitRequest, db: AsyncSession = Depends(get_session)):
    """Add a wait period to the queue"""
    try:
        # Get DuxSoup user from database
        dux_user = db.query(DuxSoupUser).filter(DuxSoupUser.user_id == user_id).first()
        if not dux_user:
            raise HTTPException(status_code=404, detail="DuxSoup user not found")
        
        # Get DuxWrap service
        service = get_duxwrap_service(user_id, dux_user.apikey, dux_user.userid)
        if not service:
            raise HTTPException(status_code=500, detail="DuxWrap service not available")
        
        # Add wait
        wait_result = await service.add_wait(request.duration_minutes)
        
        if wait_result["success"]:
            return {
                "success": True,
                "data": wait_result["data"]
            }
        else:
            raise HTTPException(status_code=400, detail=wait_result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add wait for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-queue/{user_id}")
async def clear_queue(user_id: str, db: AsyncSession = Depends(get_session)):
    """Clear the automation queue"""
    try:
        # Get DuxSoup user from database
        dux_user = db.query(DuxSoupUser).filter(DuxSoupUser.user_id == user_id).first()
        if not dux_user:
            raise HTTPException(status_code=404, detail="DuxSoup user not found")
        
        # Get DuxWrap service
        service = get_duxwrap_service(user_id, dux_user.apikey, dux_user.userid)
        if not service:
            raise HTTPException(status_code=500, detail="DuxWrap service not available")
        
        # Clear queue
        clear_result = await service.clear_queue()
        
        if clear_result["success"]:
            return {
                "success": True,
                "data": clear_result["data"]
            }
        else:
            raise HTTPException(status_code=400, detail=clear_result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear queue for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch/{user_id}")
async def batch_actions(user_id: str, request: BatchActionRequest, db: AsyncSession = Depends(get_session)):
    """Execute multiple actions in batch"""
    try:
        # Get DuxSoup user from database
        dux_user = db.query(DuxSoupUser).filter(DuxSoupUser.user_id == user_id).first()
        if not dux_user:
            raise HTTPException(status_code=404, detail="DuxSoup user not found")
        
        # Get DuxWrap service
        service = get_duxwrap_service(user_id, dux_user.apikey, dux_user.userid)
        if not service:
            raise HTTPException(status_code=500, detail="DuxWrap service not available")
        
        # Execute batch actions
        batch_result = await service.batch_actions(request.actions)
        
        return {
            "success": True,
            "data": {
                "total_actions": len(request.actions),
                "results": batch_result
            }
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute batch actions for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-connection")
async def test_connection():
    """Test DuxWrap connection with known working credentials"""
    try:
        # Use the working credentials for testing
        test_user_id = "117833704731893145427"
        test_api_key = "e96sH0Qehcqk8LWsyNjJpr9OL9qzasXR"
        
        # Create test service
        service = get_duxwrap_service("test_user", test_api_key, test_user_id)
        if not service:
            raise HTTPException(status_code=500, detail="Failed to create test service")
        
        # Get health status
        health_status = await service.get_health_status()
        
        return {
            "success": True,
            "data": {
                "connection_status": "working",
                "health": health_status,
                "test_user_id": test_user_id,
                "duxwrap_available": service.is_available()
            }
        }
        
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
