"""
Minimal test module to isolate import issues
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/minimal-test", tags=["Test"])
async def minimal_test():
    """Minimal test endpoint"""
    return {
        "message": "Minimal test is working!",
        "status": "success"
    }
