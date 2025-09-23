"""
Custom SQLAlchemy types for consistent data handling.
"""

from sqlalchemy import TypeDecorator, DateTime
from datetime import datetime, timezone
from typing import Any, Optional
from app.utils.timestamps import utc_now, ensure_timezone_aware


class UTCDateTime(TypeDecorator):
    """
    Custom SQLAlchemy DateTime type that automatically handles timezone conversion.
    
    This type ensures all datetime values are stored as UTC and returned as
    timezone-aware datetime objects.
    """
    
    impl = DateTime(timezone=True)
    cache_ok = True
    
    def process_bind_param(self, value: Any, dialect) -> Optional[datetime]:
        """Convert Python datetime to database value."""
        if value is None:
            return None
        
        if isinstance(value, str):
            # Try to parse string as datetime
            try:
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                return None
        
        if isinstance(value, datetime):
            # Ensure timezone aware and convert to UTC
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            else:
                value = value.astimezone(timezone.utc)
            return value
        
        return None
    
    def process_result_value(self, value: Any, dialect) -> Optional[datetime]:
        """Convert database value to Python datetime."""
        if value is None:
            return None
        
        if isinstance(value, datetime):
            # Ensure timezone aware
            return ensure_timezone_aware(value)
        
        return None
    
    def load_dialect_impl(self, dialect):
        """Return the underlying database type."""
        return dialect.type_descriptor(DateTime(timezone=True))


class MessageTimestamp(UTCDateTime):
    """
    Specialized timestamp type for message operations.
    """
    
    def process_bind_param(self, value: Any, dialect) -> Optional[datetime]:
        """Handle message timestamp binding."""
        if value is None:
            return utc_now()  # Default to current time for messages
        
        return super().process_bind_param(value, dialect)


class CampaignTimestamp(UTCDateTime):
    """
    Specialized timestamp type for campaign operations.
    """
    
    def process_bind_param(self, value: Any, dialect) -> Optional[datetime]:
        """Handle campaign timestamp binding."""
        if value is None:
            return utc_now()  # Default to current time for campaigns
        
        return super().process_bind_param(value, dialect)


class ContactTimestamp(UTCDateTime):
    """
    Specialized timestamp type for contact operations.
    """
    
    def process_bind_param(self, value: Any, dialect) -> Optional[datetime]:
        """Handle contact timestamp binding."""
        if value is None:
            return utc_now()  # Default to current time for contacts
        
        return super().process_bind_param(value, dialect)
