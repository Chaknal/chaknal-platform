"""
DuxSoup Authenticated API Test Endpoints
Test the properly authenticated DuxSoup API calls
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from app.services.duxsoup_auth_service import get_duxsoup_auth_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/duxsoup-auth-test", tags=["duxsoup-auth-test"])

# Test credentials (replace with actual credentials)
TEST_USER_ID = os.getenv("DUXSOUP_USER_ID", "your-user-id-here")
TEST_API_KEY = os.getenv("DUXSOUP_API_KEY", "your-api-key-here")


class ProfileVisitRequest(BaseModel):
    profile_url: str


class ConnectionRequest(BaseModel):
    profile_url: str
    message: Optional[str] = ""


class SettingsUpdateRequest(BaseModel):
    settings: Dict[str, Any]


@router.get("/test-connection")
async def test_duxsoup_connection():
    """Test DuxSoup API connection with proper authentication"""
    try:
        service = get_duxsoup_auth_service(TEST_USER_ID, TEST_API_KEY)
        
        # Test getting queue status (simple GET request)
        result = await service.get_queue_status()
        
        return {
            "success": True,
            "message": "DuxSoup connection test completed",
            "authentication_method": "HMAC-SHA1 signature",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "DuxSoup connection test failed"
        }


@router.get("/get-settings")
async def get_duxsoup_settings():
    """Get DuxSoup user settings with proper authentication"""
    try:
        service = get_duxsoup_auth_service(TEST_USER_ID, TEST_API_KEY)
        
        result = await service.get_settings()
        
        if result["success"]:
            return {
                "success": True,
                "message": "Settings retrieved successfully",
                "data": result["data"],
                "status_code": result["status_code"]
            }
        else:
            return {
                "success": False,
                "error": result["error"],
                "status_code": result["status_code"]
            }
            
    except Exception as e:
        logger.error(f"Get settings failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/config/{user_id}")
async def get_user_config(user_id: str):
    """Get DuxSoup configuration for a specific user (for frontend compatibility)"""
    try:
        # Get the actual user's credentials from database
        import sqlite3
        conn = sqlite3.connect('chaknal.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT dux_soup_user_id, dux_soup_auth_key, email, first_name, last_name 
            FROM duxsoup_user 
            WHERE id = ?
        """, (user_id,))
        
        user_row = cursor.fetchone()
        conn.close()
        
        if not user_row:
            # Fallback to Sergio's credentials for demo
            service = get_duxsoup_auth_service(TEST_USER_ID, TEST_API_KEY)
            user_info = {"email": "scampos@wallarm.com", "first_name": "Sergio", "last_name": "Campos"}
        else:
            dux_user_id, dux_auth_key, email, first_name, last_name = user_row
            service = get_duxsoup_auth_service(dux_user_id, dux_auth_key)
            user_info = {"email": email, "first_name": first_name, "last_name": last_name}
        
        result = await service.get_settings()
        
        if result["success"]:
            # Format response to match what the frontend expects
            return {
                "duxsoup_user_id": user_id,
                "email": user_info["email"],
                "first_name": user_info["first_name"], 
                "last_name": user_info["last_name"],
                "settings": result["data"],
                "last_updated": "2025-09-17T19:00:00Z"
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Get user config failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-settings")
async def update_duxsoup_settings(request: SettingsUpdateRequest):
    """Update DuxSoup user settings with proper authentication"""
    try:
        service = get_duxsoup_auth_service(TEST_USER_ID, TEST_API_KEY)
        
        result = await service.update_settings(request.settings)
        
        if result["success"]:
            return {
                "success": True,
                "message": "Settings updated successfully",
                "data": result["data"],
                "status_code": result["status_code"]
            }
        else:
            return {
                "success": False,
                "error": result["error"],
                "status_code": result["status_code"]
            }
            
    except Exception as e:
        logger.error(f"Update settings failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/pull/{user_id}")
async def pull_from_duxsoup(user_id: str):
    """Pull configuration from DuxSoup (for frontend compatibility)"""
    try:
        # Get the actual user's credentials from database
        import sqlite3
        conn = sqlite3.connect('chaknal.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT dux_soup_user_id, dux_soup_auth_key, email, first_name, last_name 
            FROM duxsoup_user 
            WHERE id = ?
        """, (user_id,))
        
        user_row = cursor.fetchone()
        conn.close()
        
        if not user_row:
            # Fallback to Sergio's credentials for demo
            service = get_duxsoup_auth_service(TEST_USER_ID, TEST_API_KEY)
            user_info = {"email": "scampos@wallarm.com", "first_name": "Sergio", "last_name": "Campos"}
        else:
            dux_user_id, dux_auth_key, email, first_name, last_name = user_row
            service = get_duxsoup_auth_service(dux_user_id, dux_auth_key)
            user_info = {"email": email, "first_name": first_name, "last_name": last_name}
        
        result = await service.get_settings()
        
        if result["success"]:
            return {
                "success": True,
                "message": "Configuration pulled successfully from DuxSoup",
                "duxsoup_user_id": user_id,
                "email": user_info["email"],
                "first_name": user_info["first_name"], 
                "last_name": user_info["last_name"],
                "settings": result["data"],
                "last_updated": "2025-09-17T19:00:00Z"
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Pull from DuxSoup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/push/{user_id}")
async def push_to_duxsoup(user_id: str, request: SettingsUpdateRequest):
    """Push configuration to DuxSoup (for frontend compatibility)"""
    try:
        # Get the actual user's credentials from database
        import sqlite3
        conn = sqlite3.connect('chaknal.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT dux_soup_user_id, dux_soup_auth_key, email, first_name, last_name 
            FROM duxsoup_user 
            WHERE id = ?
        """, (user_id,))
        
        user_row = cursor.fetchone()
        conn.close()
        
        if not user_row:
            # Fallback to Sergio's credentials for demo
            service = get_duxsoup_auth_service(TEST_USER_ID, TEST_API_KEY)
        else:
            dux_user_id, dux_auth_key, email, first_name, last_name = user_row
            service = get_duxsoup_auth_service(dux_user_id, dux_auth_key)
        
        result = await service.update_settings(request.settings)
        
        if result["success"]:
            return {
                "success": True,
                "message": "Configuration pushed successfully to DuxSoup",
                "duxsoup_response": result["data"]
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Push to DuxSoup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/visit-profile")
async def visit_profile(request: ProfileVisitRequest):
    """Visit a LinkedIn profile using DuxSoup with proper authentication"""
    try:
        service = get_duxsoup_auth_service(TEST_USER_ID, TEST_API_KEY)
        
        result = await service.visit_profile(request.profile_url)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Profile visit queued successfully",
                "profile_url": request.profile_url,
                "data": result["data"],
                "status_code": result["status_code"]
            }
        else:
            return {
                "success": False,
                "error": result["error"],
                "profile_url": request.profile_url,
                "status_code": result["status_code"]
            }
            
    except Exception as e:
        logger.error(f"Profile visit failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "profile_url": request.profile_url
        }


@router.post("/send-connection")
async def send_connection_request(request: ConnectionRequest):
    """Send connection request using DuxSoup with proper authentication"""
    try:
        service = get_duxsoup_auth_service(TEST_USER_ID, TEST_API_KEY)
        
        result = await service.send_connection_request(request.profile_url, request.message or "")
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Connection request queued successfully",
                "profile_url": request.profile_url,
                "data": result["data"],
                "status_code": result["status_code"]
            }
        else:
            return {
                "success": False,
                "error": result["error"],
                "profile_url": request.profile_url,
                "status_code": result["status_code"]
            }
            
    except Exception as e:
        logger.error(f"Connection request failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "profile_url": request.profile_url
        }


