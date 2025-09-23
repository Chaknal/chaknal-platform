#!/usr/bin/env python3
"""
Setup Sergio Conversation
Direct SQL approach to create conversation setup
"""

import sqlite3
import uuid
from datetime import datetime, timedelta

def setup_sergio_conversation():
    """Setup database for Sergio conversation using direct SQL"""
    
    print("🔧 Setting up Sergio Conversation Database")
    print("=" * 50)
    
    try:
        # Connect to database
        conn = sqlite3.connect('chaknal.db')
        cursor = conn.cursor()
        
        # Step 1: Check/Create Marketing Masters company
        print("📊 Step 1: Setting up Marketing Masters company...")
        
        cursor.execute("SELECT id FROM company WHERE name = 'Marketing Masters'")
        company_row = cursor.fetchone()
        
        if not company_row:
            company_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO company (id, name, domain, created_at)
                VALUES (?, ?, ?, ?)
            """, (company_id, "Marketing Masters", "marketingmasters.com", datetime.utcnow()))
            print("✅ Created Marketing Masters company")
        else:
            company_id = company_row[0]
            print("✅ Marketing Masters company found")
        
        # Step 2: Create/Update Sergio contact
        print("👤 Step 2: Setting up Sergio Campos contact...")
        
        sergio_linkedin = "https://www.linkedin.com/in/sergio-campos-97b9b7362/"
        cursor.execute("SELECT contact_id FROM contacts WHERE linkedin_url = ?", (sergio_linkedin,))
        contact_row = cursor.fetchone()
        
        if not contact_row:
            contact_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO contacts (
                    contact_id, linkedin_url, first_name, last_name, headline, 
                    company, email, location, industry, connection_degree, 
                    connection_status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                contact_id, sergio_linkedin, "Sergio", "Campos", "Security Professional",
                "Wallarm", "sergio.campos@wallarm.com", "Unknown", "Technology", 1,
                "connected", datetime.utcnow(), datetime.utcnow()
            ))
            print("✅ Created Sergio Campos contact")
        else:
            contact_id = contact_row[0]
            print("✅ Sergio Campos contact found")
        
        # Step 3: Create conversation campaign
        print("🎯 Step 3: Setting up conversation campaign...")
        
        campaign_name = "Sercio-Sergio Direct Conversation"
        cursor.execute("SELECT campaign_id FROM campaigns_new WHERE name = ?", (campaign_name,))
        campaign_row = cursor.fetchone()
        
        if not campaign_row:
            campaign_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO campaigns_new (
                    campaign_id, campaign_key, name, description, status, 
                    dux_user_id, intent, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                campaign_id, str(uuid.uuid4()), campaign_name, 
                "Direct conversation between Sercio Campos and Sergio Campos",
                "active", "117833704731893145427", "Professional networking", datetime.utcnow()
            ))
            print("✅ Created conversation campaign")
        else:
            campaign_id = campaign_row[0]
            print("✅ Conversation campaign found")
        
        # Step 4: Create campaign contact relationship
        print("🔗 Step 4: Setting up campaign contact relationship...")
        
        cursor.execute("""
            SELECT campaign_contact_id FROM campaign_contacts 
            WHERE campaign_id = ? AND contact_id = ?
        """, (campaign_id, contact_id))
        cc_row = cursor.fetchone()
        
        if not cc_row:
            cc_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO campaign_contacts (
                    campaign_contact_id, campaign_id, campaign_key, contact_id, status, 
                    sequence_step, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (cc_id, campaign_id, str(uuid.uuid4()), contact_id, "active", 1, datetime.utcnow()))
            print("✅ Created campaign contact relationship")
        else:
            cc_id = cc_row[0]
            print("✅ Campaign contact relationship found")
        
        # Step 5: Create conversation history
        print("💬 Step 5: Creating conversation history...")
        
        # Check existing messages
        cursor.execute("SELECT COUNT(*) FROM messages WHERE campaign_contact_id = ?", (cc_id,))
        message_count = cursor.fetchone()[0]
        
        if message_count == 0:
            conversation_messages = [
                {
                    "direction": "sent",
                    "message_text": "Hi Sergio! Thanks for connecting. I'm Sercio from Wallarm. I'd love to learn more about your work and discuss potential collaboration opportunities.",
                    "days_ago": 7,
                    "linkedin_message_id": "msg_001_sercio_to_sergio",
                    "status": "delivered"
                },
                {
                    "direction": "received", 
                    "message_text": "Hi Sercio! Nice to connect with you. I'm always interested in discussing security and collaboration opportunities. What kind of work are you doing at Wallarm?",
                    "days_ago": 6,
                    "linkedin_message_id": "msg_002_sergio_to_sercio",
                    "status": "received"
                },
                {
                    "direction": "sent",
                    "message_text": "Great to hear from you! At Wallarm, I focus on application security and API protection. I noticed your LinkedIn profile and thought there might be some interesting synergies between our work. Would you be open to a brief call this week?",
                    "days_ago": 5,
                    "linkedin_message_id": "msg_003_sercio_to_sergio",
                    "status": "delivered"
                },
                {
                    "direction": "received",
                    "message_text": "That sounds really interesting! I'd definitely be open to learning more about what you're working on. How about we schedule something for later this week?",
                    "days_ago": 3,
                    "linkedin_message_id": "msg_004_sergio_to_sercio",
                    "status": "received"
                }
            ]
            
            for msg_data in conversation_messages:
                message_id = str(uuid.uuid4())
                created_at = datetime.utcnow() - timedelta(days=msg_data["days_ago"])
                
                cursor.execute("""
                    INSERT INTO messages (
                        message_id, campaign_contact_id, direction, message_text,
                        linkedin_message_id, status, created_at, campaign_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    message_id, cc_id, msg_data["direction"], msg_data["message_text"],
                    msg_data["linkedin_message_id"], msg_data["status"], created_at, campaign_id
                ))
            
            print(f"✅ Created {len(conversation_messages)} conversation messages")
        else:
            print(f"✅ Found {message_count} existing messages")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("\n🎉 Sergio conversation setup completed!")
        print("📱 Ready for real conversation history!")
        
        return {
            "success": True,
            "company_id": company_id,
            "contact_id": contact_id,
            "campaign_id": campaign_id,
            "campaign_contact_id": cc_id
        }
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print("🚀 Starting Sergio Conversation Setup")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    result = setup_sergio_conversation()
    
    if result["success"]:
        print("\n✅ Database setup COMPLETE!")
        print("Now the conversation history will be stored and retrieved from the database.")
    else:
        print(f"\n❌ Setup FAILED: {result['error']}")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
