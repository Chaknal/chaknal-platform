from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from google.auth.transport import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pydantic import BaseModel
import httpx
from config.settings import settings


class GoogleUserInfo(BaseModel):
    email: str
    name: str
    picture: Optional[str] = None
    sub: str  # Google user ID


class GoogleOAuthHandler:
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI

        if not self.client_id or not self.client_secret:
            raise ValueError("Google OAuth credentials not configured")

    def get_authorization_url(self) -> str:
        """Generate Google OAuth authorization URL"""
        full_scopes = [
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile"
        ]
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri],
                    "scopes": full_scopes
                }
            },
            scopes=full_scopes
        )
        flow.redirect_uri = self.redirect_uri

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        return authorization_url

    async def verify_id_token(self, id_token_str: str) -> GoogleUserInfo:
        """Verify Google ID token and return user info"""
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                requests.Request(),
                self.client_id
            )

            # Extract user info
            user_info = GoogleUserInfo(
                email=idinfo['email'],
                name=idinfo.get('name', ''),
                picture=idinfo.get('picture'),
                sub=idinfo['sub']
            )

            return user_info

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google token: {str(e)}"
            )

    async def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        full_scopes = [
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile"
        ]
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri],
                    "scopes": full_scopes
                }
            },
            scopes=full_scopes
        )
        flow.redirect_uri = self.redirect_uri

        try:
            flow.fetch_token(code=authorization_code)
            return {
                "access_token": flow.credentials.token,
                "id_token": flow.credentials.id_token,
                "refresh_token": flow.credentials.refresh_token
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange code for token: {str(e)}"
            )

    async def get_user_info_from_token(self, access_token: str) -> GoogleUserInfo:
        """Get user info from Google using access token"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to get user info from Google"
                )

            user_data = response.json()
            return GoogleUserInfo(
                email=user_data['email'],
                name=user_data.get('name', ''),
                picture=user_data.get('picture'),
                sub=user_data['id']
            )