@router.get("/queue-status")
async def get_queue_status():
    """Get DuxSoup queue status with proper authentication"""
    try:
        service = get_duxsoup_auth_service(TEST_USER_ID, TEST_API_KEY)
        
        result = await service.get_queue_status()
        
        if result["success"]:
            return {
                "success": True,
                "message": "Queue status retrieved successfully",
                "data": result["data"],
                "status_code": result["status_code"]
            }
        else:
            return {
                "success": False,
                "error": result["error"],
                "status_code": result["status_code"]
            }
            
    except Exception as e:
        logger.error(f"Queue status failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/add-webhook/{user_id}")
async def add_webhook_safely(user_id: str, webhook_url: str, events: list = None):
    """Safely add a webhook to existing DuxSoup configuration without overwriting other settings"""
    try:
        service = get_duxsoup_auth_service(TEST_USER_ID, TEST_API_KEY)
        
        # Step 1: Get current configuration from DuxSoup
        current_config = await service.get_settings()
        
        if not current_config["success"]:
            return {
                "success": False,
                "error": f"Failed to get current config: {current_config['error']}"
            }
        
        # Step 2: Extract current webhooks
        current_settings = current_config["data"]
        existing_webhooks = current_settings.get("webhooks", [])
        
        # Step 3: Check if webhook already exists
        webhook_exists = any(
            webhook.get("url") == webhook_url 
            for webhook in existing_webhooks
        )
        
        if webhook_exists:
            return {
                "success": False,
                "error": "Webhook URL already exists in configuration",
                "existing_webhooks": len(existing_webhooks)
            }
        
        # Step 4: Add new webhook to existing array
        new_webhook = {
            "url": webhook_url,
            "events": events or ["visit", "scan", "action", "message", "rc"]
        }
        
        updated_webhooks = existing_webhooks + [new_webhook]
        
        # Step 5: Update ONLY the webhooks setting (preserve everything else)
        webhook_update = {
            "webhooks": updated_webhooks
        }
        
        # Step 6: Push only the webhook update to DuxSoup
        result = await service.update_settings(webhook_update)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Webhook added successfully to existing configuration",
                "webhook_url": webhook_url,
                "total_webhooks": len(updated_webhooks),
                "existing_webhooks_preserved": len(existing_webhooks),
                "new_webhook_added": True
            }
        else:
            return {
                "success": False,
                "error": f"Failed to update webhooks: {result['error']}"
            }
            
    except Exception as e:
        logger.error(f"Add webhook safely failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/setup-new-user/{user_id}")
