"""
DuxSoup Configuration API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from database.database import get_session
from app.models.duxsoup_user import DuxSoupUser
from app.models.duxsoup_user_settings import DuxSoupUserSettings
from app.services.duxwrap_new import DuxSoupWrapper, DuxSoupUser as DuxSoupUserConfig

router = APIRouter(prefix="/api/duxsoup-config", tags=["DuxSoup Configuration"])

# =============================================================================
# SCHEMAS
# =============================================================================

class DuxSoupConfigUpdate(BaseModel):
    """DuxSoup configuration update request"""
    # Throttling & Rate Limits
    throttle_time: Optional[int] = Field(None, ge=1, le=60, description="Seconds between actions")
    scan_throttle_time: Optional[int] = Field(None, ge=1000, le=10000, description="Milliseconds between profile scans")
    max_visits: Optional[int] = Field(None, ge=0, le=1000, description="Max profile visits per day (0 = unlimited)")
    max_invites: Optional[int] = Field(None, ge=0, le=100, description="Max connection requests per day")
    max_messages: Optional[int] = Field(None, ge=0, le=500, description="Max messages per day")
    max_enrolls: Optional[int] = Field(None, ge=0, le=1000, description="Max campaign enrollments per day")
    
    # Error Handling
    linkedin_limits_nooze: Optional[int] = Field(None, ge=1, le=30, description="Days to pause when LinkedIn limits hit")
    linkedin_limit_alert: Optional[bool] = Field(None, description="Alert when LinkedIn limits hit")
    pause_on_invite_error: Optional[bool] = Field(None, description="Pause when invite errors occur")
    resume_delay_on_invite_error: Optional[str] = Field(None, description="Delay before resuming after invite errors")
    
    # Profile Filtering
    skip_noname: Optional[bool] = Field(None, description="Skip profiles without names")
    skip_noimage: Optional[bool] = Field(None, description="Skip profiles without images")
    skip_incrm: Optional[bool] = Field(None, description="Skip CRM contacts")
    skip_nopremium: Optional[bool] = Field(None, description="Skip non-premium users")
    skip_3plus: Optional[bool] = Field(None, description="Skip 3rd+ connections")
    skip_nolion: Optional[bool] = Field(None, description="Skip profiles without LinkedIn Premium")
    skip_noinfluencer: Optional[bool] = Field(None, description="Skip non-influencers")
    skip_nojobseeker: Optional[bool] = Field(None, description="Skip job seekers")
    
    # Blacklist & Exclusion Rules
    exclude_blacklisted_action: Optional[bool] = Field(None, description="Exclude blacklisted profiles")
    exclude_tag_skipped_action: Optional[bool] = Field(None, description="Exclude tagged profiles")
    exclude_low_connection_count_action: Optional[bool] = Field(None, description="Exclude low connection counts")
    exclude_low_connection_count_value: Optional[int] = Field(None, ge=0, le=10000, description="Threshold for low connections")
    
    # Content Filtering
    kill_characters: Optional[str] = Field(None, description="Characters to remove from profiles")
    kill_words: Optional[str] = Field(None, description="Words that disqualify profiles")
    
    # Auto-tagging
    auto_tag_flag: Optional[bool] = Field(None, description="Enable auto-tagging")
    auto_tag_value: Optional[str] = Field(None, max_length=100, description="Tag value for auto-tagging")
    
    # Follow-up Settings
    followup_flag: Optional[bool] = Field(None, description="Enable follow-up messages")
    followup_for_all_flag: Optional[bool] = Field(None, description="Follow-up for all contacts")
    active_followup_campaign_id: Optional[str] = Field(None, max_length=100, description="Active follow-up campaign")
    
    # Connection Settings
    auto_connect: Optional[bool] = Field(None, description="Auto-connect to profiles")
    auto_follow: Optional[bool] = Field(None, description="Auto-follow profiles")
    auto_disconnect: Optional[bool] = Field(None, description="Auto-disconnect from profiles")
    auto_connect_message_flag: Optional[bool] = Field(None, description="Send message with auto-connect")
    auto_connect_message_text: Optional[str] = Field(None, description="Auto-connect message text")
    
    # Performance Settings
    skip_days: Optional[int] = Field(None, ge=0, le=30, description="Days to skip")
    page_init_delay: Optional[int] = Field(None, ge=1000, le=30000, description="Page initialization delay in milliseconds")
    wait_minutes: Optional[int] = Field(None, ge=1, le=60, description="Wait minutes between actions")
    wait_visits: Optional[int] = Field(None, ge=1, le=100, description="Wait after N visits")
    max_page_load_time: Optional[int] = Field(None, ge=5000, le=60000, description="Max page load time in milliseconds")
    
    # Notifications
    warning_notifications: Optional[bool] = Field(None, description="Enable warning notifications")
    action_notifications: Optional[bool] = Field(None, description="Enable action notifications")
    info_notifications: Optional[bool] = Field(None, description="Enable info notifications")
    
    # Advanced Features
    buy_mail: Optional[bool] = Field(None, description="Buy email addresses")
    pre_visit_dialog: Optional[bool] = Field(None, description="Show pre-visit dialog")
    auto_endorse: Optional[bool] = Field(None, description="Auto-endorse connections")
    auto_endorse_target: Optional[int] = Field(None, ge=1, le=10, description="Auto-endorse target count")
    badge_display: Optional[str] = Field(None, max_length=50, description="Badge display setting")
    auto_save_as_lead: Optional[bool] = Field(None, description="Auto-save as lead")
    auto_pdf: Optional[bool] = Field(None, description="Auto-generate PDF")
    send_inmail_flag: Optional[bool] = Field(None, description="Send InMail messages")
    send_inmail_subject: Optional[str] = Field(None, max_length=200, description="InMail subject")
    send_inmail_body: Optional[str] = Field(None, description="InMail body")
    
    # Webhooks
    webhook_profile_flag: Optional[bool] = Field(None, description="Enable webhook for profile data")
    webhooks: Optional[list] = Field(None, description="Webhook configurations")
    
    # Message Bridge
    message_bridge_flag: Optional[bool] = Field(None, description="Enable message bridge")
    message_bridge_interval: Optional[int] = Field(None, ge=60, le=3600, description="Message bridge interval in seconds")
    
    # Remote Control
    remote_control_flag: Optional[bool] = Field(None, description="Enable remote control")
    
    # UI Settings
    minimised_tools: Optional[bool] = Field(None, description="Minimized tools")
    background_mode: Optional[bool] = Field(None, description="Background mode")
    managed_download: Optional[bool] = Field(None, description="Managed download")
    hide_system_tags: Optional[bool] = Field(None, description="Hide system tags")
    
    # Campaigns
    campaigns: Optional[list] = Field(None, description="Campaign configurations")

class DuxSoupConfigResponse(BaseModel):
    """DuxSoup configuration response"""
    duxsoup_user_id: str
    email: str
    first_name: str
    last_name: str
    settings: Dict[str, Any]
    last_updated: datetime

class DuxSoupConfigPushResponse(BaseModel):
    """DuxSoup configuration push response"""
    success: bool
    message: str
    duxsoup_response: Optional[Dict[str, Any]] = None

# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/{duxsoup_user_id}", response_model=DuxSoupConfigResponse)
async def get_duxsoup_config(
    duxsoup_user_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get DuxSoup configuration for a user"""
    try:
        # Get DuxSoup user
        dux_user_result = await session.execute(
            select(DuxSoupUser).where(DuxSoupUser.id == duxsoup_user_id)
        )
        dux_user = dux_user_result.scalar_one_or_none()
        
        if not dux_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="DuxSoup user not found"
            )
        
        # Get or create settings
        settings_result = await session.execute(
            select(DuxSoupUserSettings).where(
                DuxSoupUserSettings.duxsoup_user_id == duxsoup_user_id
            )
        )
        settings = settings_result.scalar_one_or_none()
        
        if not settings:
            # Create default settings
            settings = DuxSoupUserSettings(
                duxsoup_user_id=duxsoup_user_id
            )
            session.add(settings)
            await session.commit()
            await session.refresh(settings)
        
        return DuxSoupConfigResponse(
            duxsoup_user_id=dux_user.id,
            email=dux_user.email,
            first_name=dux_user.first_name,
            last_name=dux_user.last_name,
            settings=settings.to_dux_config(),
            last_updated=settings.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get DuxSoup configuration: {str(e)}"
        )

