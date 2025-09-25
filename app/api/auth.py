from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    is_active: bool

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(request: LoginRequest):
    """Simple login endpoint for testing"""
    # Simple login for testing - in production, verify against database
    if request.username == "admin" and request.password == "admin123":
        # Simple token generation for testing
        access_token = f"test_token_{request.username}_12345"
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

@router.get("/test")
async def auth_test():
    """Test endpoint for auth router"""
    return {"message": "Auth router is working!", "status": "success"}

@router.get("/protected")
async def protected_route():
    """Protected route for testing"""
    return {
        "message": "This is a protected route",
        "user": {"id": "test_user", "email": "test@example.com", "is_active": True}
    }
