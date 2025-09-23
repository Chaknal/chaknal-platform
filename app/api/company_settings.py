from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database.database import get_session
from app.models.company import Company
from app.models.user import User
import os
import uuid
import shutil
from pathlib import Path
from typing import Optional

router = APIRouter(prefix="/api/company-settings", tags=["company-settings"])

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("static/uploads/logos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload-logo")
async def upload_company_logo(
    company_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_session)
):
    """Upload company logo for white labeling"""
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Only JPEG, PNG, GIF, and WebP images are allowed."
        )
    
    # Validate file size (max 5MB)
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 5MB."
        )
    
    # Reset file pointer
    await file.seek(0)
    
    # Get company
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    try:
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'png'
        unique_filename = f"{company_id}_{uuid.uuid4().hex[:8]}.{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Update company logo_url
        logo_url = f"/static/uploads/logos/{unique_filename}"
        company.logo_url = logo_url
        db.commit()
        
        return {
            "success": True,
            "message": "Logo uploaded successfully",
            "logo_url": logo_url
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to upload logo: {str(e)}")

@router.get("/logo/{company_id}")
async def get_company_logo(company_id: str, db: Session = Depends(get_session)):
    """Get company logo URL"""
    
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return {
        "success": True,
        "logo_url": company.logo_url,
        "company_name": company.name
    }

@router.delete("/logo/{company_id}")
async def remove_company_logo(company_id: str, db: Session = Depends(get_session)):
    """Remove company logo"""
    
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    try:
        # Remove file if it exists
        if company.logo_url:
            file_path = Path("static" + company.logo_url.replace("/static", ""))
            if file_path.exists():
                file_path.unlink()
        
        # Clear logo_url
        company.logo_url = None
        db.commit()
        
        return {
            "success": True,
            "message": "Logo removed successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to remove logo: {str(e)}")

@router.get("/branding/{company_id}")
async def get_company_branding(company_id: str, db: Session = Depends(get_session)):
    """Get complete company branding information"""
    
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return {
        "success": True,
        "data": {
            "company_id": company.id,
            "company_name": company.name,
            "logo_url": company.logo_url,
            "domain": company.domain
        }
    }

@router.put("/branding/{company_id}")
async def update_company_branding(
    company_id: str,
    company_name: Optional[str] = Form(None),
    db: Session = Depends(get_session)
):
    """Update company branding information"""
    
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    try:
        if company_name:
            company.name = company_name
        
        db.commit()
        
        return {
            "success": True,
            "message": "Company branding updated successfully",
            "data": {
                "company_id": company.id,
                "company_name": company.name,
                "logo_url": company.logo_url
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update branding: {str(e)}")