@router.put("/{duxsoup_user_id}", response_model=DuxSoupConfigResponse)
async def update_duxsoup_config(
    duxsoup_user_id: str,
    config_update: DuxSoupConfigUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update DuxSoup configuration for a user"""
    try:
        # Get DuxSoup user
        dux_user_result = await session.execute(
            select(DuxSoupUser).where(DuxSoupUser.id == duxsoup_user_id)
        )
        dux_user = dux_user_result.scalar_one_or_none()
        
        if not dux_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="DuxSoup user not found"
            )
        
        # Get or create settings
        settings_result = await session.execute(
            select(DuxSoupUserSettings).where(
                DuxSoupUserSettings.duxsoup_user_id == duxsoup_user_id
            )
        )
        settings = settings_result.scalar_one_or_none()
        
        if not settings:
            settings = DuxSoupUserSettings(duxsoup_user_id=duxsoup_user_id)
            session.add(settings)
        
        # Update settings with provided values
        update_data = config_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(settings, field):
                setattr(settings, field, value)
        
        settings.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(settings)
        
        return DuxSoupConfigResponse(
            duxsoup_user_id=dux_user.id,
            email=dux_user.email,
            first_name=dux_user.first_name,
            last_name=dux_user.last_name,
            settings=settings.to_dux_config(),
            last_updated=settings.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update DuxSoup configuration: {str(e)}"
        )

@router.post("/{duxsoup_user_id}/push", response_model=DuxSoupConfigPushResponse)
async def push_duxsoup_config(
    duxsoup_user_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Push DuxSoup configuration to DuxSoup API"""
    try:
        # Get DuxSoup user
        dux_user_result = await session.execute(
            select(DuxSoupUser).where(DuxSoupUser.id == duxsoup_user_id)
        )
        dux_user = dux_user_result.scalar_one_or_none()
        
        if not dux_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="DuxSoup user not found"
            )
        
        # Get settings
        settings_result = await session.execute(
            select(DuxSoupUserSettings).where(
                DuxSoupUserSettings.duxsoup_user_id == duxsoup_user_id
            )
        )
        settings = settings_result.scalar_one_or_none()
        
        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="DuxSoup settings not found"
            )
        
        # Create DuxSoup user configuration
        dux_user_config = DuxSoupUserConfig(
            userid=dux_user.dux_soup_user_id,
            apikey=dux_user.dux_soup_auth_key,
            label=f"{dux_user.first_name} {dux_user.last_name}"
        )
        
        # Push configuration to DuxSoup
        async with DuxSoupWrapper(dux_user_config) as dux_wrapper:
            result = await dux_wrapper.update_config(settings.to_dux_config())
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to push configuration to DuxSoup: {result.error or 'Unknown error'}"
            )
        
        return DuxSoupConfigPushResponse(
            success=True,
            message="Configuration pushed successfully to DuxSoup",
            duxsoup_response=result.data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to push DuxSoup configuration: {str(e)}"
        )