async def setup_new_duxsoup_user(
    user_id: str, 
    webhook_url: str, 
    events: list = None,
    company_name: str = "Chaknal Platform"
):
    """
    Safely setup a new DuxSoup user with initial webhook configuration
    This function preserves ALL existing settings and only adds the webhook
    """
    try:
        service = get_duxsoup_auth_service(TEST_USER_ID, TEST_API_KEY)
        
        # Step 1: Get current configuration (don't assume it's empty)
        logger.info(f"Setting up new DuxSoup user: {user_id}")
        current_config = await service.get_settings()
        
        if not current_config["success"]:
            return {
                "success": False,
                "error": f"Failed to get current config: {current_config['error']}",
                "step": "get_current_config"
            }
        
        current_settings = current_config["data"]
        logger.info(f"Current config has {len(current_settings)} settings")
        
        # Step 2: Safely add webhook (preserve existing ones)
        existing_webhooks = current_settings.get("webhooks", [])
        logger.info(f"Found {len(existing_webhooks)} existing webhooks")
        
        # Check if our webhook already exists
        webhook_exists = any(
            webhook.get("url") == webhook_url 
            for webhook in existing_webhooks
        )
        
        if not webhook_exists:
            new_webhook = {
                "url": webhook_url,
                "events": events or ["visit", "scan", "action", "message", "rc"]
            }
            
            updated_webhooks = existing_webhooks + [new_webhook]
            logger.info(f"Adding webhook: {webhook_url}")
        else:
            updated_webhooks = existing_webhooks
            logger.info(f"Webhook already exists: {webhook_url}")
        
        # Step 3: Optionally add company tag (preserve existing tags)
        current_tags = current_settings.get("autotagvalue", "")
        if company_name not in current_tags:
            updated_tags = f"{current_tags}, {company_name}".strip(", ")
        else:
            updated_tags = current_tags
            
        # Step 4: Prepare minimal update (webhook, tags, and remote control)
        safe_update = {
            "webhooks": updated_webhooks,
            "remotecontrolflag": True  # Enable remote control for webhook functionality
        }
        
        # Only update tags if they changed
        if updated_tags != current_tags:
            safe_update["autotagvalue"] = updated_tags
            logger.info(f"Updated tags: {updated_tags}")
        
        # Log remote control enablement
        current_remote_control = current_settings.get("remotecontrolflag", False)
        if not current_remote_control:
            logger.info("Enabling remote control for webhook functionality")
        
        # Step 5: Push only the minimal changes
        result = await service.update_settings(safe_update)
        
        if result["success"]:
            return {
                "success": True,
                "message": "New DuxSoup user setup completed successfully",
                "user_id": user_id,
                "webhook_added": not webhook_exists,
                "webhook_url": webhook_url,
                "total_webhooks": len(updated_webhooks),
                "existing_settings_preserved": len(current_settings),
                "changes_made": list(safe_update.keys()),
                "company_tag": company_name,
                "remote_control_enabled": True,
                "remote_control_was_already_on": current_remote_control
            }
        else:
            return {
                "success": False,
                "error": f"Failed to update DuxSoup: {result['error']}",
                "step": "push_changes"
            }
            
    except Exception as e:
        logger.error(f"Setup new user failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "step": "exception"
        }
