#!/usr/bin/env python3
"""
Populate Chaknal Platform Database with Sample Data
This script adds sample data to make the frontend functional
"""

import requests
import json
import time
from datetime import datetime, timedelta
import random

# Configuration
BACKEND_URL = "https://chaknal-backend-container.azurewebsites.net"

def create_sample_campaigns():
    """Create sample campaigns"""
    print("📊 Creating sample campaigns...")
    
    campaigns = [
        {
            "name": "LinkedIn Outreach Q4 2025",
            "description": "Outreach campaign for Q4 2025 targeting tech professionals",
            "status": "active",
            "target_audience": "Tech professionals in SaaS companies",
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=60)).isoformat(),
            "budget": 5000.00,
            "expected_leads": 200
        },
        {
            "name": "Enterprise Sales Outreach",
            "description": "Targeting enterprise decision makers for our new product",
            "status": "active",
            "target_audience": "Enterprise decision makers",
            "start_date": (datetime.now() - timedelta(days=15)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=45)).isoformat(),
            "budget": 7500.00,
            "expected_leads": 150
        },
        {
            "name": "Startup Community Engagement",
            "description": "Engaging with startup founders and investors",
            "status": "paused",
            "target_audience": "Startup founders and investors",
            "start_date": (datetime.now() - timedelta(days=60)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "budget": 3000.00,
            "expected_leads": 100
        }
    ]
    
    created_campaigns = []
    for campaign in campaigns:
        try:
            response = requests.post(f"{BACKEND_URL}/api/campaigns/", json=campaign, timeout=10)
            if response.status_code == 200:
                created_campaign = response.json()
                created_campaigns.append(created_campaign)
                print(f"   ✅ Created campaign: {campaign['name']}")
            else:
                print(f"   ❌ Failed to create campaign: {campaign['name']} - {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error creating campaign {campaign['name']}: {e}")
    
    return created_campaigns

def create_sample_contacts():
    """Create sample contacts"""
    print("👥 Creating sample contacts...")
    
    # Sample contact data
    first_names = ["John", "Sarah", "Michael", "Emily", "David", "Lisa", "Robert", "Jennifer", "James", "Maria", "William", "Jessica", "Richard", "Ashley", "Charles", "Amanda", "Thomas", "Stephanie", "Christopher", "Nicole"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
    companies = ["TechCorp", "InnovateLabs", "DataFlow", "CloudSync", "NextGen", "FutureTech", "SmartSolutions", "DigitalWorks", "ApexSystems", "PrimeTech", "EliteCorp", "VisionSoft", "QuantumTech", "NexusLabs", "PinnacleInc"]
    industries = ["Technology", "Healthcare", "Finance", "Education", "Manufacturing", "Retail", "Consulting", "Real Estate", "Marketing", "Legal"]
    titles = ["CEO", "CTO", "VP Engineering", "Director of Sales", "Head of Marketing", "Product Manager", "Sales Manager", "Marketing Director", "Operations Manager", "Business Development"]
    
    contacts = []
    for i in range(50):  # Create 50 sample contacts
        contact = {
            "first_name": random.choice(first_names),
            "last_name": random.choice(last_names),
            "email": f"{random.choice(first_names).lower()}.{random.choice(last_names).lower()}@{random.choice(companies).lower()}.com",
            "company": random.choice(companies),
            "title": random.choice(titles),
            "industry": random.choice(industries),
            "linkedin_url": f"https://linkedin.com/in/{random.choice(first_names).lower()}-{random.choice(last_names).lower()}-{random.randint(1000, 9999)}",
            "phone": f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}",
            "location": f"{random.choice(['New York', 'San Francisco', 'Los Angeles', 'Chicago', 'Boston', 'Seattle', 'Austin', 'Denver'])}",
            "status": random.choice(["new", "contacted", "responded", "qualified", "nurturing", "converted"]),
            "source": random.choice(["LinkedIn", "Website", "Referral", "Cold Outreach", "Event", "Social Media"]),
            "notes": f"Sample contact {i+1} - {random.choice(['Interested in our product', 'Potential enterprise client', 'Startup founder', 'Looking for solutions', 'Referred by colleague'])}"
        }
        contacts.append(contact)
    
    created_contacts = []
    for i, contact in enumerate(contacts):
        try:
            response = requests.post(f"{BACKEND_URL}/api/contacts/", json=contact, timeout=10)
            if response.status_code == 200:
                created_contact = response.json()
                created_contacts.append(created_contact)
                if (i + 1) % 10 == 0:
                    print(f"   ✅ Created {i + 1} contacts...")
            else:
                print(f"   ❌ Failed to create contact {i+1} - {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error creating contact {i+1}: {e}")
    
    print(f"   ✅ Created {len(created_contacts)} contacts total")
    return created_contacts

