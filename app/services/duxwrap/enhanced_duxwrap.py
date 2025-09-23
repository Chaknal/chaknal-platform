"""
Enhanced Dux-Soup API Wrapper

A comprehensive Python wrapper for the Dux-Soup API that supports:
- LinkedIn Activity API (all commands)
- User Settings API (read/write)
- Extension Control API
- Queue Management API
- User Profile API
- Prospect API

This wrapper is designed for multi-tenant Dux-Soup management platforms.
"""

import hashlib
import hmac
import base64
import time
import json
import requests
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum


class DuxCommand(Enum):
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


class ExtensionSignal(Enum):
    """Extension Control Signals"""
    EXTENSION_RELOAD = "extension_reload"
    BRIDGE_CHECK = "bridge_check"
    DATA_RESET = "data_reset"


@dataclass
class DuxUser:
    """Dux-Soup user configuration"""
    userid: str
    apikey: str
    label: str = ""
    settings_cache: Optional[Dict] = None


class DuxSoupAPIError(Exception):
    """Custom exception for Dux-Soup API errors"""
    pass


class EnhancedDuxWrap:
    """
    Enhanced Dux-Soup API wrapper supporting all API endpoints
    """
    
    VERSION = "1.0.0"
    BASE_URL = "https://app.dux-soup.com/xapi/remote/control"
    
    def __init__(self, dux_user: DuxUser):
        """
        Initialize the wrapper with a DuxUser configuration
        
        Args:
            dux_user: DuxUser object containing userid and apikey
        """
        self.dux_user = dux_user
        self.session = requests.Session()
        
    def _create_signature(self, data: str) -> str:
        """
        Create HMAC-SHA1 signature for API authentication
        
        Args:
            data: Data to sign (JSON body for POST, URL for GET)
            
        Returns:
            Base64 encoded signature
        """
        mac = hmac.new(
            bytes(self.dux_user.apikey, 'ascii'), 
            digestmod=hashlib.sha1
        )
        message = bytes(data, 'ascii')
        mac.update(message)
        sig = mac.digest()
        return str(base64.b64encode(sig), 'ascii')
    
    def _get_headers(self, data: Optional[str] = None) -> Dict[str, str]:
        """
        Get headers for API request
        
        Args:
            data: Request data for signature calculation
            
        Returns:
            Headers dictionary
        """
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"DuxSoup-Enhanced-Wrapper/{self.VERSION}"
        }
        
        if data:
            signature = self._create_signature(data)
            headers["X-Dux-Signature"] = signature
            
        return headers
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None
    ) -> Dict:
        """
        Make authenticated API request
        
        Args:
            method: HTTP method (GET/POST)
            endpoint: API endpoint
            data: Request data for POST requests
            
        Returns:
            API response as dictionary
            
        Raises:
            DuxSoupAPIError: If request fails
        """
        url = f"{self.BASE_URL}/{self.dux_user.userid}/{endpoint}"
        
        if method.upper() == "GET":
            headers = self._get_headers(url)
            response = self.session.get(url, headers=headers)
        else:
            # Add required fields for POST requests
            if data is None:
                data = {}
            
            data.update({
                "targeturl": url,
                "timestamp": int(time.time() * 1000),
                "userid": self.dux_user.userid
            })
            
            json_data = json.dumps(data)
            headers = self._get_headers(json_data)
            response = self.session.post(url, json=data, headers=headers)
        
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise DuxSoupAPIError(f"API request failed: {e}")
        except json.JSONDecodeError as e:
            raise DuxSoupAPIError(f"Invalid JSON response: {e}")
    
    # LinkedIn Activity API Methods
    
    def queue_action(
        self, 
        command: Union[str, DuxCommand], 
        params: Dict[str, Any],
        campaign_id: Optional[str] = None,
        force: bool = False,
        run_after: Optional[str] = None
    ) -> Dict:
        """
        Queue a LinkedIn activity command
        
        Args:
            command: Activity command to execute
            params: Command parameters
            campaign_id: Optional campaign ID
            force: Force action ignoring exclusion rules
            run_after: ISO date string for delayed execution
            
        Returns:
            API response with message ID
        """
        if isinstance(command, DuxCommand):
            command = command.value
            
        data = {
            "command": command,
            "params": params
        }
        
        if campaign_id:
            data["params"]["campaignid"] = campaign_id
        if force:
            data["params"]["force"] = force
        if run_after:
            data["params"]["runafter"] = run_after
            
        return self._make_request("POST", "queue", data)
    
    def visit_profile(
        self, 
        profile_url: str, 
        campaign_id: Optional[str] = None,
        force: bool = False
    ) -> Dict:
        """Queue a profile visit"""
        return self.queue_action(
            DuxCommand.VISIT,
            {"profile": profile_url},
            campaign_id=campaign_id,
            force=force
        )
    
    def enroll_profile(
        self, 
        profile_url: str, 
        campaign_id: str,
        force: bool = False
    ) -> Dict:
        """Queue a profile enrollment"""
        return self.queue_action(
            DuxCommand.ENROLL,
            {"profile": profile_url},
            campaign_id=campaign_id,
            force=force
        )
    
    def connect_profile(
        self, 
        profile_url: str, 
        message_text: Optional[str] = None,
        campaign_id: Optional[str] = None,
        force: bool = False
    ) -> Dict:
        """Queue a connection request"""
        params = {"profile": profile_url}
        if message_text:
            params["messagetext"] = message_text
            
        return self.queue_action(
            DuxCommand.CONNECT,
            params,
            campaign_id=campaign_id,
            force=force
        )
    
    def send_message(
        self, 
        profile_url: str, 
        message_text: str,
        campaign_id: Optional[str] = None,
        force: bool = False
    ) -> Dict:
        """Queue a direct message"""
        return self.queue_action(
            DuxCommand.MESSAGE,
            {
                "profile": profile_url,
                "messagetext": message_text
            },
            campaign_id=campaign_id,
            force=force
        )
    
    def send_inmail(
        self, 
        profile_url: str, 
        subject: str,
        message_text: str,
        campaign_id: Optional[str] = None,
        force: bool = False
    ) -> Dict:
        """Queue an InMail message"""
        return self.queue_action(
            DuxCommand.INMAIL,
            {
                "profile": profile_url,
                "messagesubject": subject,
                "messagetext": message_text
            },
            campaign_id=campaign_id,
            force=force
        )
    
    def tag_profile(
        self, 
        profile_url: str, 
        tags: List[str],
        campaign_id: Optional[str] = None,
        force: bool = False
    ) -> Dict:
        """Queue profile tagging"""
        return self.queue_action(
            DuxCommand.TAG,
            {
                "profile": profile_url,
                "tags": tags
            },
            campaign_id=campaign_id,
            force=force
        )
    
    def untag_profile(
        self, 
        profile_url: str, 
        tags: List[str],
        campaign_id: Optional[str] = None,
        force: bool = False
    ) -> Dict:
        """Queue profile untagging"""
        return self.queue_action(
            DuxCommand.UNTAG,
            {
                "profile": profile_url,
                "tags": tags
            },
            campaign_id=campaign_id,
            force=force
        )
    
    def save_to_pdf(
        self, 
        profile_url: str,
        campaign_id: Optional[str] = None,
        force: bool = False
    ) -> Dict:
        """Queue PDF save"""
        return self.queue_action(
            DuxCommand.SAVE_TO_PDF,
            {"profile": profile_url},
            campaign_id=campaign_id,
            force=force
        )
    
    def follow_profile(
        self, 
        profile_url: str,
        campaign_id: Optional[str] = None,
        force: bool = False
    ) -> Dict:
        """Queue profile follow"""
        return self.queue_action(
            DuxCommand.FOLLOW,
            {"profile": profile_url},
            campaign_id=campaign_id,
            force=force
        )
    
    def disconnect_profile(
        self, 
        profile_url: str,
        campaign_id: Optional[str] = None,
        force: bool = False
    ) -> Dict:
        """Queue profile disconnect"""
        return self.queue_action(
            DuxCommand.DISCONNECT,
            {"profile": profile_url},
            campaign_id=campaign_id,
            force=force
        )
    
    def endorse_profile(
        self, 
        profile_url: str,
        count: int = 3,
        campaign_id: Optional[str] = None,
        force: bool = False
    ) -> Dict:
        """Queue profile endorsement"""
        return self.queue_action(
            DuxCommand.ENDORSE,
            {
                "profile": profile_url,
                "count": count
            },
            campaign_id=campaign_id,
            force=force
        )
    
    def save_as_lead(
        self, 
        profile_url: str,
        campaign_id: Optional[str] = None,
        force: bool = False
    ) -> Dict:
        """Queue save as lead"""
        return self.queue_action(
            DuxCommand.SAVE_AS_LEAD,
            {"profile": profile_url},
            campaign_id=campaign_id,
            force=force
        )
    
    # Queue Management API Methods
    
    def get_queue_size(
        self, 
        campaign_id: Optional[str] = None,
        profile_id: Optional[str] = None,
        command: Optional[str] = None
    ) -> Dict:
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
            
        return self._make_request("GET", endpoint)
    
    def get_queue_items(
        self, 
        campaign_id: Optional[str] = None,
        profile_id: Optional[str] = None,
        command: Optional[str] = None
    ) -> Dict:
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
            
        return self._make_request("GET", endpoint)
    
    def clear_queue(self) -> Dict:
        """Clear all queued messages"""
        return self._make_request("POST", "reset")
    
    # User Settings API Methods
    
    def get_settings(self) -> Dict:
        """Get all user settings"""
        return self._make_request("GET", "settings")
    
    def update_settings(self, settings: Dict[str, Any]) -> Dict:
        """Update user settings"""
        return self._make_request("POST", "settings", {"settings": settings})
    
    def update_daily_limits(
        self, 
        max_invites: Optional[int] = None,
        max_messages: Optional[int] = None,
        max_visits: Optional[int] = None
    ) -> Dict:
        """Update daily activity limits"""
        settings = {}
        if max_invites is not None:
            settings["maxinvites"] = max_invites
        if max_messages is not None:
            settings["maxmessages"] = max_messages
        if max_visits is not None:
            settings["maxvisits"] = max_visits
            
        return self.update_settings(settings)
    
    def update_automation_settings(
        self,
        auto_connect: Optional[bool] = None,
        auto_message: Optional[bool] = None,
        auto_endorse: Optional[bool] = None,
        auto_follow: Optional[bool] = None
    ) -> Dict:
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
            
        return self.update_settings(settings)
    
    # Extension Control API Methods
    
    def send_signal(
        self, 
        signal: Union[str, ExtensionSignal], 
        params: Optional[Dict] = None
    ) -> Dict:
        """Send extension control signal"""
        if isinstance(signal, ExtensionSignal):
            signal = signal.value
            
        data = {"signal": signal}
        if params:
            data["params"] = params
            
        return self._make_request("POST", "signal", data)
    
    def reload_extension(self) -> Dict:
        """Force extension reload"""
        return self.send_signal(ExtensionSignal.EXTENSION_RELOAD)
    
    def check_message_bridge(
        self, 
        box_name: str, 
        days_back: Optional[int] = None
    ) -> Dict:
        """Check message bridge"""
        params = {"boxname": box_name}
        if days_back is not None:
            params["daysback"] = days_back
            
        return self.send_signal(ExtensionSignal.BRIDGE_CHECK, params)
    
    def reset_data(self) -> Dict:
        """Clear captured profile data"""
        return self.send_signal(ExtensionSignal.DATA_RESET)
    
    # User Profile API Methods
    
    def get_profile(self) -> Dict:
        """Get user profile information"""
        return self._make_request("GET", "profile")
    
    # Prospect API Methods
    
    def get_prospect_tags(self, profile_id: str) -> Dict:
        """Get prospect tags by profile ID"""
        return self._make_request("GET", f"prospects/{profile_id}/tags")
    
    # Utility Methods
    
    def get_queue_health(self) -> Dict:
        """Get comprehensive queue health information"""
        return {
            "size": self.get_queue_size(),
            "items": self.get_queue_items(),
            "profile": self.get_profile()
        }
    
    def batch_queue_actions(
        self, 
        actions: List[Dict[str, Any]]
    ) -> List[Dict]:
        """Queue multiple actions in batch"""
        results = []
        for action in actions:
            try:
                result = self.queue_action(
                    action["command"],
                    action["params"],
                    campaign_id=action.get("campaign_id"),
                    force=action.get("force", False),
                    run_after=action.get("run_after")
                )
                results.append({"success": True, "result": result})
            except Exception as e:
                results.append({"success": False, "error": str(e)})
        return results


