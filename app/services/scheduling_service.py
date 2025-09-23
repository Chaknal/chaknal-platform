"""
Advanced scheduling service for LinkedIn automation with DuxSoup integration.

This service handles complex scheduling scenarios including:
- DuxSoup operational hours and delays
- LinkedIn rate limits and best practices
- Timezone alignment across different regions
- Campaign sequence timing optimization
- Retry logic with exponential backoff
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum
import asyncio
import json
from dataclasses import dataclass
from app.utils.timestamps import utc_now, to_iso_string
from app.utils.transaction_tracker import TransactionType, get_transaction_tracker


class ScheduleStatus(Enum):
    """Status of scheduled operations."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class OperationType(Enum):
    """Types of operations that can be scheduled."""
    PROFILE_VIEW = "profile_view"
    CONNECTION_REQUEST = "connection_request"
    MESSAGE_SEND = "message_send"
    FOLLOW_UP = "follow_up"
    INMAIL_SEND = "inmail_send"
    PROFILE_SCRAPE = "profile_scrape"
    SEARCH_EXECUTION = "search_execution"


@dataclass
class DuxSoupAccount:
    """DuxSoup account configuration and status."""
    account_id: str
    username: str
    timezone: str
    operational_hours: Dict[str, Any]  # {"start": "09:00", "end": "17:00", "days": [1,2,3,4,5]}
    daily_limits: Dict[str, int]  # {"connections": 50, "messages": 30, "profile_views": 100}
    current_usage: Dict[str, int]  # Current day's usage
    last_activity: Optional[datetime] = None
    is_active: bool = True
    delay_patterns: Dict[str, int] = None  # {"min_delay": 30, "max_delay": 120, "random_factor": 0.2}


@dataclass
class ScheduleRequest:
    """Request to schedule an operation."""
    operation_type: OperationType
    contact_id: str
    campaign_id: str
    user_id: str
    dux_account_id: str
    priority: int = 1  # 1=highest, 5=lowest
    preferred_time: Optional[datetime] = None
    max_delay_hours: int = 48
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = None


@dataclass
class ScheduledOperation:
    """A scheduled operation with timing details."""
    operation_id: str
    request: ScheduleRequest
    scheduled_time: datetime
    status: ScheduleStatus
    dux_account: DuxSoupAccount
    estimated_duration: int  # seconds
    retry_after: Optional[datetime] = None
    failure_reason: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None


