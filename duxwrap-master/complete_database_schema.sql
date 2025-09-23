-- =============================================================================
-- COMPLETE DATABASE SCHEMA FOR DUX-SOUP LINKEDIN AUTOMATION PLATFORM
-- =============================================================================
-- 
-- This schema is designed to handle all Dux-Soup webhook events and campaign management
-- for LinkedIn automation. It includes comprehensive data models for contacts, campaigns,
-- messages, and webhook events with proper indexing and constraints.
--
-- DEPLOYMENT INSTRUCTIONS:
-- 1. Run this script on your PostgreSQL database
-- 2. Set up environment variables (see .env.example)
-- 3. Run the Python application with AzureDatabaseManager
--
-- DUX-SOUP WEBHOOK DATA STRUCTURE:
-- - message events: LinkedIn messages sent/received
-- - visit events: Profile visits and interactions
-- - action events: Connection requests, endorsements, etc.
-- - rccommand events: Robot command status updates
-- =============================================================================

-- Enable UUID extension for PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- CORE TABLES
-- =============================================================================

-- Campaigns table: Stores LinkedIn automation campaigns
-- Each campaign represents a targeted outreach effort with specific goals
CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_key UUID NOT NULL DEFAULT uuid_generate_v4(), -- Unique identifier for API access
    name VARCHAR(255) NOT NULL, -- Campaign name (e.g., "Q1 Cybersecurity Outreach")
    description TEXT, -- Detailed campaign description
    target_title VARCHAR(255), -- Target job titles (e.g., "Chief Information Security Officer")
    intent TEXT, -- Campaign intent/goals
    status VARCHAR(50) DEFAULT 'active', -- active, paused, completed, archived
    dux_user_id VARCHAR(100) NOT NULL, -- Dux-Soup user ID for multi-tenant support
    scheduled_start TIMESTAMP WITH TIME ZONE, -- When campaign should start (NULL = immediate)
    end_date TIMESTAMP WITH TIME ZONE, -- When campaign should end (NULL = never)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    settings JSONB -- Flexible campaign settings (message templates, delays, etc.)
);

