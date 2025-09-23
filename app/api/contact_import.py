from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict, Any
import pandas as pd
import uuid
from datetime import datetime
import json
import io
from dateutil import parser

from database.database import get_session
from app.models.campaign import Campaign
from app.models.contact import Contact
from app.models.campaign_contact import CampaignContact
from app.models.user import User

router = APIRouter()

def parse_date_safely(date_string):
    """Safely parse date string to datetime object"""
    if not date_string or pd.isna(date_string):
        return None
    
    try:
        # Try to parse the date string
        return parser.parse(str(date_string))
    except (ValueError, TypeError):
        # If parsing fails, return None
        return None

# Data source mappings
SOURCE_MAPPINGS = {
    "duxsoup": {
        # Handle both uppercase and mixed case field names
        "ID": "source_id",
        "id": "source_id",
        "SCANTIME": "scan_time",
        "ScanTime": "scan_time",
        "PROFILE": "linkedin_url",
        "Profile": "linkedin_url",
        "SALESPROFILE": "sales_profile_url",
        "SalesProfile": "sales_profile_url",
        "PUBLICPROFILE": "public_profile_url",
        "PublicProfile": "public_profile_url",
        "RecruiterProfile": "recruiter_profile_url",
        "FIRST NAME": "first_name",
        "First Name": "first_name",
        "MIDDLE NAME": "middle_name",
        "Middle Name": "middle_name",
        "LAST NAME": "last_name",
        "Last Name": "last_name",
        "TITLE": "job_title",
        "Title": "job_title",
        "COMPANY": "company_name",
        "Company": "company_name",
        "CompanyID": "company_id",
        "LOCATION": "location",
        "Location": "location",
        "INDUSTRY": "industry",
        "Industry": "industry",
        "CONNECTIONS": "connection_count",
        "COMPANY SIZE": "company_size",
        "COMPANY WEBSITE": "company_website",
        "EMAIL": "email",
        "PHONE": "phone",
        "LINKEDIN URL": "linkedin_url",
        "PROFILE URL": "linkedin_url",
        "My Notes": "notes"
    },
    "zoominfo": {
        "First Name": "first_name",
        "Last Name": "last_name", 
        "Job Title": "job_title",
        "Company Name": "company_name",
        "Email": "email",
        "Phone": "phone",
        "Industry": "industry",
        "Company Size": "company_size",
        "LinkedIn URL": "linkedin_url",
        "Location": "location"
    },
    "apollo": {
        "first_name": "first_name",
        "last_name": "last_name",
        "title": "job_title",
        "organization_name": "company_name",
        "email": "email",
        "phone": "phone",
        "linkedin_url": "linkedin_url",
        "industry": "industry",
        "location": "location"
    },
    # "custom" will be handled separately with direct mapping
}