class SchedulingService:
    """Service for managing LinkedIn automation scheduling."""
    
    def __init__(self):
        self.tracker = get_transaction_tracker()
        self.dux_accounts: Dict[str, DuxSoupAccount] = {}
        self.scheduled_operations: Dict[str, ScheduledOperation] = {}
        self.timezone_offsets = {
            'EST': -5, 'EDT': -4, 'CST': -6, 'CDT': -5,
            'MST': -7, 'MDT': -6, 'PST': -8, 'PDT': -7,
            'UTC': 0, 'GMT': 0
        }
    
    def register_dux_account(self, account: DuxSoupAccount):
        """Register a DuxSoup account for scheduling."""
        self.dux_accounts[account.account_id] = account
        self.tracker.log_duxsoup_activity(
            activity_type="account_added",
            dux_user_id=account.username,
            description=f"Registered DuxSoup account: {account.username}",
            metadata={
                "timezone": account.timezone,
                "operational_hours": account.operational_hours,
                "daily_limits": account.daily_limits
            }
        )
    
    def calculate_optimal_schedule_time(
        self,
        request: ScheduleRequest,
        dux_account: DuxSoupAccount
    ) -> datetime:
        """Calculate the optimal time to schedule an operation."""
        
        # Start with preferred time or current time
        base_time = request.preferred_time or utc_now()
        
        # Convert to account timezone
        account_time = self._convert_to_account_timezone(base_time, dux_account.timezone)
        
        # Check if within operational hours
        if not self._is_within_operational_hours(account_time, dux_account):
            # Move to next operational window
            account_time = self._get_next_operational_window(account_time, dux_account)
        
        # Apply delay patterns
        delay_minutes = self._calculate_delay(dux_account, request.operation_type)
        account_time += timedelta(minutes=delay_minutes)
        
        # Check daily limits
        if not self._check_daily_limits(account_time, dux_account, request.operation_type):
            # Move to next day
            account_time = self._get_next_available_slot(account_time, dux_account, request.operation_type)
        
        # Convert back to UTC
        return self._convert_to_utc(account_time, dux_account.timezone)
    
    def _convert_to_account_timezone(self, utc_time: datetime, timezone_str: str) -> datetime:
        """Convert UTC time to account timezone."""
        # Simple timezone conversion (in production, use pytz or zoneinfo)
        if timezone_str in self.timezone_offsets:
            offset_hours = self.timezone_offsets[timezone_str]
            return utc_time + timedelta(hours=offset_hours)
        return utc_time  # Default to UTC if timezone not recognized
    
    def _convert_to_utc(self, local_time: datetime, timezone_str: str) -> datetime:
        """Convert local time to UTC."""
        if timezone_str in self.timezone_offsets:
            offset_hours = self.timezone_offsets[timezone_str]
            return local_time - timedelta(hours=offset_hours)
        return local_time
    
    def _is_within_operational_hours(self, local_time: datetime, account: DuxSoupAccount) -> bool:
        """Check if time is within operational hours."""
        if not account.operational_hours:
            return True
        
        current_hour = local_time.hour
        current_day = local_time.weekday()  # 0=Monday, 6=Sunday
        
        # Check if current day is operational
        operational_days = account.operational_hours.get('days', [1, 2, 3, 4, 5])  # Default weekdays
        if current_day not in operational_days:
            return False
        
        # Check if within time range
        start_hour = int(account.operational_hours.get('start', '09:00').split(':')[0])
        end_hour = int(account.operational_hours.get('end', '17:00').split(':')[0])
        
        return start_hour <= current_hour < end_hour
    
    def _get_next_operational_window(self, local_time: datetime, account: DuxSoupAccount) -> datetime:
        """Get the next operational window."""
        if not account.operational_hours:
            return local_time + timedelta(hours=1)
        
        # Move to next day if not operational
        next_day = local_time + timedelta(days=1)
        next_day = next_day.replace(hour=9, minute=0, second=0, microsecond=0)  # Start of next day
        
        # Find next operational day
        operational_days = account.operational_hours.get('days', [1, 2, 3, 4, 5])
        while next_day.weekday() not in operational_days:
            next_day += timedelta(days=1)
        
        return next_day
    
    def _calculate_delay(self, account: DuxSoupAccount, operation_type: OperationType) -> int:
        """Calculate delay based on operation type and account patterns."""
        if not account.delay_patterns:
            return 30  # Default 30 minutes
        
        base_delay = account.delay_patterns.get('min_delay', 30)
        max_delay = account.delay_patterns.get('max_delay', 120)
        random_factor = account.delay_patterns.get('random_factor', 0.2)
        
        # Add random factor to avoid patterns
        import random
        random_adjustment = random.uniform(-random_factor, random_factor)
        delay = base_delay + (max_delay - base_delay) * random_adjustment
        
        # Operation-specific adjustments
        if operation_type == OperationType.CONNECTION_REQUEST:
            delay *= 1.5  # Connection requests need more spacing
        elif operation_type == OperationType.MESSAGE_SEND:
            delay *= 0.8  # Messages can be sent more frequently
        
        return max(5, int(delay))  # Minimum 5 minutes
    
    def _check_daily_limits(self, local_time: datetime, account: DuxSoupAccount, operation_type: OperationType) -> bool:
        """Check if daily limits allow the operation."""
        if not account.daily_limits or not account.current_usage:
            return True
        
        # Map operation types to limit keys
        limit_mapping = {
            OperationType.CONNECTION_REQUEST: 'connections',
            OperationType.MESSAGE_SEND: 'messages',
            OperationType.PROFILE_VIEW: 'profile_views',
            OperationType.INMAIL_SEND: 'inmails',
            OperationType.FOLLOW_UP: 'messages'
        }
        
        limit_key = limit_mapping.get(operation_type, 'general')
        daily_limit = account.daily_limits.get(limit_key, 100)
        current_usage = account.current_usage.get(limit_key, 0)
        
        return current_usage < daily_limit
    
    def _get_next_available_slot(self, local_time: datetime, account: DuxSoupAccount, operation_type: OperationType) -> datetime:
        """Get the next available slot considering daily limits."""
        # Move to next day and reset usage
        next_day = local_time + timedelta(days=1)
        next_day = next_day.replace(hour=9, minute=0, second=0, microsecond=0)
        
        # Reset daily usage
        account.current_usage = {key: 0 for key in account.current_usage}
        
        return next_day
    
    def schedule_operation(self, request: ScheduleRequest) -> ScheduledOperation:
        """Schedule an operation for execution."""
        
        if request.dux_account_id not in self.dux_accounts:
            raise ValueError(f"DuxSoup account {request.dux_account_id} not found")
        
        dux_account = self.dux_accounts[request.dux_account_id]
        
        # Calculate optimal schedule time
        scheduled_time = self.calculate_optimal_schedule_time(request, dux_account)
        
        # Create scheduled operation
        operation_id = f"{request.operation_type.value}_{request.contact_id}_{int(scheduled_time.timestamp())}"
        
        operation = ScheduledOperation(
            operation_id=operation_id,
            request=request,
            scheduled_time=scheduled_time,
            status=ScheduleStatus.SCHEDULED,
            dux_account=dux_account,
            estimated_duration=self._get_estimated_duration(request.operation_type),
            created_at=utc_now(),
            updated_at=utc_now()
        )
        
        self.scheduled_operations[operation_id] = operation
        
        # Log the scheduling
        self.tracker.create_transaction(
            transaction_type=TransactionType.DUXSOUP_QUEUE_ITEM_ADDED,
            user_id=request.user_id,
            entity_id=operation_id,
            entity_type="scheduled_operation",
            description=f"Scheduled {request.operation_type.value} for contact {request.contact_id}",
            metadata={
                "scheduled_time": to_iso_string(scheduled_time),
                "campaign_id": request.campaign_id,
                "contact_id": request.contact_id,
                "dux_account_id": request.dux_account_id,
                "priority": request.priority
            }
        )
        
        return operation
    
    def _get_estimated_duration(self, operation_type: OperationType) -> int:
        """Get estimated duration for operation type in seconds."""
        durations = {
            OperationType.PROFILE_VIEW: 30,
            OperationType.CONNECTION_REQUEST: 60,
            OperationType.MESSAGE_SEND: 45,
            OperationType.FOLLOW_UP: 45,
            OperationType.INMAIL_SEND: 60,
            OperationType.PROFILE_SCRAPE: 120,
            OperationType.SEARCH_EXECUTION: 180
        }
        return durations.get(operation_type, 60)
    
    def get_operations_due(self, current_time: Optional[datetime] = None) -> List[ScheduledOperation]:
        """Get operations that are due for execution."""
        if current_time is None:
            current_time = utc_now()
        
        due_operations = []
        for operation in self.scheduled_operations.values():
            if (operation.status == ScheduleStatus.SCHEDULED and 
                operation.scheduled_time <= current_time):
                due_operations.append(operation)
        
        # Sort by priority and scheduled time
        due_operations.sort(key=lambda x: (x.request.priority, x.scheduled_time))
        
        return due_operations
    
    def execute_operation(self, operation: ScheduledOperation) -> bool:
        """Execute a scheduled operation."""
        try:
            # Update status
            operation.status = ScheduleStatus.IN_PROGRESS
            operation.updated_at = utc_now()
            
            # Update account usage
            self._update_account_usage(operation.dux_account, operation.request.operation_type)
            
            # Log execution start
            self.tracker.log_duxsoup_activity(
                activity_type="command_executed",
                dux_user_id=operation.dux_account.username,
                user_id=operation.request.user_id,
                contact_id=operation.request.contact_id,
                campaign_id=operation.request.campaign_id,
                command=operation.request.operation_type.value,
                description=f"Executing {operation.request.operation_type.value}",
                metadata={
                    "operation_id": operation.operation_id,
                    "scheduled_time": to_iso_string(operation.scheduled_time)
                }
            )
            
            # Simulate execution (replace with actual DuxSoup API call)
            success = self._simulate_operation_execution(operation)
            
            if success:
                operation.status = ScheduleStatus.COMPLETED
                self.tracker.log_duxsoup_activity(
                    activity_type="queue_item_processed",
                    dux_user_id=operation.dux_account.username,
                    user_id=operation.request.user_id,
                    contact_id=operation.request.contact_id,
                    campaign_id=operation.request.campaign_id,
                    description=f"Successfully completed {operation.request.operation_type.value}",
                    success=True
                )
            else:
                operation.status = ScheduleStatus.FAILED
                operation.failure_reason = "Simulated failure"
                self.tracker.log_duxsoup_activity(
                    activity_type="queue_item_failed",
                    dux_user_id=operation.dux_account.username,
                    user_id=operation.request.user_id,
                    contact_id=operation.request.contact_id,
                    campaign_id=operation.request.campaign_id,
                    description=f"Failed to execute {operation.request.operation_type.value}",
                    success=False,
                    error_message="Simulated failure"
                )
            
            operation.updated_at = utc_now()
            return success
            
        except Exception as e:
            operation.status = ScheduleStatus.FAILED
            operation.failure_reason = str(e)
            operation.updated_at = utc_now()
            
            self.tracker.log_duxsoup_activity(
                activity_type="error",
                dux_user_id=operation.dux_account.username,
                user_id=operation.request.user_id,
                contact_id=operation.request.contact_id,
                campaign_id=operation.request.campaign_id,
                description=f"Error executing {operation.request.operation_type.value}",
                success=False,
                error_message=str(e)
            )
            
            return False
    
    def _update_account_usage(self, account: DuxSoupAccount, operation_type: OperationType):
        """Update account usage counters."""
        if not account.current_usage:
            account.current_usage = {}
        
        # Map operation types to usage keys
        usage_mapping = {
            OperationType.CONNECTION_REQUEST: 'connections',
            OperationType.MESSAGE_SEND: 'messages',
            OperationType.PROFILE_VIEW: 'profile_views',
            OperationType.INMAIL_SEND: 'inmails',
            OperationType.FOLLOW_UP: 'messages'
        }
        
        usage_key = usage_mapping.get(operation_type, 'general')
        account.current_usage[usage_key] = account.current_usage.get(usage_key, 0) + 1
        account.last_activity = utc_now()
    
    def _simulate_operation_execution(self, operation: ScheduledOperation) -> bool:
        """Simulate operation execution (replace with actual DuxSoup API call)."""
        # Simulate 90% success rate
        import random
        return random.random() < 0.9
    
    def handle_retry(self, operation: ScheduledOperation) -> bool:
        """Handle retry logic for failed operations."""
        if operation.request.retry_count >= operation.request.max_retries:
            operation.status = ScheduleStatus.FAILED
            return False
        
        # Calculate retry delay with exponential backoff
        retry_delay_hours = 2 ** operation.request.retry_count  # 1, 2, 4, 8 hours
        retry_time = utc_now() + timedelta(hours=retry_delay_hours)
        
        # Recalculate optimal time considering retry
        operation.scheduled_time = self.calculate_optimal_schedule_time(operation.request, operation.dux_account)
        operation.status = ScheduleStatus.RETRYING
        operation.retry_after = retry_time
        operation.request.retry_count += 1
        operation.updated_at = utc_now()
        
        self.tracker.log_duxsoup_activity(
            activity_type="queue_item_retry",
            dux_user_id=operation.dux_account.username,
            user_id=operation.request.user_id,
            contact_id=operation.request.contact_id,
            campaign_id=operation.request.campaign_id,
            description=f"Retrying {operation.request.operation_type.value} (attempt {operation.request.retry_count})",
            metadata={
                "retry_count": operation.request.retry_count,
                "retry_after": to_iso_string(retry_time)
            }
        )
        
        return True
    
    def get_schedule_status(self, campaign_id: str) -> Dict[str, Any]:
        """Get scheduling status for a campaign."""
        campaign_operations = [
            op for op in self.scheduled_operations.values()
            if op.request.campaign_id == campaign_id
        ]
        
        status_counts = {}
        for status in ScheduleStatus:
            status_counts[status.value] = len([op for op in campaign_operations if op.status == status])
        
        return {
            "total_operations": len(campaign_operations),
            "status_breakdown": status_counts,
            "next_due": min([op.scheduled_time for op in campaign_operations if op.status == ScheduleStatus.SCHEDULED], default=None),
            "last_updated": utc_now().isoformat()
        }
    
    def reschedule_campaign(self, campaign_id: str, delay_hours: int = 24):
        """Reschedule all operations in a campaign with a delay."""
        campaign_operations = [
            op for op in self.scheduled_operations.values()
            if op.request.campaign_id == campaign_id and op.status == ScheduleStatus.SCHEDULED
        ]
        
        for operation in campaign_operations:
            operation.scheduled_time += timedelta(hours=delay_hours)
            operation.updated_at = utc_now()
        
        self.tracker.create_transaction(
            transaction_type=TransactionType.CAMPAIGN_SEQUENCE_PAUSED,
            entity_id=campaign_id,
            entity_type="campaign",
            description=f"Rescheduled campaign with {delay_hours} hour delay",
            metadata={
                "delay_hours": delay_hours,
                "operations_affected": len(campaign_operations)
            }
        )
    
    def get_dux_account_status(self, account_id: str) -> Dict[str, Any]:
        """Get status of a DuxSoup account."""
        if account_id not in self.dux_accounts:
            return {"error": "Account not found"}
        
        account = self.dux_accounts[account_id]
        
        return {
            "account_id": account_id,
            "username": account.username,
            "timezone": account.timezone,
            "is_active": account.is_active,
            "current_usage": account.current_usage,
            "daily_limits": account.daily_limits,
            "last_activity": account.last_activity.isoformat() if account.last_activity else None,
            "operational_hours": account.operational_hours
        }
