"""
Agency Service for Multi-Client Management
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.models.agency import AgencyClient, AgencyInvitation, AgencyActivityLog
from app.models.user import User
from app.models.company import Company
from app.models.duxsoup_user import DuxSoupUser
from app.models.duxsoup_user_settings import DuxSoupUserSettings
from app.models.campaign import Campaign
from app.models.contact import Contact
from app.models.message import Message
import uuid
from datetime import datetime, timedelta
import json


class AgencyService:
    """Service for managing agency-client relationships and data access"""
    
    @staticmethod
    async def get_agency_clients(
        session: AsyncSession, 
        agency_user_id: str
    ) -> List[Dict[str, Any]]:
        """Get all clients managed by an agency user"""
        try:
            # Get agency client relationships
            query = select(AgencyClient).options(
                selectinload(AgencyClient.client_company)
            ).where(
                and_(
                    AgencyClient.agency_user_id == agency_user_id,
                    AgencyClient.is_active == True
                )
            )
            
            result = await session.execute(query)
            agency_clients = result.scalars().all()
            
            clients_data = []
            for agency_client in agency_clients:
                client_company = agency_client.client_company
                
                # Get client statistics
                stats = await AgencyService._get_client_stats(session, client_company.id)
                
                clients_data.append({
                    "id": client_company.id,
                    "name": client_company.name,
                    "domain": client_company.domain,
                    "access_level": agency_client.access_level,
                    "created_at": agency_client.created_at.isoformat(),
                    "stats": stats
                })
            
            return clients_data
            
        except Exception as e:
            print(f"Error getting agency clients: {e}")
            return []
    
    @staticmethod
    async def _get_client_stats(session: AsyncSession, client_company_id: str) -> Dict[str, Any]:
        """Get statistics for a client company"""
        try:
            # Get DuxSoup users count
            dux_users_query = select(DuxSoupUser).join(User).where(
                User.company_id == client_company_id
            )
            dux_users_result = await session.execute(dux_users_query)
            dux_users_count = len(dux_users_result.scalars().all())
            
            # Get campaigns count
            campaigns_query = select(Campaign).where(
                Campaign.company_id == client_company_id
            )
            campaigns_result = await session.execute(campaigns_query)
            campaigns_count = len(campaigns_result.scalars().all())
            
            # Get contacts count
            contacts_query = select(Contact).where(
                Contact.company_id == client_company_id
            )
            contacts_result = await session.execute(contacts_query)
            contacts_count = len(contacts_result.scalars().all())
            
            # Get messages count
            messages_query = select(Message).where(
                Message.company_id == client_company_id
            )
            messages_result = await session.execute(messages_query)
            messages_count = len(messages_result.scalars().all())
            
            return {
                "dux_accounts": dux_users_count,
                "campaigns": campaigns_count,
                "contacts": contacts_count,
                "messages": messages_count
            }
            
        except Exception as e:
            print(f"Error getting client stats: {e}")
            return {
                "dux_accounts": 0,
                "campaigns": 0,
                "contacts": 0,
                "messages": 0
            }
    
    @staticmethod
    async def add_client_to_agency(
        session: AsyncSession,
        agency_user_id: str,
        client_company_id: str,
        access_level: str = "full"
    ) -> Dict[str, Any]:
        """Add a client company to an agency user's managed clients"""
        try:
            # Check if relationship already exists
            existing_query = select(AgencyClient).where(
                and_(
                    AgencyClient.agency_user_id == agency_user_id,
                    AgencyClient.client_company_id == client_company_id
                )
            )
            existing_result = await session.execute(existing_query)
            existing = existing_result.scalar_one_or_none()
            
            if existing:
                if existing.is_active:
                    return {"success": False, "message": "Client already managed by this agency"}
                else:
                    # Reactivate existing relationship
                    existing.is_active = True
                    existing.access_level = access_level
                    existing.updated_at = datetime.utcnow()
                    await session.commit()
                    return {"success": True, "message": "Client relationship reactivated"}
            
            # Create new agency-client relationship
            agency_client = AgencyClient(
                id=str(uuid.uuid4()),
                agency_user_id=agency_user_id,
                client_company_id=client_company_id,
                access_level=access_level,
                is_active=True
            )
            
            session.add(agency_client)
            await session.commit()
            
            # Log the activity
            await AgencyService._log_activity(
                session, agency_user_id, client_company_id,
                "client_added", f"Added client to agency management"
            )
            
            return {"success": True, "message": "Client added successfully"}
            
        except Exception as e:
            await session.rollback()
            print(f"Error adding client to agency: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    @staticmethod
    async def remove_client_from_agency(
        session: AsyncSession,
        agency_user_id: str,
        client_company_id: str
    ) -> Dict[str, Any]:
        """Remove a client company from an agency user's managed clients"""
        try:
            # Find the relationship
            query = select(AgencyClient).where(
                and_(
                    AgencyClient.agency_user_id == agency_user_id,
                    AgencyClient.client_company_id == client_company_id
                )
            )
            result = await session.execute(query)
            agency_client = result.scalar_one_or_none()
            
            if not agency_client:
                return {"success": False, "message": "Client relationship not found"}
            
            # Deactivate the relationship
            agency_client.is_active = False
            agency_client.updated_at = datetime.utcnow()
            await session.commit()
            
            # Log the activity
            await AgencyService._log_activity(
                session, agency_user_id, client_company_id,
                "client_removed", f"Removed client from agency management"
            )
            
            return {"success": True, "message": "Client removed successfully"}
            
        except Exception as e:
            await session.rollback()
            print(f"Error removing client from agency: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    @staticmethod
    async def get_agency_overview(
        session: AsyncSession,
        agency_user_id: str
    ) -> Dict[str, Any]:
        """Get overview statistics for an agency user"""
        try:
            # Get all managed clients
            clients = await AgencyService.get_agency_clients(session, agency_user_id)
            
            # Calculate aggregate statistics
            total_clients = len(clients)
            total_dux_accounts = sum(client["stats"]["dux_accounts"] for client in clients)
            total_campaigns = sum(client["stats"]["campaigns"] for client in clients)
            total_contacts = sum(client["stats"]["contacts"] for client in clients)
            total_messages = sum(client["stats"]["messages"] for client in clients)
            
            # Get recent activity
            recent_activity = await AgencyService._get_recent_activity(session, agency_user_id)
            
            return {
                "total_clients": total_clients,
                "total_dux_accounts": total_dux_accounts,
                "total_campaigns": total_campaigns,
                "total_contacts": total_contacts,
                "total_messages": total_messages,
                "clients": clients,
                "recent_activity": recent_activity
            }
            
        except Exception as e:
            print(f"Error getting agency overview: {e}")
            return {
                "total_clients": 0,
                "total_dux_accounts": 0,
                "total_campaigns": 0,
                "total_contacts": 0,
                "total_messages": 0,
                "clients": [],
                "recent_activity": []
            }
    
    @staticmethod
    async def _get_recent_activity(
        session: AsyncSession,
        agency_user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent activity for an agency user"""
        try:
            query = select(AgencyActivityLog).options(
                selectinload(AgencyActivityLog.client_company)
            ).where(
                AgencyActivityLog.agency_user_id == agency_user_id
            ).order_by(
                AgencyActivityLog.created_at.desc()
            ).limit(limit)
            
            result = await session.execute(query)
            activities = result.scalars().all()
            
            return [
                {
                    "id": activity.id,
                    "client_name": activity.client_company.name,
                    "activity_type": activity.activity_type,
                    "description": activity.activity_description,
                    "created_at": activity.created_at.isoformat(),
                    "metadata": json.loads(activity.activity_metadata) if activity.activity_metadata else None
                }
                for activity in activities
            ]
            
        except Exception as e:
            print(f"Error getting recent activity: {e}")
            return []
    
    @staticmethod
    async def _log_activity(
        session: AsyncSession,
        agency_user_id: str,
        client_company_id: str,
        activity_type: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log an agency activity"""
        try:
            activity_log = AgencyActivityLog(
                id=str(uuid.uuid4()),
                agency_user_id=agency_user_id,
                client_company_id=client_company_id,
                activity_type=activity_type,
                activity_description=description,
                activity_metadata=json.dumps(metadata) if metadata else None
            )
            
            session.add(activity_log)
            await session.commit()
            
        except Exception as e:
            print(f"Error logging activity: {e}")
    
    @staticmethod
    async def create_read_only_user(
        session: AsyncSession,
        agency_user_id: str,
        client_company_id: str,
        email: str,
        first_name: str,
        last_name: str
    ) -> Dict[str, Any]:
        """Create a read-only user for a client"""
        try:
            # Check if user already exists
            existing_user_query = select(User).where(User.email == email)
            existing_result = await session.execute(existing_user_query)
            existing_user = existing_result.scalar_one_or_none()
            
            if existing_user:
                return {"success": False, "message": "User with this email already exists"}
            
            # Create read-only user
            read_only_user = User(
                id=str(uuid.uuid4()),
                email=email,
                first_name=first_name,
                last_name=last_name,
                hashed_password="",  # Will be set when user first logs in
                role="read_only",
                is_agency=False,
                company_id=client_company_id,
                is_active=True,
                is_verified=False
            )
            
            session.add(read_only_user)
            await session.commit()
            
            # Log the activity
            await AgencyService._log_activity(
                session, agency_user_id, client_company_id,
                "read_only_user_created", 
                f"Created read-only user: {email}",
                {"user_email": email, "user_name": f"{first_name} {last_name}"}
            )
            
            return {
                "success": True, 
                "message": "Read-only user created successfully",
                "user_id": read_only_user.id
            }
            
        except Exception as e:
            await session.rollback()
            print(f"Error creating read-only user: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
