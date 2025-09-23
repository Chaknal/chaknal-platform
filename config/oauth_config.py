import os
from typing import Optional


class OAuthConfig:
    """OAuth configuration settings"""

    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: Optional[str] = os.getenv("GOOGLE_REDIRECT_URI")

    # Frontend URL for OAuth redirects
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    @classmethod
    def is_google_configured(cls) -> bool:
        """Check if Google OAuth is properly configured"""
        return bool(
            cls.GOOGLE_CLIENT_ID and
            cls.GOOGLE_CLIENT_SECRET and
            cls.GOOGLE_REDIRECT_URI
        )

    @classmethod
    def get_google_config(cls) -> dict:
        """Get Google OAuth configuration"""
        return {
            "client_id": cls.GOOGLE_CLIENT_ID,
            "client_secret": cls.GOOGLE_CLIENT_SECRET,
            "redirect_uri": cls.GOOGLE_REDIRECT_URI,
            "frontend_url": cls.FRONTEND_URL
        }
