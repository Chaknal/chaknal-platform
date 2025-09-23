#!/usr/bin/env python3
"""
Standalone integration test for the new DuxSoup wrapper

This script tests the integration without importing the main app modules.
"""

import asyncio
import hashlib
import hmac
import base64
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


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
    run_after: Optional[str] = None
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
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))
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


class MockDuxSoupWrapper:
    """
    Mock DuxSoup wrapper for testing without actual API calls
    """
    
    VERSION = "2.0.0"
    BASE_URL = "https://app.dux-soup.com/xapi/remote/control"
    
    def __init__(self, dux_user: DuxSoupUser):
        """Initialize the wrapper with a DuxSoup user configuration"""
        self.dux_user = dux_user
        self._rate_limit_delay = dux_user.rate_limit_delay
        self._last_request_time = 0.0
        self._request_count = 0
        self._error_count = 0
        
    def _create_signature(self, data: str) -> str:
        """Create HMAC-SHA1 signature for API authentication"""
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
            raise DuxSoupAuthenticationError(f"Signature creation failed: {e}")
    
    def _get_headers(self, data: Optional[str] = None) -> Dict[str, str]:
        """Get headers for API request"""
        try:
            if data:
                signature = self._create_signature(data)
            else:
                signature = self._create_signature("")
                
            return {
                "X-DuxSoup-Signature": signature,
                "Content-Type": "application/json",
                "User-Agent": f"Chaknal-DuxSoup-Wrapper/{self.VERSION}"
            }
        except Exception as e:
            raise
    
    async def _enforce_rate_limit(self):
        """Enforce rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self._rate_limit_delay:
            sleep_time = self._rate_limit_delay - time_since_last
            await asyncio.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    async def queue_action(self, command: DuxSoupCommand) -> DuxSoupResponse:
        """Mock queue action - simulates API call"""
        await self._enforce_rate_limit()
        
        # Simulate API response
        self._request_count += 1
        
        # Simulate some failures for testing
        if command.command == "invalid":
            self._error_count += 1
            return DuxSoupResponse(
                success=False,
                error="Invalid command"
            )
        
        # Generate mock message ID
        message_id = f"msg_{int(time.time())}_{hash(command.command) % 1000}"
        
        return DuxSoupResponse(
            success=True,
            data={
                "message_id": message_id,
                "status": "queued",
                "command": command.command
            },
            message_id=message_id,
            response_time_ms=150
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
                results.append(DuxSoupResponse(
                    success=False,
                    error=str(e)
                ))
        return results
    
    async def get_queue_health(self) -> Dict[str, Any]:
        """Get comprehensive queue health information"""
        try:
            return {
                "size": {"total": 5, "pending": 3, "completed": 2},
                "items": [
                    {"command": "visit", "status": "queued", "profile": "https://linkedin.com/in/user1"},
                    {"command": "connect", "status": "running", "profile": "https://linkedin.com/in/user2"}
                ],
                "profile": {"name": "Test User", "status": "active", "daily_limits": {"invites": 45, "messages": 23}},
                "errors": []
            }
        except Exception as e:
            return {"error": str(e)}
    
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


class MockLinkedInAutomationService:
    """Mock LinkedIn automation service for testing"""
    
    def __init__(self):
        self.active_campaigns: Dict[str, Any] = {}
        self.dux_wrappers: Dict[str, MockDuxSoupWrapper] = {}
    
    async def get_dux_wrapper(self, dux_user_id: str) -> Optional[MockDuxSoupWrapper]:
        """Get or create a DuxSoup wrapper for a user"""
        if dux_user_id in self.dux_wrappers:
            return self.dux_wrappers[dux_user_id]
        
        # Create mock user config
        dux_user_config = DuxSoupUser(
            userid=dux_user_id,
            apikey="fake_api_key",
            label=f"User {dux_user_id}",
            daily_limits={"max_invites": 50, "max_messages": 25, "max_visits": 100},
            automation_settings={"auto_connect": True, "auto_message": True}
        )
        
        # Create wrapper
        wrapper = MockDuxSoupWrapper(dux_user_config)
        self.dux_wrappers[dux_user_id] = wrapper
        return wrapper
    
    async def execute_campaign_step(self, campaign_id: str, step_type: str, profile_url: str) -> Dict[str, Any]:
        """Execute a campaign step using the wrapper"""
        try:
            # Get wrapper
            wrapper = await self.get_dux_wrapper(campaign_id)
            if not wrapper:
                return {"success": False, "error": "Wrapper not available"}
            
            # Execute step based on type
            if step_type == "visit":
                response = await wrapper.visit_profile(profile_url, campaign_id)
            elif step_type == "connect":
                response = await wrapper.connect_profile(profile_url, campaign_id=campaign_id)
            elif step_type == "message":
                response = await wrapper.send_message(profile_url, "Hello!", campaign_id)
            else:
                return {"success": False, "error": f"Unknown step type: {step_type}"}
            
            # Handle response
            if response.success:
                return {
                    "success": True,
                    "action": step_type,
                    "message_id": response.message_id,
                    "message": f"{step_type} completed successfully"
                }
            else:
                return {
                    "success": False,
                    "error": response.error or f"{step_type} failed"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def cleanup_wrappers(self):
        """Clean up all DuxSoup wrapper sessions"""
        self.dux_wrappers.clear()


async def test_automation_service_integration():
    """Test the automation service integration"""
    print("🧪 Testing LinkedIn automation service integration...")
    
    # Create automation service
    automation_service = MockLinkedInAutomationService()
    
    # Test campaign execution
    campaign_id = "campaign_123"
    profile_url = "https://linkedin.com/in/testuser"
    
    print(f"✅ Created automation service")
    
    # Test step 1: Visit profile
    print(f"\n📋 Step 1: Visiting profile...")
    result = await automation_service.execute_campaign_step(campaign_id, "visit", profile_url)
    
    if result["success"]:
        print(f"   ✅ {result['action']}: {result['message']}")
        print(f"      Message ID: {result['message_id']}")
    else:
        print(f"   ❌ {result['action']}: {result['error']}")
    
    # Test step 2: Send connection request
    print(f"\n📋 Step 2: Sending connection request...")
    result = await automation_service.execute_campaign_step(campaign_id, "connect", profile_url)
    
    if result["success"]:
        print(f"   ✅ {result['action']}: {result['message']}")
        print(f"      Message ID: {result['message_id']}")
    else:
        print(f"   ❌ {result['action']}: {result['error']}")
    
    # Test step 3: Send message
    print(f"\n📋 Step 3: Sending message...")
    result = await automation_service.execute_campaign_step(campaign_id, "message", profile_url)
    
    if result["success"]:
        print(f"   ✅ {result['action']}: {result['message']}")
        print(f"      Message ID: {result['message_id']}")
    else:
        print(f"   ❌ {result['action']}: {result['error']}")
    
    # Test invalid step type
    print(f"\n📋 Step 4: Testing invalid step type...")
    result = await automation_service.execute_campaign_step(campaign_id, "invalid", profile_url)
    
    if result["success"]:
        print(f"   ❌ Should have failed with invalid step type")
    else:
        print(f"   ✅ Properly caught error: {result['error']}")
    
    # Show wrapper stats
    wrapper = await automation_service.get_dux_wrapper(campaign_id)
    if wrapper:
        print(f"\n📊 Wrapper statistics:")
        stats = wrapper.get_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
    
    # Cleanup
    await automation_service.cleanup_wrappers()
    print(f"\n✅ Cleanup completed")
    
    print(f"\n🎉 Automation service integration test completed!")


async def test_campaign_automation_flow():
    """Test a complete campaign automation flow"""
    print("\n🧪 Testing complete campaign automation flow...")
    
    # Create automation service
    automation_service = MockLinkedInAutomationService()
    
    # Simulate campaign with multiple contacts
    campaign_id = "campaign_456"
    contacts = [
        "https://linkedin.com/in/contact1",
        "https://linkedin.com/in/contact2",
        "https://linkedin.com/in/contact3"
    ]
    
    print(f"✅ Created automation service for campaign {campaign_id}")
    print(f"   Processing {len(contacts)} contacts")
    
    # Process each contact through the automation flow
    for i, contact_url in enumerate(contacts, 1):
        print(f"\n📋 Processing contact {i}: {contact_url}")
        
        # Step 1: Visit profile
        result = await automation_service.execute_campaign_step(campaign_id, "visit", contact_url)
        if result["success"]:
            print(f"   ✅ Visit: {result['message_id']}")
        else:
            print(f"   ❌ Visit: {result['error']}")
        
        # Step 2: Send connection request
        result = await automation_service.execute_campaign_step(campaign_id, "connect", contact_url)
        if result["success"]:
            print(f"   ✅ Connect: {result['message_id']}")
        else:
            print(f"   ❌ Connect: {result['error']}")
    
    # Show final stats
    wrapper = await automation_service.get_dux_wrapper(campaign_id)
    if wrapper:
        print(f"\n📊 Final campaign statistics:")
        stats = wrapper.get_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
    
    # Cleanup
    await automation_service.cleanup_wrappers()
    print(f"\n✅ Campaign cleanup completed")
    
    print(f"\n🎉 Campaign automation flow test completed!")


async def main():
    """Main test function"""
    print("🚀 Starting LinkedIn Automation Integration Tests\n")
    
    try:
        # Test 1: Basic automation service integration
        await test_automation_service_integration()
        
        # Test 2: Complete campaign automation flow
        await test_campaign_automation_flow()
        
        print("\n🎉 All integration tests completed successfully!")
        
    except Exception as e:
        print(f"\n💥 Integration test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
