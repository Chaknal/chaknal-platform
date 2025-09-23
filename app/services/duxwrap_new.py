"""
Chaknal Platform - DuxSoup Integration Wrapper

A clean, async-first wrapper designed specifically for our LinkedIn automation system.
This wrapper integrates directly with our database models and handles all DuxSoup API interactions.

Features:
- Async HTTP client with aiohttp
- Built-in rate limiting and retry logic
- Comprehensive error handling
- Direct database integration
- Multi-tenant support
- Campaign and sequence management
- Real-time status tracking
"""

import asyncio
import aiohttp
import hashlib
import hmac
import base64
import time
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import UUID
from enum import Enum

logger = logging.getLogger(__name__)


class DuxSoupCommandType(Enum):
    """LinkedIn Activity API Commands"""
    VISIT = "visit"
    ENROLL = "enroll"
    CONNECT = "connect"
    MESSAGE = "message"
    INMAIL = "inmail"
    TAG = "tag"
    UNTAG = "untag"
    SAVE_TO_PDF = "savetopdf"
    FOLLOW = "follow"
    DISCONNECT = "disconnect"
    ENDORSE = "endorse"
    SAVE_AS_LEAD = "saveaslead"
    WAIT = "wait"
    RESET = "reset"


class DuxSoupStatus(Enum):
    """DuxSoup operation statuses"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DuxSoupUser:
    """DuxSoup user configuration"""
    userid: str
    apikey: str
    label: str = ""
    daily_limits: Dict[str, int] = field(default_factory=lambda: {
        "max_invites": 100,
        "max_messages": 50,
        "max_visits": 200
    })
    automation_settings: Dict[str, bool] = field(default_factory=lambda: {
        "auto_connect": True,
        "auto_message": True,
        "auto_endorse": False,
        "auto_follow": False
    })
    rate_limit_delay: float = 1.0  # seconds between requests


@dataclass
class DuxSoupCommand:
    """DuxSoup command configuration"""
    command: str
    params: Dict[str, Any]
    campaign_id: Optional[str] = None
    force: bool = False
    run_after: Optional[datetime] = None
    priority: int = 1  # 1=low, 5=high
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class DuxSoupResponse:
    """Standardized DuxSoup API response"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    response_time_ms: Optional[int] = None


