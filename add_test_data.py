#!/usr/bin/env python3
"""
Script to add test data to the Chaknal Platform database
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from database.database import async_session_maker
from app.models.user import User, Organization
from app.models.company import Company
from app.models.campaign import Campaign, CampaignStatus
from app.models.contact import Contact
from app.models.campaign_contact import CampaignContact
from app.models.duxsoup_user import DuxSoupUser

async def add_test_data():
    """Add test data to the database"""
    async with async_session_maker() as session:
        try:
            print("🚀 Starting to add test data...")
            
            # 1. Create a test company
            print("📊 Creating test company...")
            company = Company(
                id=str(uuid.uuid4()),
                name="Test Company Inc.",
                domain="testcompany.com"
            )
            session.add(company)
            await session.flush()
            print(f"✅ Created company: {company.name}")
            
            # 2. Create a test organization
            print("🏢 Creating test organization...")
            organization = Organization(
                id=str(uuid.uuid4()),
                name="Sales Team",
                created_at=datetime.utcnow()
            )
            session.add(organization)
            await session.flush()
            print(f"✅ Created organization: {organization.name}")
            
            # 3. Create a test user
            print("👤 Creating test user...")
            user = User(
                id=str(uuid.uuid4()),
                email="test@testcompany.com",
                hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/vHhHw2i",  # "password123"
                is_active="true",
                is_superuser="false",
                is_verified="true",
                organization_id=organization.id,
                company_id=company.id
            )
            session.add(user)
            await session.flush()
            print(f"✅ Created user: {user.email}")
            
            # 4. Create a test DuxSoup user
            print("🤖 Creating test DuxSoup user...")
            dux_user = DuxSoupUser(
                dux_soup_user_id="test_dux_user_001",
                dux_soup_auth_key="test_auth_key_123",
                email="test@testcompany.com",
                first_name="Test",
                last_name="User"
            )
            session.add(dux_user)
            await session.flush()
            print(f"✅ Created DuxSoup user: {dux_user.dux_soup_user_id}")
            
            # 5. Create a test campaign
            print("📈 Creating test campaign...")
            campaign = Campaign(
                campaign_id=str(uuid.uuid4()),
                campaign_key=str(uuid.uuid4()),
                name="LinkedIn Outreach Campaign",
                description="Test campaign for LinkedIn automation",
                target_title="Sales Manager",
                intent="Generate leads for B2B sales",
                status="active",
                dux_user_id=dux_user.dux_soup_user_id,
                scheduled_start=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=30),
                settings={"max_connections_per_day": 50},
                daily_limits={"connections": 50, "messages": 100},
                automation_settings={"auto_connect": True, "auto_message": True}
            )
            session.add(campaign)
            await session.flush()
            print(f"✅ Created campaign: {campaign.name}")
            
            # 6. Create test contacts
            print("👥 Creating test contacts...")
            contacts = []
            for i in range(5):
                contact = Contact(
                    contact_id=str(uuid.uuid4()),
                    linkedin_id=f"linkedin_{i+1}",
                    linkedin_url=f"https://linkedin.com/in/testuser{i+1}",
                    first_name=f"Test{i+1}",
                    last_name="User",
                    headline="Sales Manager at Tech Company",
                    company=f"Tech Company {i+1}",
                    company_url=f"https://techcompany{i+1}.com",
                    location="San Francisco, CA",
                    industry="Technology",
                    connection_degree=2,
                    email=f"test{i+1}@techcompany{i+1}.com",
                    profile_data={"skills": ["Sales", "B2B", "CRM"]},
                    profile_id=f"profile_{i+1}",
                    connection_status="not_connected"
                )
                contacts.append(contact)
                session.add(contact)
            
            await session.flush()
            print(f"✅ Created {len(contacts)} test contacts")
            
            # 7. Create campaign contacts
            print("🔗 Linking contacts to campaign...")
            for i, contact in enumerate(contacts):
                campaign_contact = CampaignContact(
                    campaign_contact_id=str(uuid.uuid4()),
                    campaign_id=campaign.campaign_id,
                    campaign_key=campaign.campaign_key,
                    contact_id=contact.contact_id,
                    status="enrolled",
                    sequence_step=i+1,
                    tags='["test", "automation"]'
                )
                session.add(campaign_contact)
            
            await session.flush()
            print(f"✅ Linked {len(contacts)} contacts to campaign")
            
            # Commit all changes
            await session.commit()
            print("🎉 All test data added successfully!")
            
            # Print summary
            print("\n📊 Test Data Summary:")
            print(f"   Company: {company.name}")
            print(f"   Organization: {organization.name}")
            print(f"   User: {user.email}")
            print(f"   DuxSoup User: {dux_user.dux_soup_user_id}")
            print(f"   Campaign: {campaign.name}")
            print(f"   Contacts: {len(contacts)}")
            print(f"   Campaign Contacts: {len(contacts)}")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error adding test data: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(add_test_data())
