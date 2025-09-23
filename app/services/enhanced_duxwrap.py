"""
Enhanced DuxSoup Wrapper with runafter Support
Integrates with existing campaign system
"""

import json
import requests
import hashlib
import hmac
import base64
import time
from typing import Dict, Any, Optional
from datetime import datetime

class EnhancedDuxWrap:
    """
    Enhanced DuxSoup wrapper that supports the runafter parameter
    for proper message scheduling
    """
    
    def __init__(self, api_key: str, user_id: str):
        self.api_key = api_key
        self.user_id = user_id
        self.endpoint = 'https://app.dux-soup.com/xapi/remote/control'
    
    def _create_signature(self, data: str) -> str:
        """Create DuxSoup signature"""
        mac = hmac.new(bytes(self.api_key, 'ascii'), digestmod=hashlib.sha1)
        message = bytes(data, 'ascii')
        mac.update(message)
        sig = mac.digest()
        return str(base64.b64encode(sig), 'ascii')
    
    def call_with_runafter(
        self, 
        command: str, 
        params: Dict[str, Any], 
        runafter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Call DuxSoup command with optional runafter scheduling
        
        Args:
            command: DuxSoup command (message, connect, inmail, etc.)
            params: Command parameters
            runafter: ISO date string for scheduling (optional)
            
        Returns:
            DuxSoup API response
        """
        
        # Create request data according to official DuxSoup API docs
        request_data = {
            'command': command,
            'timestamp': int(time.time() * 1000),
            'userid': self.user_id,
            'targeturl': f'{self.endpoint}/{self.user_id}/queue',
            'params': params
        }
        
        # Add runafter if provided (at top level, not in params)
        if runafter:
            request_data['runafter'] = runafter
        
        # Create signature
        signature_data = json.dumps(request_data)
        signature = self._create_signature(signature_data)
        
        # Send request
        headers = {
            'X-Dux-Signature': signature,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            request_data['targeturl'],
            json=request_data,
            headers=headers
        )
        
        return response.json()
    
    def schedule_message(
        self,
        profile_url: str,
        message_text: str,
        campaign_id: str,
        scheduled_time: datetime,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Schedule a message for a specific time
        
        Args:
            profile_url: LinkedIn profile URL
            message_text: Message content
            campaign_id: Campaign ID for tracking
            scheduled_time: When to send the message
            force: Force the action, ignoring exclusion rules
            
        Returns:
            DuxSoup API response
        """
        
        runafter_iso = scheduled_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        return self.call_with_runafter(
            command='message',
            params={
                'profile': profile_url,
                'messagetext': message_text,
                'campaignid': campaign_id,
                'force': force
            },
            runafter=runafter_iso
        )
    
    def schedule_connection_request(
        self,
        profile_url: str,
        message_text: str,
        campaign_id: str,
        scheduled_time: datetime,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Schedule a connection request for a specific time
        
        Args:
            profile_url: LinkedIn profile URL
            message_text: Connection request message
            campaign_id: Campaign ID for tracking
            scheduled_time: When to send the request
            force: Force the action, ignoring exclusion rules
            
        Returns:
            DuxSoup API response
        """
        
        runafter_iso = scheduled_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        return self.call_with_runafter(
            command='connect',
            params={
                'profile': profile_url,
                'messagetext': message_text,
                'campaignid': campaign_id,
                'force': force
            },
            runafter=runafter_iso
        )
    
    def schedule_inmail(
        self,
        profile_url: str,
        subject: str,
        message_text: str,
        campaign_id: str,
        scheduled_time: datetime,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Schedule an InMail for a specific time
        
        Args:
            profile_url: LinkedIn profile URL
            subject: InMail subject line
            message_text: InMail content
            campaign_id: Campaign ID for tracking
            scheduled_time: When to send the InMail
            force: Force the action, ignoring exclusion rules
            
        Returns:
            DuxSoup API response
        """
        
        runafter_iso = scheduled_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        return self.call_with_runafter(
            command='inmail',
            params={
                'profile': profile_url,
                'messagesubject': subject,
                'messagetext': message_text,
                'campaignid': campaign_id,
                'force': force
            },
            runafter=runafter_iso
        )
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current DuxSoup queue status"""
        # This would use the existing DuxWrap functionality
        # For now, return a placeholder
        return {"status": "queue_status_not_implemented"}
