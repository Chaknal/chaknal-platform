"""
DuxWrap Test API Endpoints
Simple API endpoints to test the real DuxWrap integration
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import logging

from app.services.duxwrap_service import get_duxwrap_service, duxwrap_manager
from database.database import get_session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/duxwrap-test", tags=["duxwrap-test"])


class ProfileVisitRequest(BaseModel):
    profile_url: str


class ConnectionRequest(BaseModel):
    profile_url: str
    message: Optional[str] = None


class MessageRequest(BaseModel):
    profile_url: str
    message: str


@router.get("/health")
async def get_health_status():
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


@router.get("/profile")
async def get_profile():
    """Get DuxSoup profile using test credentials"""
    try:
        # Use the working credentials
        test_user_id = "117833704731893145427"
        test_api_key = "e96sH0Qehcqk8LWsyNjJpr9OL9qzasXR"
        
        # Get service
        service = get_duxwrap_service("test_user", test_api_key, test_user_id)
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
        logger.error(f"Failed to get profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue")
async def get_queue_status():
    """Get automation queue status using test credentials"""
    try:
        # Use the working credentials
        test_user_id = "117833704731893145427"
        test_api_key = "e96sH0Qehcqk8LWsyNjJpr9OL9qzasXR"
        
        # Get service
        service = get_duxwrap_service("test_user", test_api_key, test_user_id)
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
        logger.error(f"Failed to get queue status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/visit")
async def visit_profile(request: ProfileVisitRequest):
    """Queue a profile visit using test credentials"""
    try:
        # Use the working credentials
        test_user_id = "117833704731893145427"
        test_api_key = "e96sH0Qehcqk8LWsyNjJpr9OL9qzasXR"
        
        # Get service
        service = get_duxwrap_service("test_user", test_api_key, test_user_id)
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
        logger.error(f"Failed to queue visit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/connect")
async def send_connection_request(request: ConnectionRequest):
    """Queue a connection request using test credentials"""
    try:
        # Use the working credentials
        test_user_id = "117833704731893145427"
        test_api_key = "e96sH0Qehcqk8LWsyNjJpr9OL9qzasXR"
        
        # Get service
        service = get_duxwrap_service("test_user", test_api_key, test_user_id)
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
        logger.error(f"Failed to queue connection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message")
async def send_message(request: MessageRequest, db: AsyncSession = Depends(get_session)):
    """Queue a direct message using test credentials"""
    try:
        # Use the working credentials
        test_user_id = "117833704731893145427"
        test_api_key = "e96sH0Qehcqk8LWsyNjJpr9OL9qzasXR"
        
        # Get service
        service = get_duxwrap_service("test_user", test_api_key, test_user_id)
        if not service:
            raise HTTPException(status_code=500, detail="DuxWrap service not available")
        
        # Queue message
        message_result = await service.send_message(request.profile_url, request.message)
        
        if message_result["success"]:
            # Store message in database for conversation history
            try:
                from app.api.message_storage import store_outbound_message
                storage_result = await store_outbound_message(
                    contact_linkedin_url=request.profile_url,
                    message_text=request.message,
                    dux_message_id=message_result["data"]["message_id"],
                    sender_name="Sercio Campos",
                    sender_email="scampos@wallarm.com",
                    session=db
                )
                
                if storage_result["success"]:
                    logger.info(f"✅ Message stored in database: {storage_result['data']['message_id']}")
                else:
                    logger.warning(f"⚠️ Failed to store message in database: {storage_result['error']}")
                    
            except Exception as storage_error:
                logger.error(f"❌ Error storing message: {storage_error}")
            
            return {
                "success": True,
                "data": message_result["data"]
            }
        else:
            raise HTTPException(status_code=400, detail=message_result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to queue message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-queue")
async def clear_queue():
    """Clear the automation queue using test credentials"""
    try:
        # Use the working credentials
        test_user_id = "117833704731893145427"
        test_api_key = "e96sH0Qehcqk8LWsyNjJpr9OL9qzasXR"
        
        # Get service
        service = get_duxwrap_service("test_user", test_api_key, test_user_id)
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
        logger.error(f"Failed to clear queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))
