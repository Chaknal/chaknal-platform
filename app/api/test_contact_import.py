"""
Test Contact Import - Minimal test to verify module loading
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/test-contact-import", tags=["Test"])
async def test_contact_import():
    """Test endpoint to verify contact import module is loading"""
    return {
        "message": "Contact import module is working!",
        "status": "success"
    }
