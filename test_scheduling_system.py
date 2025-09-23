#!/usr/bin/env python3
"""
Test script for the advanced scheduling system with DuxSoup integration.
"""

import asyncio
import sys
sys.path.append('.')
from datetime import datetime, timedelta
from app.services.scheduling_service import (
    SchedulingService, ScheduleRequest, OperationType, 
    DuxSoupAccount, ScheduleStatus
)
from app.services.timezone_service import TimezoneService, Region
from app.utils.timestamps import utc_now


async def test_scheduling_system():
    try:
        print('🧪 Testing Advanced Scheduling System...')
        
        # Initialize services
        scheduling_service = SchedulingService()
        timezone_service = TimezoneService()
        
        # Test 1: Register DuxSoup accounts for different regions
        print('\n1. Registering DuxSoup accounts...')
        
        # East Coast account
        east_coast_account = DuxSoupAccount(
            account_id="dux-east-001",
            username="east_coast_automation",
            timezone="America/New_York",
            operational_hours={
                "start": "09:00",
                "end": "17:00",
                "days": [1, 2, 3, 4, 5]  # Monday-Friday
            },
            daily_limits={
                "connections": 50,
                "messages": 30,
                "profile_views": 100,
                "inmails": 10
            },
            current_usage={
                "connections": 0,
                "messages": 0,
                "profile_views": 0,
                "inmails": 0
            },
            delay_patterns={
                "min_delay": 30,
                "max_delay": 120,
                "random_factor": 0.2
            }
        )
        
        # West Coast account
        west_coast_account = DuxSoupAccount(
            account_id="dux-west-001",
            username="west_coast_automation",
            timezone="America/Los_Angeles",
            operational_hours={
                "start": "09:00",
                "end": "17:00",
                "days": [1, 2, 3, 4, 5]
            },
            daily_limits={
                "connections": 50,
                "messages": 30,
                "profile_views": 100,
                "inmails": 10
            },
            current_usage={
                "connections": 0,
                "messages": 0,
                "profile_views": 0,
                "inmails": 0
            },
            delay_patterns={
                "min_delay": 45,
                "max_delay": 150,
                "random_factor": 0.3
            }
        )
        
        # Register accounts
        scheduling_service.register_dux_account(east_coast_account)
        scheduling_service.register_dux_account(west_coast_account)
        print('✅ Registered 2 DuxSoup accounts')
        
        # Test 2: Test timezone calculations
        print('\n2. Testing timezone calculations...')
        
        current_time = utc_now()
        print(f'Current UTC time: {current_time.isoformat()}')
        
        # Test different regions
        for region in [Region.NORTH_AMERICA_EAST, Region.NORTH_AMERICA_WEST, Region.EUROPE_LONDON]:
            local_time = timezone_service.convert_utc_to_local(current_time, region)
            is_business = timezone_service.is_business_hours(current_time, region)
            is_optimal = timezone_service.is_optimal_time(current_time, region)
            
            print(f'  {region.value}: {local_time.strftime("%Y-%m-%d %H:%M:%S")} (Business: {is_business}, Optimal: {is_optimal})')
        
        # Test 3: Schedule operations with different priorities
        print('\n3. Scheduling operations...')
        
        # High priority connection request
        high_priority_request = ScheduleRequest(
            operation_type=OperationType.CONNECTION_REQUEST,
            contact_id="contact-001",
            campaign_id="campaign-001",
            user_id="user-001",
            dux_account_id="dux-east-001",
            priority=1,
            preferred_time=current_time + timedelta(hours=2),
            max_delay_hours=24,
            metadata={"target_company": "Tech Corp", "target_role": "CTO"}
        )
        
        # Medium priority message
        medium_priority_request = ScheduleRequest(
            operation_type=OperationType.MESSAGE_SEND,
            contact_id="contact-002",
            campaign_id="campaign-001",
            user_id="user-001",
            dux_account_id="dux-west-001",
            priority=3,
            max_delay_hours=48,
            metadata={"message_template": "follow_up_1", "personalization": "company_size"}
        )
        
        # Low priority profile view
        low_priority_request = ScheduleRequest(
            operation_type=OperationType.PROFILE_VIEW,
            contact_id="contact-003",
            campaign_id="campaign-002",
            user_id="user-002",
            dux_account_id="dux-east-001",
            priority=5,
            max_delay_hours=72,
            metadata={"research_phase": "initial", "target_industry": "finance"}
        )
        
        # Schedule operations
        operations = []
        for request in [high_priority_request, medium_priority_request, low_priority_request]:
            operation = scheduling_service.schedule_operation(request)
            operations.append(operation)
            print(f'  ✅ Scheduled {request.operation_type.value} for {request.contact_id} at {operation.scheduled_time.isoformat()}')
        
        # Test 4: Test delay calculations with timezone awareness
        print('\n4. Testing delay calculations...')
        
        for operation in operations:
            # Calculate delay considering timezone
            region = timezone_service.get_region_from_timezone(operation.dux_account.timezone)
            if region:
                optimal_time = timezone_service.get_optimal_schedule_time(
                    operation.scheduled_time,
                    region,
                    max_delay_hours=24
                )
                
                delay_hours = (optimal_time - operation.scheduled_time).total_seconds() / 3600
                print(f'  {operation.operation_id}: Optimal delay = {delay_hours:.2f} hours')
        
        # Test 5: Simulate operation execution
        print('\n5. Simulating operation execution...')
        
        # Get operations due for execution
        due_operations = scheduling_service.get_operations_due()
        print(f'  Found {len(due_operations)} operations due for execution')
        
        # Execute operations
        for operation in due_operations[:2]:  # Execute first 2
            success = scheduling_service.execute_operation(operation)
            status = "✅ Success" if success else "❌ Failed"
            print(f'  {operation.operation_id}: {status}')
        
        # Test 6: Test retry logic
        print('\n6. Testing retry logic...')
        
        # Find a failed operation and retry
        failed_operations = [op for op in operations if op.status == ScheduleStatus.FAILED]
        if failed_operations:
            operation = failed_operations[0]
            retry_success = scheduling_service.handle_retry(operation)
            print(f'  Retry for {operation.operation_id}: {"✅ Scheduled" if retry_success else "❌ Max retries reached"}')
        
        # Test 7: Get campaign status
        print('\n7. Campaign status...')
        
        campaign_status = scheduling_service.get_schedule_status("campaign-001")
        print(f'  Campaign 001 status: {campaign_status}')
        
        # Test 8: Test rescheduling
        print('\n8. Testing campaign rescheduling...')
        
        scheduling_service.reschedule_campaign("campaign-001", delay_hours=6)
        print('  ✅ Rescheduled campaign 001 with 6-hour delay')
        
        # Test 9: Get DuxSoup account status
        print('\n9. DuxSoup account status...')
        
        for account_id in ["dux-east-001", "dux-west-001"]:
            status = scheduling_service.get_dux_account_status(account_id)
            print(f'  {account_id}: {status["username"]} - Usage: {status["current_usage"]}')
        
        # Test 10: Global timezone status
        print('\n10. Global timezone status...')
        
        global_status = timezone_service.get_global_schedule_status()
        for region, info in global_status.items():
            print(f'  {region}: {info["local_time"]} (Business: {info["business_hours"]}, Optimal: {info["optimal_time"]})')
        
        print('\n🎉 Advanced scheduling system test completed successfully!')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_scheduling_system())
