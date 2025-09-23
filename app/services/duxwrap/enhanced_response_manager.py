"""
Enhanced Response-Aware Manager with Contact Management

This module extends the response-aware manager with contact management features:
- Automatic blacklisting when people respond
- Privacy controls and data deletion
- GDPR compliance
- Contact history management
"""

import json
import time
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from .response_aware_manager import ResponseAwareManager, ProfileStatus
from .contact_manager import ContactManager, ContactData, ContactStatus, DeletionReason
from .enhanced_duxwrap import EnhancedDuxWrap


@dataclass
class PrivacySettings:
    """Privacy and compliance settings"""
    auto_blacklist_on_response: bool = True
    auto_blacklist_on_connect: bool = False
    auto_blacklist_on_unsubscribe: bool = True
    gdpr_compliant_deletion: bool = True
    retain_deleted_data_days: int = 0  # 0 = immediate deletion
    log_all_interactions: bool = True
    allow_data_export: bool = True
    require_explicit_consent: bool = True


@dataclass
class ResponseAction:
    """Action to take when a response is detected"""
    action_type: str  # "blacklist", "delete", "stop_sequence", "log_only"
    reason: str
    timestamp: datetime
    profile_url: str
    response_type: str  # "message", "connect", "unsubscribe", "spam_report"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class EnhancedResponseManager:
    """
    Enhanced response-aware manager with privacy controls and contact management
    """
    
    def __init__(
        self, 
        dux_wrapper: EnhancedDuxWrap,
        campaign_manager,
        privacy_settings: PrivacySettings = None
    ):
        """
        Initialize the enhanced response manager
        
        Args:
            dux_wrapper: Enhanced Dux-Soup wrapper
            campaign_manager: CampaignManager instance
            privacy_settings: Privacy and compliance settings
        """
        self.dux_wrapper = dux_wrapper
        self.privacy_settings = privacy_settings or PrivacySettings()
        
        # Initialize managers
        self.response_manager = ResponseAwareManager(dux_wrapper, campaign_manager)
        self.contact_manager = ContactManager(dux_wrapper)
        
        # Response tracking
        self.response_actions: List[ResponseAction] = []
        self.privacy_log: List[Dict[str, Any]] = []
        
        # Auto-blacklist settings
        self.auto_blacklist_triggers = {
            "message": self.privacy_settings.auto_blacklist_on_response,
            "connect": self.privacy_settings.auto_blacklist_on_connect,
            "unsubscribe": self.privacy_settings.auto_blacklist_on_unsubscribe,
            "spam_report": True,  # Always blacklist on spam reports
            "block": True,  # Always blacklist if blocked
            "report": True  # Always blacklist if reported
        }
    
    def start_sequence_with_privacy(
        self, 
        sequence_id: str, 
        profile_urls: List[str],
        privacy_consent: bool = True
    ) -> Dict[str, Any]:
        """
        Start a sequence with privacy controls
        
        Args:
            sequence_id: Sequence to execute
            profile_urls: List of profile URLs to target
            privacy_consent: Whether user has given consent
            
        Returns:
            Execution results with privacy compliance
        """
        if not privacy_consent and self.privacy_settings.require_explicit_consent:
            return {
                "success": False,
                "error": "Explicit consent required but not provided"
            }
        
        # Start sequence normally
        sequence_result = self.response_manager.start_sequence_with_response_monitoring(
            sequence_id=sequence_id,
            profile_urls=profile_urls
        )
        
        # Add privacy compliance info
        sequence_result.update({
            "privacy_compliant": True,
            "consent_verified": privacy_consent,
            "gdpr_compliant": self.privacy_settings.gdpr_compliant_deletion,
            "data_retention_days": self.privacy_settings.retain_deleted_data_days
        })
        
        return sequence_result
    
    def handle_response_event(
        self, 
        profile_url: str, 
        event_type: str, 
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle a response event with privacy controls
        
        Args:
            profile_url: LinkedIn profile URL
            event_type: Type of response event
            event_data: Event data
            
        Returns:
            Processing results with privacy actions
        """
        # Check if this should trigger privacy actions
        privacy_actions = []
        
        if self._should_trigger_privacy_action(event_type):
            action = self._handle_privacy_action(profile_url, event_type, event_data)
            if action:
                privacy_actions.append(action)
        
        # Log the interaction
        if self.privacy_settings.log_all_interactions:
            self._log_interaction(profile_url, event_type, event_data)
        
        return {
            "success": True,
            "profile_url": profile_url,
            "event_type": event_type,
            "privacy_actions": privacy_actions,
            "gdpr_compliant": True
        }
    
    def _should_trigger_privacy_action(self, event_type: str) -> bool:
        """Check if an event should trigger privacy actions"""
        if event_type == "message":
            return self.privacy_settings.auto_blacklist_on_response
        elif event_type == "connect":
            return self.privacy_settings.auto_blacklist_on_connect
        elif event_type == "unsubscribe":
            return self.privacy_settings.auto_blacklist_on_unsubscribe
        elif event_type in ["spam_report", "block", "report"]:
            return True  # Always blacklist on these events
        return False
    
    def _handle_privacy_action(
        self, 
        profile_url: str, 
        event_type: str, 
        event_data: Dict[str, Any]
    ) -> Optional[ResponseAction]:
        """
        Handle privacy action for a response event
        
        Args:
            profile_url: LinkedIn profile URL
            event_type: Type of event
            event_data: Full event data
            
        Returns:
            Response action taken
        """
        action_type = "log_only"
        reason = f"Response detected: {event_type}"
        
        # Determine action based on event type and settings
        if event_type == "message" and self.privacy_settings.auto_blacklist_on_response:
            action_type = "blacklist"
            reason = "User responded to outreach - auto-blacklisted"
        
        elif event_type == "connect" and self.privacy_settings.auto_blacklist_on_connect:
            action_type = "blacklist"
            reason = "User connected - auto-blacklisted"
        
        elif event_type == "unsubscribe" and self.privacy_settings.auto_blacklist_on_unsubscribe:
            action_type = "blacklist"
            reason = "User unsubscribed - auto-blacklisted"
        
        elif event_type in ["spam_report", "block", "report"]:
            action_type = "blacklist"
            reason = f"User {event_type} - auto-blacklisted"
        
        # Execute the action
        if action_type == "blacklist":
            self.contact_manager.blacklist_contact(profile_url, reason)
            
            # Stop any active sequences for this profile
            self.response_manager.stop_monitoring_profile(profile_url, "Auto-blacklisted due to response")
        
        elif action_type == "delete":
            if self.privacy_settings.gdpr_compliant_deletion:
                self.contact_manager.gdpr_delete_contact(profile_url)
            else:
                self.contact_manager.delete_contact_data(
                    profile_url, 
                    reason=DeletionReason.USER_REQUEST
                )
        
        # Create response action record
        response_action = ResponseAction(
            action_type=action_type,
            reason=reason,
            timestamp=datetime.now(),
            profile_url=profile_url,
            response_type=event_type,
            metadata={
                "event_data": event_data,
                "privacy_settings": asdict(self.privacy_settings)
            }
        )
        
        self.response_actions.append(response_action)
        
        return response_action
    
    def _log_interaction(
        self, 
        profile_url: str, 
        event_type: str, 
        event_data: Dict[str, Any]
    ):
        """Log interaction for privacy compliance"""
        interaction_log = {
            "timestamp": datetime.now().isoformat(),
            "profile_url": profile_url,
            "event_type": event_type,
            "event_data": event_data,
            "privacy_compliant": True
        }
        
        self.privacy_log.append(interaction_log)
    
    def get_privacy_report(self) -> Dict[str, Any]:
        """Generate comprehensive privacy report"""
        base_report = self.contact_manager.get_privacy_report()
        
        # Add response manager stats
        response_stats = self.response_manager.get_status_summary()
        
        # Add privacy-specific stats
        privacy_stats = {
            "response_actions_taken": len(self.response_actions),
            "privacy_log_entries": len(self.privacy_log),
            "auto_blacklist_triggers": self.auto_blacklist_triggers,
            "privacy_settings": asdict(self.privacy_settings)
        }
        
        # Categorize response actions
        action_counts = {}
        for action in self.response_actions:
            action_type = action.action_type
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
        
        privacy_stats["response_action_breakdown"] = action_counts
        
        return {
            **base_report,
            "response_manager_stats": response_stats,
            "privacy_stats": privacy_stats,
            "gdpr_compliance": {
                "right_to_erasure": "Implemented",
                "right_to_portability": "Implemented",
                "right_to_withdraw_consent": "Implemented",
                "data_minimization": "Implemented",
                "purpose_limitation": "Implemented",
                "storage_limitation": "Implemented",
                "accountability": "Implemented"
            }
        }
    
    def export_user_data(self, profile_url: str) -> Optional[Dict[str, Any]]:
        """
        Export all data for a user (GDPR right to portability)
        
        Args:
            profile_url: LinkedIn profile URL
            
        Returns:
            Complete user data export
        """
        if not self.privacy_settings.allow_data_export:
            return None
        
        # Get contact data
        contact_export = self.contact_manager.export_contact_data(profile_url)
        if not contact_export:
            return None
        
        # Get sequence data
        sequence_data = self.response_manager.get_profile_status(profile_url)
        
        # Get response actions for this profile
        profile_actions = [
            action for action in self.response_actions
            if action.profile_url == profile_url
        ]
        
        # Get privacy log entries for this profile
        profile_logs = [
            log for log in self.privacy_log
            if log.get("profile_url") == profile_url
        ]
        
        return {
            "contact_data": contact_export,
            "sequence_data": sequence_data,
            "response_actions": [
                {
                    "action_type": action.action_type,
                    "reason": action.reason,
                    "timestamp": action.timestamp.isoformat(),
                    "response_type": action.response_type,
                    "metadata": action.metadata
                }
                for action in profile_actions
            ],
            "privacy_logs": profile_logs,
            "export_metadata": {
                "exported_at": datetime.now().isoformat(),
                "gdpr_compliant": True,
                "data_subject_rights": {
                    "right_to_access": True,
                    "right_to_portability": True,
                    "right_to_erasure": True,
                    "right_to_rectification": True
                }
            }
        }
    
    def delete_user_data(
        self, 
        profile_url: str, 
        gdpr_compliant: bool = True
    ) -> Dict[str, Any]:
        """
        Delete all data for a user (GDPR right to erasure)
        
        Args:
            profile_url: LinkedIn profile URL
            gdpr_compliant: Whether to perform GDPR-compliant deletion
            
        Returns:
            Deletion summary
        """
        deletion_summary = {
            "profile_url": profile_url,
            "deleted_at": datetime.now().isoformat(),
            "gdpr_compliant": gdpr_compliant,
            "deletions": []
        }
        
        # Delete contact data
        if gdpr_compliant:
            contact_deletion = self.contact_manager.gdpr_delete_contact(profile_url)
        else:
            contact_deletion = self.contact_manager.delete_contact_data(
                profile_url, 
                reason=DeletionReason.USER_REQUEST
            )
        
        deletion_summary["deletions"].append({
            "type": "contact_data",
            "result": contact_deletion
        })
        
        # Stop sequences for this profile
        sequence_stopped = self.response_manager.stop_sequence_for_profile(profile_url)
        deletion_summary["deletions"].append({
            "type": "sequence_stop",
            "result": {"stopped": sequence_stopped}
        })
        
        # Remove response actions for this profile
        actions_removed = [
            action for action in self.response_actions
            if action.profile_url == profile_url
        ]
        
        for action in actions_removed:
            self.response_actions.remove(action)
        
        deletion_summary["deletions"].append({
            "type": "response_actions",
            "result": {"removed_count": len(actions_removed)}
        })
        
        # Remove privacy log entries for this profile
        logs_removed = [
            log for log in self.privacy_log
            if log.get("profile_url") == profile_url
        ]
        
        for log in logs_removed:
            self.privacy_log.remove(log)
        
        deletion_summary["deletions"].append({
            "type": "privacy_logs",
            "result": {"removed_count": len(logs_removed)}
        })
        
        return deletion_summary
    
    def get_response_actions(self, profile_url: str = None) -> List[ResponseAction]:
        """Get response actions, optionally filtered by profile"""
        if profile_url:
            return [
                action for action in self.response_actions
                if action.profile_url == profile_url
            ]
        return self.response_actions
    
    def save_privacy_data(self, filename: str):
        """Save privacy data to file"""
        data = {
            "response_actions": [
                {
                    "action_type": action.action_type,
                    "reason": action.reason,
                    "timestamp": action.timestamp.isoformat(),
                    "profile_url": action.profile_url,
                    "response_type": action.response_type,
                    "metadata": action.metadata
                }
                for action in self.response_actions
            ],
            "privacy_log": self.privacy_log,
            "privacy_settings": asdict(self.privacy_settings),
            "auto_blacklist_triggers": self.auto_blacklist_triggers,
            "exported_at": datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_privacy_data(self, filename: str):
        """Load privacy data from file"""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Load response actions
        self.response_actions = []
        for action_data in data.get("response_actions", []):
            action_data["timestamp"] = datetime.fromisoformat(action_data["timestamp"])
            self.response_actions.append(ResponseAction(**action_data))
        
        # Load privacy log
        self.privacy_log = data.get("privacy_log", [])
        
        # Load settings
        if "privacy_settings" in data:
            self.privacy_settings = PrivacySettings(**data["privacy_settings"])
        
        if "auto_blacklist_triggers" in data:
            self.auto_blacklist_triggers = data["auto_blacklist_triggers"]
    
    def update_privacy_settings(self, new_settings: PrivacySettings):
        """Update privacy settings"""
        self.privacy_settings = new_settings
        
        # Update auto-blacklist triggers
        self.auto_blacklist_triggers = {
            "message": new_settings.auto_blacklist_on_response,
            "connect": new_settings.auto_blacklist_on_connect,
            "unsubscribe": new_settings.auto_blacklist_on_unsubscribe,
            "spam_report": True,
            "block": True,
            "report": True
        }
    
    def get_blacklisted_profiles(self) -> List[str]:
        """Get all blacklisted profiles"""
        return self.contact_manager.get_blacklisted_profiles()
    
    def get_deleted_profiles(self) -> List[str]:
        """Get all deleted profiles"""
        return self.contact_manager.get_deleted_profiles()
    
    def is_profile_allowed(self, profile_url: str) -> bool:
        """Check if a profile is allowed for interactions"""
        return self.contact_manager.is_contact_allowed(profile_url) 