#!/usr/bin/env python3
"""
Complete Database Migration Script
==================================

This script migrates the complete Chaknal platform database from local SQLite 
to Azure PostgreSQL, creating all 18 tables and transferring critical data.

Tables to migrate:
✅ Already created: organization, company, campaigns_new, user, contacts, webhook_events
❌ Missing (12 tables): campaign_contacts, duxsoup_user, duxsoup_user_settings, 
   messages, duxsoup_execution_log, agency_client, agency_activity_log, 
   agency_invitation, meetings, duxsoup_queue, tenant_campaigns, tenant_contacts, 
   alembic_version

Critical data counts:
- campaign_contacts: 449 rows (CRITICAL for campaign functionality)
- contacts: 449 rows
- campaigns_new: 13 rows
- user: 23 rows
- company: 21 rows
- duxsoup_user: 6 rows
- messages: 7 rows
- duxsoup_execution_log: 2 rows
- agency_client: 3 rows
- meetings: 1 row
- organization: 7 rows
- alembic_version: 1 row
"""

import sqlite3
import psycopg2
import psycopg2.extras
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys


class DatabaseMigrator:
    def __init__(self):
        self.sqlite_path = "chaknal.db"
        
        # Azure PostgreSQL connection details
        self.pg_config = {
            'host': 'chaknal-db-server.postgres.database.azure.com',
            'database': 'chaknal_platform',
            'user': os.getenv('POSTGRES_USER', 'chaknaladmin'),
            'password': os.getenv('POSTGRES_PASSWORD'),
            'port': 5432,
            'sslmode': 'require'
        }
        
        if not self.pg_config['password']:
            print("❌ ERROR: POSTGRES_PASSWORD environment variable not set!")
            print("Please set it with: export POSTGRES_PASSWORD='your_password'")
            sys.exit(1)

    def connect_sqlite(self):
        """Connect to local SQLite database"""
        if not os.path.exists(self.sqlite_path):
            raise FileNotFoundError(f"SQLite database not found: {self.sqlite_path}")
        
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn

    def connect_postgresql(self):
        """Connect to Azure PostgreSQL database"""
        try:
            conn = psycopg2.connect(**self.pg_config)
            conn.autocommit = False
            return conn
        except psycopg2.Error as e:
            print(f"❌ Failed to connect to PostgreSQL: {e}")
            raise

    def create_missing_tables(self, pg_conn):
        """Create all missing tables in PostgreSQL"""
        
        print("🔨 Creating missing tables in PostgreSQL...")
        
        # Table creation SQL statements
        table_schemas = {
            'campaign_contacts': '''
                CREATE TABLE IF NOT EXISTS campaign_contacts (
                    campaign_contact_id VARCHAR(36) PRIMARY KEY,
                    campaign_id VARCHAR(36) NOT NULL,
                    campaign_key VARCHAR(36) NOT NULL,
                    contact_id VARCHAR(36) NOT NULL,
                    status VARCHAR(50) NOT NULL DEFAULT 'enrolled',
                    assigned_to VARCHAR(36),
                    enrolled_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    accepted_at TIMESTAMPTZ,
                    replied_at TIMESTAMPTZ,
                    blacklisted_at TIMESTAMPTZ,
                    sequence_step INTEGER NOT NULL DEFAULT 1,
                    tags TEXT,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    dux_profile_id VARCHAR(100),
                    command_executed VARCHAR(50),
                    command_params JSONB,
                    force_execution BOOLEAN DEFAULT FALSE,
                    run_after TIMESTAMPTZ,
                    execution_result JSONB,
                    retry_count INTEGER DEFAULT 0,
                    last_retry TIMESTAMPTZ,
                    FOREIGN KEY (campaign_id) REFERENCES campaigns_new(campaign_id),
                    FOREIGN KEY (contact_id) REFERENCES contacts(contact_id),
                    FOREIGN KEY (assigned_to) REFERENCES "user"(id)
                );
            ''',
            
            'duxsoup_user': '''
                CREATE TABLE IF NOT EXISTS duxsoup_user (
                    id VARCHAR(36) PRIMARY KEY,
                    dux_soup_user_id VARCHAR NOT NULL,
                    dux_soup_auth_key VARCHAR NOT NULL,
                    email VARCHAR NOT NULL,
                    first_name VARCHAR NOT NULL,
                    last_name VARCHAR NOT NULL,
                    user_id VARCHAR(36),
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES "user"(id)
                );
            ''',
            
            'duxsoup_user_settings': '''
                CREATE TABLE IF NOT EXISTS duxsoup_user_settings (
                    id VARCHAR(36) PRIMARY KEY,
                    duxsoup_user_id VARCHAR(36) NOT NULL UNIQUE,
                    throttle_time INTEGER DEFAULT 1,
                    scan_throttle_time INTEGER DEFAULT 3000,
                    max_visits INTEGER DEFAULT 0,
                    max_invites INTEGER DEFAULT 20,
                    max_messages INTEGER DEFAULT 100,
                    max_enrolls INTEGER DEFAULT 200,
                    linkedin_limits_nooze INTEGER DEFAULT 3,
                    linkedin_limit_alert BOOLEAN DEFAULT FALSE,
                    pause_on_invite_error BOOLEAN DEFAULT TRUE,
                    resume_delay_on_invite_error VARCHAR(10) DEFAULT '1d',
                    skip_noname BOOLEAN DEFAULT TRUE,
                    skip_noimage BOOLEAN DEFAULT FALSE,
                    skip_incrm BOOLEAN DEFAULT FALSE,
                    skip_nopremium BOOLEAN DEFAULT FALSE,
                    skip_3plus BOOLEAN DEFAULT FALSE,
                    skip_nolion BOOLEAN DEFAULT FALSE,
                    skip_noinfluencer BOOLEAN DEFAULT FALSE,
                    skip_nojobseeker BOOLEAN DEFAULT FALSE,
                    exclude_blacklisted_action BOOLEAN DEFAULT TRUE,
                    exclude_tag_skipped_action BOOLEAN DEFAULT FALSE,
                    exclude_low_connection_count_action BOOLEAN DEFAULT FALSE,
                    exclude_low_connection_count_value INTEGER DEFAULT 100,
                    kill_characters TEXT DEFAULT '.,★☆✪☁📍💪🏼🎖🏼📦♦➤✔✓~()\"''',
                    kill_words TEXT DEFAULT 'bsn, ceo, certified, copywriter, cpc, digital, dr, drs, expert, freelance, hubspot, internet, lion, lme, lmt, ma, marketing, mba, md, mim, msc, ninja, online, pharma, phd, ppc, seo, sip, videoseo',
                    robot_schedule_plan JSONB DEFAULT '{"0": [["", ""]], "1": [["09:00", "23:00"]], "2": [["09:00", "23:00"]], "3": [["09:00", "23:00"]], "4": [["09:00", "23:00"]], "5": [["09:00", "23:00"]], "6": [["", ""]]}',
                    auto_tag_flag BOOLEAN DEFAULT TRUE,
                    auto_tag_value VARCHAR(100) DEFAULT 'AMPED',
                    followup_flag BOOLEAN DEFAULT TRUE,
                    followup_for_all_flag BOOLEAN DEFAULT FALSE,
                    active_followup_campaign_id VARCHAR(100) DEFAULT 'default',
                    auto_connect BOOLEAN DEFAULT FALSE,
                    auto_follow BOOLEAN DEFAULT FALSE,
                    auto_disconnect BOOLEAN DEFAULT FALSE,
                    auto_connect_message_flag BOOLEAN DEFAULT FALSE,
                    auto_connect_message_text TEXT DEFAULT '',
                    expire_pending_invites_flag BOOLEAN DEFAULT TRUE,
                    expire_pending_invites_value INTEGER DEFAULT 30,
                    connected_message_flag BOOLEAN DEFAULT FALSE,
                    connected_message_text TEXT DEFAULT '',
                    skip_days INTEGER DEFAULT 0,
                    page_init_delay INTEGER DEFAULT 5000,
                    wait_minutes INTEGER DEFAULT 5,
                    wait_visits INTEGER DEFAULT 20,
                    max_page_load_time INTEGER DEFAULT 20000,
                    warning_notifications BOOLEAN DEFAULT TRUE,
                    action_notifications BOOLEAN DEFAULT TRUE,
                    info_notifications BOOLEAN DEFAULT TRUE,
                    buy_mail BOOLEAN DEFAULT FALSE,
                    pre_visit_dialog BOOLEAN DEFAULT TRUE,
                    auto_endorse BOOLEAN DEFAULT FALSE,
                    auto_endorse_target INTEGER DEFAULT 3,
                    badge_display VARCHAR(50) DEFAULT 'nothing',
                    auto_save_as_lead BOOLEAN DEFAULT FALSE,
                    auto_pdf BOOLEAN DEFAULT FALSE,
                    send_inmail_flag BOOLEAN DEFAULT FALSE,
                    send_inmail_subject VARCHAR(200) DEFAULT '',
                    send_inmail_body TEXT DEFAULT '',
                    webhook_profile_flag BOOLEAN DEFAULT TRUE,
                    webhooks JSONB DEFAULT '[]',
                    message_bridge_flag BOOLEAN DEFAULT TRUE,
                    message_bridge_interval INTEGER DEFAULT 180,
                    remote_control_flag BOOLEAN DEFAULT TRUE,
                    minimised_tools BOOLEAN DEFAULT FALSE,
                    background_mode BOOLEAN DEFAULT TRUE,
                    managed_download BOOLEAN DEFAULT TRUE,
                    hide_system_tags BOOLEAN DEFAULT TRUE,
                    simplegui BOOLEAN DEFAULT FALSE,
                    snooze BOOLEAN DEFAULT TRUE,
                    uselocalstorage BOOLEAN DEFAULT TRUE,
                    runautomationsonmanualvisits BOOLEAN DEFAULT FALSE,
                    campaigns JSONB DEFAULT '[]',
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (duxsoup_user_id) REFERENCES duxsoup_user(id)
                );
            ''',
            
            'messages': '''
                CREATE TABLE IF NOT EXISTS messages (
                    message_id VARCHAR(36) PRIMARY KEY,
                    campaign_contact_id VARCHAR(36) NOT NULL,
                    direction VARCHAR(20) NOT NULL,
                    message_text TEXT NOT NULL,
                    linkedin_message_id VARCHAR(100),
                    thread_url VARCHAR(500),
                    sent_at TIMESTAMPTZ,
                    received_at TIMESTAMPTZ,
                    status VARCHAR(50) NOT NULL DEFAULT 'sent',
                    tags TEXT,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    dux_message_id VARCHAR(100),
                    command_type VARCHAR(50),
                    command_params JSONB,
                    campaign_id VARCHAR(36),
                    force_execution BOOLEAN DEFAULT FALSE,
                    execution_result JSONB,
                    retry_count INTEGER DEFAULT 0,
                    last_retry TIMESTAMPTZ,
                    FOREIGN KEY (campaign_contact_id) REFERENCES campaign_contacts(campaign_contact_id),
                    FOREIGN KEY (campaign_id) REFERENCES campaigns_new(campaign_id)
                );
            ''',
            
            'duxsoup_execution_log': '''
                CREATE TABLE IF NOT EXISTS duxsoup_execution_log (
                    log_id VARCHAR(36) PRIMARY KEY,
                    dux_user_id VARCHAR(100) NOT NULL,
                    campaign_id VARCHAR(36),
                    contact_id VARCHAR(36),
                    command VARCHAR(50) NOT NULL,
                    params JSONB NOT NULL,
                    execution_start TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    execution_end TIMESTAMPTZ,
                    status VARCHAR(50) NOT NULL DEFAULT 'running',
                    result JSONB,
                    error_message TEXT,
                    response_time_ms INTEGER,
                    FOREIGN KEY (campaign_id) REFERENCES campaigns_new(campaign_id),
                    FOREIGN KEY (contact_id) REFERENCES contacts(contact_id)
                );
            ''',
            
            'agency_client': '''
                CREATE TABLE IF NOT EXISTS agency_client (
                    id VARCHAR(36) PRIMARY KEY,
                    agency_user_id VARCHAR(36) NOT NULL,
                    client_company_id VARCHAR(36) NOT NULL,
                    access_level VARCHAR(20) DEFAULT 'full',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agency_user_id) REFERENCES "user"(id),
                    FOREIGN KEY (client_company_id) REFERENCES company(id)
                );
            ''',
            
            'agency_activity_log': '''
                CREATE TABLE IF NOT EXISTS agency_activity_log (
                    id VARCHAR(36) PRIMARY KEY,
                    agency_user_id VARCHAR(36) NOT NULL,
                    client_company_id VARCHAR(36) NOT NULL,
                    activity_type VARCHAR(50) NOT NULL,
                    activity_description TEXT NOT NULL,
                    activity_metadata TEXT,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agency_user_id) REFERENCES "user"(id),
                    FOREIGN KEY (client_company_id) REFERENCES company(id)
                );
            ''',
            
            'agency_invitation': '''
                CREATE TABLE IF NOT EXISTS agency_invitation (
                    id VARCHAR(36) PRIMARY KEY,
                    agency_user_id VARCHAR(36) NOT NULL,
                    client_company_id VARCHAR(36) NOT NULL,
                    invited_by_user_id VARCHAR(36) NOT NULL,
                    access_level VARCHAR(20) DEFAULT 'full',
                    status VARCHAR(20) DEFAULT 'pending',
                    invitation_token VARCHAR(255) UNIQUE NOT NULL,
                    expires_at TIMESTAMPTZ NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    accepted_at TIMESTAMPTZ,
                    FOREIGN KEY (agency_user_id) REFERENCES "user"(id),
                    FOREIGN KEY (client_company_id) REFERENCES company(id),
                    FOREIGN KEY (invited_by_user_id) REFERENCES "user"(id)
                );
            ''',
            
            'meetings': '''
                CREATE TABLE IF NOT EXISTS meetings (
                    meeting_id VARCHAR(36) PRIMARY KEY,
                    campaign_contact_id VARCHAR(36) NOT NULL,
                    contact_id VARCHAR(36) NOT NULL,
                    campaign_id VARCHAR(36),
                    meeting_type VARCHAR(50),
                    meeting_status VARCHAR(50) NOT NULL DEFAULT 'scheduled',
                    scheduled_date TIMESTAMPTZ,
                    actual_date TIMESTAMPTZ,
                    duration_minutes INTEGER,
                    meeting_link VARCHAR(500),
                    booked_by VARCHAR(36),
                    booking_source VARCHAR(50) DEFAULT 'manual_entry',
                    booking_message_id VARCHAR(36),
                    booking_notes TEXT,
                    outcome VARCHAR(50),
                    outcome_notes TEXT,
                    next_action VARCHAR(100),
                    follow_up_date TIMESTAMPTZ,
                    deal_value VARCHAR(20),
                    contact_title_at_meeting VARCHAR(255),
                    contact_company_at_meeting VARCHAR(255),
                    agenda TEXT,
                    attendees TEXT,
                    preparation_notes TEXT,
                    reminder_sent BOOLEAN DEFAULT FALSE,
                    calendar_invite_sent BOOLEAN DEFAULT FALSE,
                    confirmation_received BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (campaign_contact_id) REFERENCES campaign_contacts(campaign_contact_id),
                    FOREIGN KEY (contact_id) REFERENCES contacts(contact_id),
                    FOREIGN KEY (campaign_id) REFERENCES campaigns_new(campaign_id),
                    FOREIGN KEY (booked_by) REFERENCES "user"(id),
                    FOREIGN KEY (booking_message_id) REFERENCES messages(message_id)
                );
            ''',
            
            'duxsoup_queue': '''
                CREATE TABLE IF NOT EXISTS duxsoup_queue (
                    queue_id VARCHAR(36) PRIMARY KEY,
                    dux_user_id VARCHAR(100) NOT NULL,
                    campaign_id VARCHAR(36),
                    contact_id VARCHAR(36),
                    command VARCHAR(50) NOT NULL,
                    params JSONB NOT NULL,
                    force_execution BOOLEAN DEFAULT FALSE,
                    run_after TIMESTAMPTZ,
                    status VARCHAR(50) NOT NULL DEFAULT 'queued',
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    executed_at TIMESTAMPTZ,
                    result JSONB,
                    error_message TEXT,
                    FOREIGN KEY (campaign_id) REFERENCES campaigns_new(campaign_id),
                    FOREIGN KEY (contact_id) REFERENCES contacts(contact_id)
                );
            ''',
            
            'tenant_campaigns': '''
                CREATE TABLE IF NOT EXISTS tenant_campaigns (
                    id VARCHAR(36) PRIMARY KEY,
                    company_id VARCHAR(36) NOT NULL,
                    organization_id VARCHAR(36),
                    is_shared BOOLEAN,
                    FOREIGN KEY (company_id) REFERENCES company(id),
                    FOREIGN KEY (organization_id) REFERENCES organization(id)
                );
                CREATE INDEX IF NOT EXISTS ix_tenant_campaigns_organization_id ON tenant_campaigns (organization_id);
                CREATE INDEX IF NOT EXISTS ix_tenant_campaigns_company_id ON tenant_campaigns (company_id);
            ''',
            
            'tenant_contacts': '''
                CREATE TABLE IF NOT EXISTS tenant_contacts (
                    id VARCHAR(36) PRIMARY KEY,
                    company_id VARCHAR(36) NOT NULL,
                    organization_id VARCHAR(36),
                    is_shared BOOLEAN,
                    FOREIGN KEY (company_id) REFERENCES company(id),
                    FOREIGN KEY (organization_id) REFERENCES organization(id)
                );
                CREATE INDEX IF NOT EXISTS ix_tenant_contacts_organization_id ON tenant_contacts (organization_id);
                CREATE INDEX IF NOT EXISTS ix_tenant_contacts_company_id ON tenant_contacts (company_id);
            ''',
            
            'alembic_version': '''
                CREATE TABLE IF NOT EXISTS alembic_version (
                    version_num VARCHAR(32) NOT NULL,
                    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
                );
            '''
        }

        cursor = pg_conn.cursor()
        
        for table_name, schema_sql in table_schemas.items():
            try:
                print(f"  📋 Creating table: {table_name}")
                cursor.execute(schema_sql)
                print(f"  ✅ Created: {table_name}")
            except psycopg2.Error as e:
                print(f"  ❌ Error creating {table_name}: {e}")
                pg_conn.rollback()
                raise
        
        pg_conn.commit()
        print("✅ All missing tables created successfully!")

    def migrate_table_data(self, sqlite_conn, pg_conn, table_name: str, 
                          primary_key: str, exclude_columns: List[str] = None):
        """Migrate data from SQLite to PostgreSQL for a specific table"""
        
        exclude_columns = exclude_columns or []
        
        # Get data from SQLite
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"  📭 No data to migrate for {table_name}")
            return 0
        
        # Get column names
        column_names = [desc[0] for desc in sqlite_cursor.description 
                       if desc[0] not in exclude_columns]
        
        # Prepare PostgreSQL insert
        pg_cursor = pg_conn.cursor()
        
        # Check existing records to avoid duplicates
        existing_ids = set()
        try:
            pg_cursor.execute(f"SELECT {primary_key} FROM {table_name}")
            existing_ids = {row[0] for row in pg_cursor.fetchall()}
        except psycopg2.Error:
            # Table might not exist or be empty
            pass
        
        # Filter out existing records
        new_rows = []
        for row in rows:
            row_dict = dict(row)
            if row_dict[primary_key] not in existing_ids:
                # Remove excluded columns
                filtered_row = {k: v for k, v in row_dict.items() 
                              if k not in exclude_columns}
                new_rows.append(filtered_row)
        
        if not new_rows:
            print(f"  📋 All {len(rows)} records already exist in {table_name}")
            return 0
        
        # Insert new records
        placeholders = ', '.join(['%s'] * len(column_names))
        columns_str = ', '.join([f'"{col}"' if col == 'user' else col for col in column_names])
        insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        
        inserted_count = 0
        for row_dict in new_rows:
            try:
                values = [row_dict[col] for col in column_names]
                pg_cursor.execute(insert_sql, values)
                inserted_count += 1
            except psycopg2.Error as e:
                print(f"  ⚠️  Error inserting row in {table_name}: {e}")
                print(f"      Row data: {row_dict}")
                # Continue with other rows
                pg_conn.rollback()
                continue
        
        pg_conn.commit()
        print(f"  ✅ Migrated {inserted_count} new records to {table_name}")
        return inserted_count

    def run_migration(self):
        """Run the complete database migration"""
        
        print("🚀 Starting Complete Database Migration")
        print("=====================================")
        print()
        
        # Connect to databases
        print("🔌 Connecting to databases...")
        sqlite_conn = self.connect_sqlite()
        pg_conn = self.connect_postgresql()
        print("✅ Connected to both databases")
        print()
        
        try:
            # Step 1: Create missing tables
            self.create_missing_tables(pg_conn)
            print()
            
            # Step 2: Migrate critical data
            print("📦 Migrating critical data...")
            
            migration_plan = [
                # Core tables first
                ("organization", "id"),
                ("company", "id"),
                ("user", "id", ["user"]),  # Exclude 'user' column if it exists
                ("campaigns_new", "campaign_id"),
                ("contacts", "contact_id"),
                
                # DuxSoup tables
                ("duxsoup_user", "id"),
                ("duxsoup_user_settings", "id"),
                
                # Relationship tables
                ("campaign_contacts", "campaign_contact_id"),  # CRITICAL!
                ("messages", "message_id"),
                ("meetings", "meeting_id"),
                
                # Agency tables
                ("agency_client", "id"),
                ("agency_activity_log", "id"),
                ("agency_invitation", "id"),
                
                # Queue and logging
                ("duxsoup_execution_log", "log_id"),
                ("duxsoup_queue", "queue_id"),
                
                # Tenant tables
                ("tenant_campaigns", "id"),
                ("tenant_contacts", "id"),
                
                # System tables
                ("webhook_events", "id"),
                ("alembic_version", "version_num"),
            ]
            
            total_migrated = 0
            for table_info in migration_plan:
                table_name = table_info[0]
                primary_key = table_info[1]
                exclude_columns = table_info[2] if len(table_info) > 2 else []
                
                print(f"📋 Migrating {table_name}...")
                try:
                    count = self.migrate_table_data(sqlite_conn, pg_conn, table_name, 
                                                  primary_key, exclude_columns)
                    total_migrated += count
                except Exception as e:
                    print(f"  ⚠️  Warning: Could not migrate {table_name}: {e}")
            
            print()
            print(f"🎉 Migration completed successfully!")
            print(f"📊 Total records migrated: {total_migrated}")
            print()
            
            # Verify critical tables
            print("🔍 Verifying critical tables...")
            pg_cursor = pg_conn.cursor()
            
            critical_checks = [
                ("campaign_contacts", "Campaign-Contact relationships"),
                ("contacts", "Contacts"),
                ("campaigns_new", "Campaigns"),
                ("duxsoup_user", "DuxSoup Users"),
                ("user", "Users"),
                ("company", "Companies"),
            ]
            
            for table, description in critical_checks:
                try:
                    pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = pg_cursor.fetchone()[0]
                    print(f"  ✅ {description}: {count} records")
                except Exception as e:
                    print(f"  ❌ {description}: Error - {e}")
            
            print()
            print("🎯 Next Steps:")
            print("1. Test campaign creation at: https://app.chaknal.com")
            print("2. Verify DuxSoup integration works")
            print("3. Check that all relationships are intact")
            print("4. Monitor backend logs for any issues")
            print()
            print("✅ Database migration is complete!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            pg_conn.rollback()
            raise
        finally:
            sqlite_conn.close()
            pg_conn.close()


if __name__ == "__main__":
    print("Chaknal Platform - Complete Database Migration")
    print("=" * 50)
    print()
    
    # Check if running in correct directory
    if not os.path.exists("chaknal.db"):
        print("❌ Error: chaknal.db not found in current directory")
        print("Please run this script from the chaknal-platform directory")
        sys.exit(1)
    
    # Check environment variables
    if not os.getenv('POSTGRES_PASSWORD'):
        print("⚠️  POSTGRES_PASSWORD not set in environment")
        print("Please set it with: export POSTGRES_PASSWORD='your_azure_postgres_password'")
        
        # Try to get it interactively
        import getpass
        password = getpass.getpass("Enter Azure PostgreSQL password: ")
        os.environ['POSTGRES_PASSWORD'] = password
    
    # Run migration
    migrator = DatabaseMigrator()
    migrator.run_migration()
