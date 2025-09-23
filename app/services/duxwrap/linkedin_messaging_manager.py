"""
LinkedIn Messaging Manager

This module handles LinkedIn-specific messaging rules:
- Connection status tracking
- Degree restrictions (2nd/3rd degree for emails)
- Message sequencing based on connection acceptance
- LinkedIn API compliance
"""

import json
import time
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from .enhanced_duxwrap import EnhancedDuxWrap


class ConnectionStatus(Enum):
    """LinkedIn connection status"""
    NOT_CONNECTED = "not_connected"
    PENDING = "pending"
    CONNECTED = "connected"
    REJECTED = "rejected"
    BLOCKED = "blocked"


class MessageType(Enum):
    """LinkedIn message types"""
    CONNECTION_REQUEST = "connection_request"
    CONNECTION_MESSAGE = "connection_message"  # Message with connection request
    INMAIL = "inmail"  # Paid messaging to 1st degree
    EMAIL = "email"  # Email to 2nd/3rd degree
    FOLLOW_UP = "follow_up"  # Follow-up after connection
    ENDORSEMENT = "endorsement"
    LIKE = "like"
    COMMENT = "comment"


class DegreeLevel(Enum):
    """LinkedIn degree levels"""
    FIRST = 1
    SECOND = 2
    THIRD = 3
    UNKNOWN = 0


@dataclass
class LinkedInProfile:
    """LinkedIn profile with connection and messaging info"""
    profile_url: str
    linkedin_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None
    degree_level: DegreeLevel = DegreeLevel.UNKNOWN
    connection_status: ConnectionStatus = ConnectionStatus.NOT_CONNECTED
    connection_request_sent: Optional[datetime] = None
    connection_accepted: Optional[datetime] = None
    last_message_sent: Optional[datetime] = None
    message_count: int = 0
    can_send_email: bool = False
    can_send_inmail: bool = False
    can_send_connection: bool = True
    tags: List[str] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class MessageSequence:
    """LinkedIn message sequence with connection awareness"""
    sequence_id: str
    name: str
    steps: List[Dict[str, Any]]
    connection_required: bool = False
    email_enabled: bool = False
    inmail_enabled: bool = False
    max_messages: int = 5
    delay_between_messages: int = 24  # hours
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class MessageStatus:
    """Status of a message in a sequence"""
    profile_url: str
    sequence_id: str
    step_number: int
    message_type: MessageType
    status: str  # "pending", "sent", "failed", "blocked", "connection_required"
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    linkedin_response: Optional[Dict[str, Any]] = None


