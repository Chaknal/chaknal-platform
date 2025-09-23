from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

from database.database import get_session
from app.models.campaign import Campaign
from app.models.campaign_contact import CampaignContact
from app.models.contact import Contact
from app.models.user import User

router = APIRouter()

# =============================================================================
# SCHEMAS
# =============================================================================

class ContactAssignmentRequest(BaseModel):
    """Schema for assigning contacts to users"""
    contact_ids: List[str] = Field(..., description="List of contact IDs to assign")
    assigned_to: str = Field(..., description="User ID to assign contacts to")

class BulkAssignmentRequest(BaseModel):
    """Schema for bulk assignment operations"""
    campaign_id: str = Field(..., description="Campaign ID")
    assigned_to: str = Field(..., description="User ID to assign contacts to")
    assignment_type: str = Field(..., description="Type: 'all', 'unassigned', 'by_status'")
    status_filter: Optional[str] = Field(None, description="Status filter for 'by_status' type")

class UserAssignmentStats(BaseModel):
    """Schema for user assignment statistics"""
    user_id: str
    user_email: str
    total_assigned: int
    pending_contacts: int
    active_contacts: int
    accepted_contacts: int
    responded_contacts: int
    completed_contacts: int

class AssignmentResponse(BaseModel):
    """Schema for assignment operation response"""
    success: bool
    assigned_count: int
    message: str
    assigned_contacts: List[str]

# =============================================================================
# USER ASSIGNMENT ENDPOINTS
# =============================================================================

@router.post("/campaigns/{campaign_id}/contacts/assign", response_model=AssignmentResponse, tags=["Contact Assignment"])
async def assign_contacts_to_user(
    campaign_id: str,
    assignment: ContactAssignmentRequest,
    session: AsyncSession = Depends(get_session)
):
    """Assign specific contacts to a user"""
    try:
        # Verify campaign exists
        campaign_query = select(Campaign).where(Campaign.campaign_id == campaign_id)
        campaign_result = await session.execute(campaign_query)
        campaign = campaign_result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Verify user exists
        user_query = select(User).where(User.id == assignment.assigned_to)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update campaign contacts
        assigned_contacts = []
        for contact_id in assignment.contact_ids:
            # Find all campaign contacts for this contact (handle duplicates)
            cc_query = select(CampaignContact).where(
                CampaignContact.campaign_id == campaign_id,
                CampaignContact.contact_id == contact_id
            )
            cc_result = await session.execute(cc_query)
            campaign_contacts = cc_result.scalars().all()
            
            if campaign_contacts:
                # Update all campaign contact records for this contact
                for campaign_contact in campaign_contacts:
                    campaign_contact.assigned_to = assignment.assigned_to
                    # Only set to pending if not already processed
                    if campaign_contact.status not in ["active", "completed", "responded"]:
                        campaign_contact.status = "pending"  # Set to pending for sequence launch
                    campaign_contact.updated_at = datetime.utcnow()
                assigned_contacts.append(contact_id)
        
        await session.commit()
        
        return AssignmentResponse(
            success=True,
            assigned_count=len(assigned_contacts),
            message=f"Successfully assigned {len(assigned_contacts)} contacts to user",
            assigned_contacts=assigned_contacts
        )
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to assign contacts: {str(e)}")

@router.post("/campaigns/{campaign_id}/contacts/bulk-assign", response_model=AssignmentResponse, tags=["Contact Assignment"])
async def bulk_assign_contacts(
    campaign_id: str,
    assignment: BulkAssignmentRequest,
    session: AsyncSession = Depends(get_session)
):
    """Bulk assign contacts to a user based on criteria"""
    try:
        # Verify campaign exists
        campaign_query = select(Campaign).where(Campaign.campaign_id == campaign_id)
        campaign_result = await session.execute(campaign_query)
        campaign = campaign_result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Verify user exists
        user_query = select(User).where(User.id == assignment.assigned_to)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Build query based on assignment type
        query = select(CampaignContact).where(CampaignContact.campaign_id == campaign_id)
        
        if assignment.assignment_type == "unassigned":
            query = query.where(CampaignContact.assigned_to.is_(None))
        elif assignment.assignment_type == "by_status" and assignment.status_filter:
            query = query.where(CampaignContact.status == assignment.status_filter)
        # For "all", no additional filter needed
        
        result = await session.execute(query)
        campaign_contacts = result.scalars().all()
        
        # Update assignments
        assigned_count = 0
        for cc in campaign_contacts:
            cc.assigned_to = assignment.assigned_to
            cc.updated_at = datetime.utcnow()
            assigned_count += 1
        
        await session.commit()
        
        return AssignmentResponse(
            success=True,
            assigned_count=assigned_count,
            message=f"Successfully assigned {assigned_count} contacts to user",
            assigned_contacts=[cc.contact_id for cc in campaign_contacts]
        )
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to bulk assign contacts: {str(e)}")

