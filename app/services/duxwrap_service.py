"""
DuxWrap Service - Real DuxSoup Integration
Uses the working DuxWrap library to provide real DuxSoup functionality
"""

import sys
import os
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Add the duxwrap directory to the Python path
duxwrap_path = os.path.join(os.path.dirname(__file__), '../../duxwrap-master')
sys.path.insert(0, duxwrap_path)

try:
    from duxwrap.duxwrap import DuxWrap
    DUXWRAP_AVAILABLE = True
except ImportError:
    DUXWRAP_AVAILABLE = False
    print("Warning: DuxWrap not available, using mock data")

logger = logging.getLogger(__name__)


class DuxWrapService:
    """Service for real DuxSoup integration using DuxWrap"""
    
    def __init__(self, api_key: str, user_id: str):
        """Initialize DuxWrap service"""
        self.api_key = api_key
        self.user_id = user_id
        self.dux_wrap = None
        
        if DUXWRAP_AVAILABLE:
            try:
                self.dux_wrap = DuxWrap(api_key, user_id)
                logger.info(f"DuxWrap service initialized for user {user_id}")
            except Exception as e:
                logger.error(f"Failed to initialize DuxWrap: {e}")
                self.dux_wrap = None
        else:
            logger.warning("DuxWrap not available, service will use mock data")
    
    def is_available(self) -> bool:
        """Check if DuxWrap is available and working"""
        return self.dux_wrap is not None
    
    async def get_profile(self) -> Dict[str, Any]:
        """Get user profile information"""
        if not self.is_available():
            return {
                "success": False,
                "error": "DuxWrap not available",
                "data": None
            }
        
        try:
            profile_data = self.dux_wrap.call("profile", {})
            return {
                "success": True,
                "data": profile_data,
                "error": None
            }
        except Exception as e:
            logger.error(f"Failed to get profile: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        if not self.is_available():
            return {
                "success": False,
                "error": "DuxWrap not available",
                "data": {"size": 0, "items": []}
            }
        
        try:
            # Get queue size
            size_response = self.dux_wrap.call("size", {})
            queue_size = size_response.get("result", 0) if isinstance(size_response, dict) else 0
            
            # Get queue items
            items_response = self.dux_wrap.call("items", {})
            queue_items = items_response if isinstance(items_response, list) else []
            
            return {
                "success": True,
                "data": {
                    "size": queue_size,
                    "items": queue_items,
                    "status": "active" if queue_size > 0 else "idle"
                },
                "error": None
            }
        except Exception as e:
            logger.error(f"Failed to get queue status: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": {"size": 0, "items": []}
            }
    
    async def visit_profile(self, profile_url: str) -> Dict[str, Any]:
        """Queue a profile visit"""
        if not self.is_available():
            return {
                "success": False,
                "error": "DuxWrap not available",
                "data": None
            }
        
        try:
            visit_data = {"params": {"profile": profile_url}}
            response = self.dux_wrap.call("visit", visit_data)
            
            return {
                "success": True,
                "data": {
                    "message_id": response.get("messageid"),
                    "profile_url": profile_url,
                    "action": "visit",
                    "queued_at": datetime.utcnow().isoformat()
                },
                "error": None
            }
        except Exception as e:
            logger.error(f"Failed to queue visit for {profile_url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def send_connection_request(self, profile_url: str, message: str = None) -> Dict[str, Any]:
        """Queue a connection request"""
        if not self.is_available():
            return {
                "success": False,
                "error": "DuxWrap not available",
                "data": None
            }
        
        try:
            connect_data = {
                "params": {
                    "profile": profile_url,
                    "messagetext": message or "I'd like to connect with you!"
                }
            }
            response = self.dux_wrap.call("connect", connect_data)
            
            return {
                "success": True,
                "data": {
                    "message_id": response.get("messageid"),
                    "profile_url": profile_url,
                    "action": "connect",
                    "message": message,
                    "queued_at": datetime.utcnow().isoformat()
                },
                "error": None
            }
        except Exception as e:
            logger.error(f"Failed to queue connection for {profile_url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def send_message(self, profile_url: str, message: str, log_to_db: bool = True) -> Dict[str, Any]:
        """Queue a direct message"""
        if not self.is_available():
            return {
                "success": False,
                "error": "DuxWrap not available",
                "data": None
            }
        
        execution_start = datetime.utcnow()
        
        try:
            message_data = {
                "params": {
                    "profile": profile_url,
                    "messagetext": message
                }
            }
            response = self.dux_wrap.call("message", message_data)
            execution_end = datetime.utcnow()
            
            result_data = {
                "message_id": response.get("messageid"),
                "profile_url": profile_url,
                "action": "message",
                "message": message,
                "queued_at": execution_start.isoformat(),
                "response": response
            }
            
            # Log to database if requested
            if log_to_db:
                await self._log_execution(
                    command="message",
                    params=message_data["params"],
                    execution_start=execution_start,
                    execution_end=execution_end,
                    status="success",
                    result=response,
                    profile_url=profile_url
                )
            
            return {
                "success": True,
                "data": result_data,
                "error": None
            }
        except Exception as e:
            execution_end = datetime.utcnow()
            logger.error(f"Failed to queue message for {profile_url}: {e}")
            
            # Log failure to database
            if log_to_db:
                await self._log_execution(
                    command="message",
                    params={"profile": profile_url, "messagetext": message},
                    execution_start=execution_start,
                    execution_end=execution_end,
                    status="failed",
                    result=None,
                    error_message=str(e),
                    profile_url=profile_url
                )
            
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def clear_queue(self) -> Dict[str, Any]:
        """Clear the automation queue"""
        if not self.is_available():
            return {
                "success": False,
                "error": "DuxWrap not available",
                "data": None
            }
        
        try:
            response = self.dux_wrap.call("reset", {})
            
            return {
                "success": True,
                "data": {
                    "message_id": response.get("messageid"),
                    "action": "reset",
                    "cleared_at": datetime.utcnow().isoformat()
                },
                "error": None
            }
        except Exception as e:
            logger.error(f"Failed to clear queue: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def add_wait(self, duration_minutes: int) -> Dict[str, Any]:
        """Add a wait period to the queue"""
        if not self.is_available():
            return {
                "success": False,
                "error": "DuxWrap not available",
                "data": None
            }
        
        try:
            wait_data = {"params": {"duration": duration_minutes}}
            response = self.dux_wrap.call("wait", wait_data)
            
            return {
                "success": True,
                "data": {
                    "message_id": response.get("messageid"),
                    "action": "wait",
                    "duration_minutes": duration_minutes,
                    "queued_at": datetime.utcnow().isoformat()
                },
                "error": None
            }
        except Exception as e:
            logger.error(f"Failed to add wait: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        profile_status = await self.get_profile()
        queue_status = await self.get_queue_status()
        
        return {
            "duxwrap_available": self.is_available(),
            "profile": profile_status,
            "queue": queue_status,
            "last_checked": datetime.utcnow().isoformat(),
            "overall_status": "healthy" if profile_status["success"] and queue_status["success"] else "unhealthy"
        }
    
    async def batch_actions(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple actions in batch"""
        results = []
        
        for action in actions:
            action_type = action.get("type")
            action_data = action.get("data", {})
            
            try:
                if action_type == "visit":
                    result = await self.visit_profile(action_data.get("profile_url"))
                elif action_type == "connect":
                    result = await self.send_connection_request(
                        action_data.get("profile_url"),
                        action_data.get("message")
                    )
                elif action_type == "message":
                    result = await self.send_message(
                        action_data.get("profile_url"),
                        action_data.get("message")
                    )
                elif action_type == "wait":
                    result = await self.add_wait(action_data.get("duration_minutes", 5))
                else:
                    result = {
                        "success": False,
                        "error": f"Unknown action type: {action_type}",
                        "data": None
                    }
                
                results.append({
                    "action": action,
                    "result": result
                })
                
            except Exception as e:
                results.append({
                    "action": action,
                    "result": {
                        "success": False,
                        "error": str(e),
                        "data": None
                    }
                })
        
        return results
    
    async def _log_execution(
        self,
        command: str,
        params: dict,
        execution_start: datetime,
        execution_end: datetime,
        status: str,
        result: dict = None,
        error_message: str = None,
        profile_url: str = None
    ):
        """Log DuxWrap execution to database"""
        try:
            # Import here to avoid circular imports
            from database.database import async_session_maker
            from app.models.duxsoup_execution_log import DuxSoupExecutionLog
            from app.models.contact import Contact
            from sqlalchemy import select
            import uuid
            
            async with async_session_maker() as session:
                # Find contact if profile_url provided
                contact_id = None
                if profile_url:
                    contact_result = await session.execute(
                        select(Contact).where(Contact.linkedin_url == profile_url)
                    )
                    contact = contact_result.scalar_one_or_none()
                    if contact:
                        contact_id = contact.contact_id
                
                # Create execution log
                log_entry = DuxSoupExecutionLog(
                    log_id=str(uuid.uuid4()),
                    dux_user_id=self.user_id,
                    command=command,
                    params=params,
                    execution_start=execution_start,
                    execution_end=execution_end,
                    status=status,
                    result=result,
                    error_message=error_message,
                    response_time_ms=int((execution_end - execution_start).total_seconds() * 1000),
                    contact_id=contact_id
                )
                
                session.add(log_entry)
                await session.commit()
                
                logger.info(f"✅ Logged DuxWrap execution: {command} - {status}")
                
        except Exception as e:
            logger.error(f"❌ Failed to log execution: {e}")


class DuxWrapManager:
    """Manager for multiple DuxWrap services (multi-tenant)"""
    
    def __init__(self):
        self.services: Dict[str, DuxWrapService] = {}
    
    def add_service(self, user_id: str, api_key: str, dux_user_id: str) -> DuxWrapService:
        """Add a DuxWrap service for a user"""
        service = DuxWrapService(api_key, dux_user_id)
        self.services[user_id] = service
        logger.info(f"Added DuxWrap service for user {user_id}")
        return service
    
    def get_service(self, user_id: str) -> Optional[DuxWrapService]:
        """Get DuxWrap service for a user"""
        return self.services.get(user_id)
    
    def remove_service(self, user_id: str) -> bool:
        """Remove DuxWrap service for a user"""
        if user_id in self.services:
            del self.services[user_id]
            logger.info(f"Removed DuxWrap service for user {user_id}")
            return True
        return False
    
    async def get_all_health_status(self) -> Dict[str, Dict[str, Any]]:
        """Get health status for all services"""
        health_status = {}
        
        for user_id, service in self.services.items():
            try:
                health_status[user_id] = await service.get_health_status()
            except Exception as e:
                health_status[user_id] = {
                    "error": str(e),
                    "overall_status": "error"
                }
        
        return health_status
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for all services"""
        total_services = len(self.services)
        available_services = sum(1 for service in self.services.values() if service.is_available())
        
        return {
            "total_services": total_services,
            "available_services": available_services,
            "unavailable_services": total_services - available_services,
            "availability_rate": (available_services / max(total_services, 1)) * 100
        }


# Global manager instance
duxwrap_manager = DuxWrapManager()


def get_duxwrap_service(user_id: str, api_key: str = None, dux_user_id: str = None) -> Optional[DuxWrapService]:
    """Get or create DuxWrap service for a user"""
    service = duxwrap_manager.get_service(user_id)
    
    if service is None and api_key and dux_user_id:
        service = duxwrap_manager.add_service(user_id, api_key, dux_user_id)
    
    return service
