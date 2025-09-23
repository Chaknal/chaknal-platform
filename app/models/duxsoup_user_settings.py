"""
DuxSoup User Settings Model
Stores configuration settings for DuxSoup users
"""

from sqlalchemy import Column, String, Boolean, Integer, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base
import uuid
from datetime import datetime
from typing import Dict, Any, Optional


class DuxSoupUserSettings(Base):
    __tablename__ = "duxsoup_user_settings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    duxsoup_user_id = Column(String(36), ForeignKey("duxsoup_user.id"), nullable=False, unique=True)
    
    # Throttling & Rate Limits
    throttle_time = Column(Integer, default=1, comment="Seconds between actions")
    scan_throttle_time = Column(Integer, default=3000, comment="Milliseconds between profile scans")
    max_visits = Column(Integer, default=0, comment="Max profile visits per day (0 = unlimited)")
    max_invites = Column(Integer, default=20, comment="Max connection requests per day")
    max_messages = Column(Integer, default=100, comment="Max messages per day")
    max_enrolls = Column(Integer, default=200, comment="Max campaign enrollments per day")
    
    # Error Handling
    linkedin_limits_nooze = Column(Integer, default=3, comment="Days to pause when LinkedIn limits hit")
    linkedin_limit_alert = Column(Boolean, default=False, comment="Alert when LinkedIn limits hit")
    pause_on_invite_error = Column(Boolean, default=True, comment="Pause when invite errors occur")
    resume_delay_on_invite_error = Column(String(10), default="1d", comment="Delay before resuming after invite errors")
    
    # Profile Filtering
    skip_noname = Column(Boolean, default=True, comment="Skip profiles without names")
    skip_noimage = Column(Boolean, default=False, comment="Skip profiles without images")
    skip_incrm = Column(Boolean, default=False, comment="Skip CRM contacts")
    skip_nopremium = Column(Boolean, default=False, comment="Skip non-premium users")
    skip_3plus = Column(Boolean, default=False, comment="Skip 3rd+ connections")
    skip_nolion = Column(Boolean, default=False, comment="Skip profiles without LinkedIn Premium")
    skip_noinfluencer = Column(Boolean, default=False, comment="Skip non-influencers")
    skip_nojobseeker = Column(Boolean, default=False, comment="Skip job seekers")
    
    # Blacklist & Exclusion Rules
    exclude_blacklisted_action = Column(Boolean, default=True, comment="Exclude blacklisted profiles")
    exclude_tag_skipped_action = Column(Boolean, default=False, comment="Exclude tagged profiles")
    exclude_low_connection_count_action = Column(Boolean, default=False, comment="Exclude low connection counts")
    exclude_low_connection_count_value = Column(Integer, default=100, comment="Threshold for low connections")
    
    # Content Filtering
    kill_characters = Column(Text, default=".,★☆✪☁📍💪🏼🎖🏼📦♦➤✔✓~()\"'", comment="Characters to remove from profiles")
    kill_words = Column(Text, default="bsn, ceo, certified, copywriter, cpc, digital, dr, drs, expert, freelance, hubspot, internet, lion, lme, lmt, ma, marketing, mba, md, mim, msc, ninja, online, pharma, phd, ppc, seo, sip, videoseo", comment="Words that disqualify profiles")
    
    # Robot Schedule (stored as JSON)
    robot_schedule_plan = Column(JSON, default={
        "0": [["", ""]],  # Sunday
        "1": [["09:00", "23:00"]],  # Monday
        "2": [["09:00", "23:00"]],  # Tuesday
        "3": [["09:00", "23:00"]],  # Wednesday
        "4": [["09:00", "23:00"]],  # Thursday
        "5": [["09:00", "23:00"]],  # Friday
        "6": [["", ""]]  # Saturday
    }, comment="Robot schedule plan")
    
    # Auto-tagging
    auto_tag_flag = Column(Boolean, default=True, comment="Enable auto-tagging")
    auto_tag_value = Column(String(100), default="AMPED", comment="Tag value for auto-tagging")
    
    # Follow-up Settings
    followup_flag = Column(Boolean, default=True, comment="Enable follow-up messages")
    followup_for_all_flag = Column(Boolean, default=False, comment="Follow-up for all contacts")
    active_followup_campaign_id = Column(String(100), default="default", comment="Active follow-up campaign")
    
    # Connection Settings
    auto_connect = Column(Boolean, default=False, comment="Auto-connect to profiles")
    auto_follow = Column(Boolean, default=False, comment="Auto-follow profiles")
    auto_disconnect = Column(Boolean, default=False, comment="Auto-disconnect from profiles")
    auto_connect_message_flag = Column(Boolean, default=False, comment="Send message with auto-connect")
    auto_connect_message_text = Column(Text, default="", comment="Auto-connect message text")
    
    # Pending Invites
    expire_pending_invites_flag = Column(Boolean, default=True, comment="Expire pending invites")
    expire_pending_invites_value = Column(Integer, default=30, comment="Days to expire pending invites")
    
    # Connected Messages
    connected_message_flag = Column(Boolean, default=False, comment="Send message when connected")
    connected_message_text = Column(Text, default="", comment="Connected message text")
    
    # Performance Settings
    skip_days = Column(Integer, default=0, comment="Days to skip")
    page_init_delay = Column(Integer, default=5000, comment="Page initialization delay in milliseconds")
    wait_minutes = Column(Integer, default=5, comment="Wait minutes between actions")
    wait_visits = Column(Integer, default=20, comment="Wait after N visits")
    max_page_load_time = Column(Integer, default=20000, comment="Max page load time in milliseconds")
    
    # Notifications
    warning_notifications = Column(Boolean, default=True, comment="Enable warning notifications")
    action_notifications = Column(Boolean, default=True, comment="Enable action notifications")
    info_notifications = Column(Boolean, default=True, comment="Enable info notifications")
    
    # Advanced Features
    buy_mail = Column(Boolean, default=False, comment="Buy email addresses")
    pre_visit_dialog = Column(Boolean, default=True, comment="Show pre-visit dialog")
    auto_endorse = Column(Boolean, default=False, comment="Auto-endorse connections")
    auto_endorse_target = Column(Integer, default=3, comment="Auto-endorse target count")
    badge_display = Column(String(50), default="nothing", comment="Badge display setting")
    auto_save_as_lead = Column(Boolean, default=False, comment="Auto-save as lead")
    auto_pdf = Column(Boolean, default=False, comment="Auto-generate PDF")
    send_inmail_flag = Column(Boolean, default=False, comment="Send InMail messages")
    send_inmail_subject = Column(String(200), default="", comment="InMail subject")
    send_inmail_body = Column(Text, default="", comment="InMail body")
    
    # Webhooks
    webhook_profile_flag = Column(Boolean, default=True, comment="Enable webhook for profile data")
    webhooks = Column(JSON, default=[], comment="Webhook configurations")
    
    # Message Bridge
    message_bridge_flag = Column(Boolean, default=True, comment="Enable message bridge")
    message_bridge_interval = Column(Integer, default=180, comment="Message bridge interval in seconds")
    
    # Remote Control
    remote_control_flag = Column(Boolean, default=True, comment="Enable remote control")
    
    # UI Settings
    minimised_tools = Column(Boolean, default=False, comment="Minimized tools")
    background_mode = Column(Boolean, default=True, comment="Background mode")
    managed_download = Column(Boolean, default=True, comment="Managed download")
    hide_system_tags = Column(Boolean, default=True, comment="Hide system tags")
    simplegui = Column(Boolean, default=False, comment="Simple GUI mode")
    
    # Additional DuxSoup Settings
    snooze = Column(Boolean, default=True, comment="Snooze functionality")
    uselocalstorage = Column(Boolean, default=True, comment="Use local storage")
    runautomationsonmanualvisits = Column(Boolean, default=False, comment="Run automations on manual visits")
    
    # Campaigns (stored as JSON)
    campaigns = Column(JSON, default=[], comment="Campaign configurations")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    duxsoup_user = relationship("DuxSoupUser", back_populates="settings")
    
    def to_dux_config(self) -> Dict[str, Any]:
        """Convert to DuxSoup API configuration format"""
        return {
            "throttletime": str(self.throttle_time),
            "scanthrottletime": str(self.scan_throttle_time),
            "maxvisits": str(self.max_visits),
            "maxinvites": str(self.max_invites),
            "maxmessages": str(self.max_messages),
            "maxenrolls": self.max_enrolls,
            "linkedinlimitsnooze": self.linkedin_limits_nooze,
            "linkedinlimitalert": str(self.linkedin_limit_alert).lower(),
            "pauseoninviteerror": self.pause_on_invite_error,
            "resumedelayoninviteerror": self.resume_delay_on_invite_error,
            "expand": False,
            "skiptaggedflag": False,
            "skiptaggedvalue": "",
            "skipcustomflag": False,
            "skipcustomvalue": "",
            "skipnoname": self.skip_noname,
            "skipnoimage": self.skip_noimage,
            "skipincrm": self.skip_incrm,
            "skipnopremium": self.skip_nopremium,
            "skip3plus": self.skip_3plus,
            "skipnolion": self.skip_nolion,
            "skipnoinfluencer": self.skip_noinfluencer,
            "skipnojobseeker": self.skip_nojobseeker,
            "excludeblacklistedaction": self.exclude_blacklisted_action,
            "excludetagskippedaction": self.exclude_tag_skipped_action,
            "excludelowconnectioncountaction": self.exclude_low_connection_count_action,
            "excludelowconnectioncountvalue": self.exclude_low_connection_count_value,
            "killcharacters": self.kill_characters,
            "killwords": self.kill_words,
            "randomrange": False,
            "pauserobot": False,
            "robotscheduleplan": self.robot_schedule_plan,
            "buymail": self.buy_mail,
            "previsitdialog": self.pre_visit_dialog,
            "autoendorse": self.auto_endorse,
            "autoendorsetarget": str(self.auto_endorse_target),
            "badgedisplay": self.badge_display,
            "autotagflag": self.auto_tag_flag,
            "autotagvalue": self.auto_tag_value,
            "followupflag": self.followup_flag,
            "followupforallflag": self.followup_for_all_flag,
            "activefollowupcampaignid": self.active_followup_campaign_id,
            "autofollow": self.auto_follow,
            "autodisconnect": self.auto_disconnect,
            "autopdf": self.auto_pdf,
            "sendinmailflag": self.send_inmail_flag,
            "sendinmailsubject": self.send_inmail_subject,
            "sendinmailbody": self.send_inmail_body,
            "autosaveaslead": self.auto_save_as_lead,
            "autoconnect": self.auto_connect,
            "autoconnectmessageflag": self.auto_connect_message_flag,
            "autoconnectmessagetext": self.auto_connect_message_text,
            "expirependinginvitesflag": self.expire_pending_invites_flag,
            "expirependinginvitesvalue": self.expire_pending_invites_value,
            "connectedmessageflag": self.connected_message_flag,
            "connectedmessagetext": self.connected_message_text,
            "skipdays": str(self.skip_days),
            "pageinitdelay": str(self.page_init_delay),
            "waitminutes": self.wait_minutes,
            "waitvisits": self.wait_visits,
            "maxpageloadtime": self.max_page_load_time,
            "warningnotifications": self.warning_notifications,
            "actionnotifications": self.action_notifications,
            "infonotifications": self.info_notifications,
            "affiliatelicense": {
                "key": "CSYM-0LK8-I5QB-000",
                "productid": "",
                "status": "invalid",
                "expiry": "N/A",
                "message": "no license"
            },
            "runautomationsonmanualvisits": False,
            "manageddownload": self.managed_download,
            "hidesystemtags": self.hide_system_tags,
            "backgroundmode": self.background_mode,
            "webhookprofileflag": self.webhook_profile_flag,
            "webhooks": self.webhooks,
            "campaigns": self.campaigns,
            "messagebridgeflag": self.message_bridge_flag,
            "messagebridgeinterval": self.message_bridge_interval,
            "remotecontrolflag": self.remote_control_flag,
            "minimisedstools": self.minimised_tools,
            "menunotificationcutofftime": 1577851200000,
            "snooze": self.snooze,
            "uselocalstorage": self.uselocalstorage,
            "runautomationsonmanualvisits": self.runautomationsonmanualvisits,
            "simplegui": self.simplegui
        }
    
    @classmethod
    def from_dux_config(cls, config_data: Dict[str, Any], duxsoup_user_id: str) -> 'DuxSoupUserSettings':
        """Create DuxSoupUserSettings from DuxSoup API configuration data"""
        settings = cls(duxsoup_user_id=duxsoup_user_id)
        
        # Map DuxSoup API fields to our model fields
        field_mapping = {
            'throttletime': 'throttle_time',
            'scanthrottletime': 'scan_throttle_time',
            'maxvisits': 'max_visits',
            'maxinvites': 'max_invites',
            'maxmessages': 'max_messages',
            'maxenrolls': 'max_enrolls',
            'linkedinlimitsnooze': 'linkedin_limits_nooze',
            'linkedinlimitalert': 'linkedin_limit_alert',
            'pauseoninviteerror': 'pause_on_invite_error',
            'resumedelayoninviteerror': 'resume_delay_on_invite_error',
            'skipnoname': 'skip_noname',
            'skipnoimage': 'skip_noimage',
            'skipincrm': 'skip_incrm',
            'skipnopremium': 'skip_nopremium',
            'skip3plus': 'skip_3plus',
            'skipnolion': 'skip_nolion',
            'skipnoinfluencer': 'skip_noinfluencer',
            'skipnojobseeker': 'skip_nojobseeker',
            'excludeblacklistedaction': 'exclude_blacklisted_action',
            'excludetagskippedaction': 'exclude_tag_skipped_action',
            'excludelowconnectioncountaction': 'exclude_low_connection_count_action',
            'excludelowconnectioncountvalue': 'exclude_low_connection_count_value',
            'killcharacters': 'kill_characters',
            'killwords': 'kill_words',
            'robotscheduleplan': 'robot_schedule_plan',
            'autotagflag': 'auto_tag_flag',
            'autotagvalue': 'auto_tag_value',
            'followupflag': 'followup_flag',
            'followupforallflag': 'followup_for_all_flag',
            'activefollowupcampaignid': 'active_followup_campaign_id',
            'autoconnect': 'auto_connect',
            'autofollow': 'auto_follow',
            'autodisconnect': 'auto_disconnect',
            'autoconnectmessageflag': 'auto_connect_message_flag',
            'autoconnectmessagetext': 'auto_connect_message_text',
            'expirependinginvitesflag': 'expire_pending_invites_flag',
            'expirependinginvitesvalue': 'expire_pending_invites_value',
            'connectedmessageflag': 'connected_message_flag',
            'connectedmessagetext': 'connected_message_text',
            'skipdays': 'skip_days',
            'pageinitdelay': 'page_init_delay',
            'waitminutes': 'wait_minutes',
            'waitvisits': 'wait_visits',
            'maxpageloadtime': 'max_page_load_time',
            'warningnotifications': 'warning_notifications',
            'actionnotifications': 'action_notifications',
            'infonotifications': 'info_notifications',
            'buymail': 'buy_mail',
            'previsitdialog': 'pre_visit_dialog',
            'autoendorse': 'auto_endorse',
            'autoendorsetarget': 'auto_endorse_target',
            'badgedisplay': 'badge_display',
            'autosaveaslead': 'auto_save_as_lead',
            'autopdf': 'auto_pdf',
            'sendinmailflag': 'send_inmail_flag',
            'sendinmailsubject': 'send_inmail_subject',
            'sendinmailbody': 'send_inmail_body',
            'webhookprofileflag': 'webhook_profile_flag',
            'webhooks': 'webhooks',
            'messagebridgeflag': 'message_bridge_flag',
            'messagebridgeinterval': 'message_bridge_interval',
            'remotecontrolflag': 'remote_control_flag',
            'minimisedstools': 'minimised_tools',
            'backgroundmode': 'background_mode',
            'manageddownload': 'managed_download',
            'hidesystemtags': 'hide_system_tags',
            'simplegui': 'simplegui',
            'snooze': 'snooze',
            'uselocalstorage': 'uselocalstorage',
            'runautomationsonmanualvisits': 'runautomationsonmanualvisits',
            'campaigns': 'campaigns'
        }
        
        # Convert string values to appropriate types
        for api_field, model_field in field_mapping.items():
            if api_field in config_data:
                value = config_data[api_field]
                
                # Convert string numbers to integers
                if model_field in ['throttle_time', 'scan_throttle_time', 'max_visits', 'max_invites', 
                                 'max_messages', 'max_enrolls', 'linkedin_limits_nooze', 
                                 'exclude_low_connection_count_value', 'auto_endorse_target', 
                                 'skip_days', 'page_init_delay', 'wait_minutes', 'wait_visits', 
                                 'max_page_load_time', 'message_bridge_interval', 
                                 'expire_pending_invites_value']:
                    try:
                        value = int(value) if value else 0
                    except (ValueError, TypeError):
                        value = 0
                
                # Convert string booleans to booleans
                elif model_field in ['linkedin_limit_alert', 'pause_on_invite_error', 'skip_noname', 
                                   'skip_noimage', 'skip_incrm', 'skip_nopremium', 'skip_3plus', 
                                   'skip_nolion', 'skip_noinfluencer', 'skip_nojobseeker', 
                                   'exclude_blacklisted_action', 'exclude_tag_skipped_action', 
                                   'exclude_low_connection_count_action', 'auto_tag_flag', 
                                   'followup_flag', 'followup_for_all_flag', 'auto_connect', 
                                   'auto_follow', 'auto_disconnect', 'auto_connect_message_flag', 
                                   'expire_pending_invites_flag', 'connected_message_flag', 
                                   'warning_notifications', 'action_notifications', 'info_notifications', 
                                   'buy_mail', 'pre_visit_dialog', 'auto_endorse', 'auto_save_as_lead', 
                                   'auto_pdf', 'send_inmail_flag', 'webhook_profile_flag', 
                                   'message_bridge_flag', 'remote_control_flag', 'minimised_tools', 
                                   'background_mode', 'managed_download', 'hide_system_tags', 
                                   'simplegui', 'snooze', 'uselocalstorage', 'runautomationsonmanualvisits']:
                    if isinstance(value, str):
                        value = value.lower() in ['true', '1', 'yes', 'on']
                    elif isinstance(value, (int, float)):
                        value = bool(value)
                
                setattr(settings, model_field, value)
        
        return settings