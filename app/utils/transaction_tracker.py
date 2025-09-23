"""
Transaction tracking system for comprehensive audit trails.

This module provides transaction tracking with timestamps and types for all
operations across the platform.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import uuid
from app.utils.timestamps import utc_now, to_iso_string


class TransactionType(Enum):
    """Types of transactions that can occur in the system."""
    
    # Campaign Operations
    CAMPAIGN_CREATED = "campaign_created"
    CAMPAIGN_UPDATED = "campaign_updated"
    CAMPAIGN_DELETED = "campaign_deleted"
    CAMPAIGN_STARTED = "campaign_started"
    CAMPAIGN_PAUSED = "campaign_paused"
    CAMPAIGN_COMPLETED = "campaign_completed"
    CAMPAIGN_ARCHIVED = "campaign_archived"
    
    # Contact Operations
    CONTACT_CREATED = "contact_created"
    CONTACT_UPDATED = "contact_updated"
    CONTACT_DELETED = "contact_deleted"
    CONTACT_IMPORTED = "contact_imported"
    CONTACT_ENROLLED = "contact_enrolled"
    CONTACT_UNENROLLED = "contact_unenrolled"
    CONTACT_ASSIGNED = "contact_assigned"
    CONTACT_UNASSIGNED = "contact_unassigned"
    
    # LinkedIn Profile Operations
    PROFILE_VIEWED = "profile_viewed"  # When our user views someone's profile
    PROFILE_VIEWED_BY = "profile_viewed_by"  # When someone views our user's profile
    PROFILE_SEARCHED = "profile_searched"  # When we search for profiles
    PROFILE_SCRAPED = "profile_scraped"  # When we scrape profile data
    
    # Connection Operations
    CONNECTION_REQUEST_SENT = "connection_request_sent"
    CONNECTION_REQUEST_RECEIVED = "connection_request_received"
    CONNECTION_ACCEPTED = "connection_accepted"
    CONNECTION_ACCEPTED_BY = "connection_accepted_by"  # When someone accepts our request
    CONNECTION_REJECTED = "connection_rejected"
    CONNECTION_REJECTED_BY = "connection_rejected_by"  # When someone rejects our request
    CONNECTION_WITHDRAWN = "connection_withdrawn"
    CONNECTION_REMOVED = "connection_removed"
    
    # Message Operations
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"
    MESSAGE_QUEUED = "message_queued"
    MESSAGE_DELIVERED = "message_delivered"
    MESSAGE_READ = "message_read"
    MESSAGE_FAILED = "message_failed"
    MESSAGE_REPLIED = "message_replied"  # When someone replies to our message
    MESSAGE_REPLY_SENT = "message_reply_sent"  # When we reply to someone's message
    
    # InMail Operations
    INMAIL_SENT = "inmail_sent"
    INMAIL_RECEIVED = "inmail_received"
    INMAIL_QUEUED = "inmail_queued"
    INMAIL_DELIVERED = "inmail_delivered"
    INMAIL_READ = "inmail_read"
    INMAIL_REPLIED = "inmail_replied"
    INMAIL_REPLY_SENT = "inmail_reply_sent"
    INMAIL_FAILED = "inmail_failed"
    
    # Follow-up Operations
    FOLLOW_UP_SENT = "follow_up_sent"
    FOLLOW_UP_RECEIVED = "follow_up_received"
    FOLLOW_UP_QUEUED = "follow_up_queued"
    FOLLOW_UP_DELIVERED = "follow_up_delivered"
    FOLLOW_UP_READ = "follow_up_read"
    FOLLOW_UP_REPLIED = "follow_up_replied"
    FOLLOW_UP_REPLY_SENT = "follow_up_reply_sent"
    FOLLOW_UP_FAILED = "follow_up_failed"
    
    # Meeting Operations
    MEETING_SCHEDULED = "meeting_scheduled"
    MEETING_RESCHEDULED = "meeting_rescheduled"
    MEETING_CANCELLED = "meeting_cancelled"
    MEETING_COMPLETED = "meeting_completed"
    MEETING_INVITATION_SENT = "meeting_invitation_sent"
    MEETING_INVITATION_RECEIVED = "meeting_invitation_received"
    MEETING_INVITATION_ACCEPTED = "meeting_invitation_accepted"
    MEETING_INVITATION_DECLINED = "meeting_invitation_declined"
    
    # Email Operations (if integrated)
    EMAIL_SENT = "email_sent"
    EMAIL_RECEIVED = "email_received"
    EMAIL_QUEUED = "email_queued"
    EMAIL_DELIVERED = "email_delivered"
    EMAIL_READ = "email_read"
    EMAIL_REPLIED = "email_replied"
    EMAIL_REPLY_SENT = "email_reply_sent"
    EMAIL_FAILED = "email_failed"
    
    # User Operations
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_ACTIVITY = "user_activity"  # General user activity
    
    # DuxSoup Operations
    DUXSOUP_ACCOUNT_ADDED = "duxsoup_account_added"
    DUXSOUP_ACCOUNT_UPDATED = "duxsoup_account_updated"
    DUXSOUP_ACCOUNT_DELETED = "duxsoup_account_deleted"
    DUXSOUP_COMMAND_EXECUTED = "duxsoup_command_executed"
    DUXSOUP_QUEUE_ITEM_ADDED = "duxsoup_queue_item_added"
    DUXSOUP_QUEUE_ITEM_PROCESSED = "duxsoup_queue_item_processed"
    DUXSOUP_QUEUE_ITEM_FAILED = "duxsoup_queue_item_failed"
    DUXSOUP_QUEUE_ITEM_RETRY = "duxsoup_queue_item_retry"
    DUXSOUP_SESSION_STARTED = "duxsoup_session_started"
    DUXSOUP_SESSION_ENDED = "duxsoup_session_ended"
    DUXSOUP_ERROR = "duxsoup_error"
    
    # LinkedIn API Operations
    LINKEDIN_API_CALL = "linkedin_api_call"
    LINKEDIN_API_SUCCESS = "linkedin_api_success"
    LINKEDIN_API_ERROR = "linkedin_api_error"
    LINKEDIN_RATE_LIMIT = "linkedin_rate_limit"
    LINKEDIN_AUTH_REFRESH = "linkedin_auth_refresh"
    
    # Contact Status Changes
    CONTACT_STATUS_CHANGED = "contact_status_changed"
    CONTACT_ACCEPTED_CONNECTION = "contact_accepted_connection"
    CONTACT_REPLIED_TO_MESSAGE = "contact_replied_to_message"
    CONTACT_VIEWED_PROFILE = "contact_viewed_profile"
    CONTACT_ENGAGED = "contact_engaged"  # General engagement
    CONTACT_UNENGAGED = "contact_unengaged"  # No response after multiple attempts
    
    # Campaign Status Changes
    CAMPAIGN_CONTACT_ADDED = "campaign_contact_added"
    CAMPAIGN_CONTACT_REMOVED = "campaign_contact_removed"
    CAMPAIGN_CONTACT_STATUS_CHANGED = "campaign_contact_status_changed"
    CAMPAIGN_SEQUENCE_STARTED = "campaign_sequence_started"
    CAMPAIGN_SEQUENCE_PAUSED = "campaign_sequence_paused"
    CAMPAIGN_SEQUENCE_RESUMED = "campaign_sequence_resumed"
    CAMPAIGN_SEQUENCE_COMPLETED = "campaign_sequence_completed"
    
    # System Operations
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    DATABASE_MIGRATION = "database_migration"
    BACKUP_CREATED = "backup_created"
    ERROR_OCCURRED = "error_occurred"
    PERFORMANCE_ALERT = "performance_alert"
    SECURITY_ALERT = "security_alert"
    
    # Analytics and Reporting
    ANALYTICS_GENERATED = "analytics_generated"
    REPORT_GENERATED = "report_generated"
    DASHBOARD_VIEWED = "dashboard_viewed"
    EXPORT_REQUESTED = "export_requested"
    EXPORT_COMPLETED = "export_completed"


@dataclass
class TransactionRecord:
    """Record of a single transaction."""
    
    transaction_id: str
    transaction_type: TransactionType
    transaction_time: datetime
    user_id: Optional[str] = None
    entity_id: Optional[str] = None  # ID of the main entity affected
    entity_type: Optional[str] = None  # Type of entity (campaign, contact, etc.)
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    success: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "transaction_id": self.transaction_id,
            "transaction_type": self.transaction_type.value,
            "transaction_time": to_iso_string(self.transaction_time),
            "user_id": self.user_id,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "description": self.description,
            "metadata": self.metadata or {},
            "success": self.success,
            "error_message": self.error_message
        }


class TransactionTracker:
    """Main transaction tracking class."""
    
    def __init__(self):
        self.transactions: List[TransactionRecord] = []
    
    def create_transaction(
        self,
        transaction_type: TransactionType,
        user_id: Optional[str] = None,
        entity_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> TransactionRecord:
        """Create a new transaction record."""
        
        transaction = TransactionRecord(
            transaction_id=str(uuid.uuid4()),
            transaction_type=transaction_type,
            transaction_time=utc_now(),
            user_id=user_id,
            entity_id=entity_id,
            entity_type=entity_type,
            description=description,
            metadata=metadata,
            success=success,
            error_message=error_message
        )
        
        self.transactions.append(transaction)
        return transaction
    
    def log_campaign_operation(
        self,
        operation: str,
        campaign_id: str,
        user_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> TransactionRecord:
        """Log a campaign-related transaction."""
        
        transaction_type_map = {
            "create": TransactionType.CAMPAIGN_CREATED,
            "update": TransactionType.CAMPAIGN_UPDATED,
            "delete": TransactionType.CAMPAIGN_DELETED,
            "start": TransactionType.CAMPAIGN_STARTED,
            "pause": TransactionType.CAMPAIGN_PAUSED,
            "complete": TransactionType.CAMPAIGN_COMPLETED,
            "archive": TransactionType.CAMPAIGN_ARCHIVED
        }
        
        transaction_type = transaction_type_map.get(operation, TransactionType.CAMPAIGN_UPDATED)
        
        return self.create_transaction(
            transaction_type=transaction_type,
            user_id=user_id,
            entity_id=campaign_id,
            entity_type="campaign",
            description=description,
            metadata=metadata,
            success=success,
            error_message=error_message
        )
    
    def log_contact_operation(
        self,
        operation: str,
        contact_id: str,
        user_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> TransactionRecord:
        """Log a contact-related transaction."""
        
        transaction_type_map = {
            "create": TransactionType.CONTACT_CREATED,
            "update": TransactionType.CONTACT_UPDATED,
            "delete": TransactionType.CONTACT_DELETED,
            "import": TransactionType.CONTACT_IMPORTED,
            "enroll": TransactionType.CONTACT_ENROLLED,
            "unenroll": TransactionType.CONTACT_UNENROLLED,
            "assign": TransactionType.CONTACT_ASSIGNED,
            "unassign": TransactionType.CONTACT_UNASSIGNED
        }
        
        transaction_type = transaction_type_map.get(operation, TransactionType.CONTACT_UPDATED)
        
        return self.create_transaction(
            transaction_type=transaction_type,
            user_id=user_id,
            entity_id=contact_id,
            entity_type="contact",
            description=description,
            metadata=metadata,
            success=success,
            error_message=error_message
        )
    
    def log_message_operation(
        self,
        operation: str,
        message_id: str,
        user_id: Optional[str] = None,
        contact_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> TransactionRecord:
        """Log a message-related transaction."""
        
        transaction_type_map = {
            "send": TransactionType.MESSAGE_SENT,
            "receive": TransactionType.MESSAGE_RECEIVED,
            "queue": TransactionType.MESSAGE_QUEUED,
            "deliver": TransactionType.MESSAGE_DELIVERED,
            "read": TransactionType.MESSAGE_READ,
            "fail": TransactionType.MESSAGE_FAILED
        }
        
        transaction_type = transaction_type_map.get(operation, TransactionType.MESSAGE_SENT)
        
        return self.create_transaction(
            transaction_type=transaction_type,
            user_id=user_id,
            entity_id=message_id,
            entity_type="message",
            description=description,
            metadata={
                **(metadata or {}),
                "contact_id": contact_id,
                "campaign_id": campaign_id
            },
            success=success,
            error_message=error_message
        )
    
    def log_meeting_operation(
        self,
        operation: str,
        meeting_id: str,
        user_id: Optional[str] = None,
        contact_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> TransactionRecord:
        """Log a meeting-related transaction."""
        
        transaction_type_map = {
            "schedule": TransactionType.MEETING_SCHEDULED,
            "reschedule": TransactionType.MEETING_RESCHEDULED,
            "cancel": TransactionType.MEETING_CANCELLED,
            "complete": TransactionType.MEETING_COMPLETED,
            "invitation_sent": TransactionType.MEETING_INVITATION_SENT,
            "invitation_received": TransactionType.MEETING_INVITATION_RECEIVED,
            "invitation_accepted": TransactionType.MEETING_INVITATION_ACCEPTED,
            "invitation_declined": TransactionType.MEETING_INVITATION_DECLINED
        }
        
        transaction_type = transaction_type_map.get(operation, TransactionType.MEETING_SCHEDULED)
        
        return self.create_transaction(
            transaction_type=transaction_type,
            user_id=user_id,
            entity_id=meeting_id,
            entity_type="meeting",
            description=description,
            metadata={
                **(metadata or {}),
                "contact_id": contact_id
            },
            success=success,
            error_message=error_message
        )
    
    def log_linkedin_activity(
        self,
        activity_type: str,
        contact_id: str,
        user_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        linkedin_profile_url: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> TransactionRecord:
        """Log LinkedIn-specific activities."""
        
        transaction_type_map = {
            "profile_viewed": TransactionType.PROFILE_VIEWED,
            "profile_viewed_by": TransactionType.PROFILE_VIEWED_BY,
            "profile_searched": TransactionType.PROFILE_SEARCHED,
            "profile_scraped": TransactionType.PROFILE_SCRAPED,
            "connection_request_sent": TransactionType.CONNECTION_REQUEST_SENT,
            "connection_request_received": TransactionType.CONNECTION_REQUEST_RECEIVED,
            "connection_accepted": TransactionType.CONNECTION_ACCEPTED,
            "connection_accepted_by": TransactionType.CONNECTION_ACCEPTED_BY,
            "connection_rejected": TransactionType.CONNECTION_REJECTED,
            "connection_rejected_by": TransactionType.CONNECTION_REJECTED_BY,
            "connection_withdrawn": TransactionType.CONNECTION_WITHDRAWN,
            "connection_removed": TransactionType.CONNECTION_REMOVED,
            "message_sent": TransactionType.MESSAGE_SENT,
            "message_received": TransactionType.MESSAGE_RECEIVED,
            "message_replied": TransactionType.MESSAGE_REPLIED,
            "message_reply_sent": TransactionType.MESSAGE_REPLY_SENT,
            "inmail_sent": TransactionType.INMAIL_SENT,
            "inmail_received": TransactionType.INMAIL_RECEIVED,
            "inmail_replied": TransactionType.INMAIL_REPLIED,
            "inmail_reply_sent": TransactionType.INMAIL_REPLY_SENT,
            "follow_up_sent": TransactionType.FOLLOW_UP_SENT,
            "follow_up_received": TransactionType.FOLLOW_UP_RECEIVED,
            "follow_up_replied": TransactionType.FOLLOW_UP_REPLIED,
            "follow_up_reply_sent": TransactionType.FOLLOW_UP_REPLY_SENT,
            "contact_engaged": TransactionType.CONTACT_ENGAGED,
            "contact_unengaged": TransactionType.CONTACT_UNENGAGED
        }
        
        transaction_type = transaction_type_map.get(activity_type, TransactionType.USER_ACTIVITY)
        
        return self.create_transaction(
            transaction_type=transaction_type,
            user_id=user_id,
            entity_id=contact_id,
            entity_type="contact",
            description=description,
            metadata={
                **(metadata or {}),
                "campaign_id": campaign_id,
                "linkedin_profile_url": linkedin_profile_url
            },
            success=success,
            error_message=error_message
        )
    
    def log_duxsoup_activity(
        self,
        activity_type: str,
        dux_user_id: str,
        user_id: Optional[str] = None,
        contact_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        command: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> TransactionRecord:
        """Log DuxSoup-specific activities."""
        
        transaction_type_map = {
            "account_added": TransactionType.DUXSOUP_ACCOUNT_ADDED,
            "account_updated": TransactionType.DUXSOUP_ACCOUNT_UPDATED,
            "account_deleted": TransactionType.DUXSOUP_ACCOUNT_DELETED,
            "command_executed": TransactionType.DUXSOUP_COMMAND_EXECUTED,
            "queue_item_added": TransactionType.DUXSOUP_QUEUE_ITEM_ADDED,
            "queue_item_processed": TransactionType.DUXSOUP_QUEUE_ITEM_PROCESSED,
            "queue_item_failed": TransactionType.DUXSOUP_QUEUE_ITEM_FAILED,
            "queue_item_retry": TransactionType.DUXSOUP_QUEUE_ITEM_RETRY,
            "session_started": TransactionType.DUXSOUP_SESSION_STARTED,
            "session_ended": TransactionType.DUXSOUP_SESSION_ENDED,
            "error": TransactionType.DUXSOUP_ERROR
        }
        
        transaction_type = transaction_type_map.get(activity_type, TransactionType.DUXSOUP_COMMAND_EXECUTED)
        
        return self.create_transaction(
            transaction_type=transaction_type,
            user_id=user_id,
            entity_id=dux_user_id,
            entity_type="duxsoup_account",
            description=description,
            metadata={
                **(metadata or {}),
                "contact_id": contact_id,
                "campaign_id": campaign_id,
                "command": command
            },
            success=success,
            error_message=error_message
        )
    
    def log_campaign_sequence_activity(
        self,
        activity_type: str,
        campaign_id: str,
        contact_id: Optional[str] = None,
        user_id: Optional[str] = None,
        sequence_step: Optional[int] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> TransactionRecord:
        """Log campaign sequence activities."""
        
        transaction_type_map = {
            "contact_added": TransactionType.CAMPAIGN_CONTACT_ADDED,
            "contact_removed": TransactionType.CAMPAIGN_CONTACT_REMOVED,
            "status_changed": TransactionType.CAMPAIGN_CONTACT_STATUS_CHANGED,
            "sequence_started": TransactionType.CAMPAIGN_SEQUENCE_STARTED,
            "sequence_paused": TransactionType.CAMPAIGN_SEQUENCE_PAUSED,
            "sequence_resumed": TransactionType.CAMPAIGN_SEQUENCE_RESUMED,
            "sequence_completed": TransactionType.CAMPAIGN_SEQUENCE_COMPLETED
        }
        
        transaction_type = transaction_type_map.get(activity_type, TransactionType.CAMPAIGN_CONTACT_STATUS_CHANGED)
        
        return self.create_transaction(
            transaction_type=transaction_type,
            user_id=user_id,
            entity_id=campaign_id,
            entity_type="campaign",
            description=description,
            metadata={
                **(metadata or {}),
                "contact_id": contact_id,
                "sequence_step": sequence_step
            },
            success=success,
            error_message=error_message
        )
    
    def get_transactions(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        user_id: Optional[str] = None,
        transaction_type: Optional[TransactionType] = None,
        limit: int = 100
    ) -> List[TransactionRecord]:
        """Get filtered list of transactions."""
        
        filtered = self.transactions
        
        if entity_type:
            filtered = [t for t in filtered if t.entity_type == entity_type]
        
        if entity_id:
            filtered = [t for t in filtered if t.entity_id == entity_id]
        
        if user_id:
            filtered = [t for t in filtered if t.user_id == user_id]
        
        if transaction_type:
            filtered = [t for t in filtered if t.transaction_type == transaction_type]
        
        return sorted(filtered, key=lambda x: x.transaction_time, reverse=True)[:limit]
    
    def get_entity_history(self, entity_type: str, entity_id: str) -> List[TransactionRecord]:
        """Get complete history for a specific entity."""
        return self.get_transactions(entity_type=entity_type, entity_id=entity_id)
    
    def get_user_activity(self, user_id: str, limit: int = 50) -> List[TransactionRecord]:
        """Get recent activity for a specific user."""
        return self.get_transactions(user_id=user_id, limit=limit)
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics based on recent transactions."""
        recent_transactions = [t for t in self.transactions if (utc_now() - t.transaction_time).total_seconds() < 3600]  # Last hour
        
        total_transactions = len(recent_transactions)
        successful_transactions = len([t for t in recent_transactions if t.success])
        failed_transactions = total_transactions - successful_transactions
        
        success_rate = (successful_transactions / total_transactions * 100) if total_transactions > 0 else 0
        
        return {
            "total_transactions_last_hour": total_transactions,
            "successful_transactions": successful_transactions,
            "failed_transactions": failed_transactions,
            "success_rate_percent": round(success_rate, 2),
            "last_transaction_time": to_iso_string(max([t.transaction_time for t in recent_transactions])) if recent_transactions else None
        }


# Global transaction tracker instance
transaction_tracker = TransactionTracker()


def get_transaction_tracker() -> TransactionTracker:
    """Get the global transaction tracker instance."""
    return transaction_tracker


def log_transaction(
    transaction_type: TransactionType,
    user_id: Optional[str] = None,
    entity_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    description: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    success: bool = True,
    error_message: Optional[str] = None
) -> TransactionRecord:
    """Convenience function to log a transaction."""
    return transaction_tracker.create_transaction(
        transaction_type=transaction_type,
        user_id=user_id,
        entity_id=entity_id,
        entity_type=entity_type,
        description=description,
        metadata=metadata,
        success=success,
        error_message=error_message
    )
