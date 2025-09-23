"""
DuxSoup Authentication Service
Implements proper HMAC-SHA1 authentication as per official DuxSoup documentation
"""

import hashlib
import hmac
import base64
import json
import time
import aiohttp
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DuxSoupAuthService:
    """
    Properly authenticated DuxSoup API service using HMAC-SHA1 signatures
    Based on official DuxSoup documentation
    """
    
    BASE_URL = "https://app.dux-soup.com/xapi/remote/control"
    
    def __init__(self, user_id: str, api_key: str):
        """
        Initialize with DuxSoup credentials
        
        Args:
            user_id: DuxSoup user ID
            api_key: DuxSoup API key
        """
        self.user_id = user_id
        self.api_key = api_key
        
    def _calculate_hmac(self, message: str) -> str:
        """
        Calculate HMAC-SHA1 signature for authentication
        
        Args:
            message: Message to sign (URL for GET, JSON body for POST)
            
        Returns:
            Base64 encoded HMAC signature
        """
        try:
            # Create HMAC-SHA1 hash
            mac = hmac.new(
                self.api_key.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha1
            )
            
            # Return base64 encoded signature
            return base64.b64encode(mac.digest()).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Failed to calculate HMAC: {e}")
            raise Exception(f"HMAC calculation failed: {e}")
    
    async def get_settings(self) -> Dict[str, Any]:
        """
        Get DuxSoup user settings using proper authentication
        
        Returns:
            DuxSoup settings configuration
        """
        try:
            # Construct URL for GET request
            url = f"{self.BASE_URL}/{self.user_id}/settings"
            
            # For GET requests, sign the full URL
            signature = self._calculate_hmac(url)
            
            # Headers with HMAC signature
            headers = {
                "Content-Type": "application/json",
                "X-Dux-Signature": signature
            }
            
            logger.info(f"Getting DuxSoup settings for user {self.user_id}")
            logger.debug(f"URL: {url}")
            logger.debug(f"Signature: {signature[:20]}...")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=30) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        logger.info("✅ Successfully retrieved DuxSoup settings")
                        return {
                            "success": True,
                            "data": data,
                            "status_code": response.status
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ DuxSoup API error {response.status}: {error_text}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "status_code": response.status
                        }
                        
        except Exception as e:
            logger.error(f"❌ Exception getting DuxSoup settings: {e}")
            return {
                "success": False,
                "error": str(e),
                "status_code": None
            }
    
    async def update_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update DuxSoup user settings using proper authentication
        
        Args:
            settings: Settings dictionary to update
            
        Returns:
            Update result
        """
        try:
            # Construct URL for POST request
            url = f"{self.BASE_URL}/{self.user_id}/settings"
            
            # Request body for POST (must include targeturl as per DuxSoup API)
            request_body = {
                "targeturl": url,
                "userid": self.user_id,
                "timestamp": int(time.time() * 1000),
                "settings": settings
            }
            
            # Convert to JSON string for signing
            json_body = json.dumps(request_body, separators=(',', ':'))
            
            # For POST requests, sign the JSON body
            signature = self._calculate_hmac(json_body)
            
            # Headers with HMAC signature
            headers = {
                "Content-Type": "application/json",
                "X-Dux-Signature": signature
            }
            
            logger.info(f"Updating DuxSoup settings for user {self.user_id}")
            logger.debug(f"URL: {url}")
            logger.debug(f"Body: {json_body[:100]}...")
            logger.debug(f"Signature: {signature[:20]}...")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=json_body, headers=headers, timeout=30) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        logger.info("✅ Successfully updated DuxSoup settings")
                        return {
                            "success": True,
                            "data": data,
                            "status_code": response.status
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ DuxSoup API error {response.status}: {error_text}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "status_code": response.status
                        }
                        
        except Exception as e:
            logger.error(f"❌ Exception updating DuxSoup settings: {e}")
            return {
                "success": False,
                "error": str(e),
                "status_code": None
            }
    
    async def visit_profile(self, profile_url: str) -> Dict[str, Any]:
        """
        Queue a profile visit using DuxSoup API
        
        Args:
            profile_url: LinkedIn profile URL to visit
            
        Returns:
            Visit result
        """
        try:
            # Construct URL for POST request (correct DuxSoup endpoint)
            url = f"{self.BASE_URL}/{self.user_id}/queue"
            
            # Request body for profile visit command
            request_body = {
                "command": "visit",
                "targeturl": url,
                "userid": self.user_id,
                "timestamp": int(time.time() * 1000),
                "params": {
                    "profile": profile_url
                }
            }
            
            # Convert to JSON string for signing
            json_body = json.dumps(request_body, separators=(',', ':'))
            
            # For POST requests, sign the JSON body
            signature = self._calculate_hmac(json_body)
            
            # Headers with HMAC signature
            headers = {
                "Content-Type": "application/json",
                "X-Dux-Signature": signature
            }
            
            logger.info(f"Queuing profile visit: {profile_url}")
            logger.debug(f"URL: {url}")
            logger.debug(f"Command: visit")
            logger.debug(f"Signature: {signature[:20]}...")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=json_body, headers=headers, timeout=30) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        logger.info("✅ Successfully queued profile visit")
                        return {
                            "success": True,
                            "data": data,
                            "status_code": response.status,
                            "profile_url": profile_url
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Profile visit failed {response.status}: {error_text}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "status_code": response.status,
                            "profile_url": profile_url
                        }
                        
        except Exception as e:
            logger.error(f"❌ Exception visiting profile: {e}")
            return {
                "success": False,
                "error": str(e),
                "status_code": None,
                "profile_url": profile_url
            }
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """
        Get DuxSoup queue status
        
        Returns:
            Queue status information
        """
        try:
            # Construct URL for GET request (correct DuxSoup endpoint)
            url = f"{self.BASE_URL}/{self.user_id}/queue/size"
            
            # For GET requests, sign the full URL
            signature = self._calculate_hmac(url)
            
            # Headers with HMAC signature
            headers = {
                "Content-Type": "application/json",
                "X-Dux-Signature": signature
            }
            
            logger.info(f"Getting queue status for user {self.user_id}")
            logger.debug(f"URL: {url}")
            logger.debug(f"Signature: {signature[:20]}...")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=30) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        logger.info("✅ Successfully retrieved queue status")
                        return {
                            "success": True,
                            "data": data,
                            "status_code": response.status
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Queue status failed {response.status}: {error_text}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "status_code": response.status
                        }
                        
        except Exception as e:
            logger.error(f"❌ Exception getting queue status: {e}")
            return {
                "success": False,
                "error": str(e),
                "status_code": None
            }
    
    async def send_connection_request(self, profile_url: str, message: str = "") -> Dict[str, Any]:
        """
        Send connection request using DuxSoup API
        
        Args:
            profile_url: LinkedIn profile URL
            message: Optional connection message
            
        Returns:
            Connection request result
        """
        try:
            # Construct URL for POST request (correct DuxSoup endpoint)
            url = f"{self.BASE_URL}/{self.user_id}/queue"
            
            # Request body for connection request command
            request_body = {
                "command": "connect",
                "targeturl": url,
                "userid": self.user_id,
                "timestamp": int(time.time() * 1000),
                "params": {
                    "profile": profile_url,
                    "messagetext": message
                }
            }
            
            # Convert to JSON string for signing
            json_body = json.dumps(request_body, separators=(',', ':'))
            
            # For POST requests, sign the JSON body
            signature = self._calculate_hmac(json_body)
            
            # Headers with HMAC signature
            headers = {
                "Content-Type": "application/json",
                "X-Dux-Signature": signature
            }
            
            logger.info(f"Sending connection request to: {profile_url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=json_body, headers=headers, timeout=30) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        logger.info("✅ Successfully queued connection request")
                        return {
                            "success": True,
                            "data": data,
                            "status_code": response.status,
                            "profile_url": profile_url
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Connection request failed {response.status}: {error_text}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "status_code": response.status,
                            "profile_url": profile_url
                        }
                        
        except Exception as e:
            logger.error(f"❌ Exception sending connection request: {e}")
            return {
                "success": False,
                "error": str(e),
                "status_code": None,
                "profile_url": profile_url
            }


# Global service instance
duxsoup_auth_service = None

def get_duxsoup_auth_service(user_id: str, api_key: str) -> DuxSoupAuthService:
    """Get or create DuxSoup authentication service"""
    global duxsoup_auth_service
    
    if not duxsoup_auth_service or duxsoup_auth_service.user_id != user_id:
        duxsoup_auth_service = DuxSoupAuthService(user_id, api_key)
    
    return duxsoup_auth_service
