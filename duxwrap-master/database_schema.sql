-- Dux-Soup LinkedIn Automation Database Schema
-- Complete schema for webhook processing and campaign management

-- Enable UUID support
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 1.  WEBHOOK EVENT LANDING ZONE
--    (raw, unprocessed Dux-Soup payloads)
-- ============================================================
CREATE TABLE IF NOT EXISTS webhook_events (
    event_id      UUID PRIMARY KEY        DEFAULT uuid_generate_v4(),
    dux_user_id   VARCHAR(100)            NOT NULL,          -- Dux-Soup account
    event_type    VARCHAR(50)             NOT NULL,          -- message | visit | action | rccommand
    event_name    VARCHAR(50)             NOT NULL,          -- create | received | completed | …
    raw_data      JSONB                   NOT NULL,          -- full payload for replay/debug
    processed     BOOLEAN                 DEFAULT FALSE,     -- flipped when ETL succeeds
    contact_id    UUID,                                      -- filled by ETL
    campaign_id   UUID,                                      -- filled by ETL
    created_at    TIMESTAMPTZ             DEFAULT NOW()
);

-- Fast retrieval
CREATE INDEX IF NOT EXISTS idx_we_created_at  ON webhook_events (created_at);
CREATE INDEX IF NOT EXISTS idx_we_processed   ON webhook_events (processed);
CREATE INDEX IF NOT EXISTS idx_we_type_user   ON webhook_events (event_type, dux_user_id);

-- ============================================================
-- 2.  CONTACTS
--    (unique LinkedIn profiles extracted from payloads)
-- ============================================================
CREATE TABLE IF NOT EXISTS contacts (
    contact_id    UUID PRIMARY KEY        DEFAULT uuid_generate_v4(),
    linkedin_id   VARCHAR(100) UNIQUE,        -- stable LI internal ID
    linkedin_url  VARCHAR(500),
    first_name    VARCHAR(100),
    last_name     VARCHAR(100),
    headline      VARCHAR(500),
    company       VARCHAR(255),
    location      VARCHAR(255),
    industry      VARCHAR(255),
    connection_degree INTEGER,
    profile_data  JSONB,                                 -- full raw profile for enrichment
    created_at    TIMESTAMPTZ             DEFAULT NOW(),
    updated_at    TIMESTAMPTZ             DEFAULT NOW()
);

-- Quick look-ups
CREATE INDEX IF NOT EXISTS idx_contacts_linkedin_id  ON contacts (linkedin_id);
CREATE INDEX IF NOT EXISTS idx_contacts_company      ON contacts (company);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION touch_updated_at() RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END; $$ LANGUAGE plpgsql;

CREATE TRIGGER trg_contacts_touch
BEFORE UPDATE ON contacts
FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

-- ============================================================
-- 3.  CAMPAIGNS  (optional but common in LinkedIn automation)
-- ============================================================
CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id   UUID PRIMARY KEY        DEFAULT uuid_generate_v4(),
    campaign_key  UUID                    NOT NULL DEFAULT uuid_generate_v4(), -- for API joins
    name          VARCHAR(255)            NOT NULL,
    status        VARCHAR(20)             DEFAULT 'active', -- active | paused | completed
    dux_user_id   VARCHAR(100)            NOT NULL,
    scheduled_start TIMESTAMPTZ,
    end_date      TIMESTAMPTZ,
    created_at    TIMESTAMPTZ             DEFAULT NOW(),
    updated_at    TIMESTAMPTZ             DEFAULT NOW(),
    settings      JSONB
);

ALTER TABLE campaigns
ADD CONSTRAINT chk_campaign_status
  CHECK (status IN ('active','paused','completed'));

