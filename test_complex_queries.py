#!/usr/bin/env python3
"""
Complex Query Testing Script for Chaknal Platform
Tests filtering, pagination, joins, aggregations, and complex scenarios
"""

import asyncio
import json
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, or_, desc, asc, text
from sqlalchemy.orm import selectinload, joinedload
from database.database import async_session_maker
from app.models.user import User, Organization
from app.models.company import Company
from app.models.campaign import Campaign, CampaignStatus
from app.models.contact import Contact
from app.models.campaign_contact import CampaignContact
from app.models.duxsoup_user import DuxSoupUser
from app.models.message import Message
from app.models.webhook_event import WebhookEvent

async def test_complex_queries():
    """Test various complex database queries"""
    async with async_session_maker() as session:
        print("🔍 Testing Complex Database Queries...")
        print("=" * 50)
        
        # 1. Test filtering and pagination
        print("\n1️⃣ Testing Filtering and Pagination")
        print("-" * 30)
        
        # Get active campaigns with pagination
        active_campaigns_query = select(Campaign).where(
            Campaign.status == "active"
        ).order_by(desc(Campaign.created_at)).limit(3).offset(0)
        
        result = await session.execute(active_campaigns_query)
        active_campaigns = result.scalars().all()
        
        print(f"📈 Active campaigns (limit 3): {len(active_campaigns)}")
        for campaign in active_campaigns:
            print(f"   - {campaign.name} ({campaign.status}) - Created: {campaign.created_at}")
        
        # 2. Test complex joins and relationships
        print("\n2️⃣ Testing Complex Joins and Relationships")
        print("-" * 40)
        
        # Get campaigns with their contacts and user info
        campaigns_with_contacts_query = select(Campaign).options(
            selectinload(Campaign.campaign_contacts).selectinload(CampaignContact.contact),
            selectinload(Campaign.webhook_events)
        ).where(Campaign.status.in_(["active", "paused"]))
        
        result = await session.execute(campaigns_with_contacts_query)
        campaigns_with_contacts = result.scalars().all()
        
        print(f"📊 Campaigns with contacts and webhooks: {len(campaigns_with_contacts)}")
        for campaign in campaigns_with_contacts:
            contact_count = len(campaign.campaign_contacts)
            webhook_count = len(campaign.webhook_events)
            print(f"   - {campaign.name}: {contact_count} contacts, {webhook_count} webhooks")
        
        # 3. Test aggregation queries
        print("\n3️⃣ Testing Aggregation Queries")
        print("-" * 30)
        
        # Count contacts by industry
        industry_stats_query = select(
            Contact.industry,
            func.count(Contact.contact_id).label('contact_count')
        ).group_by(Contact.industry).order_by(desc('contact_count'))
        
        result = await session.execute(industry_stats_query)
        industry_stats = result.all()
        
        print("🏭 Contacts by Industry:")
        for industry, count in industry_stats:
            print(f"   - {industry}: {count} contacts")
        
        # Count campaigns by status
        campaign_status_query = select(
            Campaign.status,
            func.count(Campaign.campaign_id).label('campaign_count')
        ).group_by(Campaign.status).order_by(desc('campaign_count'))
        
        result = await session.execute(campaign_status_query)
        campaign_status_stats = result.all()
        
        print("\n📊 Campaigns by Status:")
        for status, count in campaign_status_stats:
            print(f"   - {status}: {count} campaigns")
        
        # 4. Test advanced filtering
        print("\n4️⃣ Testing Advanced Filtering")
        print("-" * 30)
        
        # Get contacts with specific criteria
        advanced_contact_query = select(Contact).where(
            and_(
                Contact.connection_degree <= 2,
                Contact.industry.in_(["Technology", "Marketing"]),
                Contact.location.like("%San Francisco%")
            )
        ).order_by(asc(Contact.last_name))
        
        result = await session.execute(advanced_contact_query)
        filtered_contacts = result.scalars().all()
        
        print(f"🎯 Filtered contacts (SF, Tech/Marketing, ≤2 degrees): {len(filtered_contacts)}")
        for contact in filtered_contacts[:5]:  # Show first 5
            print(f"   - {contact.first_name} {contact.last_name} ({contact.industry}) - {contact.location}")
        
        # 5. Test date-based queries
        print("\n5️⃣ Testing Date-based Queries")
        print("-" * 30)
        
        # Get recent campaign contacts
        recent_date = datetime.utcnow() - timedelta(days=7)
        recent_contacts_query = select(CampaignContact).where(
            CampaignContact.enrolled_at >= recent_date
        ).options(
            selectinload(CampaignContact.contact),
            selectinload(CampaignContact.campaign)
        ).order_by(desc(CampaignContact.enrolled_at))
        
        result = await session.execute(recent_contacts_query)
        recent_contacts = result.scalars().all()
        
        print(f"📅 Recent campaign contacts (last 7 days): {len(recent_contacts)}")
        for contact in recent_contacts[:3]:  # Show first 3
            print(f"   - {contact.contact.first_name} {contact.contact.last_name} enrolled in {contact.campaign.name}")
        
        # 6. Test complex search scenarios
        print("\n6️⃣ Testing Complex Search Scenarios")
        print("-" * 35)
        
        # Search for contacts by multiple criteria
        search_query = select(Contact).where(
            or_(
                Contact.first_name.ilike("%james%"),
                Contact.last_name.ilike("%wilson%"),
                Contact.company.ilike("%salesforce%"),
                Contact.headline.ilike("%manager%")
            )
        ).options(selectinload(Contact.campaign_contacts))
        
        result = await session.execute(search_query)
        search_results = result.scalars().all()
        
        print(f"🔍 Search results for 'james', 'wilson', 'salesforce', 'manager': {len(search_results)}")
        for contact in search_results:
            campaign_count = len(contact.campaign_contacts)
            print(f"   - {contact.first_name} {contact.last_name} at {contact.company} ({campaign_count} campaigns)")
        
        # 7. Test performance queries
        print("\n7️⃣ Testing Performance and Analytics Queries")
        print("-" * 40)
        
        # Get campaign performance metrics
        performance_query = select(
            Campaign.campaign_id,
            Campaign.name,
            Campaign.status,
            func.count(CampaignContact.campaign_contact_id).label('total_contacts'),
            func.count(CampaignContact.campaign_contact_id).filter(
                CampaignContact.status == "accepted"
            ).label('accepted_contacts'),
            func.count(CampaignContact.campaign_contact_id).filter(
                CampaignContact.status == "replied"
            ).label('replied_contacts')
        ).outerjoin(CampaignContact).group_by(
            Campaign.campaign_id, Campaign.name, Campaign.status
        ).order_by(desc('total_contacts'))
        
        result = await session.execute(performance_query)
        performance_metrics = result.all()
        
        print("📊 Campaign Performance Metrics:")
        for metric in performance_metrics:
            campaign_id, name, status, total, accepted, replied = metric
            acceptance_rate = (accepted / total * 100) if total > 0 else 0
            reply_rate = (replied / total * 100) if total > 0 else 0
            print(f"   - {name} ({status}): {total} contacts, {acceptance_rate:.1f}% accepted, {reply_rate:.1f}% replied")
        
        # 8. Test JSON field queries
        print("\n8️⃣ Testing JSON Field Queries")
        print("-" * 30)
        
        # Get contacts with specific skills
        skills_query = select(Contact).where(
            Contact.profile_data.contains('{"skills": ["Leadership"]}')
        ).limit(5)
        
        result = await session.execute(skills_query)
        leadership_contacts = result.scalars().all()
        
        print(f"🎯 Contacts with Leadership skills: {len(leadership_contacts)}")
        for contact in leadership_contacts:
            skills = contact.profile_data.get("skills", []) if contact.profile_data else []
            print(f"   - {contact.first_name} {contact.last_name}: {skills}")
        
        # 9. Test subqueries
        print("\n9️⃣ Testing Subqueries")
        print("-" * 25)
        
        # Get companies with most users
        company_user_count_query = select(
            Company.name,
            func.count(User.id).label('user_count')
        ).join(User).group_by(Company.id, Company.name).having(
            func.count(User.id) > 0
        ).order_by(desc('user_count'))
        
        result = await session.execute(company_user_count_query)
        company_user_counts = result.all()
        
        print("🏢 Companies by User Count:")
        for company_name, user_count in company_user_counts:
            print(f"   - {company_name}: {user_count} users")
        
        # 10. Test raw SQL queries
        print("\n🔟 Testing Raw SQL Queries")
        print("-" * 25)
        
        # Complex raw SQL query
        raw_sql = text("""
            SELECT 
                c.name as company_name,
                o.name as org_name,
                COUNT(u.id) as user_count,
                COUNT(DISTINCT camp.campaign_id) as campaign_count
            FROM company c
            LEFT JOIN organization o ON c.id = o.id
            LEFT JOIN user u ON o.id = u.organization_id
            LEFT JOIN campaigns_new camp ON u.id = camp.dux_user_id
            GROUP BY c.id, c.name, o.id, o.name
            HAVING user_count > 0
            ORDER BY user_count DESC, campaign_count DESC
        """)
        
        result = await session.execute(raw_sql)
        raw_results = result.all()
        
        print("🔧 Raw SQL Results (Company-Org-User-Campaign):")
        for row in raw_results:
            print(f"   - {row.company_name} > {row.org_name}: {row.user_count} users, {row.campaign_count} campaigns")
        
        print("\n✅ All complex queries tested successfully!")
        print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_complex_queries())
