#!/usr/bin/env python3
"""
Critical Campaign Contacts Migration
===================================

This script specifically addresses the most critical missing piece:
the campaign_contacts table and its 449 rows of data.

This table is essential for campaign functionality - without it,
campaigns cannot be linked to contacts, breaking the entire workflow.
"""

import sqlite3
import psycopg2
import os
import sys
from datetime import datetime


def migrate_campaign_contacts():
    """Migrate the critical campaign_contacts table"""
    
    print("🚨 CRITICAL: Migrating campaign_contacts table")
    print("=" * 50)
    
    # Database connections
    sqlite_path = "chaknal.db"
    pg_config = {
        'host': 'chaknal-db-server.postgres.database.azure.com',
        'database': 'chaknal_platform',
        'user': 'chaknaladmin',
        'password': os.getenv('POSTGRES_PASSWORD'),
        'port': 5432,
        'sslmode': 'require'
    }
    
    if not pg_config['password']:
        print("❌ POSTGRES_PASSWORD environment variable not set!")
        import getpass
        pg_config['password'] = getpass.getpass("Enter Azure PostgreSQL password: ")
    
    # Connect to SQLite
    if not os.path.exists(sqlite_path):
        print(f"❌ SQLite database not found: {sqlite_path}")
        return False
    
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    
    # Connect to PostgreSQL
    try:
        pg_conn = psycopg2.connect(**pg_config)
        print("✅ Connected to Azure PostgreSQL")
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        return False
    
    try:
        pg_cursor = pg_conn.cursor()
        
        # 1. Create campaign_contacts table if it doesn't exist
        print("\n🔨 Creating campaign_contacts table...")
        
        create_table_sql = '''
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
                last_retry TIMESTAMPTZ
            );
        '''
        
        pg_cursor.execute(create_table_sql)
        pg_conn.commit()
        print("✅ campaign_contacts table created")
        
        # 2. Check existing data
        pg_cursor.execute("SELECT COUNT(*) FROM campaign_contacts")
        existing_count = pg_cursor.fetchone()[0]
        print(f"📊 Existing records in PostgreSQL: {existing_count}")
        
        # 3. Get data from SQLite
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute("SELECT COUNT(*) FROM campaign_contacts")
        sqlite_count = sqlite_cursor.fetchone()[0]
        print(f"📊 Records in SQLite: {sqlite_count}")
        
        if sqlite_count == 0:
            print("⚠️  No data to migrate from SQLite")
            return True
        
        # 4. Get existing IDs to avoid duplicates
        pg_cursor.execute("SELECT campaign_contact_id FROM campaign_contacts")
        existing_ids = {row[0] for row in pg_cursor.fetchall()}
        print(f"📋 Found {len(existing_ids)} existing records to skip")
        
        # 5. Migrate data
        sqlite_cursor.execute("SELECT * FROM campaign_contacts")
        rows = sqlite_cursor.fetchall()
        
        column_names = [desc[0] for desc in sqlite_cursor.description]
        
        migrated_count = 0
        for row in rows:
            row_dict = dict(row)
            
            # Skip if already exists
            if row_dict['campaign_contact_id'] in existing_ids:
                continue
            
            # Prepare insert
            columns_str = ', '.join(column_names)
            placeholders = ', '.join(['%s'] * len(column_names))
            insert_sql = f"INSERT INTO campaign_contacts ({columns_str}) VALUES ({placeholders})"
            
            try:
                values = [row_dict[col] for col in column_names]
                pg_cursor.execute(insert_sql, values)
                migrated_count += 1
            except Exception as e:
                print(f"⚠️  Error inserting record {row_dict['campaign_contact_id']}: {e}")
                pg_conn.rollback()
                continue
        
        pg_conn.commit()
        print(f"✅ Migrated {migrated_count} campaign_contact records")
        
        # 6. Verify final count
        pg_cursor.execute("SELECT COUNT(*) FROM campaign_contacts")
        final_count = pg_cursor.fetchone()[0]
        print(f"📊 Final count in PostgreSQL: {final_count}")
        
        # 7. Test a sample query
        print("\n🔍 Testing campaign-contact relationships...")
        pg_cursor.execute("""
            SELECT c.name as campaign_name, COUNT(cc.contact_id) as contact_count
            FROM campaigns_new c
            LEFT JOIN campaign_contacts cc ON c.campaign_id = cc.campaign_id
            GROUP BY c.campaign_id, c.name
            ORDER BY contact_count DESC
            LIMIT 5
        """)
        
        results = pg_cursor.fetchall()
        print("Top campaigns by contact count:")
        for campaign_name, contact_count in results:
            print(f"  📋 {campaign_name}: {contact_count} contacts")
        
        print("\n🎉 CRITICAL MIGRATION COMPLETED!")
        print("✅ Campaign creation should now work properly")
        print("\n🎯 Next: Test campaign creation at https://app.chaknal.com")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        pg_conn.rollback()
        return False
    finally:
        sqlite_conn.close()
        pg_conn.close()


if __name__ == "__main__":
    success = migrate_campaign_contacts()
    if success:
        print("\n✅ SUCCESS: Critical migration completed")
        sys.exit(0)
    else:
        print("\n❌ FAILED: Critical migration failed")
        sys.exit(1)