# Convenience functions for multi-tenant usage

class DuxSoupManager:
    """
    Multi-tenant Dux-Soup manager for handling multiple accounts
    """
    
    def __init__(self):
        self.users: Dict[str, EnhancedDuxWrap] = {}
    
    def add_user(self, user_id: str, dux_user: DuxUser) -> None:
        """Add a Dux-Soup user to the manager"""
        self.users[user_id] = EnhancedDuxWrap(dux_user)
    
    def get_user(self, user_id: str) -> Optional[EnhancedDuxWrap]:
        """Get a Dux-Soup user wrapper"""
        return self.users.get(user_id)
    
    def remove_user(self, user_id: str) -> None:
        """Remove a Dux-Soup user from the manager"""
        if user_id in self.users:
            del self.users[user_id]
    
    def get_all_queue_health(self) -> Dict[str, Dict]:
        """Get queue health for all users"""
        health = {}
        for user_id, wrapper in self.users.items():
            try:
                health[user_id] = wrapper.get_queue_health()
            except Exception as e:
                health[user_id] = {"error": str(e)}
        return health
    
    def batch_action_across_users(
        self, 
        user_ids: List[str], 
        command: str, 
        params: Dict[str, Any]
    ) -> Dict[str, Dict]:
        """Execute the same action across multiple users"""
        results = {}
        for user_id in user_ids:
            if user_id in self.users:
                try:
                    results[user_id] = self.users[user_id].queue_action(
                        command, params
                    )
                except Exception as e:
                    results[user_id] = {"error": str(e)}
            else:
                results[user_id] = {"error": "User not found"}
        return results 