-- Contacts table: Stores LinkedIn contact profiles
-- Extracted from Dux-Soup webhook data with comprehensive profile information
CREATE TABLE IF NOT EXISTS contacts (
    contact_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    linkedin_id VARCHAR(100) UNIQUE, -- LinkedIn profile ID
    linkedin_url VARCHAR(500), -- Full LinkedIn profile URL
    first_name VARCHAR(100), -- Contact's first name
    last_name VARCHAR(100), -- Contact's last name
    headline VARCHAR(500), -- LinkedIn headline/title
    company VARCHAR(255), -- Current company
    company_url VARCHAR(500), -- Company LinkedIn URL
    location VARCHAR(255), -- Geographic location
    industry VARCHAR(255), -- Industry classification
    connection_degree INTEGER, -- LinkedIn connection degree (1st, 2nd, 3rd)
    email VARCHAR(255), -- Email address (if available)
    phone VARCHAR(50), -- Phone number (if available)
    profile_data JSONB, -- Complete raw profile data from Dux-Soup
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Campaign-Contacts junction table: Links contacts to campaigns with status tracking
-- Tracks the relationship between contacts and campaigns, including engagement status
CREATE TABLE IF NOT EXISTS campaign_contacts (
    campaign_contact_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    campaign_key UUID NOT NULL, -- Denormalized for performance
    contact_id UUID REFERENCES contacts(contact_id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'enrolled', -- enrolled, accepted, replied, blacklisted, completed
    enrolled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- When contact was added to campaign
    accepted_at TIMESTAMP WITH TIME ZONE, -- When connection was accepted
    replied_at TIMESTAMP WITH TIME ZONE, -- When contact replied to a message
    blacklisted_at TIMESTAMP WITH TIME ZONE, -- When contact was blacklisted
    sequence_step INTEGER DEFAULT 1, -- Current step in the messaging sequence
    tags TEXT[], -- Array of tags for categorization
    UNIQUE(campaign_id, contact_id) -- Prevent duplicate enrollments
);

-- Messages table: Stores all LinkedIn messages (sent and received)
-- Complete message history for campaign tracking and Slack integration
CREATE TABLE IF NOT EXISTS messages (
    message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_contact_id UUID REFERENCES campaign_contacts(campaign_contact_id) ON DELETE CASCADE,
    direction VARCHAR(20) NOT NULL, -- 'sent' or 'received'
    message_text TEXT NOT NULL, -- Message content
    linkedin_message_id VARCHAR(100), -- LinkedIn's internal message ID
    thread_url VARCHAR(500), -- LinkedIn conversation thread URL
    sent_at TIMESTAMP WITH TIME ZONE, -- When message was sent
    received_at TIMESTAMP WITH TIME ZONE, -- When message was received
    status VARCHAR(50) DEFAULT 'sent', -- sent, delivered, read, failed
    tags TEXT[], -- Message tags for categorization
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Webhook Events table: Raw Dux-Soup webhook data storage
-- Stores all incoming webhook events before processing
CREATE TABLE IF NOT EXISTS webhook_events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dux_user_id VARCHAR(100) NOT NULL, -- Dux-Soup user ID
    event_type VARCHAR(50) NOT NULL, -- message, visit, action, rccommand
    event_name VARCHAR(50) NOT NULL, -- create, received, completed, ready, etc.
    contact_id UUID REFERENCES contacts(contact_id) ON DELETE SET NULL,
    campaign_id UUID REFERENCES campaigns(campaign_id) ON DELETE SET NULL,
    raw_data JSONB NOT NULL, -- Complete raw webhook payload
    processed BOOLEAN DEFAULT FALSE, -- Whether event has been processed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- PERFORMANCE INDEXES
-- =============================================================================

-- Webhook events indexes for fast querying
CREATE INDEX IF NOT EXISTS idx_webhook_events_type ON webhook_events(event_type);
CREATE INDEX IF NOT EXISTS idx_webhook_events_user ON webhook_events(dux_user_id);
CREATE INDEX IF NOT EXISTS idx_webhook_events_created_at ON webhook_events(created_at);
CREATE INDEX IF NOT EXISTS idx_webhook_events_processed ON webhook_events(processed);

-- Campaign indexes for campaign management
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_user ON campaigns(dux_user_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_scheduled_start ON campaigns(scheduled_start);
CREATE INDEX IF NOT EXISTS idx_campaigns_campaign_key ON campaigns(campaign_key);

-- Contact indexes for profile lookups
CREATE INDEX IF NOT EXISTS idx_contacts_linkedin_id ON contacts(linkedin_id);
CREATE INDEX IF NOT EXISTS idx_contacts_linkedin_url ON contacts(linkedin_url);
CREATE INDEX IF NOT EXISTS idx_contacts_company ON contacts(company);

-- Campaign-contact indexes for relationship queries
CREATE INDEX IF NOT EXISTS idx_campaign_contacts_status ON campaign_contacts(status);
CREATE INDEX IF NOT EXISTS idx_campaign_contacts_campaign_key ON campaign_contacts(campaign_key);
CREATE INDEX IF NOT EXISTS idx_campaign_contacts_contact ON campaign_contacts(contact_id);

-- Message indexes for conversation tracking
CREATE INDEX IF NOT EXISTS idx_messages_direction ON messages(direction);
CREATE INDEX IF NOT EXISTS idx_messages_campaign_contact ON messages(campaign_contact_id);
CREATE INDEX IF NOT EXISTS idx_messages_sent_at ON messages(sent_at);

-- =============================================================================
-- DATA VALIDATION CONSTRAINTS
-- =============================================================================

-- Ensure campaign status is valid
ALTER TABLE campaigns ADD CONSTRAINT chk_campaign_status 
    CHECK (status IN ('active', 'paused', 'completed', 'archived'));

-- Ensure message direction is valid
ALTER TABLE messages ADD CONSTRAINT chk_message_direction 
    CHECK (direction IN ('sent', 'received'));

-- Ensure campaign contact status is valid
ALTER TABLE campaigns ADD CONSTRAINT chk_campaign_contact_status 
    CHECK (status IN ('enrolled', 'accepted', 'replied', 'blacklisted', 'completed'));

-- =============================================================================
-- HELPER FUNCTIONS
-- =============================================================================

-- Function to update the updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to automatically update updated_at columns
CREATE TRIGGER update_campaigns_updated_at 
    BEFORE UPDATE ON campaigns 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contacts_updated_at 
    BEFORE UPDATE ON contacts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to get campaign statistics
CREATE OR REPLACE FUNCTION get_campaign_stats(campaign_uuid UUID)
RETURNS TABLE(
    total_contacts BIGINT,
    accepted_count BIGINT,
    replied_count BIGINT,
    blacklisted_count BIGINT,
    messages_sent BIGINT,
    messages_received BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(cc.contact_id)::BIGINT as total_contacts,
        COUNT(CASE WHEN cc.status = 'accepted' THEN 1 END)::BIGINT as accepted_count,
        COUNT(CASE WHEN cc.status = 'replied' THEN 1 END)::BIGINT as replied_count,
        COUNT(CASE WHEN cc.status = 'blacklisted' THEN 1 END)::BIGINT as blacklisted_count,
        COUNT(CASE WHEN m.direction = 'sent' THEN 1 END)::BIGINT as messages_sent,
        COUNT(CASE WHEN m.direction = 'received' THEN 1 END)::BIGINT as messages_received
    FROM campaigns c
    LEFT JOIN campaign_contacts cc ON c.campaign_id = cc.campaign_id
    LEFT JOIN messages m ON cc.campaign_contact_id = m.campaign_contact_id
    WHERE c.campaign_id = campaign_uuid;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- SAMPLE DATA INSERTION (for testing)
-- =============================================================================

-- Insert sample campaign
INSERT INTO campaigns (campaign_id, campaign_key, name, description, target_title, dux_user_id, status)
VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    '550e8400-e29b-41d4-a716-446655440001',
    'Q1 Cybersecurity Outreach',
    'Targeting CISOs and security leaders for partnership discussions',
    'Chief Information Security Officer',
    'test_user_123',
    'active'
) ON CONFLICT (campaign_id) DO NOTHING;

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

-- View for active campaigns with contact counts
CREATE OR REPLACE VIEW active_campaigns_view AS
SELECT 
    c.*,
    COALESCE(cnt.total_contacts, 0) as total_contacts,
    COALESCE(cnt.accepted_count, 0) as accepted_count,
    COALESCE(cnt.replied_count, 0) as replied_count
FROM campaigns c
LEFT JOIN (
    SELECT 
        campaign_key, 
        COUNT(contact_id) as total_contacts,
        COUNT(CASE WHEN status = 'accepted' THEN 1 END) as accepted_count,
        COUNT(CASE WHEN status = 'replied' THEN 1 END) as replied_count
    FROM campaign_contacts
    GROUP BY campaign_key
) cnt ON c.campaign_key = cnt.campaign_key
WHERE c.status = 'active'
AND (c.scheduled_start IS NULL OR c.scheduled_start <= NOW())
AND (c.end_date IS NULL OR c.end_date >= NOW());

-- View for recent webhook events
CREATE OR REPLACE VIEW recent_webhook_events_view AS
SELECT 
    we.*,
    c.first_name,
    c.last_name,
    c.company
FROM webhook_events we
LEFT JOIN contacts c ON we.contact_id = c.contact_id
WHERE we.created_at >= NOW() - INTERVAL '24 hours'
ORDER BY we.created_at DESC;

-- =============================================================================
-- COMMENTS FOR DOCUMENTATION
-- =============================================================================

COMMENT ON TABLE campaigns IS 'LinkedIn automation campaigns with targeting and scheduling';
COMMENT ON TABLE contacts IS 'LinkedIn contact profiles extracted from Dux-Soup webhook data';
COMMENT ON TABLE campaign_contacts IS 'Junction table linking contacts to campaigns with engagement tracking';
COMMENT ON TABLE messages IS 'Complete message history for campaign tracking and Slack integration';
COMMENT ON TABLE webhook_events IS 'Raw Dux-Soup webhook data storage before processing';

COMMENT ON COLUMN campaigns.campaign_key IS 'Unique identifier for API access and external integrations';
COMMENT ON COLUMN campaigns.scheduled_start IS 'When campaign should start (NULL = immediate)';
COMMENT ON COLUMN campaigns.end_date IS 'When campaign should end (NULL = never)';
COMMENT ON COLUMN contacts.profile_data IS 'Complete raw profile data from Dux-Soup webhooks';
COMMENT ON COLUMN webhook_events.raw_data IS 'Complete raw webhook payload from Dux-Soup';

-- =============================================================================
-- DEPLOYMENT COMPLETE
-- =============================================================================

-- This schema is now ready for use with the Dux-Soup LinkedIn automation platform.
-- The Python application will use AzureDatabaseManager to interact with these tables.
-- All webhook events from Dux-Soup will be stored and processed according to this schema. 