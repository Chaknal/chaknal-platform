"""
Simple test module to verify basic functionality
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/simple-test")
async def simple_test():
    """Simple test endpoint"""
    return {"message": "Simple test is working!", "status": "success"}
