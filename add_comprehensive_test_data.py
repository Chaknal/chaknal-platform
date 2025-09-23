#!/usr/bin/env python3
"""
Comprehensive test data script for Chaknal Platform
Creates multiple campaigns, users, contacts, and scenarios for testing
"""

import asyncio
import uuid
import json
from datetime import datetime, timedelta
from database.database import async_session_maker
from app.models.user import User, Organization
from app.models.company import Company
from app.models.campaign import Campaign, CampaignStatus
from app.models.contact import Contact
from app.models.campaign_contact import CampaignContact
from app.models.duxsoup_user import DuxSoupUser
from app.models.message import Message
from app.models.webhook_event import WebhookEvent
from app.models.duxsoup_queue import DuxSoupQueue
from app.models.duxsoup_user_settings import DuxSoupUserSettings

async def add_comprehensive_test_data():
    """Add comprehensive test data to the database"""
    async with async_session_maker() as session:
        try:
            print("🚀 Starting comprehensive test data creation...")
            
            # 1. Create multiple companies
            print("📊 Creating multiple companies...")
            companies = []
            company_data = [
                {"name": "TechCorp Solutions", "domain": "techcorp.com"},
                {"name": "SalesForce Pro", "domain": "salesforcepro.com"},
                {"name": "Marketing Masters", "domain": "marketingmasters.com"},
                {"name": "Startup Hub", "domain": "startuphub.com"},
                {"name": "Enterprise Solutions", "domain": "enterprisesolutions.com"}
            ]
            
            for company_info in company_data:
                company = Company(
                    id=str(uuid.uuid4()),
                    name=company_info["name"],
                    domain=company_info["domain"]
                )
                companies.append(company)
                session.add(company)
            
            await session.flush()
            print(f"✅ Created {len(companies)} companies")
            
            # 2. Create multiple organizations
            print("🏢 Creating multiple organizations...")
            organizations = []
            org_data = [
                {"name": "TechCorp Sales Team", "company": companies[0]},
                {"name": "TechCorp Marketing Team", "company": companies[0]},
                {"name": "SalesForce Business Development", "company": companies[1]},
                {"name": "SalesForce Customer Success", "company": companies[1]},
                {"name": "Marketing Masters Product Team", "company": companies[2]},
                {"name": "Marketing Masters Engineering", "company": companies[2]},
                {"name": "Startup Hub Growth Team", "company": companies[3]},
                {"name": "Enterprise Solutions Operations", "company": companies[4]},
                {"name": "TechCorp Sales Operations", "company": companies[0]},
                {"name": "TechCorp Digital Marketing", "company": companies[0]},
                {"name": "SalesForce Strategic Partnerships", "company": companies[1]},
                {"name": "SalesForce Client Relations", "company": companies[1]},
                {"name": "Marketing Masters UX Design", "company": companies[2]},
                {"name": "Marketing Masters Data Science", "company": companies[2]},
                {"name": "Startup Hub Innovation Lab", "company": companies[3]},
                {"name": "Enterprise Solutions Quality Assurance", "company": companies[4]}
            ]
            
            for org_info in org_data:
                organization = Organization(
                    id=str(uuid.uuid4()),
                    name=org_info["name"],
                    created_at=datetime.utcnow()
                )
                organizations.append(organization)
                session.add(organization)
            
            await session.flush()
            print(f"✅ Created {len(organizations)} organizations")
            
            # 3. Create multiple users
            print("👥 Creating multiple users...")
            users = []
            user_data = [
                {"email": "john.sales@techcorp.com", "first_name": "John", "last_name": "Sales", "role": "admin", "company": companies[0], "org": organizations[0]},
                {"email": "sarah.marketing@techcorp.com", "first_name": "Sarah", "last_name": "Marketing", "role": "manager", "company": companies[0], "org": organizations[1]},
                {"email": "mike.bd@salesforcepro.com", "first_name": "Mike", "last_name": "Business", "role": "manager", "company": companies[1], "org": organizations[2]},
                {"email": "lisa.cs@salesforcepro.com", "first_name": "Lisa", "last_name": "Customer", "role": "user", "company": companies[1], "org": organizations[3]},
                {"email": "alex.product@marketingmasters.com", "first_name": "Alex", "last_name": "Product", "role": "admin", "company": companies[2], "org": organizations[4]},
                {"email": "david.eng@marketingmasters.com", "first_name": "David", "last_name": "Engineer", "role": "user", "company": companies[2], "org": organizations[5]},
                {"email": "emma.growth@startuphub.com", "first_name": "Emma", "last_name": "Growth", "role": "manager", "company": companies[3], "org": organizations[6]},
                {"email": "tom.ops@enterprisesolutions.com", "first_name": "Tom", "last_name": "Operations", "role": "admin", "company": companies[4], "org": organizations[7]}
            ]
            
            for user_info in user_data:
                user = User(
                    id=str(uuid.uuid4()),
                    email=user_info["email"],
                    hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/vHhHw2i",  # "password123"
                    is_active="true",
                    is_superuser="false" if user_info["role"] != "admin" else "true",
                    is_verified="true",
                    organization_id=user_info["org"].id,
                    company_id=user_info["company"].id
                )
                users.append(user)
                session.add(user)
            
            await session.flush()
            print(f"✅ Created {len(users)} users")
            
            # 4. Create multiple DuxSoup users
            print("🤖 Creating multiple DuxSoup users...")
            dux_users = []
            dux_data = [
                {"dux_id": "dux_techcorp_001", "email": "john.sales@techcorp.com", "first_name": "John", "last_name": "Sales"},
                {"dux_id": "dux_techcorp_002", "email": "sarah.marketing@techcorp.com", "first_name": "Sarah", "last_name": "Marketing"},
                {"dux_id": "dux_salesforce_001", "email": "mike.bd@salesforcepro.com", "first_name": "Mike", "last_name": "Business"},
                {"dux_id": "dux_marketing_001", "email": "alex.product@marketingmasters.com", "first_name": "Alex", "last_name": "Product"},
                {"dux_id": "dux_startup_001", "email": "emma.growth@startuphub.com", "first_name": "Emma", "last_name": "Growth"}
            ]
            
            for dux_info in dux_data:
                dux_user = DuxSoupUser(
                    dux_soup_user_id=dux_info["dux_id"],
                    dux_soup_auth_key=f"auth_key_{dux_info['dux_id']}",
                    email=dux_info["email"],
                    first_name=dux_info["first_name"],
                    last_name=dux_info["last_name"]
                )
                dux_users.append(dux_user)
                session.add(dux_user)
            
            await session.flush()
            print(f"✅ Created {len(dux_users)} DuxSoup users")
            
            # 5. Create multiple campaigns with different statuses
            print("📈 Creating multiple campaigns...")
            campaigns = []
            campaign_data = [
                {
                    "name": "LinkedIn B2B Sales Campaign",
                    "description": "Target sales managers and directors for B2B software",
                    "target_title": "Sales Manager",
                    "intent": "Generate qualified B2B sales leads",
                    "status": "active",
                    "dux_user": dux_users[0],
                    "settings": {"max_connections_per_day": 50, "auto_message": True},
                    "daily_limits": {"connections": 50, "messages": 100},
                    "automation_settings": {"auto_connect": True, "auto_message": True, "follow_up_sequence": True}
                },
                {
                    "name": "Marketing Professionals Outreach",
                    "description": "Connect with marketing managers and CMOs",
                    "target_title": "Marketing Manager",
                    "intent": "Build marketing partnerships and collaborations",
                    "status": "paused",
                    "dux_user": dux_users[1],
                    "settings": {"max_connections_per_day": 30, "auto_message": False},
                    "daily_limits": {"connections": 30, "messages": 50},
                    "automation_settings": {"auto_connect": True, "auto_message": False, "follow_up_sequence": False}
                },
                {
                    "name": "Startup Founder Network",
                    "description": "Connect with startup founders and CEOs",
                    "target_title": "Founder",
                    "intent": "Build startup ecosystem connections",
                    "status": "active",
                    "dux_user": dux_users[2],
                    "settings": {"max_connections_per_day": 25, "auto_message": True},
                    "daily_limits": {"connections": 25, "messages": 75},
                    "automation_settings": {"auto_connect": True, "auto_message": True, "follow_up_sequence": True}
                },
                {
                    "name": "Product Manager Network",
                    "description": "Connect with product managers and product owners",
                    "target_title": "Product Manager",
                    "intent": "Share product insights and best practices",
                    "status": "draft",
                    "dux_user": dux_users[3],
                    "settings": {"max_connections_per_day": 20, "auto_message": False},
                    "daily_limits": {"connections": 20, "messages": 40},
                    "automation_settings": {"auto_connect": False, "auto_message": False, "follow_up_sequence": False}
                },
                {
                    "name": "Growth Hacking Community",
                    "description": "Connect with growth hackers and growth marketers",
                    "target_title": "Growth Hacker",
                    "intent": "Share growth strategies and tactics",
                    "status": "completed",
                    "dux_user": dux_users[4],
                    "settings": {"max_connections_per_day": 40, "auto_message": True},
                    "daily_limits": {"connections": 40, "messages": 80},
                    "automation_settings": {"auto_connect": True, "auto_message": True, "follow_up_sequence": True}
                }
            ]
            
            for i, campaign_info in enumerate(campaign_data):
                campaign = Campaign(
                    campaign_id=str(uuid.uuid4()),
                    campaign_key=str(uuid.uuid4()),
                    name=campaign_info["name"],
                    description=campaign_info["description"],
                    target_title=campaign_info["target_title"],
                    intent=campaign_info["intent"],
                    status=campaign_info["status"],
                    dux_user_id=campaign_info["dux_user"].dux_soup_user_id,
                    scheduled_start=datetime.utcnow() + timedelta(days=i),
                    end_date=datetime.utcnow() + timedelta(days=30+i),
                    settings=campaign_info["settings"],
                    daily_limits=campaign_info["daily_limits"],
                    automation_settings=campaign_info["automation_settings"]
                )
                campaigns.append(campaign)
                session.add(campaign)
            
            await session.flush()
            print(f"✅ Created {len(campaigns)} campaigns")
            
            # 6. Create diverse contacts
            print("👥 Creating diverse contacts...")
            contacts = []
            contact_data = [
                # Sales professionals
                {"first_name": "James", "last_name": "Wilson", "company": "SalesForce Inc.", "title": "Senior Sales Manager", "industry": "Technology", "location": "San Francisco, CA", "connection_degree": 2},
                {"first_name": "Maria", "last_name": "Garcia", "company": "Oracle Corp.", "title": "Sales Director", "industry": "Technology", "location": "Austin, TX", "connection_degree": 3},
                {"first_name": "Robert", "last_name": "Chen", "company": "Microsoft", "title": "Enterprise Sales Manager", "industry": "Technology", "location": "Seattle, WA", "connection_degree": 1},
                
                # Marketing professionals
                {"first_name": "Jennifer", "last_name": "Brown", "company": "HubSpot", "title": "Marketing Manager", "industry": "Marketing", "location": "Boston, MA", "connection_degree": 2},
                {"first_name": "Michael", "last_name": "Davis", "company": "Mailchimp", "title": "Senior Marketing Manager", "industry": "Marketing", "location": "Atlanta, GA", "connection_degree": 2},
                {"first_name": "Lisa", "last_name": "Miller", "company": "Canva", "title": "Growth Marketing Manager", "industry": "Design", "location": "Sydney, Australia", "connection_degree": 3},
                
                # Startup founders
                {"first_name": "Alex", "last_name": "Johnson", "company": "TechStartup", "title": "Founder & CEO", "industry": "Technology", "location": "New York, NY", "connection_degree": 2},
                {"first_name": "Sophie", "last_name": "Taylor", "company": "InnovateLab", "title": "Co-Founder", "industry": "Healthcare", "location": "Los Angeles, CA", "connection_degree": 3},
                {"first_name": "Daniel", "last_name": "Anderson", "company": "GreenTech", "title": "Founder", "industry": "Clean Energy", "location": "Portland, OR", "connection_degree": 2},
                
                # Product managers
                {"first_name": "Rachel", "last_name": "Martinez", "company": "Slack", "title": "Senior Product Manager", "industry": "Technology", "location": "San Francisco, CA", "connection_degree": 2},
                {"first_name": "Kevin", "last_name": "Thompson", "company": "Notion", "title": "Product Manager", "industry": "Technology", "location": "San Francisco, CA", "connection_degree": 1},
                {"first_name": "Amanda", "last_name": "White", "company": "Figma", "title": "Product Manager", "industry": "Design", "location": "San Francisco, CA", "connection_degree": 2},
                
                # Growth hackers
                {"first_name": "Chris", "last_name": "Lee", "company": "Dropbox", "title": "Growth Hacker", "industry": "Technology", "location": "San Francisco, CA", "connection_degree": 2},
                {"first_name": "Nina", "last_name": "Rodriguez", "company": "Airbnb", "title": "Growth Marketing Manager", "industry": "Travel", "location": "San Francisco, CA", "connection_degree": 3},
                {"first_name": "Paul", "last_name": "Kim", "company": "Uber", "title": "Growth Hacker", "industry": "Transportation", "location": "San Francisco, CA", "connection_degree": 2}
            ]
            
            for i, contact_info in enumerate(contact_data):
                contact = Contact(
                    contact_id=str(uuid.uuid4()),
                    linkedin_id=f"linkedin_{i+1:03d}",
                    linkedin_url=f"https://linkedin.com/in/{contact_info['first_name'].lower()}{contact_info['last_name'].lower()}{i+1}",
                    first_name=contact_info["first_name"],
                    last_name=contact_info["last_name"],
                    headline=f"{contact_info['title']} at {contact_info['company']}",
                    company=contact_info["company"],
                    company_url=f"https://{contact_info['company'].lower().replace(' ', '').replace('.', '').replace(',', '')}.com",
                    location=contact_info["location"],
                    industry=contact_info["industry"],
                    connection_degree=contact_info["connection_degree"],
                    email=f"{contact_info['first_name'].lower()}.{contact_info['last_name'].lower()}@{contact_info['company'].lower().replace(' ', '').replace('.', '').replace(',', '')}.com",
                    profile_data={
                        "skills": ["Leadership", "Strategy", contact_info["industry"]],
                        "experience_years": 5 + (i % 5),
                        "education": "Bachelor's Degree",
                        "certifications": ["Sales Certification", "Marketing Certification"] if i < 6 else []
                    },
                    profile_id=f"profile_{i+1:03d}",
                    connection_status="not_connected",
                    degree_level=contact_info["connection_degree"]
                )
                contacts.append(contact)
                session.add(contact)
            
            await session.flush()
            print(f"✅ Created {len(contacts)} diverse contacts")
            
            # 7. Create campaign contacts with different statuses
            print("🔗 Linking contacts to campaigns...")
            campaign_contacts = []
            
            # Distribute contacts across campaigns
            contacts_per_campaign = len(contacts) // len(campaigns)
            for i, campaign in enumerate(campaigns):
                start_idx = i * contacts_per_campaign
                end_idx = start_idx + contacts_per_campaign if i < len(campaigns) - 1 else len(contacts)
                campaign_contacts_list = contacts[start_idx:end_idx]
                
                for j, contact in enumerate(campaign_contacts_list):
                    # Different statuses for variety
                    statuses = ["enrolled", "accepted", "replied", "blacklisted"]
                    status = statuses[j % len(statuses)]
                    
                    # Different sequence steps
                    sequence_step = j + 1
                    
                    # Different tags based on campaign
                    tags = []
                    if "Sales" in campaign.name:
                        tags = ["sales", "b2b", "enterprise"]
                    elif "Marketing" in campaign.name:
                        tags = ["marketing", "growth", "digital"]
                    elif "Startup" in campaign.name:
                        tags = ["startup", "founder", "ecosystem"]
                    elif "Product" in campaign.name:
                        tags = ["product", "management", "strategy"]
                    elif "Growth" in campaign.name:
                        tags = ["growth", "hacking", "optimization"]
                    
                    campaign_contact = CampaignContact(
                        campaign_contact_id=str(uuid.uuid4()),
                        campaign_id=campaign.campaign_id,
                        campaign_key=campaign.campaign_key,
                        contact_id=contact.contact_id,
                        status=status,
                        sequence_step=sequence_step,
                        tags=json.dumps(tags),
                        enrolled_at=datetime.utcnow() - timedelta(days=j),
                        accepted_at=datetime.utcnow() - timedelta(days=j-1) if status in ["accepted", "replied"] else None,
                        replied_at=datetime.utcnow() - timedelta(days=j-2) if status == "replied" else None,
                        blacklisted_at=datetime.utcnow() - timedelta(days=j-3) if status == "blacklisted" else None
                    )
                    campaign_contacts.append(campaign_contact)
                    session.add(campaign_contact)
            
            await session.flush()
            print(f"✅ Created {len(campaign_contacts)} campaign contacts")
            
            # 8. Create some messages
            print("💬 Creating sample messages...")
            messages = []
            message_templates = [
                "Hi {first_name}, I noticed your work at {company} and would love to connect!",
                "Hello {first_name}, I'm reaching out because I think we could collaborate on some interesting projects.",
                "Hi there {first_name}! I'm building connections in the {industry} space and would love to learn from your experience.",
                "Hello {first_name}, I came across your profile and was impressed by your work in {industry}. Would love to connect!",
                "Hi {first_name}, I'm expanding my network in the {industry} sector and would appreciate connecting with you."
            ]
            
            for i, campaign_contact in enumerate(campaign_contacts[:20]):  # Create messages for first 20 contacts
                contact = next(c for c in contacts if c.contact_id == campaign_contact.contact_id)
                campaign = next(c for c in campaigns if c.campaign_id == campaign_contact.campaign_id)
                
                message_text = message_templates[i % len(message_templates)].format(
                    first_name=contact.first_name,
                    company=contact.company,
                    industry=contact.industry
                )
                
                message = Message(
                    message_id=str(uuid.uuid4()),
                    campaign_contact_id=campaign_contact.campaign_contact_id,
                    direction="sent",
                    message_text=message_text,
                    status="delivered",
                    sent_at=datetime.utcnow() - timedelta(days=i),
                    created_at=datetime.utcnow() - timedelta(days=i)
                )
                messages.append(message)
                session.add(message)
            
            await session.flush()
            print(f"✅ Created {len(messages)} sample messages")
            
            # 9. Create DuxSoup user settings
            print("⚙️ Creating DuxSoup user settings...")
            for dux_user in dux_users:
                settings = DuxSoupUserSettings(
                    setting_id=str(uuid.uuid4()),
                    dux_user_id=dux_user.dux_soup_user_id,
                    settings_type="automation",
                    settings_data={
                        "max_connections_per_day": 50,
                        "auto_message": True,
                        "follow_up_sequence": True,
                        "connection_request_message": "Hi, I'd love to connect!",
                        "follow_up_delay_days": 3,
                        "max_follow_ups": 2
                    }
                )
                session.add(settings)
            
            await session.flush()
            print(f"✅ Created DuxSoup user settings")
            
            # 10. Create some webhook events
            print("🔔 Creating sample webhook events...")
            webhook_events = []
            event_types = ["message", "visit", "action", "rccommand"]
            event_names = ["create", "received", "completed", "ready", "failed"]
            
            for i in range(15):
                webhook_event = WebhookEvent(
                    event_id=str(uuid.uuid4()),
                    dux_user_id=dux_users[i % len(dux_users)].dux_soup_user_id,
                    event_type=event_types[i % len(event_types)],
                    event_name=event_names[i % len(event_names)],
                    contact_id=contacts[i % len(contacts)].contact_id if i < len(contacts) else None,
                    campaign_id=campaigns[i % len(campaigns)].campaign_id if i < len(campaigns) else None,
                    raw_data={
                        "event_id": f"webhook_{i+1}",
                        "timestamp": str(datetime.utcnow()),
                        "user_agent": "DuxSoup/2.0",
                        "ip_address": "192.168.1.1",
                        "payload": {"action": "connection_request", "status": "sent"}
                    },
                    processed=False
                )
                webhook_events.append(webhook_event)
                session.add(webhook_event)
            
            await session.flush()
            print(f"✅ Created {len(webhook_events)} webhook events")
            
            # Commit all changes
            await session.commit()
            print("🎉 All comprehensive test data added successfully!")
            
            # Print summary
            print("\n📊 Comprehensive Test Data Summary:")
            print(f"   Companies: {len(companies)}")
            print(f"   Organizations: {len(organizations)}")
            print(f"   Users: {len(users)}")
            print(f"   DuxSoup Users: {len(dux_users)}")
            print(f"   Campaigns: {len(campaigns)}")
            print(f"   Contacts: {len(contacts)}")
            print(f"   Campaign Contacts: {len(campaign_contacts)}")
            print(f"   Messages: {len(messages)}")
            print(f"   Webhook Events: {len(webhook_events)}")
            
            print("\n🎯 Campaign Statuses:")
            for campaign in campaigns:
                print(f"   - {campaign.name}: {campaign.status}")
            
            print("\n🔍 Data Distribution:")
            print(f"   - Contacts per campaign: ~{len(contacts) // len(campaigns)}")
            print(f"   - Users per company: ~{len(users) // len(companies)}")
            print(f"   - Organizations per company: ~{len(organizations) // len(companies)}")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error adding comprehensive test data: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(add_comprehensive_test_data())
