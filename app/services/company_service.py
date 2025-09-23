"""
Company Service for Chaknal Platform
Handles automatic company association based on email domains
"""

from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.company import Company
from app.models.user import User, Organization
import uuid

class CompanyService:
    """Service for managing company associations and organizations"""
    
    @staticmethod
    async def get_or_create_company_by_domain(
        session: AsyncSession, 
        domain: str,
        company_name: Optional[str] = None
    ) -> Company:
        """
        Get existing company by domain or create new one
        """
        try:
            # Try to find existing company
            company_query = select(Company).where(Company.domain == domain)
            result = await session.execute(company_query)
            company = result.scalar_one_or_none()
            
            if company:
                return company
            
            # Create new company if it doesn't exist
            if not company_name:
                # Extract company name from domain
                company_name = domain.replace('.com', '').replace('.org', '').replace('.net', '')
                company_name = company_name.replace('-', ' ').replace('_', ' ').title()
            
            company = Company(
                id=str(uuid.uuid4()),
                name=company_name,
                domain=domain
            )
            
            session.add(company)
            await session.flush()
            
            print(f"✅ Created new company: {company_name} ({domain})")
            return company
            
        except Exception as e:
            print(f"❌ Error creating company: {e}")
            raise
    
    @staticmethod
    async def get_or_create_default_organization(
        session: AsyncSession,
        company_id: str,
        org_name: str = "Default Team"
    ) -> Organization:
        """
        Get existing default organization or create new one
        """
        try:
            # Try to find existing default organization
            org_query = select(Organization).where(
                Organization.company_id == company_id,
                Organization.name == org_name
            )
            result = await session.execute(org_query)
            organization = result.scalar_one_or_none()
            
            if organization:
                return organization
            
            # Create new default organization
            organization = Organization(
                id=str(uuid.uuid4()),
                name=org_name,
                company_id=company_id
            )
            
            session.add(organization)
            await session.flush()
            
            print(f"✅ Created new organization: {org_name} for company {company_id}")
            return organization
            
        except Exception as e:
            print(f"❌ Error creating organization: {e}")
            raise
    
    @staticmethod
    async def associate_user_with_company(
        session: AsyncSession,
        user_email: str,
        user_id: str,
        preferred_org_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Automatically associate user with company based on email domain
        """
        try:
            # Extract domain from email
            domain = user_email.split('@')[1]
            
            # Get or create company
            company = await CompanyService.get_or_create_company_by_domain(session, domain)
            
            # Get or create default organization
            org_name = preferred_org_name or "Default Team"
            organization = await CompanyService.get_or_create_default_organization(
                session, company.id, org_name
            )
            
            # Update user with company and organization
            user_query = select(User).where(User.id == user_id)
            result = await session.execute(user_query)
            user = result.scalar_one_or_none()
            
            if user:
                user.company_id = company.id
                user.organization_id = organization.id
                await session.flush()
                
                print(f"✅ Associated user {user_email} with company {company.name} and organization {organization.name}")
                
                return {
                    "company": {
                        "id": company.id,
                        "name": company.name,
                        "domain": company.domain
                    },
                    "organization": {
                        "id": organization.id,
                        "name": organization.name
                    }
                }
            else:
                raise Exception(f"User {user_id} not found")
                
        except Exception as e:
            print(f"❌ Error associating user with company: {e}")
            raise
    
    @staticmethod
    async def get_company_by_user_email(
        session: AsyncSession,
        user_email: str
    ) -> Optional[Company]:
        """
        Get company associated with user's email domain
        """
        try:
            domain = user_email.split('@')[1]
            company_query = select(Company).where(Company.domain == domain)
            result = await session.execute(company_query)
            return result.scalar_one_or_none()
        except Exception as e:
            print(f"❌ Error getting company by email: {e}")
            return None
    
    @staticmethod
    async def get_organizations_by_company(
        session: AsyncSession,
        company_id: str
    ) -> list:
        """
        Get all organizations for a specific company
        """
        try:
            org_query = select(Organization).where(Organization.company_id == company_id)
            result = await session.execute(org_query)
            return result.scalars().all()
        except Exception as e:
            print(f"❌ Error getting organizations: {e}")
            return []
    
    @staticmethod
    async def create_custom_organization(
        session: AsyncSession,
        company_id: str,
        org_name: str,
        description: Optional[str] = None
    ) -> Organization:
        """
        Create a custom organization within a company
        """
        try:
            organization = Organization(
                id=str(uuid.uuid4()),
                name=org_name,
                company_id=company_id,
                description=description
            )
            
            session.add(organization)
            await session.flush()
            
            print(f"✅ Created custom organization: {org_name} for company {company_id}")
            return organization
            
        except Exception as e:
            print(f"❌ Error creating custom organization: {e}")
            raise
    
    @staticmethod
    async def move_user_to_organization(
        session: AsyncSession,
        user_id: str,
        new_org_id: str
    ) -> bool:
        """
        Move user to a different organization within the same company
        """
        try:
            # Verify user exists
            user_query = select(User).where(User.id == user_id)
            result = await session.execute(user_query)
            user = result.scalar_one_or_none()
            
            if not user:
                raise Exception(f"User {user_id} not found")
            
            # Verify new organization exists and belongs to same company
            org_query = select(Organization).where(Organization.id == new_org_id)
            result = await session.execute(org_query)
            new_org = result.scalar_one_or_none()
            
            if not new_org:
                raise Exception(f"Organization {new_org_id} not found")
            
            if new_org.company_id != user.company_id:
                raise Exception("Cannot move user to organization in different company")
            
            # Move user
            user.organization_id = new_org_id
            await session.flush()
            
            print(f"✅ Moved user {user.email} to organization {new_org.name}")
            return True
            
        except Exception as e:
            print(f"❌ Error moving user: {e}")
            return False
