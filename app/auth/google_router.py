from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from .google_oauth import GoogleOAuthHandler, GoogleUserInfo
from .jwt_handler import create_access_token, Token
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.database import async_session_maker
from app.models.company import Company
import os

router = APIRouter(prefix="/auth/google", tags=["Google OAuth"])


# Dependency to get database session
async def get_session():
    async with async_session_maker() as session:
        yield session


async def get_or_create_company_by_domain(email: str, session: AsyncSession) -> str:
    """Get or create a company based on email domain"""
    try:
        # Extract domain from email
        domain = email.split('@')[1].lower()
        
        # Skip common email providers
        common_providers = {'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com'}
        if domain in common_providers:
            domain = 'personal'  # Use 'personal' for common email providers
        
        # Look for existing company with this domain
        result = await session.execute(select(Company).where(Company.domain == domain))
        company = result.scalar_one_or_none()
        
        if not company:
            # Create new company
            company_name = domain.replace('.com', '').replace('.', ' ').title()
            if domain == 'personal':
                company_name = 'Personal'
            
            company = Company(
                name=company_name,
                domain=domain
            )
            session.add(company)
            await session.commit()
            await session.refresh(company)
        
        return company.id
        
    except Exception as e:
        print(f"Error getting/creating company: {e}")
        return None


class GoogleAuthResponse(BaseModel):
    access_token: str
    token_type: str
    user_info: GoogleUserInfo

# Initialize Google OAuth handler
try:
    google_oauth = GoogleOAuthHandler()
except ValueError as e:
    print(f"Warning: Google OAuth not configured: {e}")
    google_oauth = None

@router.get("/login")
async def google_login():
    """Redirect to Google OAuth login"""
    if not google_oauth:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth not configured"
        )

    auth_url = google_oauth.get_authorization_url()
    return RedirectResponse(url=auth_url)

@router.get("/callback")
async def google_callback(code: str, session: AsyncSession = Depends(get_session)):
    """Handle Google OAuth callback"""
    if not google_oauth:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth not configured"
        )

    try:
        # Exchange code for tokens
        tokens = await google_oauth.exchange_code_for_token(code)

        # Get user info from access token
        user_info = await google_oauth.get_user_info_from_token(tokens["access_token"])

        # Get or create company based on email domain
        company_id = await get_or_create_company_by_domain(user_info.email, session)

        # Create JWT token for our app with company info
        access_token = create_access_token(
            data={
                "sub": user_info.email, 
                "google_id": user_info.sub,
                "company_id": company_id
            }
        )

        # Redirect to frontend with token
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(
            url=f"{frontend_url}/auth/callback?token={access_token}&email={user_info.email}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authentication failed: {str(e)}"
        )

@router.post("/verify-token")
async def verify_google_token(id_token: str):
    """Verify Google ID token and return user info"""
    if not google_oauth:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth not configured"
        )

    try:
        user_info = await google_oauth.verify_id_token(id_token)

        # Create JWT token for our app
        access_token = create_access_token(
            data={"sub": user_info.email, "google_id": user_info.sub}
        )

        return GoogleAuthResponse(
            access_token=access_token,
            token_type="bearer",
            user_info=user_info
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}"
        )

@router.get("/user-info")
async def get_google_user_info(access_token: str):
    """Get user info from Google access token"""
    if not google_oauth:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth not configured"
        )

    try:
        user_info = await google_oauth.get_user_info_from_token(access_token)
        return user_info

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to get user info: {str(e)}"
        )
