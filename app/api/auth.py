from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import async_session_maker
from app.models.user import User
from app.auth.jwt_handler import create_access_token, get_current_user
from app.auth.google_oauth import get_google_oauth_router
from config.oauth_config import OAuthConfig
from pydantic import BaseModel
from typing import List


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: str
    email: str
    is_active: bool

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_db():
    async with async_session_maker() as session:
        yield session

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # Simple login for testing - in production, verify against database
    if form_data.username == "admin" and form_data.password == "admin123":
        access_token = create_access_token(data={"sub": form_data.username})
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/protected", response_model=UserResponse)
async def protected_route(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        is_active=current_user.is_active
    )

# Include Google OAuth router if configured
if OAuthConfig.is_google_configured():
    router.include_router(get_google_oauth_router(), prefix="/google", tags=["google-oauth"])
