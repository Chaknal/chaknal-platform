#!/usr/bin/env python3
"""
Populate production database with test data - simplified version
"""

import asyncio
import sys
import os
from datetime import datetime, timezone
import uuid

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from database.database import async_session_maker
from app.models.company import Company
from app.models.user import User
from app.models.duxsoup_user import DuxSoupUser
from app.models.campaign import Campaign
from app.models.contact import Contact
from app.models.campaign_contact import CampaignContact

async def populate_production_data():
    """Add test data to production database"""
    print("🚀 Starting to populate production database...")
    
    async with async_session_maker() as session:
        try:
            # Create test company
            company = Company(
                company_id=str(uuid.uuid4()),
                name="Test Company Inc.",
                domain="testcompany.com",
                industry="Technology",
                size="50-200",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(company)
            await session.flush()
            print("✅ Created company: Test Company Inc.")
            
            # Create test user
            user = User(
                user_id=str(uuid.uuid4()),
                email="test@testcompany.com",
                first_name="Test",
                last_name="User",
                company_id=company.company_id,
                role="admin",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(user)
            await session.flush()
            print("✅ Created user: test@testcompany.com")
            
            # Create test DuxSoup user
            duxsoup_user = DuxSoupUser(
                dux_soup_user_id=str(uuid.uuid4()),
                dux_soup_auth_key="test_auth_key_123",
                email="test@testcompany.com",
                first_name="Test",
                last_name="User",
                user_id=user.user_id,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(duxsoup_user)
            await session.flush()
            print("✅ Created DuxSoup user: test_dux_user_001")
            
            # Create test campaign
            campaign = Campaign(
                campaign_id=str(uuid.uuid4()),
                campaign_key="linkedin-outreach-2024",
                name="LinkedIn Outreach Campaign",
                target_title="Sales Manager",
                intent="Lead Generation",
                initial_action="inmail",
                initial_message="Hi {first_name}, I noticed your profile and thought you might be interested in our solution.",
                initial_subject="Quick question about your sales process",
                follow_up_actions=["connection_request", "inmail"],
                delay_days=3,
                random_delay=True,
                launch_date=datetime.utcnow(),
                end_date=datetime.utcnow().replace(month=12, day=31),
                status="active",
                created_by=user.user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
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
                    contact_id=str(uuid.uuid4()),
                    full_name=f"{contact_data['first_name']} {contact_data['last_name']}",
                    first_name=contact_data['first_name'],
                    last_name=contact_data['last_name'],
                    email=contact_data['email'],
                    company_name=contact_data['company_name'],
                    job_title=contact_data['job_title'],
                    linkedin_url=contact_data['linkedin_url'],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(contact)
                contacts.append(contact)
            
            await session.flush()
            print(f"✅ Created {len(contacts)} test contacts")
            
            # Link contacts to campaign
            for contact in contacts:
                campaign_contact = CampaignContact(
                    campaign_contact_id=str(uuid.uuid4()),
                    campaign_id=campaign.campaign_id,
                    campaign_key=campaign.campaign_key,
                    contact_id=contact.contact_id,
                    status="pending",
                    assigned_to=user.user_id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(campaign_contact)
            
            await session.flush()
            print(f"✅ Linked {len(contacts)} contacts to campaign")
            
            # Commit all changes
            await session.commit()
            print("🎉 All production data added successfully!")
            
            print("\n📊 Production Data Summary:")
            print(f"   Company: Test Company Inc.")
            print(f"   User: test@testcompany.com")
            print(f"   DuxSoup User: test_dux_user_001")
            print(f"   Campaign: LinkedIn Outreach Campaign")
            print(f"   Contacts: {len(contacts)}")
            print(f"   Campaign Contacts: {len(contacts)}")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error adding production data: {str(e)}")
            raise

if __name__ == "__main__":
    asyncio.run(populate_production_data())