class DuxSoupAPIError(Exception):
    """Custom exception for DuxSoup API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class DuxSoupRateLimitError(DuxSoupAPIError):
    """Exception for rate limit violations"""
    pass


class DuxSoupAuthenticationError(DuxSoupAPIError):
    """Exception for authentication failures"""
    pass


class DuxSoupWrapper:
    """
    Production-ready DuxSoup API wrapper for Chaknal Platform
    """
    
    VERSION = "2.0.0"
    BASE_URL = "https://app.dux-soup.com/xapi/remote/control"
    
    def __init__(self, dux_user: DuxSoupUser):
        """
        Initialize the wrapper with a DuxSoup user configuration
        
        Args:
            dux_user: DuxSoup user configuration
        """
        self.dux_user = dux_user
        self.session: Optional[aiohttp.ClientSession] = None
        self._rate_limit_delay = dux_user.rate_limit_delay
        self._last_request_time = 0.0
        self._request_count = 0
        self._error_count = 0
        
    async def __aenter__(self):
        """Async context manager entry"""
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers={
                "User-Agent": f"Chaknal-DuxSoup-Wrapper/{self.VERSION}",
                "Accept": "application/json"
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _create_signature(self, data: str) -> str:
        """
        Create HMAC-SHA1 signature for API authentication
        
        Args:
            data: Data to sign (JSON body for POST, URL for GET)
            
        Returns:
            Base64 encoded signature
        """
        try:
            mac = hmac.new(
                bytes(self.dux_user.apikey, 'ascii'), 
                digestmod=hashlib.sha1
            )
            message = bytes(data, 'ascii')
            mac.update(message)
            sig = mac.digest()
            return str(base64.b64encode(sig), 'ascii')
        except Exception as e:
            logger.error(f"Failed to create signature: {e}")
            raise DuxSoupAuthenticationError(f"Signature creation failed: {e}")
    
    def _get_headers(self, data: Optional[str] = None) -> Dict[str, str]:
        """
        Get headers for API request
        
        Args:
            data: Request data for signature generation
            
        Returns:
            Request headers
        """
        try:
            if data:
                signature = self._create_signature(data)
            else:
                signature = self._create_signature("")
                
            return {
                "X-Dux-Signature": signature,
                "Content-Type": "application/json",
                "User-Agent": f"Chaknal-DuxSoup-Wrapper/{self.VERSION}"
            }
        except Exception as e:
            logger.error(f"Failed to create headers: {e}")
            raise
    
    async def _enforce_rate_limit(self):
        """Enforce rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self._rate_limit_delay:
            sleep_time = self._rate_limit_delay - time_since_last
            await asyncio.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        retry_count: int = 0
    ) -> DuxSoupResponse:
        """
        Make authenticated API request with retry logic
        
        Args:
            method: HTTP method (GET/POST)
            endpoint: API endpoint
            data: Request data for POST requests
            retry_count: Current retry attempt
            
        Returns:
            Standardized DuxSoup response
            
        Raises:
            DuxSoupAPIError: If request fails after retries
        """
        if not self.session:
            raise DuxSoupAPIError("Session not initialized. Use async context manager.")
        
        # Enforce rate limiting
        await self._enforce_rate_limit()
        
        url = f"{self.BASE_URL}/{self.dux_user.userid}/{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                headers = self._get_headers(url)
                async with self.session.get(url, headers=headers) as response:
                    response_time = int((time.time() - start_time) * 1000)
                    
                    if response.status == 429:  # Rate limit
                        raise DuxSoupRateLimitError("Rate limit exceeded")
                    
                    response.raise_for_status()
                    result = await response.json()
                    
                    self._request_count += 1
                    return DuxSoupResponse(
                        success=True,
                        data=result,
                        response_time_ms=response_time
                    )
            else:
                # Add required fields for POST requests (matching original DuxSoup API)
                if data is None:
                    data = {}
                
                # Create request data matching original DuxSoup format
                request_data = {
                    "command": data.get("command", ""),
                    "targeturl": url,
                    "userid": self.dux_user.userid,
                    "timestamp": int(time.time() * 1000),
                    "params": data.get("params", {})
                }
                
                json_data = json.dumps(request_data)
                headers = self._get_headers(json_data)
                
                async with self.session.post(url, json=request_data, headers=headers) as response:
                    response_time = int((time.time() - start_time) * 1000)
                    
                    if response.status == 429:  # Rate limit
                        raise DuxSoupRateLimitError("Rate limit exceeded")
                    
                    response.raise_for_status()
                    result = await response.json()
                    
                    self._request_count += 1
                    return DuxSoupResponse(
                        success=True,
                        data=result,
                        response_time_ms=response_time
                    )
                    
        except DuxSoupRateLimitError:
            # Wait longer for rate limit
            wait_time = min(60, (2 ** retry_count) * 5)  # Exponential backoff
            logger.warning(f"Rate limit hit, waiting {wait_time}s before retry {retry_count + 1}")
            await asyncio.sleep(wait_time)
            
            if retry_count < 3:
                return await self._make_request(method, endpoint, data, retry_count + 1)
            else:
                raise DuxSoupRateLimitError("Rate limit exceeded after retries")
                
        except aiohttp.ClientError as e:
            self._error_count += 1
            logger.error(f"Network error: {e}")
            raise DuxSoupAPIError(f"Network error: {e}")
            
        except aiohttp.HTTPStatusError as e:
            self._error_count += 1
            logger.error(f"HTTP error {e.status}: {e.message}")
            
            if e.status == 401:
                raise DuxSoupAuthenticationError(f"Authentication failed: {e.message}", e.status)
            elif e.status == 403:
                raise DuxSoupAPIError(f"Access forbidden: {e.message}", e.status)
            elif e.status >= 500 and retry_count < 3:
                # Retry server errors
                wait_time = (2 ** retry_count) * 2
                logger.info(f"Server error, retrying in {wait_time}s (attempt {retry_count + 1})")
                await asyncio.sleep(wait_time)
                return await self._make_request(method, endpoint, data, retry_count + 1)
            else:
                raise DuxSoupAPIError(f"HTTP error {e.status}: {e.message}", e.status)
                
        except json.JSONDecodeError as e:
            self._error_count += 1
            logger.error(f"Invalid JSON response: {e}")
            raise DuxSoupAPIError(f"Invalid JSON response: {e}")
            
        except Exception as e:
            self._error_count += 1
            logger.error(f"Unexpected error: {e}")
            raise DuxSoupAPIError(f"Unexpected error: {e}")
    
    # LinkedIn Activity API Methods
    
    async def queue_action(self, command: DuxSoupCommand) -> DuxSoupResponse:
        """
        Queue a LinkedIn activity command
        
        Args:
            command: Command configuration
            
        Returns:
            Standardized DuxSoup response
        """
        try:
            # Create params matching original DuxSoup API format
            params = dict(command.params)
            
            # Add optional parameters if specified
            if command.campaign_id:
                params["campaignid"] = command.campaign_id
            if command.force:
                params["force"] = command.force
            if command.run_after:
                params["runafter"] = command.run_after.isoformat()
            
            data = {
                "command": command.command,
                "params": params
            }
            
            response = await self._make_request("POST", "queue", data)
            
            # Extract message ID if available
            if response.data and "message_id" in response.data:
                response.message_id = response.data["message_id"]
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to queue action {command.command}: {e}")
            return DuxSoupResponse(
                success=False,
                error=str(e)
            )
    
    async def visit_profile(
        self, 
        profile_url: str, 
        campaign_id: Optional[str] = None,
        force: bool = False
    ) -> DuxSoupResponse:
        """Queue a profile visit"""
        command = DuxSoupCommand(
            command="visit",
            params={"profile": profile_url},
            campaign_id=campaign_id,
            force=force
        )
        return await self.queue_action(command)
    
    async def connect_profile(
        self, 
        profile_url: str, 
        message_text: Optional[str] = None,
        campaign_id: Optional[str] = None,
        force: bool = False
    ) -> DuxSoupResponse:
        """Queue a connection request"""
        params = {"profile": profile_url}
        if message_text:
            params["messagetext"] = message_text
            
        command = DuxSoupCommand(
            command="connect",
            params=params,
            campaign_id=campaign_id,
            force=force
        )
        return await self.queue_action(command)
    
    async def send_message(
        self, 
        profile_url: str, 
        message_text: str,
        campaign_id: Optional[str] = None,
        force: bool = False
    ) -> DuxSoupResponse:
        """Queue a direct message"""
        command = DuxSoupCommand(
            command="message",
            params={
                "profile": profile_url,
                "messagetext": message_text
            },
            campaign_id=campaign_id,
            force=force
        )
        return await self.queue_action(command)
    
    async def send_inmail(
        self, 
        profile_url: str, 
        subject: str,
        message_text: str,
        campaign_id: Optional[str] = None,
        force: bool = False
    ) -> DuxSoupResponse:
        """Queue an InMail message"""
        command = DuxSoupCommand(
            command="inmail",
            params={
                "profile": profile_url,
                "messagesubject": subject,
                "messagetext": message_text
            },
            campaign_id=campaign_id,
            force=force
        )
        return await self.queue_action(command)
    
    async def follow_profile(
        self, 
        profile_url: str, 
        campaign_id: Optional[str] = None,
        force: bool = False
    ) -> DuxSoupResponse:
        """Queue a profile follow"""
        command = DuxSoupCommand(
            command="follow",
            params={"profile": profile_url},
            campaign_id=campaign_id,
            force=force
        )
        return await self.queue_action(command)
    
    async def endorse_profile(
        self, 
        profile_url: str, 
        skills: List[str],
        campaign_id: Optional[str] = None,
        force: bool = False
    ) -> DuxSoupResponse:
        """Queue a profile endorsement"""
        command = DuxSoupCommand(
            command="endorse",
            params={
                "profile": profile_url,
                "skills": skills
            },
            campaign_id=campaign_id,
            force=force
        )
        return await self.queue_action(command)
    
    async def tag_profile(
        self, 
        profile_url: str, 
        tags: List[str],
        campaign_id: Optional[str] = None,
        force: bool = False
    ) -> DuxSoupResponse:
        """Queue profile tagging"""
        command = DuxSoupCommand(
            command="tag",
            params={
                "profile": profile_url,
                "tags": tags
            },
            campaign_id=campaign_id,
            force=force
        )
        return await self.queue_action(command)
    
    async def save_to_pdf(
        self, 
        profile_url: str,
        campaign_id: Optional[str] = None,
        force: bool = False
    ) -> DuxSoupResponse:
        """Queue profile PDF save"""
        command = DuxSoupCommand(
            command="savetopdf",
            params={"profile": profile_url},
            campaign_id=campaign_id,
            force=force
        )
        return await self.queue_action(command)
    
    async def save_as_lead(
        self, 
        profile_url: str,
        campaign_id: Optional[str] = None,
        force: bool = False
    ) -> DuxSoupResponse:
        """Queue profile save as lead"""
        command = DuxSoupCommand(
            command="saveaslead",
            params={"profile": profile_url},
            campaign_id=campaign_id,
            force=force
        )
        return await self.queue_action(command)
    
    async def create_campaign(
        self,
        campaign_name: str,
        campaign_id: str,
        description: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> DuxSoupResponse:
        """Create a new campaign in DuxSoup"""
        try:
            data = {
                "command": "create_campaign",
                "params": {
                    "campaign_name": campaign_name,
                    "campaign_id": campaign_id
                }
            }
            
            if description:
                data["params"]["description"] = description
            
            if settings:
                data["params"]["settings"] = settings
            
            # Add required fields for POST requests
            data.update({
                "targeturl": f"{self.BASE_URL}/{self.dux_user.userid}/campaigns",
                "timestamp": int(time.time() * 1000),
                "userid": self.dux_user.userid
            })
            
            json_data = json.dumps(data)
            headers = self._get_headers(json_data)
            
            url = f"{self.BASE_URL}/{self.dux_user.userid}/campaigns"
            
            async with self.session.post(url, json=data, headers=headers) as response:
                response_time = int((time.time() - time.time()) * 1000)
                
                if response.status == 429:  # Rate limit
                    raise DuxSoupRateLimitError("Rate limit exceeded")
                
                response.raise_for_status()
                result = await response.json()
                
                self._request_count += 1
                return DuxSoupResponse(
                    success=True,
                    data=result,
                    response_time_ms=response_time
                )
                
        except Exception as e:
            logger.error(f"Failed to create campaign {campaign_name}: {e}")
            return DuxSoupResponse(
                success=False,
                error=str(e)
            )
    
    async def get_campaigns(self) -> DuxSoupResponse:
        """Get all campaigns for the user"""
        try:
            url = f"{self.BASE_URL}/{self.dux_user.userid}/campaigns"
            headers = self._get_headers(url)
            
            async with self.session.get(url, headers=headers) as response:
                response_time = int((time.time() - time.time()) * 1000)
                
                if response.status == 429:  # Rate limit
                    raise DuxSoupRateLimitError("Rate limit exceeded")
                
                response.raise_for_status()
                result = await response.json()
                
                self._request_count += 1
                return DuxSoupResponse(
                    success=True,
                    data=result,
                    response_time_ms=response_time
                )
                
        except Exception as e:
            logger.error(f"Failed to get campaigns: {e}")
            return DuxSoupResponse(
                success=False,
                error=str(e)
            )
    
    # Queue Management API Methods
    
    async def get_queue_size(
        self, 
        campaign_id: Optional[str] = None,
        profile_id: Optional[str] = None,
        command: Optional[str] = None
    ) -> DuxSoupResponse:
        """Get queue size"""
        endpoint = "queue/size"
        if any([campaign_id, profile_id, command]):
            params = []
            if campaign_id:
                params.append(f"campaignid={campaign_id}")
            if profile_id:
                params.append(f"profileid={profile_id}")
            if command:
                params.append(f"command={command}")
            endpoint += "?" + "&".join(params)
            
        return await self._make_request("GET", endpoint)
    
    async def get_queue_items(
        self, 
        campaign_id: Optional[str] = None,
        profile_id: Optional[str] = None,
        command: Optional[str] = None
    ) -> DuxSoupResponse:
        """Get queue items (max 100)"""
        endpoint = "queue/items"
        if any([campaign_id, profile_id, command]):
            params = []
            if campaign_id:
                params.append(f"campaignid={campaign_id}")
            if profile_id:
                params.append(f"profileid={profile_id}")
            if command:
                params.append(f"command={command}")
            endpoint += "?" + "&".join(params)
            
        return await self._make_request("GET", endpoint)
    
    async def clear_queue(self) -> DuxSoupResponse:
        """Clear all queued messages"""
        return await self._make_request("POST", "reset")
    
    # User Settings API Methods
    
    async def get_settings(self) -> DuxSoupResponse:
        """Get all user settings"""
        return await self._make_request("GET", "settings")
    
    async def update_settings(self, settings: Dict[str, Any]) -> DuxSoupResponse:
        """Update user settings"""
        return await self._make_request("POST", "settings", {"settings": settings})
    
    async def update_daily_limits(
        self, 
        max_invites: Optional[int] = None,
        max_messages: Optional[int] = None,
        max_visits: Optional[int] = None
    ) -> DuxSoupResponse:
        """Update daily activity limits"""
        settings = {}
        if max_invites is not None:
            settings["maxinvites"] = max_invites
        if max_messages is not None:
            settings["maxmessages"] = max_messages
        if max_visits is not None:
            settings["maxvisits"] = max_visits
            
        return await self.update_settings(settings)
    
    async def update_automation_settings(
        self,
        auto_connect: Optional[bool] = None,
        auto_message: Optional[bool] = None,
        auto_endorse: Optional[bool] = None,
        auto_follow: Optional[bool] = None
    ) -> DuxSoupResponse:
        """Update automation settings"""
        settings = {}
        if auto_connect is not None:
            settings["autoconnect"] = auto_connect
        if auto_message is not None:
            settings["connectedmessageflag"] = auto_message
        if auto_endorse is not None:
            settings["autoendorse"] = auto_endorse
        if auto_follow is not None:
            settings["autofollow"] = auto_follow
            
        return await self.update_settings(settings)
    
    # Extension Control API Methods
    
    async def reload_extension(self) -> DuxSoupResponse:
        """Force extension reload"""
        return await self._make_request("POST", "signal", {"signal": "extension_reload"})
    
    async def check_message_bridge(
        self, 
        box_name: str, 
        days_back: Optional[int] = None
    ) -> DuxSoupResponse:
        """Check message bridge"""
        params = {"signal": "bridge_check", "params": {"boxname": box_name}}
        if days_back is not None:
            params["params"]["daysback"] = days_back
            
        return await self._make_request("POST", "signal", params)
    
    async def reset_data(self) -> DuxSoupResponse:
        """Clear captured profile data"""
        return await self._make_request("POST", "signal", {"signal": "data_reset"})
    
    # User Profile API Methods
    
    async def get_profile(self) -> DuxSoupResponse:
        """Get user profile information"""
        return await self._make_request("GET", "profile")
    
    # Utility Methods
    
    async def get_queue_health(self) -> Dict[str, Any]:
        """Get comprehensive queue health information"""
        try:
            size_response = await self.get_queue_size()
            items_response = await self.get_queue_items()
            profile_response = await self.get_profile()
            
            return {
                "size": size_response.data if size_response.success else None,
                "items": items_response.data if items_response.success else None,
                "profile": profile_response.data if profile_response.success else None,
                "errors": [
                    size_response.error if not size_response.success else None,
                    items_response.error if not items_response.success else None,
                    profile_response.error if not profile_response.success else None
                ]
            }
        except Exception as e:
            logger.error(f"Failed to get queue health: {e}")
            return {"error": str(e)}
    
    async def batch_queue_actions(
        self, 
        commands: List[DuxSoupCommand]
    ) -> List[DuxSoupResponse]:
        """Queue multiple actions in batch"""
        results = []
        for command in commands:
            try:
                result = await self.queue_action(command)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to queue command {command.command}: {e}")
                results.append(DuxSoupResponse(
                    success=False,
                    error=str(e)
                ))
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get wrapper statistics"""
        return {
            "version": self.VERSION,
            "user_id": self.dux_user.userid,
            "request_count": self._request_count,
            "error_count": self._error_count,
            "success_rate": (self._request_count - self._error_count) / max(self._request_count, 1) * 100,
            "rate_limit_delay": self._rate_limit_delay
        }
    
    async def get_config(self) -> DuxSoupResponse:
        """Get DuxSoup configuration"""
        try:
            url = f"{self.BASE_URL}/{self.dux_user.userid}/settings?token={self.dux_user.apikey}"
            
            # Request body with userid and token (like the original example)
            request_data = {
                "targeturl": url,
                "userid": self.dux_user.userid,
                "token": self.dux_user.apikey,
                "timestamp": int(datetime.utcnow().timestamp() * 1000),
                "params": {}
            }
            
            headers = {
                "Content-Type": "application/json",
                "token": self.dux_user.apikey,
                "userid": self.dux_user.userid
            }
            
            async with aiohttp.ClientSession() as client:
                response = await client.post(url, json=request_data, headers=headers, timeout=30.0)
                
            if response.status == 200:
                data = await response.json()
                return DuxSoupResponse(
                    success=True,
                    data=data
                )
            else:
                return DuxSoupResponse(
                    success=False,
                    error=f"HTTP {response.status}"
                )
                
        except Exception as e:
            return DuxSoupResponse(
                success=False,
                error=str(e)
            )
    
    async def update_config(self, config: Dict[str, Any]) -> DuxSoupResponse:
        """Update DuxSoup configuration"""
        try:
            url = f"{self.BASE_URL}/{self.dux_user.userid}/settings?token={self.dux_user.apikey}"
            
            # Request body with userid and token (like the original example)
            request_data = {
                "targeturl": url,
                "userid": self.dux_user.userid,
                "token": self.dux_user.apikey,
                "timestamp": int(datetime.utcnow().timestamp() * 1000),
                "params": config
            }
            
            headers = {
                "Content-Type": "application/json",
                "token": self.dux_user.apikey,
                "userid": self.dux_user.userid
            }
            
            async with aiohttp.ClientSession() as client:
                response = await client.post(url, json=request_data, headers=headers, timeout=30.0)
                
            if response.status == 200:
                data = await response.json()
                return DuxSoupResponse(
                    success=True,
                    data=data
                )
            else:
                return DuxSoupResponse(
                    success=False,
                    error=f"HTTP {response.status}"
                )
                
        except Exception as e:
            return DuxSoupResponse(
                success=False,
                error=str(e)
            )


class DuxSoupManager:
    """
    Multi-tenant DuxSoup manager for handling multiple accounts
    """
    
    def __init__(self):
        self.users: Dict[str, DuxSoupWrapper] = {}
        self._lock = asyncio.Lock()
    
    async def add_user(self, user_id: str, dux_user: DuxSoupUser) -> None:
        """Add a DuxSoup user to the manager"""
        async with self._lock:
            if user_id in self.users:
                await self.remove_user(user_id)
            
            wrapper = DuxSoupWrapper(dux_user)
            await wrapper.__aenter__()
            self.users[user_id] = wrapper
            logger.info(f"Added DuxSoup user: {user_id}")
    
    def get_user(self, user_id: str) -> Optional[DuxSoupWrapper]:
        """Get a DuxSoup user wrapper"""
        return self.users.get(user_id)
    
    async def remove_user(self, user_id: str) -> None:
        """Remove a DuxSoup user from the manager"""
        async with self._lock:
            if user_id in self.users:
                await self.users[user_id].__aexit__(None, None, None)
                del self.users[user_id]
                logger.info(f"Removed DuxSoup user: {user_id}")
    
    async def get_all_queue_health(self) -> Dict[str, Dict]:
        """Get queue health for all users"""
        health_data = {}
        for user_id, wrapper in self.users.items():
            try:
                health_data[user_id] = await wrapper.get_queue_health()
            except Exception as e:
                health_data[user_id] = {"error": str(e)}
        return health_data
    
    async def cleanup(self):
        """Clean up all user sessions"""
        async with self._lock:
            for user_id in list(self.users.keys()):
                await self.remove_user(user_id)
    
    def get_all_stats(self) -> Dict[str, Dict]:
        """Get statistics for all users"""
        return {
            user_id: wrapper.get_stats() 
            for user_id, wrapper in self.users.items()
        }