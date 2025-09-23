"""
Custom timestamp utilities for consistent datetime handling across the platform.

This module provides timezone-aware datetime functions that ensure all timestamps
are stored and handled consistently throughout the application.
"""

from datetime import datetime, timezone
from typing import Optional, Union
import pytz


def utc_now() -> datetime:
    """
    Get current UTC datetime with timezone info.
    
    Returns:
        datetime: Current UTC datetime with timezone info
    """
    return datetime.now(timezone.utc)


def to_utc(dt: Optional[Union[datetime, str]]) -> Optional[datetime]:
    """
    Convert any datetime to UTC timezone.
    
    Args:
        dt: datetime object or ISO string
        
    Returns:
        datetime: UTC timezone-aware datetime or None
    """
    if dt is None:
        return None
    
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except ValueError:
            return None
    
    if dt.tzinfo is None:
        # Assume UTC if no timezone info
        return dt.replace(tzinfo=timezone.utc)
    
    return dt.astimezone(timezone.utc)


def to_iso_string(dt: Optional[datetime]) -> Optional[str]:
    """
    Convert datetime to ISO string format.
    
    Args:
        dt: datetime object
        
    Returns:
        str: ISO formatted string or None
    """
    if dt is None:
        return None
    
    # Ensure timezone aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.isoformat()


def format_for_display(dt: Optional[datetime], format_str: str = "%Y-%m-%d %H:%M:%S UTC") -> Optional[str]:
    """
    Format datetime for display purposes.
    
    Args:
        dt: datetime object
        format_str: Format string
        
    Returns:
        str: Formatted string or None
    """
    if dt is None:
        return None
    
    # Ensure timezone aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.strftime(format_str)


def parse_user_timestamp(timestamp_str: str) -> Optional[datetime]:
    """
    Parse user-provided timestamp string into UTC datetime.
    
    Args:
        timestamp_str: Timestamp string in various formats
        
    Returns:
        datetime: UTC timezone-aware datetime or None
    """
    if not timestamp_str:
        return None
    
    # Common timestamp formats to try
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(timestamp_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    
    # Try ISO format parsing
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except ValueError:
        pass
    
    return None


def get_message_timestamp(message_type: str = "sent") -> datetime:
    """
    Get timestamp for message operations.
    
    Args:
        message_type: Type of message operation (sent, received, etc.)
        
    Returns:
        datetime: UTC timezone-aware datetime
    """
    return utc_now()


def get_campaign_timestamp() -> datetime:
    """
    Get timestamp for campaign operations.
    
    Returns:
        datetime: UTC timezone-aware datetime
    """
    return utc_now()


def get_contact_timestamp() -> datetime:
    """
    Get timestamp for contact operations.
    
    Returns:
        datetime: UTC timezone-aware datetime
    """
    return utc_now()


def is_valid_timestamp(dt: Optional[datetime]) -> bool:
    """
    Check if datetime is valid and timezone-aware.
    
    Args:
        dt: datetime object
        
    Returns:
        bool: True if valid and timezone-aware
    """
    if dt is None:
        return False
    
    return dt.tzinfo is not None


def ensure_timezone_aware(dt: Optional[datetime]) -> Optional[datetime]:
    """
    Ensure datetime is timezone-aware, defaulting to UTC.
    
    Args:
        dt: datetime object
        
    Returns:
        datetime: Timezone-aware datetime or None
    """
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    
    return dt


def compare_timestamps(dt1: Optional[datetime], dt2: Optional[datetime]) -> int:
    """
    Compare two timestamps safely.
    
    Args:
        dt1: First datetime
        dt2: Second datetime
        
    Returns:
        int: -1 if dt1 < dt2, 0 if equal, 1 if dt1 > dt2
    """
    if dt1 is None and dt2 is None:
        return 0
    if dt1 is None:
        return -1
    if dt2 is None:
        return 1
    
    # Ensure both are timezone aware
    dt1 = ensure_timezone_aware(dt1)
    dt2 = ensure_timezone_aware(dt2)
    
    if dt1 < dt2:
        return -1
    elif dt1 > dt2:
        return 1
    else:
        return 0
