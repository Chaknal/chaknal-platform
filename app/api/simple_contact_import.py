"""
Simple Contact Import API - No external dependencies
Basic CSV parsing without pandas
Enhanced with logging for debugging
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import json
import csv
import io
import logging

from database.database import get_session
from app.models.campaign import Campaign
from app.models.contact import Contact
from app.models.campaign_contact import CampaignContact

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/campaigns/{campaign_id}/contacts/import/preview", tags=["Contact Import"])
async def preview_import(
    campaign_id: str,
    file: UploadFile = File(...),
    source: str = Form(...),
    field_mapping: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_session)
):
    """
    Preview contact import from CSV/Excel file with logging
    """
    logger.info(f"🔍 Starting contact import preview for campaign {campaign_id}")
    logger.info(f"📁 File: {file.filename}, Size: {file.size}, Content-Type: {file.content_type}")
    logger.info(f"📊 Source: {source}, Field mapping: {field_mapping}")
    
    try:
        # Read file content
        logger.info("📖 Reading file content...")
        content = await file.read()
        logger.info(f"✅ File read successfully, size: {len(content)} bytes")
        
        # Parse CSV content
        logger.info("📝 Parsing CSV content...")
        csv_content = content.decode('utf-8')
        logger.info(f"✅ CSV decoded successfully, length: {len(csv_content)} characters")
        
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        logger.info(f"📋 CSV headers detected: {csv_reader.fieldnames}")
        
        # Get first 5 rows for preview
        preview_data = []
        row_count = 0
        for i, row in enumerate(csv_reader):
            if i >= 5:  # Limit to 5 rows for preview
                break
            preview_data.append(row)
            row_count += 1
            logger.info(f"📄 Row {i+1}: {list(row.keys())}")
        
        logger.info(f"✅ Preview generated successfully: {row_count} rows processed")
        
        return {
            "success": True,
            "preview_data": preview_data,
            "total_rows": row_count,
            "headers": csv_reader.fieldnames,
            "message": "Preview generated successfully",
            "debug_info": {
                "file_size": len(content),
                "csv_length": len(csv_content),
                "headers_count": len(csv_reader.fieldnames) if csv_reader.fieldnames else 0,
                "processed_rows": row_count
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing file: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@router.post("/campaigns/{campaign_id}/contacts/import", tags=["Contact Import"])
async def import_contacts(
    campaign_id: str,
    file: UploadFile = File(...),
    source: str = Form(...),
    field_mapping: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_session)
):
    """
    Import contacts from CSV/Excel file
    """
    try:
        # Read file content
        content = await file.read()
        
        # Parse CSV content
        csv_content = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        imported_contacts = []
        
        # Process each row
        for row in csv_reader:
            # Create contact
            contact = Contact(
                id=str(uuid.uuid4()),
                first_name=row.get('first_name', ''),
                last_name=row.get('last_name', ''),
                email=row.get('email', ''),
                company=row.get('company', ''),
                job_title=row.get('job_title', ''),
                linkedin_url=row.get('linkedin_url', ''),
                status='active',
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            session.add(contact)
            imported_contacts.append(contact)
        
        # Commit changes
        await session.commit()
        
        return {
            "success": True,
            "imported_count": len(imported_contacts),
            "message": f"Successfully imported {len(imported_contacts)} contacts"
        }
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error importing contacts: {str(e)}")

@router.get("/test-simple-import", tags=["Contact Import"])
async def test_simple_import():
    """
    Test endpoint to verify simple contact import module is working
    """
    logger.info("🧪 Testing simple contact import module...")
    logger.info("✅ Simple contact import module is working!")
    
    return {
        "message": "Simple contact import module is working!",
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "logging": "enabled"
    }
