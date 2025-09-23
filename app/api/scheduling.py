"""
Scheduling API endpoints for LinkedIn automation.

This module provides REST API endpoints for managing:
- DuxSoup account registration and management
- Operation scheduling and execution
- Campaign scheduling and rescheduling
- Timezone management and optimal timing
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import asyncio

from app.services.scheduling_service import (
    SchedulingService, ScheduleRequest, OperationType, 
    DuxSoupAccount, ScheduleStatus
)
from app.services.timezone_service import TimezoneService, Region
from app.services.transaction_service import TransactionService
from database.database import get_session
from app.utils.timestamps import utc_now

router = APIRouter(prefix="/api/scheduling", tags=["scheduling"])

# Global services (in production, these would be dependency injected)
scheduling_service = SchedulingService()
timezone_service = TimezoneService()

# Pydantic models for API requests/responses
class DuxSoupAccountRequest(BaseModel):
    account_id: str
    username: str
    timezone: str
    operational_hours: Dict[str, Any]
    daily_limits: Dict[str, int]
    delay_patterns: Optional[Dict[str, int]] = None

class ScheduleOperationRequest(BaseModel):
    operation_type: str
    contact_id: str
    campaign_id: str
    user_id: str
    dux_account_id: str
    priority: int = 1
    preferred_time: Optional[datetime] = None
    max_delay_hours: int = 48
    metadata: Optional[Dict[str, Any]] = None

class RescheduleCampaignRequest(BaseModel):
    campaign_id: str
    delay_hours: int = 24

class TimezoneStatusResponse(BaseModel):
    region: str
    local_time: str
    business_hours: bool
    optimal_time: bool
    timezone: str
    weekday: int
    hour: int

@router.post("/accounts/register")
async def register_dux_account(account_request: DuxSoupAccountRequest):
    """Register a new DuxSoup account for scheduling."""
    try:
        # Create DuxSoup account
        account = DuxSoupAccount(
            account_id=account_request.account_id,
            username=account_request.username,
            timezone=account_request.timezone,
            operational_hours=account_request.operational_hours,
            daily_limits=account_request.daily_limits,
            current_usage={key: 0 for key in account_request.daily_limits.keys()},
            delay_patterns=account_request.delay_patterns or {
                "min_delay": 30,
                "max_delay": 120,
                "random_factor": 0.2
            }
        )
        
        # Register with scheduling service
        scheduling_service.register_dux_account(account)
        
        return {
            "success": True,
            "message": f"DuxSoup account {account_request.username} registered successfully",
            "account_id": account_request.account_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to register account: {str(e)}")

@router.get("/accounts")
async def list_dux_accounts():
    """List all registered DuxSoup accounts."""
    try:
        accounts = []
        for account_id, account in scheduling_service.dux_accounts.items():
            accounts.append({
                "account_id": account_id,
                "username": account.username,
                "timezone": account.timezone,
                "is_active": account.is_active,
                "current_usage": account.current_usage,
                "daily_limits": account.daily_limits,
                "last_activity": account.last_activity.isoformat() if account.last_activity else None
            })
        
        return {
            "success": True,
            "accounts": accounts,
            "total": len(accounts)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list accounts: {str(e)}")

@router.get("/accounts/{account_id}/status")
async def get_account_status(account_id: str):
    """Get detailed status of a DuxSoup account."""
    try:
        status = scheduling_service.get_dux_account_status(account_id)
        
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        
        return {
            "success": True,
            "status": status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get account status: {str(e)}")

@router.post("/operations/schedule")
async def schedule_operation(request: ScheduleOperationRequest, background_tasks: BackgroundTasks):
    """Schedule a new operation for execution."""
    try:
        # Convert operation type string to enum
        operation_type = OperationType(request.operation_type)
        
        # Create schedule request
        schedule_request = ScheduleRequest(
            operation_type=operation_type,
            contact_id=request.contact_id,
            campaign_id=request.campaign_id,
            user_id=request.user_id,
            dux_account_id=request.dux_account_id,
            priority=request.priority,
            preferred_time=request.preferred_time,
            max_delay_hours=request.max_delay_hours,
            metadata=request.metadata
        )
        
        # Schedule the operation
        operation = scheduling_service.schedule_operation(schedule_request)
        
        return {
            "success": True,
            "operation_id": operation.operation_id,
            "scheduled_time": operation.scheduled_time.isoformat(),
            "status": operation.status.value,
            "estimated_duration": operation.estimated_duration
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid operation type: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule operation: {str(e)}")

@router.get("/operations/due")
async def get_due_operations():
    """Get operations that are due for execution."""
    try:
        due_operations = scheduling_service.get_operations_due()
        
        operations = []
        for op in due_operations:
            operations.append({
                "operation_id": op.operation_id,
                "operation_type": op.request.operation_type.value,
                "contact_id": op.request.contact_id,
                "campaign_id": op.request.campaign_id,
                "scheduled_time": op.scheduled_time.isoformat(),
                "priority": op.request.priority,
                "status": op.status.value
            })
        
        return {
            "success": True,
            "operations": operations,
            "total": len(operations)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get due operations: {str(e)}")

@router.post("/operations/{operation_id}/execute")
async def execute_operation(operation_id: str, background_tasks: BackgroundTasks):
    """Execute a scheduled operation."""
    try:
        if operation_id not in scheduling_service.scheduled_operations:
            raise HTTPException(status_code=404, detail="Operation not found")
        
        operation = scheduling_service.scheduled_operations[operation_id]
        
        # Execute the operation
        success = scheduling_service.execute_operation(operation)
        
        return {
            "success": success,
            "operation_id": operation_id,
            "status": operation.status.value,
            "message": "Operation executed successfully" if success else "Operation failed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute operation: {str(e)}")

@router.get("/campaigns/{campaign_id}/status")
async def get_campaign_schedule_status(campaign_id: str):
    """Get scheduling status for a campaign."""
    try:
        status = scheduling_service.get_schedule_status(campaign_id)
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "status": status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get campaign status: {str(e)}")

@router.post("/campaigns/{campaign_id}/reschedule")
async def reschedule_campaign(campaign_id: str, request: RescheduleCampaignRequest):
    """Reschedule all operations in a campaign."""
    try:
        scheduling_service.reschedule_campaign(campaign_id, request.delay_hours)
        
        return {
            "success": True,
            "message": f"Campaign {campaign_id} rescheduled with {request.delay_hours} hour delay",
            "campaign_id": campaign_id,
            "delay_hours": request.delay_hours
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reschedule campaign: {str(e)}")

@router.get("/timezones/status")
async def get_global_timezone_status():
    """Get global timezone status across all regions."""
    try:
        status = timezone_service.get_global_schedule_status()
        
        return {
            "success": True,
            "timezones": status,
            "current_utc": utc_now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get timezone status: {str(e)}")

@router.get("/timezones/optimal/{region}")
async def get_optimal_schedule_time(region: str, hours_ahead: int = 24):
    """Get optimal schedule time for a specific region."""
    try:
        region_enum = Region(region)
        base_time = utc_now()
        optimal_time = timezone_service.get_optimal_schedule_time(base_time, region_enum, hours_ahead)
        
        return {
            "success": True,
            "region": region,
            "base_time": base_time.isoformat(),
            "optimal_time": optimal_time.isoformat(),
            "hours_ahead": hours_ahead
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid region: {region}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get optimal time: {str(e)}")

@router.post("/operations/process-due")
async def process_due_operations(background_tasks: BackgroundTasks):
    """Process all due operations (background task)."""
    try:
        due_operations = scheduling_service.get_operations_due()
        
        if not due_operations:
            return {
                "success": True,
                "message": "No operations due for execution",
                "processed": 0
            }
        
        # Process operations in background
        async def process_operations():
            processed = 0
            for operation in due_operations:
                try:
                    success = scheduling_service.execute_operation(operation)
                    processed += 1
                except Exception as e:
                    print(f"Error processing operation {operation.operation_id}: {e}")
        
        background_tasks.add_task(process_operations)
        
        return {
            "success": True,
            "message": f"Processing {len(due_operations)} due operations",
            "due_count": len(due_operations)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process due operations: {str(e)}")

@router.get("/health")
async def scheduling_health():
    """Health check for scheduling services."""
    try:
        # Check scheduling service
        total_operations = len(scheduling_service.scheduled_operations)
        due_operations = len(scheduling_service.get_operations_due())
        registered_accounts = len(scheduling_service.dux_accounts)
        
        # Check timezone service
        timezone_status = timezone_service.get_global_schedule_status()
        active_regions = len([tz for tz in timezone_status.values() if tz['business_hours']])
        
        return {
            "status": "healthy",
            "timestamp": utc_now().isoformat(),
            "scheduling": {
                "total_operations": total_operations,
                "due_operations": due_operations,
                "registered_accounts": registered_accounts
            },
            "timezones": {
                "total_regions": len(timezone_status),
                "active_regions": active_regions
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": utc_now().isoformat(),
            "error": str(e)
        }