@router.post("/{duxsoup_user_id}/test-webhook")
async def test_webhook(
    duxsoup_user_id: str,
    webhook_url: str,
    session: AsyncSession = Depends(get_session)
):
    """Test a webhook URL by sending a sample payload"""
    try:
        import aiohttp
        import json
        
        # Sample webhook payload
        test_payload = {
            "event_type": "test_webhook",
            "timestamp": datetime.utcnow().isoformat(),
            "duxsoup_user_id": duxsoup_user_id,
            "message": "This is a test webhook from Chaknal Platform",
            "data": {
                "test": True,
                "source": "duxsoup_config_test"
            }
        }
        
        async with aiohttp.ClientSession() as client:
            async with client.post(
                webhook_url,
                json=test_payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status < 400:
                    return {
                        "success": True,
                        "message": f"Webhook test successful! Status: {response.status}",
                        "response_status": response.status
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Webhook test failed! Status: {response.status}",
                        "response_status": response.status
                    }
                    
    except Exception as e:
        return {
            "success": False,
            "message": f"Webhook test failed: {str(e)}"
        }

@router.post("/{duxsoup_user_id}/pull", response_model=DuxSoupConfigResponse)
async def pull_duxsoup_config(
    duxsoup_user_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Pull DuxSoup configuration from DuxSoup API"""
    try:
        # Get DuxSoup user
        dux_user_result = await session.execute(
            select(DuxSoupUser).where(DuxSoupUser.id == duxsoup_user_id)
        )
        dux_user = dux_user_result.scalar_one_or_none()
        
        if not dux_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="DuxSoup user not found"
            )
        
        # Create DuxSoup user configuration
        dux_user_config = DuxSoupUserConfig(
            userid=dux_user.dux_soup_user_id,
            apikey=dux_user.dux_soup_auth_key,
            label=f"{dux_user.first_name} {dux_user.last_name}"
        )
        
        # Pull configuration from DuxSoup
        async with DuxSoupWrapper(dux_user_config) as dux_wrapper:
            result = await dux_wrapper.get_config()
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to pull configuration from DuxSoup: {result.error or 'Unknown error'}"
            )
        
        # Update or create settings
        settings_result = await session.execute(
            select(DuxSoupUserSettings).where(
                DuxSoupUserSettings.duxsoup_user_id == duxsoup_user_id
            )
        )
        settings = settings_result.scalar_one_or_none()
        
        if settings:
            # Update existing settings
            settings = DuxSoupUserSettings.from_dux_config(result.data, duxsoup_user_id)
            settings.id = settings.id  # Keep existing ID
            settings.updated_at = datetime.utcnow()
        else:
            # Create new settings
            settings = DuxSoupUserSettings.from_dux_config(result.data, duxsoup_user_id)
            session.add(settings)
        
        await session.commit()
        await session.refresh(settings)
        
        return DuxSoupConfigResponse(
            duxsoup_user_id=dux_user.id,
            email=dux_user.email,
            first_name=dux_user.first_name,
            last_name=dux_user.last_name,
            settings=settings.to_dux_config(),
            last_updated=settings.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pull DuxSoup configuration: {str(e)}"
        )