class LinkedInMessagingManager:
    """
    Manages LinkedIn messaging with proper connection and degree restrictions
    """
    
    def __init__(self, dux_wrapper: EnhancedDuxWrap):
        """
        Initialize the LinkedIn messaging manager
        
        Args:
            dux_wrapper: Enhanced Dux-Soup wrapper
        """
        self.dux_wrapper = dux_wrapper
        self.profiles: Dict[str, LinkedInProfile] = {}
        self.sequences: Dict[str, MessageSequence] = {}
        self.message_statuses: List[MessageStatus] = []
        self.connection_requests: Dict[str, datetime] = {}
        
        # LinkedIn messaging rules
        self.messaging_rules = {
            "connection_request": {
                "requires_connection": False,
                "allowed_degrees": [DegreeLevel.SECOND, DegreeLevel.THIRD],
                "max_per_day": 100,
                "cooldown_hours": 24
            },
            "connection_message": {
                "requires_connection": False,
                "allowed_degrees": [DegreeLevel.SECOND, DegreeLevel.THIRD],
                "max_per_day": 100,
                "cooldown_hours": 24
            },
            "inmail": {
                "requires_connection": False,
                "allowed_degrees": [DegreeLevel.SECOND, DegreeLevel.THIRD],
                "max_per_day": 50,
                "cooldown_hours": 48,
                "requires_paid_account": True
            },
            "email": {
                "requires_connection": False,
                "allowed_degrees": [DegreeLevel.SECOND, DegreeLevel.THIRD],
                "max_per_day": 200,
                "cooldown_hours": 12
            },
            "follow_up": {
                "requires_connection": False,  # 1st degree can message immediately
                "allowed_degrees": [DegreeLevel.FIRST],
                "max_per_day": 100,
                "cooldown_hours": 24
            }
        }
    
    def add_profile(self, profile_data: LinkedInProfile) -> bool:
        """
        Add a LinkedIn profile with connection info
        
        Args:
            profile_data: LinkedIn profile information
            
        Returns:
            True if added successfully
        """
        self.profiles[profile_data.profile_url] = profile_data
        return True
    
    def update_connection_status(
        self, 
        profile_url: str, 
        status: ConnectionStatus,
        accepted_at: Optional[datetime] = None
    ) -> bool:
        """
        Update connection status for a profile
        
        Args:
            profile_url: LinkedIn profile URL
            status: New connection status
            accepted_at: When connection was accepted (if applicable)
            
        Returns:
            True if updated successfully
        """
        if profile_url not in self.profiles:
            return False
        
        profile = self.profiles[profile_url]
        profile.connection_status = status
        
        if status == ConnectionStatus.CONNECTED and accepted_at:
            profile.connection_accepted = accepted_at
        elif status == ConnectionStatus.PENDING:
            profile.connection_request_sent = datetime.now()
        
        return True
    
    def update_degree_level(
        self, 
        profile_url: str, 
        degree: DegreeLevel
    ) -> bool:
        """
        Update degree level for a profile
        
        Args:
            profile_url: LinkedIn profile URL
            degree: LinkedIn degree level
            
        Returns:
            True if updated successfully
        """
        if profile_url not in self.profiles:
            return False
        
        profile = self.profiles[profile_url]
        profile.degree_level = degree
        
        # Update messaging capabilities based on degree
        profile.can_send_email = degree in [DegreeLevel.SECOND, DegreeLevel.THIRD]
        profile.can_send_inmail = degree == DegreeLevel.FIRST
        profile.can_send_connection = degree in [DegreeLevel.SECOND, DegreeLevel.THIRD]
        
        return True
    
    def can_send_message(
        self, 
        profile_url: str, 
        message_type: MessageType
    ) -> Dict[str, Any]:
        """
        Check if a message can be sent to a profile
        
        Args:
            profile_url: LinkedIn profile URL
            message_type: Type of message to send
            
        Returns:
            Dictionary with can_send, reason, and restrictions
        """
        if profile_url not in self.profiles:
            return {
                "can_send": False,
                "reason": "Profile not found",
                "restrictions": []
            }
        
        profile = self.profiles[profile_url]
        rules = self.messaging_rules.get(message_type.value, {})
        
        restrictions = []
        
        # Check connection requirement
        if rules.get("requires_connection", False):
            if profile.connection_status != ConnectionStatus.CONNECTED:
                # Exception: 1st degree connections don't need explicit connection acceptance
                if profile.degree_level != DegreeLevel.FIRST:
                    restrictions.append("Connection required")
                else:
                    # 1st degree can message immediately
                    pass
        
        # Check degree restrictions
        allowed_degrees = rules.get("allowed_degrees", [])
        if profile.degree_level not in allowed_degrees:
            restrictions.append(f"Degree level {profile.degree_level.value} not allowed")
        
        # Check daily limits
        daily_count = self._get_daily_message_count(profile_url, message_type)
        max_per_day = rules.get("max_per_day", 0)
        if daily_count >= max_per_day:
            restrictions.append(f"Daily limit reached ({daily_count}/{max_per_day})")
        
        # Check cooldown period
        last_message = self._get_last_message_time(profile_url, message_type)
        if last_message:
            cooldown_hours = rules.get("cooldown_hours", 0)
            time_since_last = datetime.now() - last_message
            if time_since_last < timedelta(hours=cooldown_hours):
                remaining_hours = cooldown_hours - (time_since_last.total_seconds() / 3600)
                restrictions.append(f"Cooldown period active ({remaining_hours:.1f} hours remaining)")
        
        # Check specific message type restrictions
        if message_type == MessageType.EMAIL and not profile.can_send_email:
            restrictions.append("Email not available for this degree level")
        
        if message_type == MessageType.INMAIL:
            if profile.degree_level not in [DegreeLevel.SECOND, DegreeLevel.THIRD]:
                restrictions.append("InMail only available for 2nd/3rd degree connections")
            elif not profile.can_send_inmail:
                restrictions.append("InMail not available for this degree level")
        
        if message_type == MessageType.CONNECTION_REQUEST and not profile.can_send_connection:
            restrictions.append("Connection request not available for this degree level")
        
        can_send = len(restrictions) == 0
        
        return {
            "can_send": can_send,
            "reason": "All checks passed" if can_send else "; ".join(restrictions),
            "restrictions": restrictions,
            "profile_info": {
                "degree_level": profile.degree_level.value,
                "connection_status": profile.connection_status.value,
                "can_send_email": profile.can_send_email,
                "can_send_inmail": profile.can_send_inmail,
                "can_send_connection": profile.can_send_connection
            }
        }
    
    def send_message(
        self, 
        profile_url: str, 
        message_type: MessageType,
        message_data: Dict[str, Any],
        sequence_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message with LinkedIn compliance checks
        
        Args:
            profile_url: LinkedIn profile URL
            message_type: Type of message to send
            message_data: Message content and parameters
            sequence_id: Optional sequence ID for tracking
            
        Returns:
            Send result with status and details
        """
        # Check if message can be sent
        can_send_check = self.can_send_message(profile_url, message_type)
        
        if not can_send_check["can_send"]:
            return {
                "success": False,
                "error": can_send_check["reason"],
                "restrictions": can_send_check["restrictions"],
                "message_type": message_type.value
            }
        
        # Prepare message for Dux-Soup
        dux_message_data = self._prepare_dux_message(message_type, message_data)
        
        try:
            # Send message via Dux-Soup
            if message_type == MessageType.CONNECTION_REQUEST:
                result = self.dux_wrapper.connect_profile(
                    profile_url,
                    dux_message_data.get("message", ""),
                    **{k: v for k, v in dux_message_data.items() if k != "message"}
                )
            elif message_type == MessageType.EMAIL:
                # Email not directly supported by Dux-Soup API, use InMail instead
                result = self.dux_wrapper.send_inmail(
                    profile_url,
                    dux_message_data.get("subject", "Message from LinkedIn"),
                    dux_message_data.get("message", ""),
                    **{k: v for k, v in dux_message_data.items() if k not in ["message", "subject"]}
                )
            elif message_type == MessageType.INMAIL:
                result = self.dux_wrapper.send_inmail(
                    profile_url,
                    dux_message_data.get("subject", "Message from LinkedIn"),
                    dux_message_data.get("message", ""),
                    **{k: v for k, v in dux_message_data.items() if k not in ["message", "subject"]}
                )
            elif message_type == MessageType.FOLLOW_UP:
                result = self.dux_wrapper.send_message(
                    profile_url,
                    dux_message_data.get("message", ""),
                    **{k: v for k, v in dux_message_data.items() if k != "message"}
                )
            else:
                return {
                    "success": False,
                    "error": f"Unsupported message type: {message_type.value}"
                }
            
            # Record message status
            message_status = MessageStatus(
                profile_url=profile_url,
                sequence_id=sequence_id or "manual",
                step_number=0,
                message_type=message_type,
                status="sent" if result.get("success") else "failed",
                sent_at=datetime.now(),
                error_message=result.get("error"),
                linkedin_response=result
            )
            
            self.message_statuses.append(message_status)
            
            # Update profile message count
            if profile_url in self.profiles:
                self.profiles[profile_url].message_count += 1
                self.profiles[profile_url].last_message_sent = datetime.now()
            
            return {
                "success": result.get("success", False),
                "message_id": result.get("messageid"),
                "message_type": message_type.value,
                "sent_at": datetime.now().isoformat(),
                "linkedin_response": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception sending message: {str(e)}",
                "message_type": message_type.value
            }
    
    def create_connection_aware_sequence(
        self, 
        sequence_id: str,
        name: str,
        steps: List[Dict[str, Any]]
    ) -> MessageSequence:
        """
        Create a sequence that respects LinkedIn connection rules
        
        Args:
            sequence_id: Unique sequence identifier
            name: Sequence name
            steps: List of sequence steps
            
        Returns:
            Created message sequence
        """
        # Analyze steps to determine connection requirements
        connection_required = any(
            step.get("message_type") == MessageType.FOLLOW_UP.value
            for step in steps
        )
        
        email_enabled = any(
            step.get("message_type") == MessageType.EMAIL.value
            for step in steps
        )
        
        inmail_enabled = any(
            step.get("message_type") == MessageType.INMAIL.value
            for step in steps
        )
        
        sequence = MessageSequence(
            sequence_id=sequence_id,
            name=name,
            steps=steps,
            connection_required=connection_required,
            email_enabled=email_enabled,
            inmail_enabled=inmail_enabled
        )
        
        self.sequences[sequence_id] = sequence
        return sequence
    
    def execute_sequence(
        self, 
        sequence_id: str, 
        profile_urls: List[str]
    ) -> Dict[str, Any]:
        """
        Execute a sequence with LinkedIn compliance
        
        Args:
            sequence_id: Sequence to execute
            profile_urls: List of profile URLs to target
            
        Returns:
            Execution results
        """
        if sequence_id not in self.sequences:
            return {
                "success": False,
                "error": f"Sequence {sequence_id} not found"
            }
        
        sequence = self.sequences[sequence_id]
        results = {
            "sequence_id": sequence_id,
            "total_profiles": len(profile_urls),
            "profiles_processed": 0,
            "messages_sent": 0,
            "messages_blocked": 0,
            "connection_required": 0,
            "errors": []
        }
        
        for profile_url in profile_urls:
            if profile_url not in self.profiles:
                results["errors"].append(f"Profile {profile_url} not found")
                continue
            
            profile = self.profiles[profile_url]
            results["profiles_processed"] += 1
            
            # Check if sequence can be executed for this profile
            sequence_check = self._can_execute_sequence(sequence, profile)
            
            if not sequence_check["can_execute"]:
                if "connection required" in sequence_check["reason"].lower():
                    results["connection_required"] += 1
                else:
                    results["messages_blocked"] += 1
                results["errors"].append(f"{profile_url}: {sequence_check['reason']}")
                continue
            
            # Execute sequence steps
            for i, step in enumerate(sequence.steps):
                message_type = MessageType(step["message_type"])
                message_data = step.get("message_data", {})
                
                # Check if this step can be sent
                can_send = self.can_send_message(profile_url, message_type)
                
                if not can_send["can_send"]:
                    # Record blocked message
                    message_status = MessageStatus(
                        profile_url=profile_url,
                        sequence_id=sequence_id,
                        step_number=i + 1,
                        message_type=message_type,
                        status="blocked",
                        error_message=can_send["reason"]
                    )
                    self.message_statuses.append(message_status)
                    results["messages_blocked"] += 1
                    break
                
                # Send message
                send_result = self.send_message(
                    profile_url=profile_url,
                    message_type=message_type,
                    message_data=message_data,
                    sequence_id=sequence_id
                )
                
                if send_result["success"]:
                    results["messages_sent"] += 1
                else:
                    results["errors"].append(f"{profile_url} step {i+1}: {send_result['error']}")
                    break
                
                # Add delay between steps if specified
                if i < len(sequence.steps) - 1 and sequence.delay_between_messages > 0:
                    time.sleep(sequence.delay_between_messages * 3600)  # Convert hours to seconds
        
        return results
    
    def get_messaging_report(self) -> Dict[str, Any]:
        """Generate messaging report with LinkedIn compliance info"""
        total_profiles = len(self.profiles)
        connected_profiles = sum(
            1 for p in self.profiles.values() 
            if p.connection_status == ConnectionStatus.CONNECTED
        )
        pending_profiles = sum(
            1 for p in self.profiles.values() 
            if p.connection_status == ConnectionStatus.PENDING
        )
        
        total_messages = sum(p.message_count for p in self.profiles.values())
        
        # Message type breakdown
        message_type_counts = {}
        for status in self.message_statuses:
            msg_type = status.message_type.value
            message_type_counts[msg_type] = message_type_counts.get(msg_type, 0) + 1
        
        return {
            "total_profiles": total_profiles,
            "connection_stats": {
                "connected": connected_profiles,
                "pending": pending_profiles,
                "not_connected": total_profiles - connected_profiles - pending_profiles
            },
            "messaging_stats": {
                "total_messages_sent": total_messages,
                "message_type_breakdown": message_type_counts,
                "sequences_created": len(self.sequences)
            },
            "compliance_info": {
                "linkedin_rules_enforced": True,
                "connection_aware_messaging": True,
                "degree_restrictions": True,
                "daily_limits_tracked": True
            }
        }
    
    def _prepare_dux_message(
        self, 
        message_type: MessageType, 
        message_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare message data for Dux-Soup API"""
        if message_type == MessageType.CONNECTION_REQUEST:
            return {
                "message": message_data.get("message", ""),
                "note": message_data.get("note", "")
            }
        elif message_type == MessageType.EMAIL:
            return {
                "subject": message_data.get("subject", ""),
                "message": message_data.get("message", "")
            }
        else:
            return {
                "message": message_data.get("message", "")
            }
    
    def _can_execute_sequence(
        self, 
        sequence: MessageSequence, 
        profile: LinkedInProfile
    ) -> Dict[str, Any]:
        """Check if a sequence can be executed for a profile"""
        # For 1st degree connections, connection is not required for messaging
        # They can receive direct messages immediately
        if sequence.connection_required and profile.connection_status != ConnectionStatus.CONNECTED:
            # Exception: 1st degree connections don't need explicit connection acceptance
            if profile.degree_level != DegreeLevel.FIRST:
                return {
                    "can_execute": False,
                    "reason": "Connection required but not connected (2nd/3rd degree)"
                }
        
        if sequence.email_enabled and not profile.can_send_email:
            return {
                "can_execute": False,
                "reason": "Email messaging not available for this degree level"
            }
        
        if sequence.inmail_enabled and not profile.can_send_inmail:
            return {
                "can_execute": False,
                "reason": "InMail messaging not available for this degree level"
            }
        
        return {"can_execute": True, "reason": "All checks passed"}
    
    def _get_daily_message_count(
        self, 
        profile_url: str, 
        message_type: MessageType
    ) -> int:
        """Get count of messages sent today for a profile and message type"""
        today = datetime.now().date()
        count = 0
        
        for status in self.message_statuses:
            if (status.profile_url == profile_url and 
                status.message_type == message_type and
                status.sent_at and 
                status.sent_at.date() == today):
                count += 1
        
        return count
    
    def _get_last_message_time(
        self, 
        profile_url: str, 
        message_type: MessageType
    ) -> Optional[datetime]:
        """Get timestamp of last message sent to a profile"""
        last_message = None
        
        for status in self.message_statuses:
            if (status.profile_url == profile_url and 
                status.message_type == message_type and
                status.sent_at):
                if not last_message or status.sent_at > last_message:
                    last_message = status.sent_at
        
        return last_message 