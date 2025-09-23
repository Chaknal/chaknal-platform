"""
Campaign and Sequence Manager for Dux-Soup

This module provides functionality to create and manage campaigns and sequences
using the enhanced Dux-Soup wrapper.
"""

import json
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from .enhanced_duxwrap import EnhancedDuxWrap, DuxUser, DuxCommand


class SequenceStepType(Enum):
    """Types of sequence steps"""
    VISIT = "visit"
    CONNECT = "connect"
    MESSAGE = "message"
    INMAIL = "inmail"
    FOLLOW = "follow"
    ENDORSE = "endorse"
    TAG = "tag"
    SAVE_TO_PDF = "savetopdf"
    SAVE_AS_LEAD = "saveaslead"
    WAIT = "wait"


@dataclass
class SequenceStep:
    """A single step in a sequence"""
    step_type: SequenceStepType
    order: int
    params: Dict[str, Any]
    wait_days: int = 0
    campaign_id: Optional[str] = None
    force: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls"""
        return {
            "command": self.step_type.value,
            "params": self.params,
            "campaign_id": self.campaign_id,
            "force": self.force,
            "wait_days": self.wait_days
        }


@dataclass
class Campaign:
    """A Dux-Soup campaign"""
    id: str
    name: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class Sequence:
    """A sequence of LinkedIn actions"""
    id: str
    name: str
    steps: List[SequenceStep]
    description: Optional[str] = None
    created_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "steps": [step.to_dict() for step in self.steps],
            "created_at": self.created_at
        }


class CampaignManager:
    """
    Manages campaigns and sequences for Dux-Soup
    """
    
    def __init__(self, dux_wrapper: EnhancedDuxWrap):
        """
        Initialize the campaign manager
        
        Args:
            dux_wrapper: Enhanced Dux-Soup wrapper instance
        """
        self.dux_wrapper = dux_wrapper
        self.campaigns: Dict[str, Campaign] = {}
        self.sequences: Dict[str, Sequence] = {}
    
    def create_campaign(
        self, 
        name: str, 
        description: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> Campaign:
        """
        Create a new campaign
        
        Args:
            name: Campaign name
            description: Campaign description
            settings: Campaign settings
            
        Returns:
            Created campaign
        """
        campaign_id = f"campaign_{int(time.time())}"
        campaign = Campaign(
            id=campaign_id,
            name=name,
            description=description,
            created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            settings=settings or {}
        )
        
        self.campaigns[campaign_id] = campaign
        return campaign
    
    def create_sequence(
        self, 
        name: str, 
        description: Optional[str] = None
    ) -> Sequence:
        """
        Create a new sequence
        
        Args:
            name: Sequence name
            description: Sequence description
            
        Returns:
            Created sequence
        """
        sequence_id = f"sequence_{int(time.time())}"
        sequence = Sequence(
            id=sequence_id,
            name=name,
            description=description,
            steps=[],
            created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        
        self.sequences[sequence_id] = sequence
        return sequence
    
    def add_step_to_sequence(
        self, 
        sequence_id: str, 
        step_type: SequenceStepType,
        params: Dict[str, Any],
        wait_days: int = 0,
        campaign_id: Optional[str] = None,
        force: bool = False
    ) -> SequenceStep:
        """
        Add a step to a sequence
        
        Args:
            sequence_id: ID of the sequence
            step_type: Type of step to add
            params: Step parameters
            wait_days: Days to wait after this step
            campaign_id: Campaign ID to assign
            force: Force the action
            
        Returns:
            Created step
        """
        if sequence_id not in self.sequences:
            raise ValueError(f"Sequence {sequence_id} not found")
        
        sequence = self.sequences[sequence_id]
        step = SequenceStep(
            step_type=step_type,
            order=len(sequence.steps) + 1,
            params=params,
            wait_days=wait_days,
            campaign_id=campaign_id,
            force=force
        )
        
        sequence.steps.append(step)
        return step
    
    def execute_sequence_on_profile(
        self, 
        sequence_id: str, 
        profile_url: str,
        campaign_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a sequence on a single profile
        
        Args:
            sequence_id: ID of the sequence to execute
            profile_url: LinkedIn profile URL
            campaign_id: Campaign ID to assign (overrides sequence campaign_id)
            
        Returns:
            List of queued action results
        """
        if sequence_id not in self.sequences:
            raise ValueError(f"Sequence {sequence_id} not found")
        
        sequence = self.sequences[sequence_id]
        results = []
        
        for step in sequence.steps:
            # Prepare parameters with profile URL
            step_params = step.params.copy()
            if "profile" not in step_params:
                step_params["profile"] = profile_url
            
            # Use provided campaign_id or step's campaign_id
            step_campaign_id = campaign_id or step.campaign_id
            
            # Calculate run_after time if there's a wait
            run_after = None
            if step.wait_days > 0:
                import datetime
                run_after = (datetime.datetime.now() + 
                           datetime.timedelta(days=step.wait_days)).isoformat()
            
            try:
                result = self.dux_wrapper.queue_action(
                    command=step.step_type.value,
                    params=step_params,
                    campaign_id=step_campaign_id,
                    force=step.force,
                    run_after=run_after
                )
                results.append({
                    "step": step.order,
                    "type": step.step_type.value,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "step": step.order,
                    "type": step.step_type.value,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    def execute_sequence_on_profiles(
        self, 
        sequence_id: str, 
        profile_urls: List[str],
        campaign_id: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Execute a sequence on multiple profiles
        
        Args:
            sequence_id: ID of the sequence to execute
            profile_urls: List of LinkedIn profile URLs
            campaign_id: Campaign ID to assign
            
        Returns:
            Dictionary mapping profile URLs to results
        """
        results = {}
        
        for profile_url in profile_urls:
            try:
                profile_results = self.execute_sequence_on_profile(
                    sequence_id, profile_url, campaign_id
                )
                results[profile_url] = profile_results
            except Exception as e:
                results[profile_url] = [{"error": str(e)}]
        
        return results
    
    def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """Get a campaign by ID"""
        return self.campaigns.get(campaign_id)
    
    def get_sequence(self, sequence_id: str) -> Optional[Sequence]:
        """Get a sequence by ID"""
        return self.sequences.get(sequence_id)
    
    def list_campaigns(self) -> List[Campaign]:
        """List all campaigns"""
        return list(self.campaigns.values())
    
    def list_sequences(self) -> List[Sequence]:
        """List all sequences"""
        return list(self.sequences.values())
    
    def delete_campaign(self, campaign_id: str) -> bool:
        """Delete a campaign"""
        if campaign_id in self.campaigns:
            del self.campaigns[campaign_id]
            return True
        return False
    
    def delete_sequence(self, sequence_id: str) -> bool:
        """Delete a sequence"""
        if sequence_id in self.sequences:
            del self.sequences[sequence_id]
            return True
        return False
    
    def save_campaigns_to_file(self, filename: str) -> None:
        """Save campaigns to JSON file"""
        data = {
            "campaigns": [campaign.to_dict() for campaign in self.campaigns.values()],
            "sequences": [sequence.to_dict() for sequence in self.sequences.values()]
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_campaigns_from_file(self, filename: str) -> None:
        """Load campaigns from JSON file"""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Load campaigns
        for campaign_data in data.get("campaigns", []):
            campaign = Campaign(**campaign_data)
            self.campaigns[campaign.id] = campaign
        
        # Load sequences
        for sequence_data in data.get("sequences", []):
            steps = []
            for step_data in sequence_data.get("steps", []):
                step = SequenceStep(
                    step_type=SequenceStepType(step_data["command"]),
                    order=step_data.get("order", 0),
                    params=step_data.get("params", {}),
                    wait_days=step_data.get("wait_days", 0),
                    campaign_id=step_data.get("campaign_id"),
                    force=step_data.get("force", False)
                )
                steps.append(step)
            
            sequence = Sequence(
                id=sequence_data["id"],
                name=sequence_data["name"],
                description=sequence_data.get("description"),
                steps=steps,
                created_at=sequence_data.get("created_at")
            )
            self.sequences[sequence.id] = sequence


# Pre-built sequence templates
class SequenceTemplates:
    """Pre-built sequence templates"""
    
    @staticmethod
    def connection_sequence(manager: CampaignManager, name: str = "Connection Sequence") -> str:
        """Create a basic connection sequence"""
        sequence = manager.create_sequence(name, "Basic connection sequence")
        
        # Step 1: Visit profile
        manager.add_step_to_sequence(
            sequence.id,
            SequenceStepType.VISIT,
            {},
            wait_days=0
        )
        
        # Step 2: Send connection request (wait 2 days)
        manager.add_step_to_sequence(
            sequence.id,
            SequenceStepType.CONNECT,
            {"messagetext": "Hi _FN_, I'd love to connect and learn more about your work!"},
            wait_days=2
        )
        
        # Step 3: Follow up message (wait 5 days)
        manager.add_step_to_sequence(
            sequence.id,
            SequenceStepType.MESSAGE,
            {"messagetext": "Hi _FN_, thanks for connecting! I'd love to learn more about your experience at _COMPANY_. Would you be open to a quick chat?"},
            wait_days=5
        )
        
        return sequence.id
    
    @staticmethod
    def endorsement_sequence(manager: CampaignManager, name: str = "Endorsement Sequence") -> str:
        """Create an endorsement sequence"""
        sequence = manager.create_sequence(name, "Endorsement sequence")
        
        # Step 1: Visit profile
        manager.add_step_to_sequence(
            sequence.id,
            SequenceStepType.VISIT,
            {},
            wait_days=0
        )
        
        # Step 2: Endorse top 3 skills
        manager.add_step_to_sequence(
            sequence.id,
            SequenceStepType.ENDORSE,
            {"count": 3},
            wait_days=1
        )
        
        # Step 3: Send thank you message
        manager.add_step_to_sequence(
            sequence.id,
            SequenceStepType.MESSAGE,
            {"messagetext": "Hi _FN_, I just endorsed some of your skills! Your profile is impressive."},
            wait_days=2
        )
        
        return sequence.id
    
    @staticmethod
    def lead_generation_sequence(manager: CampaignManager, name: str = "Lead Generation Sequence") -> str:
        """Create a lead generation sequence"""
        sequence = manager.create_sequence(name, "Lead generation sequence")
        
        # Step 1: Visit and save as lead
        manager.add_step_to_sequence(
            sequence.id,
            SequenceStepType.VISIT,
            {},
            wait_days=0
        )
        
        manager.add_step_to_sequence(
            sequence.id,
            SequenceStepType.SAVE_AS_LEAD,
            {},
            wait_days=0
        )
        
        # Step 2: Send connection request
        manager.add_step_to_sequence(
            sequence.id,
            SequenceStepType.CONNECT,
            {"messagetext": "Hi _FN_, I noticed your work at _COMPANY_ and would love to connect!"},
            wait_days=1
        )
        
        # Step 3: Follow up with value proposition
        manager.add_step_to_sequence(
            sequence.id,
            SequenceStepType.MESSAGE,
            {"messagetext": "Hi _FN_, thanks for connecting! I'd love to share some insights about _INDUSTRY_ that might be valuable for your team."},
            wait_days=3
        )
        
        return sequence.id 