"""
Advanced timezone management service for global LinkedIn automation.

This service handles:
- Multiple timezone support
- DST (Daylight Saving Time) transitions
- Business hours across different regions
- Optimal scheduling windows
- Timezone-aware delay calculations
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import pytz
from app.utils.timestamps import utc_now


class Region(Enum):
    """Geographic regions for timezone management."""
    NORTH_AMERICA_EAST = "America/New_York"
    NORTH_AMERICA_CENTRAL = "America/Chicago"
    NORTH_AMERICA_MOUNTAIN = "America/Denver"
    NORTH_AMERICA_WEST = "America/Los_Angeles"
    EUROPE_LONDON = "Europe/London"
    EUROPE_PARIS = "Europe/Paris"
    EUROPE_BERLIN = "Europe/Berlin"
    ASIA_TOKYO = "Asia/Tokyo"
    ASIA_SHANGHAI = "Asia/Shanghai"
    ASIA_DUBAI = "Asia/Dubai"
    AUSTRALIA_SYDNEY = "Australia/Sydney"
    UTC = "UTC"


@dataclass
class BusinessHours:
    """Business hours configuration for a region."""
    region: Region
    timezone: str
    weekdays: List[int]  # 0=Monday, 6=Sunday
    start_hour: int
    end_hour: int
    lunch_start: Optional[int] = None  # Lunch break start hour
    lunch_end: Optional[int] = None   # Lunch break end hour
    timezone_offset: int = 0  # UTC offset in hours


@dataclass
class OptimalTiming:
    """Optimal timing configuration for LinkedIn activities."""
    region: Region
    best_hours: List[Tuple[int, int]]  # [(start_hour, end_hour), ...]
    avoid_hours: List[Tuple[int, int]]  # Hours to avoid
    peak_hours: List[Tuple[int, int]]  # Peak activity hours
    weekend_activity: bool = False
    holiday_activity: bool = False


class TimezoneService:
    """Service for managing timezones and optimal scheduling."""
    
    def __init__(self):
        self.regions = {
            Region.NORTH_AMERICA_EAST: BusinessHours(
                region=Region.NORTH_AMERICA_EAST,
                timezone="America/New_York",
                weekdays=[1, 2, 3, 4, 5],  # Monday-Friday
                start_hour=9,
                end_hour=17,
                lunch_start=12,
                lunch_end=13,
                timezone_offset=-5  # EST, -4 for EDT
            ),
            Region.NORTH_AMERICA_CENTRAL: BusinessHours(
                region=Region.NORTH_AMERICA_CENTRAL,
                timezone="America/Chicago",
                weekdays=[1, 2, 3, 4, 5],
                start_hour=9,
                end_hour=17,
                lunch_start=12,
                lunch_end=13,
                timezone_offset=-6  # CST, -5 for CDT
            ),
            Region.NORTH_AMERICA_MOUNTAIN: BusinessHours(
                region=Region.NORTH_AMERICA_MOUNTAIN,
                timezone="America/Denver",
                weekdays=[1, 2, 3, 4, 5],
                start_hour=9,
                end_hour=17,
                lunch_start=12,
                lunch_end=13,
                timezone_offset=-7  # MST, -6 for MDT
            ),
            Region.NORTH_AMERICA_WEST: BusinessHours(
                region=Region.NORTH_AMERICA_WEST,
                timezone="America/Los_Angeles",
                weekdays=[1, 2, 3, 4, 5],
                start_hour=9,
                end_hour=17,
                lunch_start=12,
                lunch_end=13,
                timezone_offset=-8  # PST, -7 for PDT
            ),
            Region.EUROPE_LONDON: BusinessHours(
                region=Region.EUROPE_LONDON,
                timezone="Europe/London",
                weekdays=[1, 2, 3, 4, 5],
                start_hour=9,
                end_hour=17,
                lunch_start=12,
                lunch_end=13,
                timezone_offset=0  # GMT, +1 for BST
            ),
            Region.EUROPE_PARIS: BusinessHours(
                region=Region.EUROPE_PARIS,
                timezone="Europe/Paris",
                weekdays=[1, 2, 3, 4, 5],
                start_hour=9,
                end_hour=17,
                lunch_start=12,
                lunch_end=13,
                timezone_offset=1  # CET, +2 for CEST
            ),
            Region.EUROPE_BERLIN: BusinessHours(
                region=Region.EUROPE_BERLIN,
                timezone="Europe/Berlin",
                weekdays=[1, 2, 3, 4, 5],
                start_hour=9,
                end_hour=17,
                lunch_start=12,
                lunch_end=13,
                timezone_offset=1  # CET, +2 for CEST
            ),
            Region.ASIA_TOKYO: BusinessHours(
                region=Region.ASIA_TOKYO,
                timezone="Asia/Tokyo",
                weekdays=[1, 2, 3, 4, 5],
                start_hour=9,
                end_hour=18,
                lunch_start=12,
                lunch_end=13,
                timezone_offset=9  # JST
            ),
            Region.ASIA_SHANGHAI: BusinessHours(
                region=Region.ASIA_SHANGHAI,
                timezone="Asia/Shanghai",
                weekdays=[1, 2, 3, 4, 5],
                start_hour=9,
                end_hour=18,
                lunch_start=12,
                lunch_end=13,
                timezone_offset=8  # CST
            ),
            Region.ASIA_DUBAI: BusinessHours(
                region=Region.ASIA_DUBAI,
                timezone="Asia/Dubai",
                weekdays=[1, 2, 3, 4, 5],
                start_hour=9,
                end_hour=17,
                lunch_start=12,
                lunch_end=13,
                timezone_offset=4  # GST
            ),
            Region.AUSTRALIA_SYDNEY: BusinessHours(
                region=Region.AUSTRALIA_SYDNEY,
                timezone="Australia/Sydney",
                weekdays=[1, 2, 3, 4, 5],
                start_hour=9,
                end_hour=17,
                lunch_start=12,
                lunch_end=13,
                timezone_offset=10  # AEST, +11 for AEDT
            ),
            Region.UTC: BusinessHours(
                region=Region.UTC,
                timezone="UTC",
                weekdays=[1, 2, 3, 4, 5],
                start_hour=9,
                end_hour=17,
                timezone_offset=0
            )
        }
        
        # Optimal timing for LinkedIn activities
        self.optimal_timing = {
            Region.NORTH_AMERICA_EAST: OptimalTiming(
                region=Region.NORTH_AMERICA_EAST,
                best_hours=[(9, 11), (14, 16)],  # Best times for outreach
                avoid_hours=[(12, 13), (17, 19)],  # Lunch and commute
                peak_hours=[(10, 11), (15, 16)],  # Peak activity
                weekend_activity=True
            ),
            Region.NORTH_AMERICA_CENTRAL: OptimalTiming(
                region=Region.NORTH_AMERICA_CENTRAL,
                best_hours=[(9, 11), (14, 16)],
                avoid_hours=[(12, 13), (17, 19)],
                peak_hours=[(10, 11), (15, 16)],
                weekend_activity=True
            ),
            Region.NORTH_AMERICA_MOUNTAIN: OptimalTiming(
                region=Region.NORTH_AMERICA_MOUNTAIN,
                best_hours=[(9, 11), (14, 16)],
                avoid_hours=[(12, 13), (17, 19)],
                peak_hours=[(10, 11), (15, 16)],
                weekend_activity=True
            ),
            Region.NORTH_AMERICA_WEST: OptimalTiming(
                region=Region.NORTH_AMERICA_WEST,
                best_hours=[(9, 11), (14, 16)],
                avoid_hours=[(12, 13), (17, 19)],
                peak_hours=[(10, 11), (15, 16)],
                weekend_activity=True
            ),
            Region.EUROPE_LONDON: OptimalTiming(
                region=Region.EUROPE_LONDON,
                best_hours=[(9, 11), (14, 16)],
                avoid_hours=[(12, 13), (17, 19)],
                peak_hours=[(10, 11), (15, 16)],
                weekend_activity=False
            ),
            Region.EUROPE_PARIS: OptimalTiming(
                region=Region.EUROPE_PARIS,
                best_hours=[(9, 11), (14, 16)],
                avoid_hours=[(12, 13), (17, 19)],
                peak_hours=[(10, 11), (15, 16)],
                weekend_activity=False
            ),
            Region.EUROPE_BERLIN: OptimalTiming(
                region=Region.EUROPE_BERLIN,
                best_hours=[(9, 11), (14, 16)],
                avoid_hours=[(12, 13), (17, 19)],
                peak_hours=[(10, 11), (15, 16)],
                weekend_activity=False
            ),
            Region.ASIA_TOKYO: OptimalTiming(
                region=Region.ASIA_TOKYO,
                best_hours=[(9, 11), (14, 16)],
                avoid_hours=[(12, 13), (17, 19)],
                peak_hours=[(10, 11), (15, 16)],
                weekend_activity=False
            ),
            Region.ASIA_SHANGHAI: OptimalTiming(
                region=Region.ASIA_SHANGHAI,
                best_hours=[(9, 11), (14, 16)],
                avoid_hours=[(12, 13), (17, 19)],
                peak_hours=[(10, 11), (15, 16)],
                weekend_activity=False
            ),
            Region.ASIA_DUBAI: OptimalTiming(
                region=Region.ASIA_DUBAI,
                best_hours=[(9, 11), (14, 16)],
                avoid_hours=[(12, 13), (17, 19)],
                peak_hours=[(10, 11), (15, 16)],
                weekend_activity=False
            ),
            Region.AUSTRALIA_SYDNEY: OptimalTiming(
                region=Region.AUSTRALIA_SYDNEY,
                best_hours=[(9, 11), (14, 16)],
                avoid_hours=[(12, 13), (17, 19)],
                peak_hours=[(10, 11), (15, 16)],
                weekend_activity=False
            )
        }
    
    def get_timezone_info(self, region: Region) -> BusinessHours:
        """Get timezone information for a region."""
        return self.regions[region]
    
    def convert_utc_to_local(self, utc_time: datetime, region: Region) -> datetime:
        """Convert UTC time to local time for a region."""
        try:
            tz = pytz.timezone(self.regions[region].timezone)
            return utc_time.astimezone(tz)
        except Exception:
            # Fallback to simple offset calculation
            offset_hours = self.regions[region].timezone_offset
            return utc_time + timedelta(hours=offset_hours)
    
    def convert_local_to_utc(self, local_time: datetime, region: Region) -> datetime:
        """Convert local time to UTC for a region."""
        try:
            tz = pytz.timezone(self.regions[region].timezone)
            # Assume local_time is naive and in the region's timezone
            local_aware = tz.localize(local_time)
            return local_aware.astimezone(pytz.UTC)
        except Exception:
            # Fallback to simple offset calculation
            offset_hours = self.regions[region].timezone_offset
            return local_time - timedelta(hours=offset_hours)
    
    def is_business_hours(self, utc_time: datetime, region: Region) -> bool:
        """Check if UTC time falls within business hours for a region."""
        local_time = self.convert_utc_to_local(utc_time, region)
        business_hours = self.regions[region]
        
        # Check if it's a business day
        if local_time.weekday() not in business_hours.weekdays:
            return False
        
        # Check if it's within business hours
        current_hour = local_time.hour
        if not (business_hours.start_hour <= current_hour < business_hours.end_hour):
            return False
        
        # Check if it's during lunch break
        if (business_hours.lunch_start and business_hours.lunch_end and
            business_hours.lunch_start <= current_hour < business_hours.lunch_end):
            return False
        
        return True
    
    def get_next_business_hour(self, utc_time: datetime, region: Region) -> datetime:
        """Get the next business hour for a region."""
        local_time = self.convert_utc_to_local(utc_time, region)
        business_hours = self.regions[region]
        
        # If it's already business hours, return current time
        if self.is_business_hours(utc_time, region):
            return utc_time
        
        # Move to next business day
        next_day = local_time + timedelta(days=1)
        next_day = next_day.replace(hour=business_hours.start_hour, minute=0, second=0, microsecond=0)
        
        # Find next business day
        while next_day.weekday() not in business_hours.weekdays:
            next_day += timedelta(days=1)
        
        return self.convert_local_to_utc(next_day, region)
    
    def is_optimal_time(self, utc_time: datetime, region: Region) -> bool:
        """Check if time is optimal for LinkedIn activities."""
        local_time = self.convert_utc_to_local(utc_time, region)
        optimal_timing = self.optimal_timing.get(region)
        
        if not optimal_timing:
            return True  # Default to optimal if no specific timing
        
        current_hour = local_time.hour
        
        # Check if it's within best hours
        for start_hour, end_hour in optimal_timing.best_hours:
            if start_hour <= current_hour < end_hour:
                return True
        
        # Check if it's within avoid hours
        for start_hour, end_hour in optimal_timing.avoid_hours:
            if start_hour <= current_hour < end_hour:
                return False
        
        return False
    
    def get_optimal_schedule_time(
        self,
        base_time: datetime,
        region: Region,
        max_delay_hours: int = 48
    ) -> datetime:
        """Get optimal schedule time for a region."""
        local_time = self.convert_utc_to_local(base_time, region)
        optimal_timing = self.optimal_timing.get(region)
        
        if not optimal_timing:
            return self.get_next_business_hour(base_time, region)
        
        # Try to find optimal time within max delay
        for hours_ahead in range(0, max_delay_hours + 1):
            candidate_time = local_time + timedelta(hours=hours_ahead)
            candidate_utc = self.convert_local_to_utc(candidate_time, region)
            
            if (self.is_business_hours(candidate_utc, region) and
                self.is_optimal_time(candidate_utc, region)):
                return candidate_utc
        
        # Fallback to next business hour
        return self.get_next_business_hour(base_time, region)
    
    def calculate_delay_with_timezone(
        self,
        base_time: datetime,
        region: Region,
        operation_type: str,
        dux_account_delay_patterns: Dict[str, int]
    ) -> datetime:
        """Calculate delay considering timezone and optimal timing."""
        
        # Get base delay from DuxSoup account
        min_delay = dux_account_delay_patterns.get('min_delay', 30)
        max_delay = dux_account_delay_patterns.get('max_delay', 120)
        random_factor = dux_account_delay_patterns.get('random_factor', 0.2)
        
        # Calculate base delay
        import random
        base_delay_minutes = min_delay + random.uniform(0, max_delay - min_delay)
        
        # Apply operation-specific multipliers
        operation_multipliers = {
            'connection_request': 1.5,
            'message_send': 0.8,
            'profile_view': 0.6,
            'inmail_send': 1.2,
            'follow_up': 0.9
        }
        
        multiplier = operation_multipliers.get(operation_type, 1.0)
        delay_minutes = base_delay_minutes * multiplier
        
        # Add random factor to avoid patterns
        random_adjustment = random.uniform(-random_factor, random_factor)
        delay_minutes *= (1 + random_adjustment)
        
        # Ensure minimum delay
        delay_minutes = max(5, delay_minutes)
        
        # Calculate delay time
        delay_time = base_time + timedelta(minutes=delay_minutes)
        
        # Check if delay time is optimal, if not, adjust
        if not self.is_optimal_time(delay_time, region):
            delay_time = self.get_optimal_schedule_time(delay_time, region, max_delay_hours=24)
        
        return delay_time
    
    def get_region_from_timezone(self, timezone_str: str) -> Optional[Region]:
        """Get region from timezone string."""
        timezone_mapping = {
            'America/New_York': Region.NORTH_AMERICA_EAST,
            'America/Chicago': Region.NORTH_AMERICA_CENTRAL,
            'America/Denver': Region.NORTH_AMERICA_MOUNTAIN,
            'America/Los_Angeles': Region.NORTH_AMERICA_WEST,
            'Europe/London': Region.EUROPE_LONDON,
            'Europe/Paris': Region.EUROPE_PARIS,
            'Europe/Berlin': Region.EUROPE_BERLIN,
            'Asia/Tokyo': Region.ASIA_TOKYO,
            'Asia/Shanghai': Region.ASIA_SHANGHAI,
            'Asia/Dubai': Region.ASIA_DUBAI,
            'Australia/Sydney': Region.AUSTRALIA_SYDNEY,
            'UTC': Region.UTC
        }
        return timezone_mapping.get(timezone_str)
    
    def get_global_schedule_status(self) -> Dict[str, Any]:
        """Get global schedule status across all regions."""
        current_utc = utc_now()
        status = {}
        
        for region in Region:
            local_time = self.convert_utc_to_local(current_utc, region)
            business_hours = self.is_business_hours(current_utc, region)
            optimal_time = self.is_optimal_time(current_utc, region)
            
            status[region.value] = {
                'local_time': local_time.isoformat(),
                'business_hours': business_hours,
                'optimal_time': optimal_time,
                'timezone': self.regions[region].timezone,
                'weekday': local_time.weekday(),
                'hour': local_time.hour
            }
        
        return status
    
    def get_cross_region_optimal_time(
        self,
        base_time: datetime,
        regions: List[Region],
        operation_type: str
    ) -> Dict[Region, datetime]:
        """Get optimal times across multiple regions."""
        optimal_times = {}
        
        for region in regions:
            optimal_time = self.get_optimal_schedule_time(base_time, region)
            optimal_times[region] = optimal_time
        
        return optimal_times
    
    def calculate_timezone_delay(
        self,
        source_region: Region,
        target_region: Region,
        base_time: datetime
    ) -> timedelta:
        """Calculate delay needed when moving between timezones."""
        source_local = self.convert_utc_to_local(base_time, source_region)
        target_local = self.convert_utc_to_local(base_time, target_region)
        
        # Calculate time difference
        time_diff = target_local.hour - source_local.hour
        
        # If target is ahead, we need to delay
        if time_diff > 0:
            return timedelta(hours=time_diff)
        elif time_diff < 0:
            # If target is behind, we can execute immediately
            return timedelta(0)
        else:
            # Same time, no delay needed
            return timedelta(0)