def create_sample_messages():
    """Create sample messages"""
    print("💬 Creating sample messages...")
    
    message_templates = [
        "Hi {first_name}, I noticed your work at {company} and thought you might be interested in our solution.",
        "Hello {first_name}, I'd love to connect and share how we've helped companies like {company} achieve their goals.",
        "Hi {first_name}, I saw your recent post about {industry} and thought our platform might be relevant.",
        "Hello {first_name}, I'm reaching out because I believe our solution could help {company} with their challenges.",
        "Hi {first_name}, I'd like to introduce you to our platform that's been helping companies in {industry}."
    ]
    
    # Get existing contacts and campaigns
    try:
        contacts_response = requests.get(f"{BACKEND_URL}/api/contacts/", timeout=10)
        campaigns_response = requests.get(f"{BACKEND_URL}/api/campaigns/", timeout=10)
        
        contacts = contacts_response.json() if contacts_response.status_code == 200 else []
        campaigns = campaigns_response.json() if campaigns_response.status_code == 200 else []
        
        if not contacts or not campaigns:
            print("   ⚠️ No contacts or campaigns found, skipping messages")
            return []
        
        messages = []
        for i in range(min(30, len(contacts))):  # Create up to 30 messages
            contact = contacts[i]
            campaign = random.choice(campaigns)
            
            message_content = random.choice(message_templates).format(
                first_name=contact.get('first_name', 'there'),
                company=contact.get('company', 'your company'),
                industry=contact.get('industry', 'your industry')
            )
            
            message = {
                "contact_id": contact['id'],
                "campaign_id": campaign['id'],
                "content": message_content,
                "type": random.choice(["connection_request", "follow_up", "introduction", "nurture"]),
                "status": random.choice(["sent", "delivered", "opened", "replied"]),
                "sent_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                "channel": "LinkedIn"
            }
            messages.append(message)
        
        created_messages = []
        for i, message in enumerate(messages):
            try:
                response = requests.post(f"{BACKEND_URL}/api/messages/", json=message, timeout=10)
                if response.status_code == 200:
                    created_message = response.json()
                    created_messages.append(created_message)
                    if (i + 1) % 10 == 0:
                        print(f"   ✅ Created {i + 1} messages...")
                else:
                    print(f"   ❌ Failed to create message {i+1} - {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error creating message {i+1}: {e}")
        
        print(f"   ✅ Created {len(created_messages)} messages total")
        return created_messages
        
    except Exception as e:
        print(f"   ❌ Error getting contacts/campaigns: {e}")
        return []

def create_sample_analytics():
    """Create sample analytics data"""
    print("📈 Creating sample analytics data...")
    
    # This would typically be handled by the analytics endpoints
    # For now, we'll just verify the analytics endpoints are working
    try:
        response = requests.get(f"{BACKEND_URL}/api/contact-dashboard/overview", timeout=10)
        if response.status_code == 200:
            print("   ✅ Analytics endpoints are working")
        else:
            print(f"   ⚠️ Analytics endpoint returned: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️ Analytics endpoint error: {e}")

def main():
    """Main function to populate sample data"""
    print("🚀 Populating Chaknal Platform with Sample Data")
    print("=" * 50)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Check if backend is accessible
    try:
        health_response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if health_response.status_code != 200:
            print("❌ Backend is not accessible. Please check the URL and try again.")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return
    
    print("✅ Backend is accessible")
    print()
    
    # Create sample data
    campaigns = create_sample_campaigns()
    print()
    
    contacts = create_sample_contacts()
    print()
    
    messages = create_sample_messages()
    print()
    
    create_sample_analytics()
    print()
    
    # Summary
    print("📋 Sample Data Summary:")
    print(f"   Campaigns: {len(campaigns)}")
    print(f"   Contacts: {len(contacts)}")
    print(f"   Messages: {len(messages)}")
    print()
    
    if campaigns and contacts:
        print("🎉 Sample data created successfully!")
        print("   The frontend should now display data.")
        print(f"   Visit: https://agreeable-bush-01890e00f.1.azurestaticapps.net")
    else:
        print("⚠️ Some data creation failed. Check the errors above.")

if __name__ == "__main__":
    main()
