"""
Contact Import API - Simplified and Robust Implementation
Handles CSV and Excel file imports for contact management
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import json
import io
import csv

from database.database import get_session
from app.models.campaign import Campaign
from app.models.contact import Contact
from app.models.campaign_contact import CampaignContact

router = APIRouter()

# Simplified data source mappings
SOURCE_MAPPINGS = {
    "duxsoup": {
        "ID": "source_id",
        "FIRST NAME": "first_name",
        "Last Name": "last_name", 
        "TITLE": "job_title",
        "COMPANY": "company_name",
        "EMAIL": "email",
        "LINKEDIN URL": "linkedin_url",
        "LOCATION": "location",
        "INDUSTRY": "industry"
    },
    "zoominfo": {
        "First Name": "first_name",
        "Last Name": "last_name",
        "Job Title": "job_title", 
        "Company Name": "company_name",
        "Email": "email",
        "LinkedIn URL": "linkedin_url",
        "Location": "location"
    },
    "apollo": {
        "first_name": "first_name",
        "last_name": "last_name",
        "title": "job_title",
        "organization_name": "company_name", 
        "email": "email",
        "linkedin_url": "linkedin_url",
        "location": "location"
    }
}

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
        # Validate campaign exists
        campaign_query = select(Campaign).where(Campaign.campaign_id == campaign_id)
        result = await session.execute(campaign_query)
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Read and parse file
        content = await file.read()
        
        # Determine file type and read
        if file.filename.endswith('.csv'):
            csv_content = content.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            rows = list(csv_reader)
        elif file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Excel files not supported in this version. Use CSV format.")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV format.")
        
        # Get field mapping
        if field_mapping:
            mapping = json.loads(field_mapping)
        elif source in SOURCE_MAPPINGS:
            mapping = SOURCE_MAPPINGS[source]
        else:
            # For custom source, create a direct mapping
            mapping = {field: field for field in csv_reader.fieldnames}
        
        # Preview first 10 rows
        preview_data = []
        for i, row in enumerate(rows[:10]):
            mapped_row = {}
            for source_field, target_field in mapping.items():
                if source_field in row and row[source_field] and row[source_field].strip():
                    mapped_row[target_field] = str(row[source_field]).strip()
            preview_data.append(mapped_row)
        
        return {
            "preview": preview_data,
            "total_rows": len(rows),
            "available_fields": csv_reader.fieldnames,
            "mapping": mapping
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to preview import: {str(e)}")

@router.post("/campaigns/{campaign_id}/contacts/import", tags=["Contact Import"])
async def import_contacts(
    campaign_id: str,
    file: UploadFile = File(...),
    source: str = Form(...),
    field_mapping: Optional[str] = Form(None),
    assign_to_team: bool = Form(True),
    session: AsyncSession = Depends(get_session)
):
    """Import contacts from various data sources"""
    try:
        # Validate campaign exists
        campaign_query = select(Campaign).where(Campaign.campaign_id == campaign_id)
        result = await session.execute(campaign_query)
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Read and parse file
        content = await file.read()
        
        # Determine file type and read
        if file.filename.endswith('.csv'):
            csv_content = content.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            rows = list(csv_reader)
        elif file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Excel files not supported in this version. Use CSV format.")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV format.")
        
        # Get field mapping
        if field_mapping:
            mapping = json.loads(field_mapping)
        elif source in SOURCE_MAPPINGS:
            mapping = SOURCE_MAPPINGS[source]
        else:
            # For custom source, create a direct mapping
            mapping = {field: field for field in csv_reader.fieldnames}
        
        # Process contacts
        import_batch_id = str(uuid.uuid4())
        processed_contacts = []
        errors = []
        
        for index, row in enumerate(rows):
            try:
                # Map fields
                contact_data = {}
                for source_field, target_field in mapping.items():
                    if source_field in row and row[source_field] and row[source_field].strip():
                        value = row[source_field]
                        if value is not None:
                            contact_data[target_field] = str(value).strip()
                
                # Validate required fields
                if not contact_data.get('first_name') and not contact_data.get('last_name'):
                    errors.append(f"Row {index + 1}: Missing name information")
                    continue
                
                if not contact_data.get('email') and not contact_data.get('linkedin_url'):
                    errors.append(f"Row {index + 1}: Missing email or LinkedIn URL")
                    continue
                
                # Create full name if not provided
                first_name = contact_data.get('first_name', '')
                last_name = contact_data.get('last_name', '')
                full_name = f"{first_name} {last_name}".strip()
                
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
                    contact = existing_contact
                    for field, value in contact_data.items():
                        if hasattr(contact, field):
                            setattr(contact, field, value)
                    contact.updated_at = datetime.utcnow()
                else:
                    # Create new contact
                    contact = Contact(
                        contact_id=str(uuid.uuid4()),
                        full_name=full_name,
                        first_name=first_name,
                        last_name=last_name,
                        email=contact_data.get('email'),
                        linkedin_url=contact_data.get('linkedin_url'),
                        company_name=contact_data.get('company_name'),
                        job_title=contact_data.get('job_title'),
                        location=contact_data.get('location'),
                        industry=contact_data.get('industry'),
                        import_batch_id=import_batch_id,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    session.add(contact)
                
                # Create campaign contact relationship
                campaign_contact = CampaignContact(
                    campaign_contact_id=str(uuid.uuid4()),
                    campaign_id=campaign_id,
                    campaign_key=campaign.campaign_key,
                    contact_id=contact.contact_id,
                    status="pending",
                    assigned_to=None,
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

@router.get("/campaigns/{campaign_id}/contacts/import/status/{batch_id}", tags=["Contact Import"])
async def get_import_status(
    campaign_id: str,
    batch_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get status of a contact import batch"""
    try:
        # Query contacts by batch ID
        contacts_query = select(Contact).where(Contact.import_batch_id == batch_id)
        result = await session.execute(contacts_query)
        contacts = result.scalars().all()
        
        return {
            "batch_id": batch_id,
            "total_contacts": len(contacts),
            "status": "completed" if contacts else "processing"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get import status: {str(e)}")
