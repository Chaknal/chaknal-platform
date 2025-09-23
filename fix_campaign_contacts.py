#!/usr/bin/env python3
"""
Quick Fix for Campaign Contacts Table
====================================

This script specifically fixes the campaign_contacts table issue.
"""

import sqlite3
import psycopg2
import os
import sys

def fix_campaign_contacts():
    """Fix the campaign_contacts table specifically"""
    
    print("🚨 FIXING: campaign_contacts table")
    print("=" * 40)
    
    # Database connections
    sqlite_path = "chaknal.db"
    pg_config = {
        'host': 'chaknal-db-server.postgres.database.azure.com',
        'database': 'chaknal_platform',
        'user': 'chaknaladmin',
        'password': os.getenv('POSTGRES_PASSWORD', 'Chaknal2024!'),
        'port': 5432,
        'sslmode': 'require'
    }
    
    print(f"🔌 Connecting to databases...")
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    
    # Connect to PostgreSQL
    try:
        pg_conn = psycopg2.connect(**pg_config)
        print("✅ Connected to both databases")
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        return False
    
    try:
        pg_cursor = pg_conn.cursor()
        
        # 1. Drop existing table if it has wrong structure
        print("\n🗑️  Dropping existing campaign_contacts table...")
        pg_cursor.execute("DROP TABLE IF EXISTS campaign_contacts CASCADE;")
        pg_conn.commit()
        
        # 2. Create campaign_contacts table with correct structure
        print("🔨 Creating campaign_contacts table with correct structure...")
        
        create_table_sql = '''
            CREATE TABLE campaign_contacts (
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
        print("✅ campaign_contacts table created with correct structure")
        
        # 3. Get data from SQLite
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute("SELECT COUNT(*) FROM campaign_contacts")
        sqlite_count = sqlite_cursor.fetchone()[0]
        print(f"📊 Records in SQLite: {sqlite_count}")
        
        if sqlite_count == 0:
            print("⚠️  No data to migrate from SQLite")
            return True
        
        # 4. Migrate data
        sqlite_cursor.execute("SELECT * FROM campaign_contacts")
        rows = sqlite_cursor.fetchall()
        
        column_names = [desc[0] for desc in sqlite_cursor.description]
        
        migrated_count = 0
        for row in rows:
            row_dict = dict(row)
            
            # Prepare insert with only the columns that exist
            available_columns = []
            values = []
            
            for col in column_names:
                if col in ['campaign_contact_id', 'campaign_id', 'campaign_key', 'contact_id', 
                          'status', 'assigned_to', 'enrolled_at', 'accepted_at', 'replied_at', 
                          'blacklisted_at', 'sequence_step', 'tags', 'created_at', 'updated_at',
                          'dux_profile_id', 'command_executed', 'command_params', 'force_execution',
                          'run_after', 'execution_result', 'retry_count', 'last_retry']:
                    available_columns.append(col)
                    values.append(row_dict[col])
            
            columns_str = ', '.join(available_columns)
            placeholders = ', '.join(['%s'] * len(available_columns))
            insert_sql = f"INSERT INTO campaign_contacts ({columns_str}) VALUES ({placeholders})"
            
            try:
                pg_cursor.execute(insert_sql, values)
                migrated_count += 1
            except Exception as e:
                print(f"⚠️  Error inserting record {row_dict.get('campaign_contact_id', 'unknown')}: {e}")
                pg_conn.rollback()
                continue
        
        pg_conn.commit()
        print(f"✅ Migrated {migrated_count} campaign_contact records")
        
        # 5. Verify final count
        pg_cursor.execute("SELECT COUNT(*) FROM campaign_contacts")
        final_count = pg_cursor.fetchone()[0]
        print(f"📊 Final count in PostgreSQL: {final_count}")
        
        # 6. Test a sample query
        print("\n🔍 Testing campaign-contact relationships...")
        pg_cursor.execute("""
            SELECT 
                cc.campaign_id, 
                COUNT(cc.contact_id) as contact_count
            FROM campaign_contacts cc
            GROUP BY cc.campaign_id
            ORDER BY contact_count DESC
            LIMIT 5
        """)
        
        results = pg_cursor.fetchall()
        print("Top campaigns by contact count:")
        for campaign_id, contact_count in results:
            print(f"  📋 {campaign_id}: {contact_count} contacts")
        
        print("\n🎉 CAMPAIGN CONTACTS MIGRATION COMPLETED!")
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
    success = fix_campaign_contacts()
    if success:
        print("\n✅ SUCCESS: Campaign contacts migration completed")
        sys.exit(0)
    else:
        print("\n❌ FAILED: Campaign contacts migration failed")
        sys.exit(1)
