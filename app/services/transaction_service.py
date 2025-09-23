"""
Transaction logging service that integrates with the database.

This service handles all transaction logging and provides methods for
tracking every activity in the platform.
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.transaction_log import TransactionLog
from app.utils.transaction_tracker import TransactionType, TransactionRecord, get_transaction_tracker
from app.utils.timestamps import utc_now


class TransactionService:
    """Service for managing transaction logs."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.tracker = get_transaction_tracker()
    
    async def log_transaction(
        self,
        transaction_type: TransactionType,
        user_id: Optional[str] = None,
        entity_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        campaign_id: Optional[str] = None,
        contact_id: Optional[str] = None,
        dux_user_id: Optional[str] = None
    ) -> TransactionLog:
        """Log a transaction to the database."""
        
        # Create in-memory record
        record = self.tracker.create_transaction(
            transaction_type=transaction_type,
            user_id=user_id,
            entity_id=entity_id,
            entity_type=entity_type,
            description=description,
            metadata=metadata,
            success=success,
            error_message=error_message
        )
        
        # Create database record
        transaction_log = TransactionLog(
            transaction_id=record.transaction_id,
            transaction_type=transaction_type.value,
            transaction_time=record.transaction_time,
            user_id=user_id,
            entity_id=entity_id,
            entity_type=entity_type,
            description=description,
            transaction_metadata=metadata,
            success=success,
            error_message=error_message,
            campaign_id=campaign_id,
            contact_id=contact_id,
            dux_user_id=dux_user_id
        )
        
        self.session.add(transaction_log)
        await self.session.commit()
        
        return transaction_log
    
    async def log_linkedin_activity(
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
    ) -> TransactionLog:
        """Log LinkedIn activity with automatic transaction type mapping."""
        
        # Map activity type to transaction type
        activity_mapping = {
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
        
        transaction_type = activity_mapping.get(activity_type, TransactionType.USER_ACTIVITY)
        
        return await self.log_transaction(
            transaction_type=transaction_type,
            user_id=user_id,
            entity_id=contact_id,
            entity_type="contact",
            description=description,
            metadata={
                **(metadata or {}),
                "linkedin_profile_url": linkedin_profile_url
            },
            success=success,
            error_message=error_message,
            campaign_id=campaign_id,
            contact_id=contact_id
        )
    
    async def log_message_activity(
        self,
        message_id: str,
        activity_type: str,
        user_id: Optional[str] = None,
        contact_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        message_content: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> TransactionLog:
        """Log message-related activities."""
        
        activity_mapping = {
            "sent": TransactionType.MESSAGE_SENT,
            "received": TransactionType.MESSAGE_RECEIVED,
            "queued": TransactionType.MESSAGE_QUEUED,
            "delivered": TransactionType.MESSAGE_DELIVERED,
            "read": TransactionType.MESSAGE_READ,
            "failed": TransactionType.MESSAGE_FAILED,
            "replied": TransactionType.MESSAGE_REPLIED,
            "reply_sent": TransactionType.MESSAGE_REPLY_SENT
        }
        
        transaction_type = activity_mapping.get(activity_type, TransactionType.MESSAGE_SENT)
        
        return await self.log_transaction(
            transaction_type=transaction_type,
            user_id=user_id,
            entity_id=message_id,
            entity_type="message",
            description=description,
            metadata={
                **(metadata or {}),
                "message_content": message_content,
                "contact_id": contact_id,
                "campaign_id": campaign_id
            },
            success=success,
            error_message=error_message,
            campaign_id=campaign_id,
            contact_id=contact_id
        )
    
    async def log_campaign_activity(
        self,
        campaign_id: str,
        activity_type: str,
        user_id: Optional[str] = None,
        contact_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> TransactionLog:
        """Log campaign-related activities."""
        
        activity_mapping = {
            "created": TransactionType.CAMPAIGN_CREATED,
            "updated": TransactionType.CAMPAIGN_UPDATED,
            "deleted": TransactionType.CAMPAIGN_DELETED,
            "started": TransactionType.CAMPAIGN_STARTED,
            "paused": TransactionType.CAMPAIGN_PAUSED,
            "completed": TransactionType.CAMPAIGN_COMPLETED,
            "archived": TransactionType.CAMPAIGN_ARCHIVED,
            "contact_added": TransactionType.CAMPAIGN_CONTACT_ADDED,
            "contact_removed": TransactionType.CAMPAIGN_CONTACT_REMOVED,
            "contact_status_changed": TransactionType.CAMPAIGN_CONTACT_STATUS_CHANGED,
            "sequence_started": TransactionType.CAMPAIGN_SEQUENCE_STARTED,
            "sequence_paused": TransactionType.CAMPAIGN_SEQUENCE_PAUSED,
            "sequence_resumed": TransactionType.CAMPAIGN_SEQUENCE_RESUMED,
            "sequence_completed": TransactionType.CAMPAIGN_SEQUENCE_COMPLETED
        }
        
        transaction_type = activity_mapping.get(activity_type, TransactionType.CAMPAIGN_UPDATED)
        
        return await self.log_transaction(
            transaction_type=transaction_type,
            user_id=user_id,
            entity_id=campaign_id,
            entity_type="campaign",
            description=description,
            transaction_metadata=metadata,
            success=success,
            error_message=error_message,
            campaign_id=campaign_id,
            contact_id=contact_id
        )
    
    async def get_transaction_history(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        user_id: Optional[str] = None,
        transaction_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[TransactionLog]:
        """Get transaction history with filtering."""
        
        query = select(TransactionLog)
        
        if entity_type:
            query = query.where(TransactionLog.entity_type == entity_type)
        
        if entity_id:
            query = query.where(TransactionLog.entity_id == entity_id)
        
        if user_id:
            query = query.where(TransactionLog.user_id == user_id)
        
        if transaction_type:
            query = query.where(TransactionLog.transaction_type == transaction_type)
        
        query = query.order_by(desc(TransactionLog.transaction_time)).offset(offset).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_contact_activity(self, contact_id: str, limit: int = 50) -> List[TransactionLog]:
        """Get all activity for a specific contact."""
        return await self.get_transaction_history(
            entity_type="contact",
            entity_id=contact_id,
            limit=limit
        )
    
    async def get_campaign_activity(self, campaign_id: str, limit: int = 50) -> List[TransactionLog]:
        """Get all activity for a specific campaign."""
        return await self.get_transaction_history(
            entity_type="campaign",
            entity_id=campaign_id,
            limit=limit
        )
    
    async def get_user_activity(self, user_id: str, limit: int = 50) -> List[TransactionLog]:
        """Get all activity for a specific user."""
        return await self.get_transaction_history(
            user_id=user_id,
            limit=limit
        )
    
    async def get_recent_activity(self, hours: int = 24, limit: int = 100) -> List[TransactionLog]:
        """Get recent activity within specified hours."""
        from datetime import timedelta
        
        cutoff_time = utc_now() - timedelta(hours=hours)
        
        query = select(TransactionLog).where(
            TransactionLog.transaction_time >= cutoff_time
        ).order_by(desc(TransactionLog.transaction_time)).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_activity_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get activity statistics for the specified time period."""
        from datetime import timedelta
        
        cutoff_time = utc_now() - timedelta(hours=hours)
        
        # Get total transactions
        total_query = select(TransactionLog).where(TransactionLog.transaction_time >= cutoff_time)
        total_result = await self.session.execute(total_query)
        total_transactions = len(total_result.scalars().all())
        
        # Get successful transactions
        success_query = select(TransactionLog).where(
            TransactionLog.transaction_time >= cutoff_time,
            TransactionLog.success == True
        )
        success_result = await self.session.execute(success_query)
        successful_transactions = len(success_result.scalars().all())
        
        # Get failed transactions
        failed_transactions = total_transactions - successful_transactions
        
        # Calculate success rate
        success_rate = (successful_transactions / total_transactions * 100) if total_transactions > 0 else 0
        
        return {
            "total_transactions": total_transactions,
            "successful_transactions": successful_transactions,
            "failed_transactions": failed_transactions,
            "success_rate_percent": round(success_rate, 2),
            "time_period_hours": hours
        }
