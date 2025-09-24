#!/usr/bin/env python3
"""
Populate Azure PostgreSQL database with test data
"""

import asyncio
import sys
import os
from datetime import datetime, timezone
import uuid

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Set the database URL to the Azure PostgreSQL database with async driver
os.environ['DATABASE_URL'] = 'postgresql+asyncpg://chaknaladmin:YourSecurePassword123!@chaknal-db-server.postgres.database.azure.com:5432/chaknal_platform'

from database.database import async_session_maker
from app.models.company import Company
from app.models.user import User
from app.models.duxsoup_user import DuxSoupUser
from app.models.campaign import Campaign
from app.models.contact import Contact
from app.models.campaign_contact import CampaignContact

async def populate_azure_database():
    """Add test data to Azure PostgreSQL database"""
    print("🚀 Starting to populate Azure PostgreSQL database...")
    
    async with async_session_maker() as session:
        try:
            # Create test company
            company = Company(
                name="Test Company Inc.",
                domain="testcompany.com"
            )
            session.add(company)
            await session.flush()
            print("✅ Created company: Test Company Inc.")
            
            # Create test user
            user = User(
                email="test@testcompany.com",
                hashed_password="testpassword",  # In production, this should be properly hashed
                first_name="Test",
                last_name="User",
                company_id=company.id,
                role="admin",
                is_active=True
            )
            session.add(user)
            await session.flush()
            print("✅ Created user: test@testcompany.com")
            
            # Create test campaign
            campaign = Campaign(
                name="LinkedIn Outreach Campaign",
                target_title="Sales Manager",
                intent="Lead Generation",
                dux_user_id="test_dux_user",
                initial_action="inmail",
                initial_message="Hi {first_name}, I noticed your profile and thought you might be interested in our solution.",
                initial_subject="Quick question about your sales process",
                follow_up_actions=["connection_request", "inmail"],
                delay_days=3,
                random_delay=True,
                end_date=datetime.utcnow().replace(month=12, day=31),
                status="active"
            )
            session.add(campaign)
            await session.flush()
            print("✅ Created campaign: LinkedIn Outreach Campaign")
            
            # Create test contacts
            contacts_data = [
                {
                    "first_name": "John",
                    "last_name": "Smith",
                    "email": "john.smith@techcorp.com",
                    "company_name": "TechCorp Inc.",
                    "job_title": "Sales Manager",
                    "linkedin_url": "https://linkedin.com/in/johnsmith"
                },
                {
                    "first_name": "Sarah",
                    "last_name": "Johnson",
                    "email": "sarah.johnson@innovate.com",
                    "company_name": "Innovate Solutions",
                    "job_title": "VP of Sales",
                    "linkedin_url": "https://linkedin.com/in/sarahjohnson"
                },
                {
                    "first_name": "Mike",
                    "last_name": "Davis",
                    "email": "mike.davis@growth.com",
                    "company_name": "Growth Partners",
                    "job_title": "Sales Director",
                    "linkedin_url": "https://linkedin.com/in/mikedavis"
                }
            ]
            
            contacts = []
            for contact_data in contacts_data:
                contact = Contact(
                    full_name=f"{contact_data['first_name']} {contact_data['last_name']}",
                    first_name=contact_data['first_name'],
                    last_name=contact_data['last_name'],
                    email=contact_data['email'],
                    company_name=contact_data['company_name'],
                    job_title=contact_data['job_title'],
                    linkedin_url=contact_data['linkedin_url']
                )
                session.add(contact)
                contacts.append(contact)
            
            await session.flush()
            print(f"✅ Created {len(contacts)} test contacts")
            
            # Link contacts to campaign
            for contact in contacts:
                campaign_contact = CampaignContact(
                    campaign_id=campaign.campaign_id,
                    campaign_key=campaign.campaign_key,
                    contact_id=contact.contact_id,
                    status="pending",
                    assigned_to=user.id
                )
                session.add(campaign_contact)
            
            await session.flush()
            print(f"✅ Linked {len(contacts)} contacts to campaign")
            
            # Commit all changes
            await session.commit()
            print("🎉 All Azure database data added successfully!")
            
            print("\n📊 Azure Database Data Summary:")
            print(f"   Company: Test Company Inc.")
            print(f"   User: test@testcompany.com")
            print(f"   Campaign: LinkedIn Outreach Campaign")
            print(f"   Contacts: {len(contacts)}")
            print(f"   Campaign Contacts: {len(contacts)}")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error adding Azure database data: {str(e)}")
            raise

if __name__ == "__main__":
    asyncio.run(populate_azure_database())