@router.post("/campaigns/{campaign_id}/contacts/import", tags=["Contact Import"])
async def import_contacts(
    campaign_id: str,
    file: UploadFile = File(...),
    source: str = Form(...),
    field_mapping: Optional[str] = Form(None),
    assign_to_team: bool = Form(True),
    session: AsyncSession = Depends(get_session)
):
    """Import contacts from various data sources (DuxSoup, ZoomInfo, Apollo, custom)"""
    try:
        # Validate campaign exists
        campaign_query = select(Campaign).where(Campaign.campaign_id == campaign_id)
        result = await session.execute(campaign_query)
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Validate source
        if source not in SOURCE_MAPPINGS and source != "custom":
            raise HTTPException(status_code=400, detail=f"Unsupported source: {source}")
        
        # Read and parse file
        content = await file.read()
        
        # Determine file type and read
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV or Excel.")
        
        # Get field mapping
        if field_mapping:
            mapping = json.loads(field_mapping)
        elif source in SOURCE_MAPPINGS:
            mapping = SOURCE_MAPPINGS[source]
        else:
            # For custom source, create a direct mapping (field name = field name)
            mapping = {field: field for field in df.columns}
        
        # Process contacts
        import_batch_id = str(uuid.uuid4())
        processed_contacts = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Map fields
                contact_data = {}
                for source_field, target_field in mapping.items():
                    if source_field in row and pd.notna(row[source_field]):
                        value = row[source_field]
                        # Convert to string and strip whitespace
                        if value is not None:
                            contact_data[target_field] = str(value).strip()
                
                # Validate required fields
                if not contact_data.get('full_name') and not (contact_data.get('first_name') and contact_data.get('last_name')):
                    errors.append(f"Row {index + 1}: Missing name information")
                    continue
                
                if not contact_data.get('email') and not contact_data.get('linkedin_url'):
                    errors.append(f"Row {index + 1}: Missing email or LinkedIn URL")
                    continue
                
                # Create full name if not provided
                if not contact_data.get('full_name'):
                    first_name = contact_data.get('first_name', '')
                    last_name = contact_data.get('last_name', '')
                    contact_data['full_name'] = f"{first_name} {last_name}".strip()
                
                # Check for duplicates
                existing_contact = None
                if contact_data.get('email'):
                    email_query = select(Contact).where(Contact.email == contact_data['email'])
                    result = await session.execute(email_query)
                    existing_contact = result.scalar_one_or_none()
                
                if not existing_contact and contact_data.get('linkedin_url'):
                    linkedin_query = select(Contact).where(Contact.linkedin_url == contact_data['linkedin_url'])
                    result = await session.execute(linkedin_query)
                    existing_contact = result.scalar_one_or_none()
                
                if existing_contact:
                    # Update existing contact
                    datetime_fields = ['scan_time', 'connection_request_sent', 'connection_accepted', 'last_message_sent']
                    
                    for field, value in contact_data.items():
                        if hasattr(existing_contact, field) and value:
                            # Special handling for datetime fields
                            if field in datetime_fields:
                                parsed_date = parse_date_safely(value)
                                if parsed_date:
                                    setattr(existing_contact, field, parsed_date)
                            else:
                                setattr(existing_contact, field, value)
                    existing_contact.updated_at = datetime.utcnow()
                    contact = existing_contact
                else:
                    # Create new contact
                    contact = Contact(
                        contact_id=str(uuid.uuid4()),
                        full_name=contact_data.get('full_name', ''),
                        first_name=contact_data.get('first_name', ''),
                        middle_name=contact_data.get('middle_name', ''),
                        last_name=contact_data.get('last_name', ''),
                        email=contact_data.get('email'),
                        phone=contact_data.get('phone'),
                        job_title=contact_data.get('job_title'),
                        company_name=contact_data.get('company_name'),
                        linkedin_url=contact_data.get('linkedin_url'),
                        location=contact_data.get('location'),
                        industry=contact_data.get('industry'),
                        company_size=contact_data.get('company_size'),
                        company_website=contact_data.get('company_website'),
                        connection_count=contact_data.get('connection_count'),
                        sales_profile_url=contact_data.get('sales_profile_url'),
                        public_profile_url=contact_data.get('public_profile_url'),
                        recruiter_profile_url=contact_data.get('recruiter_profile_url'),
                        company_id=contact_data.get('company_id'),
                        scan_time=parse_date_safely(contact_data.get('scan_time')),
                        connection_request_sent=parse_date_safely(contact_data.get('connection_request_sent')),
                        connection_accepted=parse_date_safely(contact_data.get('connection_accepted')),
                        last_message_sent=parse_date_safely(contact_data.get('last_message_sent')),
                        data_source=source,
                        source_id=contact_data.get('source_id', str(uuid.uuid4())),
                        import_batch_id=import_batch_id,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    session.add(contact)
                
                # Create campaign contact relationship
                campaign_contact = CampaignContact(
                    campaign_contact_id=str(uuid.uuid4()),
                    campaign_id=campaign_id,
                    campaign_key=campaign.campaign_key,  # Use the campaign's key
                    contact_id=contact.contact_id,
                    status="pending",
                    assigned_to=None,  # Will be assigned later if assign_to_team is True
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(campaign_contact)
                
                processed_contacts.append({
                    "contact_id": contact.contact_id,
                    "full_name": contact.full_name,
                    "email": contact.email,
                    "company_name": contact.company_name,
                    "job_title": contact.job_title
                })
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        # Assign to team if requested
        if assign_to_team and processed_contacts:
            await assign_contacts_to_team(campaign_id, processed_contacts, session)
        
        await session.commit()
        
        return {
            "message": "Contacts imported successfully",
            "import_batch_id": import_batch_id,
            "total_processed": len(processed_contacts),
            "errors": errors,
            "contacts": processed_contacts[:10]  # Return first 10 for preview
        }
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to import contacts: {str(e)}")

@router.post("/campaigns/{campaign_id}/contacts/import/preview", tags=["Contact Import"])
async def preview_import(
    campaign_id: str,
    file: UploadFile = File(...),
    source: str = Form(...),
    field_mapping: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_session)
):
    """Preview contacts before importing"""
    try:
        # Read and parse file
        content = await file.read()
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Get field mapping
        if field_mapping:
            mapping = json.loads(field_mapping)
        elif source in SOURCE_MAPPINGS:
            mapping = SOURCE_MAPPINGS[source]
        else:
            # For custom source, create a direct mapping (field name = field name)
            mapping = {field: field for field in df.columns}
        
        # Preview first 10 rows
        preview_data = []
        for index, row in df.head(10).iterrows():
            mapped_row = {}
            for source_field, target_field in mapping.items():
                if source_field in row and pd.notna(row[source_field]):
                    mapped_row[target_field] = str(row[source_field]).strip()
            preview_data.append(mapped_row)
        
        return {
            "preview": preview_data,
            "total_rows": len(df),
            "available_fields": list(df.columns),
            "mapping": mapping
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to preview import: {str(e)}")

async def assign_contacts_to_team(campaign_id: str, contacts: List[Dict], session: AsyncSession):
    """Assign contacts to team members evenly"""
    try:
        # Get all active users
        users_query = select(User).where(User.is_active == True)
        result = await session.execute(users_query)
        users = result.scalars().all()
        
        if not users:
            return  # No users to assign to
        
        # Distribute contacts evenly
        contacts_per_user = len(contacts) // len(users)
        remainder = len(contacts) % len(users)
        
        contact_index = 0
        for user_index, user in enumerate(users):
            # Calculate how many contacts this user gets
            user_contact_count = contacts_per_user
            if user_index < remainder:
                user_contact_count += 1
            
            # Assign contacts to this user
            for i in range(user_contact_count):
                if contact_index < len(contacts):
                    contact_id = contacts[contact_index]['contact_id']
                    
                    # Update campaign contact assignment
                    campaign_contact_query = select(CampaignContact).where(
                        CampaignContact.campaign_id == campaign_id,
                        CampaignContact.contact_id == contact_id
                    )
                    result = await session.execute(campaign_contact_query)
                    campaign_contact = result.scalar_one_or_none()
                    
                    if campaign_contact:
                        campaign_contact.assigned_to = user.user_id
                        campaign_contact.updated_at = datetime.utcnow()
                    
                    contact_index += 1
        
    except Exception as e:
        print(f"Error assigning contacts to team: {e}")

@router.get("/campaigns/{campaign_id}/contacts/assignments", tags=["Contact Import"])
async def get_contact_assignments(
    campaign_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get contact assignments for a campaign"""
    try:
        # Get campaign contacts with assignments
        query = select(CampaignContact, Contact, User).join(
            Contact, CampaignContact.contact_id == Contact.contact_id
        ).outerjoin(
            User, CampaignContact.assigned_to == User.user_id
        ).where(
            CampaignContact.campaign_id == campaign_id
        )
        
        result = await session.execute(query)
        assignments = result.fetchall()
        
        # Group by user
        user_assignments = {}
        unassigned = []
        
        for campaign_contact, contact, user in assignments:
            if user:
                if user.user_id not in user_assignments:
                    user_assignments[user.user_id] = {
                        "user": {
                            "user_id": user.user_id,
                            "username": user.username,
                            "email": user.email
                        },
                        "contacts": []
                    }
                
                user_assignments[user.user_id]["contacts"].append({
                    "contact_id": contact.contact_id,
                    "full_name": contact.full_name,
                    "email": contact.email,
                    "company_name": contact.company_name,
                    "job_title": contact.job_title,
                    "status": campaign_contact.status
                })
            else:
                unassigned.append({
                    "contact_id": contact.contact_id,
                    "full_name": contact.full_name,
                    "email": contact.email,
                    "company_name": contact.company_name,
                    "job_title": contact.job_title,
                    "status": campaign_contact.status
                })
        
        return {
            "user_assignments": list(user_assignments.values()),
            "unassigned": unassigned,
            "total_assigned": sum(len(assignment["contacts"]) for assignment in user_assignments.values()),
            "total_unassigned": len(unassigned)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get assignments: {str(e)}")

@router.post("/campaigns/{campaign_id}/contacts/reassign", tags=["Contact Import"])
async def reassign_contacts(
    campaign_id: str,
    contact_ids: List[str],
    assigned_to: str,
    session: AsyncSession = Depends(get_session)
):
    """Reassign contacts to a different team member"""
    try:
        # Update campaign contacts
        for contact_id in contact_ids:
            query = select(CampaignContact).where(
                CampaignContact.campaign_id == campaign_id,
                CampaignContact.contact_id == contact_id
            )
            result = await session.execute(query)
            campaign_contact = result.scalar_one_or_none()
            
            if campaign_contact:
                campaign_contact.assigned_to = assigned_to
                campaign_contact.updated_at = datetime.utcnow()
        
        await session.commit()
        
        return {"message": f"Reassigned {len(contact_ids)} contacts successfully"}
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to reassign contacts: {str(e)}")
