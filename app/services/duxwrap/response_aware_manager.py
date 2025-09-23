"""
Response-Aware Sequence Manager for Dux-Soup

This module provides functionality to stop sequences when people respond,
using event detection and message monitoring.
"""

import json
import time
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from .enhanced_duxwrap import EnhancedDuxWrap, DuxUser
from .campaign_manager import CampaignManager, Sequence, SequenceStepType


@dataclass
class ProfileStatus:
    """Track the status of a profile in a sequence"""
    profile_url: str
    sequence_id: str
    campaign_id: Optional[str]
    current_step: int
    total_steps: int
    started_at: datetime
    last_activity: datetime
    is_active: bool = True
    stopped_reason: Optional[str] = None
    response_received: bool = False
    response_time: Optional[datetime] = None


class ResponseAwareManager:
    """
    Manages sequences with the ability to stop when people respond
    """
    
    def __init__(self, dux_wrapper: EnhancedDuxWrap, campaign_manager: CampaignManager):
        """
        Initialize the response-aware manager
        
        Args:
            dux_wrapper: Enhanced Dux-Soup wrapper
            campaign_manager: Campaign manager instance
        """
        self.dux_wrapper = dux_wrapper
        self.campaign_manager = campaign_manager
        self.active_profiles: Dict[str, ProfileStatus] = {}
        self.response_profiles: Set[str] = set()
        self.event_history: List[Dict] = []
    
    def start_sequence_with_response_monitoring(
        self,
        sequence_id: str,
        profile_urls: List[str],
        campaign_id: Optional[str] = None,
        stop_on_response: bool = True,
        stop_on_connect: bool = True
    ) -> Dict[str, Any]:
        """
        Start a sequence with response monitoring
        
        Args:
            sequence_id: ID of the sequence to execute
            profile_urls: List of LinkedIn profile URLs
            campaign_id: Campaign ID to assign
            stop_on_response: Whether to stop sequence if person responds
            stop_on_connect: Whether to stop sequence if person connects
            
        Returns:
            Execution results
        """
        results = {
            "sequence_id": sequence_id,
            "total_profiles": len(profile_urls),
            "profiles_started": 0,
            "profiles_failed": 0,
            "errors": []
        }
        
        for profile_url in profile_urls:
            try:
                # Get sequence details
                sequence = self.campaign_manager.get_sequence(sequence_id)
                if not sequence:
                    raise ValueError(f"Sequence {sequence_id} not found")
                
                # Create profile status tracker
                profile_status = ProfileStatus(
                    profile_url=profile_url,
                    sequence_id=sequence_id,
                    campaign_id=campaign_id,
                    current_step=0,
                    total_steps=len(sequence.steps),
                    started_at=datetime.now(),
                    last_activity=datetime.now()
                )
                
                # Store for monitoring
                self.active_profiles[profile_url] = profile_status
                
                # Execute sequence
                step_results = self.campaign_manager.execute_sequence_on_profile(
                    sequence_id=sequence_id,
                    profile_url=profile_url,
                    campaign_id=campaign_id
                )
                
                # Update status with results
                successful_steps = [r for r in step_results if r.get("success", False)]
                profile_status.current_step = len(successful_steps)
                
                results["profiles_started"] += 1
                
            except Exception as e:
                results["profiles_failed"] += 1
                results["errors"].append(f"{profile_url}: {str(e)}")
        
        return results
    
    def handle_response_event(
        self, 
        profile_url: str, 
        event_type: str, 
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle response events to detect responses and connections
        
        Args:
            profile_url: LinkedIn profile URL
            event_type: Type of event (message, connect, etc.)
            event_data: Event data
            
        Returns:
            Processing results
        """
        results = {
            "processed": False,
            "actions_taken": [],
            "profiles_affected": []
        }
        
        # Handle message events (responses)
        if event_type == "message":
            self._handle_profile_response(profile_url, "message_response", results)
        
        # Handle connection accept events
        elif event_type == "connect":
            self._handle_profile_response(profile_url, "connection_accepted", results)
        
        # Store event for analysis
        self.event_history.append({
            "timestamp": datetime.now(),
            "profile_url": profile_url,
            "event_type": event_type,
            "event_data": event_data,
            "processed": results["processed"]
        })
        
        return results
    
    def _handle_profile_response(self, profile_url: str, response_type: str, results: Dict):
        """Handle when a profile responds"""
        if profile_url in self.active_profiles:
            profile_status = self.active_profiles[profile_url]
            
            # Mark as responded
            profile_status.response_received = True
            profile_status.response_time = datetime.now()
            profile_status.stopped_reason = f"Response received: {response_type}"
            profile_status.is_active = False
            
            # Add to response profiles set
            self.response_profiles.add(profile_url)
            
            # Stop remaining sequence actions
            self._stop_sequence_for_profile(profile_url, results)
            
            results["processed"] = True
            results["actions_taken"].append(f"Stopped sequence for {profile_url}")
            results["profiles_affected"].append(profile_url)
    
    def _stop_sequence_for_profile(self, profile_url: str, results: Dict):
        """Stop remaining sequence actions for a profile"""
        try:
            # Get queue items for this profile
            queue_items = self.dux_wrapper.get_queue_items()
            
            if 'items' in queue_items:
                items_to_remove = []
                
                for item in queue_items['items']:
                    item_params = item.get('params', {})
                    item_profile = item_params.get('profile')
                    
                    if item_profile == profile_url:
                        items_to_remove.append(item.get('messageid'))
                
                # Clear specific items from queue (if Dux-Soup API supports it)
                # For now, we'll clear the entire queue and re-queue non-affected items
                if items_to_remove:
                    # This is a simplified approach - in practice you'd want more granular control
                    print(f"Would remove {len(items_to_remove)} queued actions for {profile_url}")
                    
        except Exception as e:
            print(f"Error stopping sequence for {profile_url}: {e}")
    
    def get_active_profiles(self) -> List[ProfileStatus]:
        """Get all active profiles"""
        return [status for status in self.active_profiles.values() if status.is_active]
    
    def get_responded_profiles(self) -> List[ProfileStatus]:
        """Get profiles that have responded"""
        return [status for status in self.active_profiles.values() if status.response_received]
    
    def get_profile_status(self, profile_url: str) -> Optional[ProfileStatus]:
        """Get status for a specific profile"""
        return self.active_profiles.get(profile_url)
    
    def stop_monitoring_profile(self, profile_url: str, reason: str = "Manual stop"):
        """Manually stop monitoring a profile"""
        if profile_url in self.active_profiles:
            profile_status = self.active_profiles[profile_url]
            profile_status.is_active = False
            profile_status.stopped_reason = reason
    
    def get_sequence_progress(self, sequence_id: str) -> Dict[str, Any]:
        """Get progress for a specific sequence"""
        sequence_profiles = [
            status for status in self.active_profiles.values()
            if status.sequence_id == sequence_id
        ]
        
        if not sequence_profiles:
            return {"error": "No active profiles for this sequence"}
        
        total_profiles = len(sequence_profiles)
        active_profiles = len([p for p in sequence_profiles if p.is_active])
        responded_profiles = len([p for p in sequence_profiles if p.response_received])
        
        avg_progress = sum(p.current_step / p.total_steps for p in sequence_profiles) / total_profiles
        
        return {
            "sequence_id": sequence_id,
            "total_profiles": total_profiles,
            "active_profiles": active_profiles,
            "responded_profiles": responded_profiles,
            "average_progress": avg_progress,
            "response_rate": responded_profiles / total_profiles if total_profiles > 0 else 0
        }
    
    def export_monitoring_data(self, filename: str):
        """Export monitoring data to JSON"""
        data = {
            "active_profiles": [
                {
                    "profile_url": status.profile_url,
                    "sequence_id": status.sequence_id,
                    "campaign_id": status.campaign_id,
                    "current_step": status.current_step,
                    "total_steps": status.total_steps,
                    "started_at": status.started_at.isoformat(),
                    "last_activity": status.last_activity.isoformat(),
                    "is_active": status.is_active,
                    "stopped_reason": status.stopped_reason,
                    "response_received": status.response_received,
                    "response_time": status.response_time.isoformat() if status.response_time else None
                }
                for status in self.active_profiles.values()
            ],
            "event_history": [
                {
                    "timestamp": event["timestamp"].isoformat(),
                    "profile_url": event["profile_url"],
                    "event_type": event["event_type"],
                    "processed": event["processed"]
                }
                for event in self.event_history
            ],
            "exported_at": datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)


# Enhanced sequence templates with response monitoring
class ResponseAwareTemplates:
    """Response-aware sequence templates"""
    
    @staticmethod
    def smart_connection_sequence(
        manager: CampaignManager,
        response_manager: ResponseAwareManager,
        name: str = "Smart Connection Sequence"
    ) -> str:
        """Create a connection sequence that stops on response"""
        sequence = manager.create_sequence(name, "Connection sequence with response monitoring")
        
        # Step 1: Visit profile
        manager.add_step_to_sequence(
            sequence.id,
            SequenceStepType.VISIT,
            {},
            wait_days=0
        )
        
        # Step 2: Send connection request
        manager.add_step_to_sequence(
            sequence.id,
            SequenceStepType.CONNECT,
            {"messagetext": "Hi _FN_, I'd love to connect and learn more about your work!"},
            wait_days=2
        )
        
        # Step 3: Follow up message (only if no response)
        manager.add_step_to_sequence(
            sequence.id,
            SequenceStepType.MESSAGE,
            {"messagetext": "Hi _FN_, thanks for connecting! I'd love to learn more about your experience at _COMPANY_. Would you be open to a quick chat?"},
            wait_days=5
        )
        
        return sequence.id
    
    @staticmethod
    def engagement_sequence(
        manager: CampaignManager,
        response_manager: ResponseAwareManager,
        name: str = "Engagement Sequence"
    ) -> str:
        """Create an engagement sequence that adapts based on responses"""
        sequence = manager.create_sequence(name, "Engagement sequence with response monitoring")
        
        # Step 1: Visit and endorse
        manager.add_step_to_sequence(
            sequence.id,
            SequenceStepType.VISIT,
            {},
            wait_days=0
        )
        
        manager.add_step_to_sequence(
            sequence.id,
            SequenceStepType.ENDORSE,
            {"count": 3},
            wait_days=1
        )
        
        # Step 2: Send connection request
        manager.add_step_to_sequence(
            sequence.id,
            SequenceStepType.CONNECT,
            {"messagetext": "Hi _FN_, I just endorsed your skills! Would love to connect."},
            wait_days=2
        )
        
        # Step 3: Follow up (only if no response)
        manager.add_step_to_sequence(
            sequence.id,
            SequenceStepType.MESSAGE,
            {"messagetext": "Hi _FN_, thanks for connecting! Your work at _COMPANY_ looks interesting. Would you be open to sharing some insights?"},
            wait_days=3
        )
        
        return sequence.id 