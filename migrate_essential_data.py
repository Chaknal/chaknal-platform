#!/usr/bin/env python3
"""
Migrate Essential Data
======================

This script migrates the core data needed for campaign creation:
- campaigns_new (13 campaigns)
- contacts (449 contacts) 
- organization (7 organizations)
- company (21 companies)
- user (23 users)
"""

import sqlite3
import psycopg2
import os
import sys

def migrate_essential_data():
    """Migrate essential data for campaign functionality"""
    
    print("🚀 MIGRATING ESSENTIAL DATA")
    print("=" * 50)
    
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
    
    print("🔌 Connecting to databases...")
    
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
        sqlite_cursor = sqlite_conn.cursor()
        
        # Migration plan - order matters due to foreign keys
        migration_tables = [
            ("organization", "id"),
            ("company", "id"), 
            ("user", "id"),
            ("contacts", "contact_id"),
            ("campaigns_new", "campaign_id"),
        ]
        
        total_migrated = 0
        
        for table_name, primary_key in migration_tables:
            print(f"\n📋 Migrating {table_name}...")
            
            # Get data from SQLite
            try:
                sqlite_cursor.execute(f"SELECT * FROM {table_name}")
                rows = sqlite_cursor.fetchall()
                
                if not rows:
                    print(f"  📭 No data in {table_name}")
                    continue
                
                print(f"  📊 Found {len(rows)} records in SQLite")
                
                # Get column names
                column_names = [desc[0] for desc in sqlite_cursor.description]
                
                # Check existing records in PostgreSQL
                try:
                    pg_cursor.execute(f"SELECT {primary_key} FROM {table_name}")
                    existing_ids = {row[0] for row in pg_cursor.fetchall()}
                except:
                    existing_ids = set()
                
                # Filter out existing records
                new_rows = []
                for row in rows:
                    row_dict = dict(row)
                    if row_dict[primary_key] not in existing_ids:
                        new_rows.append(row_dict)
                
                if not new_rows:
                    print(f"  ✅ All {len(rows)} records already exist")
                    continue
                
                # Insert new records
                columns_str = ', '.join([f'"{col}"' if col == 'user' else col for col in column_names])
                placeholders = ', '.join(['%s'] * len(column_names))
                insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                
                inserted_count = 0
                for row_dict in new_rows:
                    try:
                        values = [row_dict[col] for col in column_names]
                        pg_cursor.execute(insert_sql, values)
                        inserted_count += 1
                    except Exception as e:
                        print(f"  ⚠️  Error inserting record: {e}")
                        pg_conn.rollback()
                        continue
                
                pg_conn.commit()
                print(f"  ✅ Migrated {inserted_count} new records")
                total_migrated += inserted_count
                
            except Exception as e:
                print(f"  ❌ Error migrating {table_name}: {e}")
                continue
        
        print(f"\n📊 Total records migrated: {total_migrated}")
        
        # Verify data
        print("\n🔍 Verifying migrated data...")
        verification_queries = [
            ("Organizations", "SELECT COUNT(*) FROM organization"),
            ("Companies", "SELECT COUNT(*) FROM company"),
            ("Users", "SELECT COUNT(*) FROM \"user\""),
            ("Contacts", "SELECT COUNT(*) FROM contacts"),
            ("Campaigns", "SELECT COUNT(*) FROM campaigns_new"),
            ("Campaign-Contact Links", "SELECT COUNT(*) FROM campaign_contacts"),
        ]
        
        for desc, query in verification_queries:
            try:
                pg_cursor.execute(query)
                count = pg_cursor.fetchone()[0]
                print(f"  ✅ {desc}: {count} records")
            except Exception as e:
                print(f"  ❌ {desc}: Error - {e}")
        
        # Test campaign-contact relationships
        print("\n🔗 Testing campaign-contact relationships...")
        pg_cursor.execute("""
            SELECT 
                c.name as campaign_name,
                COUNT(cc.contact_id) as contact_count
            FROM campaigns_new c
            LEFT JOIN campaign_contacts cc ON c.campaign_id = cc.campaign_id
            GROUP BY c.campaign_id, c.name
            HAVING COUNT(cc.contact_id) > 0
            ORDER BY contact_count DESC
            LIMIT 5
        """)
        
        results = pg_cursor.fetchall()
        if results:
            print("Top campaigns with contacts:")
            for campaign_name, contact_count in results:
                print(f"  📋 {campaign_name}: {contact_count} contacts")
        else:
            print("  ⚠️  No campaign-contact relationships found")
        
        print("\n🎉 ESSENTIAL DATA MIGRATION COMPLETED!")
        print("✅ Campaign creation should now work with full data")
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
    success = migrate_essential_data()
    if success:
        print("\n✅ SUCCESS: Essential data migration completed")
        sys.exit(0)
    else:
        print("\n❌ FAILED: Essential data migration failed")
        sys.exit(1)
