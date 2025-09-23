#!/usr/bin/env python3
"""
Create Sergio Conversation Setup
Create the necessary database records to enable conversation storage between Sercio and Sergio
"""

import asyncio
import sys
import os
from datetime import datetime
import uuid

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def create_sergio_conversation_setup():
    """Create database setup for Sergio conversation"""
    
    print("🔧 Creating Sergio Conversation Database Setup")
    print("=" * 50)
    
    try:
        from database.database import async_session_maker
        from models.contact import Contact
        from models.campaign import Campaign
        from models.campaign_contact import CampaignContact
        from models.message import Message
        from models.company import Company
        from sqlalchemy import select
        
        async with async_session_maker() as session:
            
            # Step 1: Create or get Marketing Masters company
            print("📊 Step 1: Setting up Marketing Masters company...")
            
            result = await session.execute(
                select(Company).where(Company.name == "Marketing Masters")
            )
            company = result.scalar_one_or_none()
            
            if not company:
                company = Company(
                    id=str(uuid.uuid4()),
                    name="Marketing Masters",
                    domain="marketingmasters.com",
                    created_at=datetime.utcnow()
                )
                session.add(company)
                await session.flush()
                print("✅ Created Marketing Masters company")
            else:
                print("✅ Marketing Masters company found")
            
            # Step 2: Create or get Sergio contact
            print("👤 Step 2: Setting up Sergio Campos contact...")
            
            sergio_linkedin = "https://www.linkedin.com/in/sergio-campos-97b9b7362/"
            result = await session.execute(
                select(Contact).where(Contact.linkedin_url == sergio_linkedin)
            )
            sergio_contact = result.scalar_one_or_none()
            
            if not sergio_contact:
                sergio_contact = Contact(
                    contact_id=str(uuid.uuid4()),
                    linkedin_url=sergio_linkedin,
                    first_name="Sergio",
                    last_name="Campos",
                    headline="Security Professional",
                    company="Wallarm",
                    email="sergio.campos@wallarm.com",
                    location="Unknown",
                    industry="Technology",
                    connection_degree=1,
                    connection_status="connected",
                    created_at=datetime.utcnow()
                )
                session.add(sergio_contact)
                await session.flush()
                print("✅ Created Sergio Campos contact")
            else:
                print("✅ Sergio Campos contact found")
            
            # Step 3: Create or get Sercio-Sergio conversation campaign
            print("🎯 Step 3: Setting up conversation campaign...")
            
            campaign_name = "Sercio-Sergio Direct Conversation"
            result = await session.execute(
                select(Campaign).where(Campaign.name == campaign_name)
            )
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                campaign = Campaign(
                    campaign_id=str(uuid.uuid4()),
                    name=campaign_name,
                    description="Direct conversation between Sercio Campos and Sergio Campos",
                    status="active",
                    company_id=company.id,
                    created_at=datetime.utcnow()
                )
                session.add(campaign)
                await session.flush()
                print("✅ Created conversation campaign")
            else:
                print("✅ Conversation campaign found")
            
            # Step 4: Create or get campaign contact relationship
            print("🔗 Step 4: Setting up campaign contact relationship...")
            
            result = await session.execute(
                select(CampaignContact).where(
                    CampaignContact.campaign_id == campaign.campaign_id,
                    CampaignContact.contact_id == sergio_contact.contact_id
                )
            )
            campaign_contact = result.scalar_one_or_none()
            
            if not campaign_contact:
                campaign_contact = CampaignContact(
                    campaign_contact_id=str(uuid.uuid4()),
                    campaign_id=campaign.campaign_id,
                    contact_id=sergio_contact.contact_id,
                    status="active",
                    sequence_step=1,
                    created_at=datetime.utcnow()
                )
                session.add(campaign_contact)
                await session.flush()
                print("✅ Created campaign contact relationship")
            else:
                print("✅ Campaign contact relationship found")
            
            # Step 5: Create initial conversation history
            print("💬 Step 5: Creating conversation history...")
            
            # Check if messages already exist
            result = await session.execute(
                select(Message).where(Message.campaign_contact_id == campaign_contact.campaign_contact_id)
            )
            existing_messages = result.scalars().all()
            
            if len(existing_messages) == 0:
                # Create conversation history
                conversation_messages = [
                    {
                        "direction": "outbound",
                        "message_text": "Hi Sergio! Thanks for connecting. I'm Sercio from Wallarm. I'd love to learn more about your work and discuss potential collaboration opportunities.",
                        "days_ago": 7,
                        "linkedin_message_id": "msg_001_sercio_to_sergio"
                    },
                    {
                        "direction": "inbound", 
                        "message_text": "Hi Sercio! Nice to connect with you. I'm always interested in discussing security and collaboration opportunities. What kind of work are you doing at Wallarm?",
                        "days_ago": 6,
                        "linkedin_message_id": "msg_002_sergio_to_sercio"
                    },
                    {
                        "direction": "outbound",
                        "message_text": "Great to hear from you! At Wallarm, I focus on application security and API protection. I noticed your LinkedIn profile and thought there might be some interesting synergies between our work. Would you be open to a brief call this week?",
                        "days_ago": 5,
                        "linkedin_message_id": "msg_003_sercio_to_sergio"
                    },
                    {
                        "direction": "inbound",
                        "message_text": "That sounds really interesting! I'd definitely be open to learning more about what you're working on. How about we schedule something for later this week?",
                        "days_ago": 3,
                        "linkedin_message_id": "msg_004_sergio_to_sercio"
                    }
                ]
                
                for i, msg_data in enumerate(conversation_messages):
                    message = Message(
                        message_id=str(uuid.uuid4()),
                        campaign_contact_id=campaign_contact.campaign_contact_id,
                        direction=msg_data["direction"],
                        message_text=msg_data["message_text"],
                        linkedin_message_id=msg_data["linkedin_message_id"],
                        status="delivered" if msg_data["direction"] == "outbound" else "received",
                        created_at=datetime.utcnow() - timedelta(days=msg_data["days_ago"]),
                        campaign_id=campaign.campaign_id
                    )
                    session.add(message)
                
                print(f"✅ Created {len(conversation_messages)} conversation messages")
            else:
                print(f"✅ Found {len(existing_messages)} existing messages")
            
            # Commit all changes
            await session.commit()
            
            print("\n🎉 Database setup completed successfully!")
            print(f"📊 Company: {company.name} ({company.id})")
            print(f"👤 Contact: {sergio_contact.first_name} {sergio_contact.last_name} ({sergio_contact.contact_id})")
            print(f"🎯 Campaign: {campaign.name} ({campaign.campaign_id})")
            print(f"🔗 Campaign Contact: {campaign_contact.campaign_contact_id}")
            print(f"💬 LinkedIn URL: {sergio_linkedin}")
            
            return {
                "success": True,
                "data": {
                    "company_id": company.id,
                    "contact_id": sergio_contact.contact_id,
                    "campaign_id": campaign.campaign_id,
                    "campaign_contact_id": campaign_contact.campaign_contact_id,
                    "linkedin_url": sergio_linkedin
                }
            }
            
    except Exception as e:
        print(f"❌ Failed to create database setup: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    from datetime import timedelta
    
    print("🚀 Starting Sergio Conversation Database Setup")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    result = asyncio.run(create_sergio_conversation_setup())
    
    if result["success"]:
        print("\n✅ Setup completed successfully!")
        print("Database is ready for Sercio ↔ Sergio conversation storage")
    else:
        print(f"\n❌ Setup failed: {result['error']}")
    
    print(f"\nSetup completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