@router.get("/campaigns/{campaign_id}/assignments/stats", response_model=List[UserAssignmentStats], tags=["Contact Assignment"])
async def get_assignment_stats(
    campaign_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get assignment statistics for all users in a campaign"""
    try:
        # Get all users with their assignment counts
        query = select(
            User.id,
            User.email,
            func.count(CampaignContact.campaign_contact_id).label('total_assigned'),
            func.count(CampaignContact.campaign_contact_id).filter(
                CampaignContact.status == 'pending'
            ).label('pending_contacts'),
            func.count(CampaignContact.campaign_contact_id).filter(
                CampaignContact.status == 'active'
            ).label('active_contacts'),
            func.count(CampaignContact.campaign_contact_id).filter(
                CampaignContact.status == 'accepted'
            ).label('accepted_contacts'),
            func.count(CampaignContact.campaign_contact_id).filter(
                CampaignContact.status == 'responded'
            ).label('responded_contacts'),
            func.count(CampaignContact.campaign_contact_id).filter(
                CampaignContact.status == 'completed'
            ).label('completed_contacts')
        ).select_from(
            User
        ).outerjoin(
            CampaignContact, 
            (CampaignContact.assigned_to == User.id) & 
            (CampaignContact.campaign_id == campaign_id)
        ).group_by(User.id, User.email)
        
        result = await session.execute(query)
        stats = result.all()
        
        return [
            UserAssignmentStats(
                user_id=stat.id,
                user_email=stat.email,
                total_assigned=stat.total_assigned or 0,
                pending_contacts=stat.pending_contacts or 0,
                active_contacts=stat.active_contacts or 0,
                accepted_contacts=stat.accepted_contacts or 0,
                responded_contacts=stat.responded_contacts or 0,
                completed_contacts=stat.completed_contacts or 0
            ) for stat in stats
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get assignment stats: {str(e)}")

@router.get("/campaigns/{campaign_id}/contacts/unassigned", response_model=List[Dict[str, Any]], tags=["Contact Assignment"])
async def get_unassigned_contacts(
    campaign_id: str,
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session)
):
    """Get unassigned contacts in a campaign"""
    try:
        query = select(CampaignContact, Contact).join(
            Contact, CampaignContact.contact_id == Contact.contact_id
        ).where(
            CampaignContact.campaign_id == campaign_id,
            CampaignContact.assigned_to.is_(None)
        ).offset(offset).limit(limit)
        
        result = await session.execute(query)
        contacts = result.all()
        
        return [
            {
                "campaign_contact_id": cc.campaign_contact_id,
                "contact_id": cc.contact_id,
                "full_name": contact.full_name or f"{contact.first_name} {contact.last_name}".strip(),
                "company_name": contact.company_name,
                "job_title": contact.job_title,
                "status": cc.status,
                "enrolled_at": cc.enrolled_at
            } for cc, contact in contacts
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get unassigned contacts: {str(e)}")

@router.get("/campaigns/{campaign_id}/contacts/assigned", response_model=List[Dict[str, Any]], tags=["Contact Assignment"])
async def get_assigned_contacts(
    campaign_id: str,
    user_id: Optional[str] = Query(None, description="Filter by assigned user"),
    status: Optional[str] = Query(None, description="Filter by contact status"),
    limit: int = Query(1000, le=5000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session)
):
    """Get all assigned contacts in a campaign with optional filtering"""
    try:
        query = select(CampaignContact, Contact, User).join(
            Contact, CampaignContact.contact_id == Contact.contact_id
        ).join(
            User, CampaignContact.assigned_to == User.id
        ).where(
            CampaignContact.campaign_id == campaign_id,
            CampaignContact.assigned_to.isnot(None)
        )
        
        # Apply filters
        if user_id:
            query = query.where(CampaignContact.assigned_to == user_id)
        if status:
            query = query.where(CampaignContact.status == status)
            
        query = query.offset(offset).limit(limit)
        
        result = await session.execute(query)
        contacts = result.all()
        
        return [
            {
                "campaign_contact_id": cc.campaign_contact_id,
                "contact_id": cc.contact_id,
                "full_name": contact.full_name or f"{contact.first_name} {contact.last_name}".strip(),
                "company_name": contact.company_name,
                "job_title": contact.job_title,
                "status": cc.status,
                "enrolled_at": cc.enrolled_at,
                "assigned_to": user.id,
                "assigned_to_email": user.email,
                "assigned_to_name": user.email.split('@')[0].replace('.', ' ').title(),
                "sequence_step": cc.sequence_step
            } for cc, contact, user in contacts
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get assigned contacts: {str(e)}")

@router.delete("/campaigns/{campaign_id}/contacts/{contact_id}/assignment", tags=["Contact Assignment"])
async def unassign_contact(
    campaign_id: str,
    contact_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Remove assignment from a contact"""
    try:
        query = select(CampaignContact).where(
            CampaignContact.campaign_id == campaign_id,
            CampaignContact.contact_id == contact_id
        )
        result = await session.execute(query)
        campaign_contact = result.scalar_one_or_none()
        
        if not campaign_contact:
            raise HTTPException(status_code=404, detail="Campaign contact not found")
        
        campaign_contact.assigned_to = None
        campaign_contact.updated_at = datetime.utcnow()
        
        await session.commit()
        
        return {"success": True, "message": "Contact unassigned successfully"}
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to unassign contact: {str(e)}")

# =============================================================================
# SEQUENCE LAUNCHER ENDPOINTS
# =============================================================================

@router.post("/campaigns/{campaign_id}/launch-sequence", tags=["Sequence Launcher"])
async def launch_sequence_for_user(
    campaign_id: str,
    request: dict,
    session: AsyncSession = Depends(get_session)
):
    """Launch sequence for all contacts assigned to a specific user using DuxSoup API"""
    try:
        user_id = request.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        # Verify campaign exists
        campaign_query = select(Campaign).where(Campaign.campaign_id == campaign_id)
        campaign_result = await session.execute(campaign_query)
        campaign = campaign_result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Verify user exists
        user_query = select(User).where(User.id == user_id)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Use DuxSoup sequence launcher
        from app.services.dux_sequence_launcher import DuxSequenceLauncher
        launcher = DuxSequenceLauncher()
        
        result = await launcher.launch_sequence_for_user(
            campaign_id=campaign_id,
            user_id=user_id,
            session=session
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "launched_count": result["launched_count"],
                "user_email": user.email,
                "details": result.get("results", [])
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to launch sequence: {str(e)}")

@router.post("/webhooks/dux-raw", tags=["Webhooks"])
async def handle_dux_raw_webhook(
    request: dict,
    session: AsyncSession = Depends(get_session)
):
    """Store raw DuxSoup webhook data in the database for analysis"""
    try:
        from app.models.webhook_event import WebhookEvent
        from app.models.contact import Contact
        from app.models.campaign_contact import CampaignContact
        from sqlalchemy import select
        import uuid
        from datetime import datetime
        
        # Extract webhook data (matching DuxSoup's actual format)
        event_type = request.get("type", request.get("event_type", "unknown"))
        event_name = request.get("event", request.get("event_name", "unknown"))
        dux_user_id = request.get("dux_user_id", "unknown")
        profile_url = request.get("profile_url") or request.get("profile")
        contact_id = request.get("contact_id")
        campaign_id = request.get("campaign_id")
        
        # Try to find contact by profile URL if not provided
        if not contact_id and profile_url:
            result = await session.execute(
                select(Contact).where(Contact.linkedin_url == profile_url)
            )
            contact = result.scalar_one_or_none()
            if contact:
                contact_id = contact.contact_id
                
                # Find campaign for this contact
                cc_result = await session.execute(
                    select(CampaignContact).where(
                        CampaignContact.contact_id == contact_id,
                        CampaignContact.assigned_to.isnot(None)
                    ).order_by(CampaignContact.created_at.desc()).limit(1)
                )
                campaign_contact = cc_result.scalar_one_or_none()
                if campaign_contact:
                    campaign_id = campaign_contact.campaign_id
        
        # Create webhook event record
        webhook_event = WebhookEvent(
            event_id=str(uuid.uuid4()),
            dux_user_id=dux_user_id,
            event_type=event_type,
            event_name=event_name,
            contact_id=contact_id,
            campaign_id=campaign_id,
            raw_data=request,
            processed=False,
            created_at=datetime.utcnow()
        )
        
        session.add(webhook_event)
        await session.commit()
        
        # Log the event for debugging
        print(f"📥 Stored webhook event: {event_type}:{event_name} for contact {contact_id}")
        if profile_url:
            print(f"   Profile URL: {profile_url}")
        
        return {
            "success": True,
            "message": "Webhook event stored successfully",
            "event_id": webhook_event.event_id,
            "event_type": event_type,
            "event_name": event_name
        }
        
    except Exception as e:
        await session.rollback()
        print(f"❌ Error storing webhook event: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to store webhook event: {str(e)}")

@router.get("/webhooks/events", tags=["Webhooks"])
async def get_webhook_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    contact_id: Optional[str] = Query(None, description="Filter by contact ID"),
    campaign_id: Optional[str] = Query(None, description="Filter by campaign ID"),
    limit: int = Query(50, le=200, description="Number of events to return"),
    offset: int = Query(0, ge=0, description="Number of events to skip"),
    session: AsyncSession = Depends(get_session)
):
    """Get webhook events for debugging and analysis"""
    try:
        from app.models.webhook_event import WebhookEvent
        from sqlalchemy import select, and_, desc
        
        # Build query with filters
        query = select(WebhookEvent)
        conditions = []
        
        if event_type:
            conditions.append(WebhookEvent.event_type == event_type)
        if contact_id:
            conditions.append(WebhookEvent.contact_id == contact_id)
        if campaign_id:
            conditions.append(WebhookEvent.campaign_id == campaign_id)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(desc(WebhookEvent.created_at)).offset(offset).limit(limit)
        
        result = await session.execute(query)
        events = result.scalars().all()
        
        return {
            "events": [
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "event_name": event.event_name,
                    "dux_user_id": event.dux_user_id,
                    "contact_id": event.contact_id,
                    "campaign_id": event.campaign_id,
                    "processed": event.processed,
                    "created_at": event.created_at.isoformat() if event.created_at else None,
                    "raw_data": event.raw_data
                } for event in events
            ],
            "total": len(events),
            "filters": {
                "event_type": event_type,
                "contact_id": contact_id,
                "campaign_id": campaign_id
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get webhook events: {str(e)}")

@router.post("/campaigns/{campaign_id}/create-dux-campaign", tags=["Campaigns"])
async def create_dux_campaign(
    campaign_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Create a campaign in DuxSoup for testing"""
    try:
        from app.services.dux_sequence_launcher import DuxSequenceLauncher
        from sqlalchemy import select
        from app.models.campaign import Campaign
        
        # Get campaign details
        campaign_query = select(Campaign).where(Campaign.campaign_id == campaign_id)
        campaign_result = await session.execute(campaign_query)
        campaign = campaign_result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Get DuxSoup user configuration
        launcher = DuxSequenceLauncher()
        dux_config = await launcher.get_dux_user_config(campaign.dux_user_id, session)
        if not dux_config:
            raise HTTPException(status_code=404, detail="DuxSoup user not configured")
        
        # Test campaign creation
        from app.services.duxwrap_new import DuxSoupWrapper
        async with DuxSoupWrapper(dux_config) as wrapper:
            # Test getting existing campaigns
            campaigns_result = await wrapper.get_campaigns()
            
            # Test creating campaign
            campaign_result = await wrapper.create_campaign(
                campaign_name=campaign.name,
                campaign_id=campaign.campaign_id,
                description=campaign.description
            )
            
            return {
                "success": True,
                "message": "Campaign creation test completed",
                "existing_campaigns": campaigns_result.data if campaigns_result.success else None,
                "campaign_creation": {
                    "success": campaign_result.success,
                    "data": campaign_result.data if campaign_result.success else None,
                    "error": campaign_result.error if not campaign_result.success else None
                }
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test campaign creation: {str(e)}")

@router.post("/webhooks/dux-status-update", tags=["Webhooks"])
async def handle_dux_status_update(
    request: dict,
    session: AsyncSession = Depends(get_session)
):
    """Handle comprehensive DuxSoup webhook updates including messages and responses"""
    try:
        # Extract webhook data (handle both our format and DuxSoup's format)
        campaign_id = request.get("campaign_id")
        contact_id = request.get("contact_id") 
        
        # Check for status in payload (DuxSoup format) or top level (our format)
        payload = request.get("payload", {})
        status = request.get("status") or payload.get("status")
        
        profile_url = request.get("profile_url") or request.get("profile")
        message_content = request.get("message_content") or request.get("message")
        message_direction = request.get("message_direction", "sent")
        linkedin_message_id = request.get("linkedin_message_id")
        thread_url = request.get("thread_url")
        event_type = request.get("event_type", "status_update")
        
        # Extract action from payload for better event type detection
        action = payload.get("action", "")
        
        # Map DuxSoup actions to our status system
        if action == "INVITATION_ACCEPT" or (action == "connection_request" and status == "accepted"):
            status = "accepted"
        elif action == "INVITATION_DECLINE" or (action == "connection_request" and status == "declined"):
            status = "declined"
        elif action == "MESSAGE" and message_content:
            status = "replied"
        
        # Handle DuxSoup's format - try to find contact by LinkedIn profile URL
        if not contact_id and profile_url:
            # Try to find contact by LinkedIn URL
            from sqlalchemy import select
            from app.models.contact import Contact
            result = await session.execute(
                select(Contact).where(Contact.linkedin_url == profile_url)
            )
            contact = result.scalar_one_or_none()
            if contact:
                contact_id = contact.contact_id
                # Find campaign for this contact
                from app.models.campaign_contact import CampaignContact
                cc_result = await session.execute(
                    select(CampaignContact).where(
                        CampaignContact.contact_id == contact_id,
                        CampaignContact.assigned_to.isnot(None)
                    ).order_by(CampaignContact.created_at.desc()).limit(1)
                )
                campaign_contact = cc_result.scalar_one_or_none()
                if campaign_contact:
                    campaign_id = campaign_contact.campaign_id
        
        # Log the incoming webhook for debugging
        print(f"📥 Received DuxSoup webhook: {event_type} for contact {contact_id}")
        print(f"   Action: {action}, Status: {status}, Direction: {message_direction}")
        if message_content:
            print(f"   Message: {message_content[:100]}...")
        if payload:
            print(f"   Payload: {payload}")
        
        if not all([campaign_id, contact_id]):
            raise HTTPException(status_code=400, detail="Missing required fields: campaign_id, contact_id")
        
        # Use DuxSoup sequence launcher to handle the webhook
        from app.services.dux_sequence_launcher import DuxSequenceLauncher
        launcher = DuxSequenceLauncher()
        
        # Handle different types of webhook events
        if event_type == "message" and message_content:
            # Handle message content
            result = await launcher.handle_message_webhook(
                campaign_id=campaign_id,
                contact_id=contact_id,
                message_content=message_content,
                message_direction=message_direction,
                linkedin_message_id=linkedin_message_id,
                thread_url=thread_url,
                profile_url=profile_url,
                session=session
            )
        else:
            # Handle status updates
            result = await launcher.update_contact_status_from_webhook(
                campaign_id=campaign_id,
                contact_id=contact_id,
                status=status,
                session=session
            )
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "contact_id": contact_id,
                "event_type": event_type,
                "data": result.get("data", {})
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
        
    except Exception as e:
        await session.rollback()
        print(f"❌ Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process webhook: {str(e)}")

@router.get("/users/{user_id}/assigned-contacts", response_model=List[Dict[str, Any]], tags=["Sequence Launcher"])
async def get_user_assigned_contacts(
    user_id: str,
    campaign_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session)
):
    """Get all contacts assigned to a specific user"""
    try:
        query = select(CampaignContact, Contact, Campaign).join(
            Contact, CampaignContact.contact_id == Contact.contact_id
        ).join(
            Campaign, CampaignContact.campaign_id == Campaign.campaign_id
        ).where(CampaignContact.assigned_to == user_id)
        
        if campaign_id:
            query = query.where(CampaignContact.campaign_id == campaign_id)
        if status:
            query = query.where(CampaignContact.status == status)
        
        result = await session.execute(query)
        contacts = result.all()
        
        return [
            {
                "campaign_contact_id": cc.campaign_contact_id,
                "campaign_id": cc.campaign_id,
                "campaign_name": campaign.name,
                "contact_id": cc.contact_id,
                "full_name": contact.full_name or f"{contact.first_name} {contact.last_name}".strip(),
                "company_name": contact.company_name,
                "job_title": contact.job_title,
                "status": cc.status,
                "sequence_step": cc.sequence_step,
                "enrolled_at": cc.enrolled_at,
                "assigned_at": cc.updated_at
            } for cc, contact, campaign in contacts
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user assigned contacts: {str(e)}")
