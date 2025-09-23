"""
Contacts API Router - Rebuilt from scratch
Simple, clean implementation of contact endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter()

# Pydantic models
class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    linkedin_url: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None

class ContactResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    linkedin_url: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    status: str = "active"

# In-memory storage for now
contacts_db = []

@router.get("/contacts/", response_model=List[ContactResponse])
async def get_contacts():
    """Get all contacts"""
    return contacts_db

@router.post("/contacts/", response_model=ContactResponse)
async def create_contact(contact: ContactCreate):
    """Create a new contact"""
    contact_id = str(uuid.uuid4())
    now = datetime.now()
    
    new_contact = ContactResponse(
        id=contact_id,
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone=contact.phone,
        company=contact.company,
        job_title=contact.job_title,
        linkedin_url=contact.linkedin_url,
        location=contact.location,
        industry=contact.industry,
        created_at=now,
        updated_at=now,
        status="active"
    )
    
    contacts_db.append(new_contact)
    return new_contact

@router.get("/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: str):
    """Get a specific contact by ID"""
    for contact in contacts_db:
        if contact.id == contact_id:
            return contact
    
    raise HTTPException(status_code=404, detail="Contact not found")

@router.put("/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: str, contact: ContactCreate):
    """Update a contact"""
    for i, existing_contact in enumerate(contacts_db):
        if existing_contact.id == contact_id:
            updated_contact = ContactResponse(
                id=contact_id,
                first_name=contact.first_name,
                last_name=contact.last_name,
                email=contact.email,
                phone=contact.phone,
                company=contact.company,
                job_title=contact.job_title,
                linkedin_url=contact.linkedin_url,
                location=contact.location,
                industry=contact.industry,
                created_at=existing_contact.created_at,
                updated_at=datetime.now(),
                status=existing_contact.status
            )
            contacts_db[i] = updated_contact
            return updated_contact
    
    raise HTTPException(status_code=404, detail="Contact not found")

@router.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: str):
    """Delete a contact"""
    for i, contact in enumerate(contacts_db):
        if contact.id == contact_id:
            del contacts_db[i]
            return {"message": "Contact deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Contact not found")

@router.get("/contacts/stats")
async def get_contact_stats():
    """Get contact statistics"""
    total_contacts = len(contacts_db)
    active_contacts = len([c for c in contacts_db if c.status == "active"])
    
    return {
        "total_contacts": total_contacts,
        "active_contacts": active_contacts,
        "inactive_contacts": total_contacts - active_contacts
    }

@router.get("/contacts/filters")
async def get_contact_filters():
    """Get available contact filters"""
    return {
        "industries": list(set([c.industry for c in contacts_db if c.industry])),
        "companies": list(set([c.company for c in contacts_db if c.company])),
        "locations": list(set([c.location for c in contacts_db if c.location])),
        "job_titles": list(set([c.job_title for c in contacts_db if c.job_title]))
    }
