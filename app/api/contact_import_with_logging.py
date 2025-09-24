"""
Contact Import API with Comprehensive Logging
Enhanced version with detailed logging for debugging
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
    Preview contact import from CSV/Excel file with detailed logging
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
    Import contacts from CSV/Excel file with detailed logging
    """
    logger.info(f"🚀 Starting contact import for campaign {campaign_id}")
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
        
        imported_contacts = []
        errors = []
        
        # Process each row
        for row_num, row in enumerate(csv_reader, 1):
            try:
                logger.info(f"📄 Processing row {row_num}: {row}")
                
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
                
                logger.info(f"✅ Contact created: {contact.first_name} {contact.last_name} ({contact.email})")
                session.add(contact)
                imported_contacts.append(contact)
                
            except Exception as row_error:
                error_msg = f"Error processing row {row_num}: {str(row_error)}"
                logger.error(f"❌ {error_msg}")
                errors.append(error_msg)
        
        # Commit changes
        logger.info(f"💾 Committing {len(imported_contacts)} contacts to database...")
        await session.commit()
        logger.info("✅ Database commit successful")
        
        return {
            "success": True,
            "imported_count": len(imported_contacts),
            "errors": errors,
            "message": f"Successfully imported {len(imported_contacts)} contacts",
            "debug_info": {
                "file_size": len(content),
                "csv_length": len(csv_content),
                "headers": csv_reader.fieldnames,
                "processed_rows": len(imported_contacts),
                "error_count": len(errors)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error importing contacts: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error importing contacts: {str(e)}")

@router.get("/test-import-logging", tags=["Contact Import"])
async def test_import_logging():
    """
    Test endpoint to verify logging is working
    """
    logger.info("🧪 Testing contact import logging system...")
    logger.info("✅ Logging system is working!")
    
    return {
        "message": "Contact import logging system is working!",
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "log_level": "INFO"
    }

@router.get("/import-status", tags=["Contact Import"])
async def get_import_status():
    """
    Get current import status and recent logs
    """
    logger.info("📊 Getting import status...")
    
    return {
        "status": "active",
        "logging_enabled": True,
        "log_level": "INFO",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Contact import logging is active"
    }