CREATE INDEX IF NOT EXISTS idx_campaigns_user   ON campaigns (dux_user_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns (status);

CREATE TRIGGER trg_campaigns_touch
BEFORE UPDATE ON campaigns
FOR EACH ROW EXECUTE FUNCTION touch_updated_at();

-- ============================================================
-- 4.  CAMPAIGN ↔ CONTACT MAPPINGS
-- ============================================================
CREATE TABLE IF NOT EXISTS campaign_contacts (
    campaign_contact_id UUID PRIMARY KEY  DEFAULT uuid_generate_v4(),
    campaign_id   UUID REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    contact_id    UUID REFERENCES contacts(contact_id)  ON DELETE CASCADE,
    status        VARCHAR(20)            DEFAULT 'enrolled',  -- enrolled | accepted | replied | …
    sequence_step INTEGER                DEFAULT 1,
    enrolled_at   TIMESTAMPTZ            DEFAULT NOW(),
    accepted_at   TIMESTAMPTZ,
    replied_at    TIMESTAMPTZ,
    UNIQUE (campaign_id, contact_id)
);

CREATE INDEX IF NOT EXISTS idx_cc_status ON campaign_contacts (status);
CREATE INDEX IF NOT EXISTS idx_cc_contact ON campaign_contacts (contact_id);

-- ============================================================
-- 5.  MESSAGES  (every LinkedIn DM, inbound or outbound)
-- ============================================================
CREATE TABLE IF NOT EXISTS messages (
    message_id    UUID PRIMARY KEY        DEFAULT uuid_generate_v4(),
    campaign_contact_id UUID REFERENCES campaign_contacts(campaign_contact_id) ON DELETE CASCADE,
    direction     VARCHAR(10)             NOT NULL,   -- sent | received
    message_text  TEXT                    NOT NULL,
    linkedin_message_id VARCHAR(100),
    thread_url    VARCHAR(500),
    sent_at       TIMESTAMPTZ,
    received_at   TIMESTAMPTZ,
    created_at    TIMESTAMPTZ             DEFAULT NOW()
);

ALTER TABLE messages
ADD CONSTRAINT chk_msg_direction
  CHECK (direction IN ('sent','received'));

CREATE INDEX IF NOT EXISTS idx_msgs_cc   ON messages (campaign_contact_id);
CREATE INDEX IF NOT EXISTS idx_msgs_sent ON messages (sent_at);

-- ============================================================
-- DONE – core ingestion schema
-- ============================================================

-- Additional useful views for reporting

-- View: Recent webhook events
CREATE OR REPLACE VIEW recent_webhook_events AS
SELECT 
    event_id,
    dux_user_id,
    event_type,
    event_name,
    processed,
    created_at
FROM webhook_events
ORDER BY created_at DESC;

-- View: Campaign performance summary
CREATE OR REPLACE VIEW campaign_performance AS
SELECT 
    c.campaign_id,
    c.name,
    c.status,
    c.dux_user_id,
    COUNT(cc.contact_id) as total_contacts,
    COUNT(CASE WHEN cc.status = 'enrolled' THEN 1 END) as enrolled,
    COUNT(CASE WHEN cc.status = 'accepted' THEN 1 END) as accepted,
    COUNT(CASE WHEN cc.status = 'replied' THEN 1 END) as replied,
    COUNT(m.message_id) as total_messages,
    c.created_at
FROM campaigns c
LEFT JOIN campaign_contacts cc ON c.campaign_id = cc.campaign_id
LEFT JOIN messages m ON cc.campaign_contact_id = m.campaign_contact_id
GROUP BY c.campaign_id, c.name, c.status, c.dux_user_id, c.created_at
ORDER BY c.created_at DESC;

-- View: Contact engagement summary
CREATE OR REPLACE VIEW contact_engagement AS
SELECT 
    co.contact_id,
    co.first_name,
    co.last_name,
    co.company,
    co.linkedin_url,
    COUNT(cc.campaign_id) as campaigns_involved,
    COUNT(m.message_id) as total_messages,
    COUNT(CASE WHEN m.direction = 'received' THEN 1 END) as messages_received,
    COUNT(CASE WHEN m.direction = 'sent' THEN 1 END) as messages_sent,
    MAX(m.created_at) as last_activity
FROM contacts co
LEFT JOIN campaign_contacts cc ON co.contact_id = cc.contact_id
LEFT JOIN messages m ON cc.campaign_contact_id = m.campaign_contact_id
GROUP BY co.contact_id, co.first_name, co.last_name, co.company, co.linkedin_url
ORDER BY last_activity DESC NULLS LAST; 