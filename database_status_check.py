#!/usr/bin/env python3
"""
Database Status Check
====================

This script checks the current state of both SQLite and PostgreSQL databases
to understand what needs to be migrated.
"""

import sqlite3
import psycopg2
import os
import sys
from tabulate import tabulate


def check_database_status():
    """Check the status of both databases"""
    
    print("📊 Database Status Check")
    print("=" * 50)
    
    # SQLite connection
    sqlite_path = "chaknal.db"
    if not os.path.exists(sqlite_path):
        print(f"❌ SQLite database not found: {sqlite_path}")
        return
    
    sqlite_conn = sqlite3.connect(sqlite_path)
    
    # PostgreSQL connection
    pg_config = {
        'host': 'chaknal-db-server.postgres.database.azure.com',
        'database': 'chaknal_platform',
        'user': 'chaknaladmin',
        'password': os.getenv('POSTGRES_PASSWORD'),
        'port': 5432,
        'sslmode': 'require'
    }
    
    if not pg_config['password']:
        print("⚠️  POSTGRES_PASSWORD not set. Please set it to check PostgreSQL status.")
        pg_conn = None
    else:
        try:
            pg_conn = psycopg2.connect(**pg_config)
            print("✅ Connected to both databases")
        except Exception as e:
            print(f"❌ Failed to connect to PostgreSQL: {e}")
            pg_conn = None
    
    # Get SQLite table info
    print("\n📋 SQLite Database (Local):")
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    sqlite_tables = [row[0] for row in sqlite_cursor.fetchall()]
    
    sqlite_data = []
    for table in sorted(sqlite_tables):
        sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = sqlite_cursor.fetchone()[0]
        sqlite_data.append([table, count, "✅" if count > 0 else "📭"])
    
    print(tabulate(sqlite_data, headers=["Table", "Rows", "Status"], tablefmt="grid"))
    print(f"Total SQLite tables: {len(sqlite_tables)}")
    
    # Get PostgreSQL table info
    if pg_conn:
        print("\n📋 PostgreSQL Database (Azure):")
        pg_cursor = pg_conn.cursor()
        
        # Get all tables
        pg_cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        pg_tables = [row[0] for row in pg_cursor.fetchall()]
        
        pg_data = []
        for table in pg_tables:
            try:
                pg_cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
                count = pg_cursor.fetchone()[0]
                status = "✅" if count > 0 else "📭"
                exists_in_sqlite = "🔄" if table in sqlite_tables else "🆕"
                pg_data.append([table, count, status, exists_in_sqlite])
            except Exception as e:
                pg_data.append([table, "ERROR", "❌", ""])
        
        print(tabulate(pg_data, headers=["Table", "Rows", "Status", "In SQLite"], tablefmt="grid"))
        print(f"Total PostgreSQL tables: {len(pg_tables)}")
        
        # Compare tables
        print("\n🔍 Migration Analysis:")
        missing_in_pg = set(sqlite_tables) - set(pg_tables)
        only_in_pg = set(pg_tables) - set(sqlite_tables)
        
        if missing_in_pg:
            print(f"\n❌ Missing in PostgreSQL ({len(missing_in_pg)} tables):")
            for table in sorted(missing_in_pg):
                sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = sqlite_cursor.fetchone()[0]
                importance = "🚨 CRITICAL" if table == "campaign_contacts" else "⚠️  Important" if count > 0 else "📭 Empty"
                print(f"  - {table}: {count} rows ({importance})")
        
        if only_in_pg:
            print(f"\n🆕 Only in PostgreSQL ({len(only_in_pg)} tables):")
            for table in sorted(only_in_pg):
                print(f"  - {table}")
        
        # Check critical relationships
        print("\n🔗 Critical Relationship Check:")
        critical_checks = [
            ("campaigns_new", "campaign_id", "Campaigns"),
            ("contacts", "contact_id", "Contacts"), 
            ("campaign_contacts", "campaign_contact_id", "Campaign-Contact Links"),
            ("duxsoup_user", "id", "DuxSoup Users"),
            ("user", "id", "Users"),
        ]
        
        for table, pk, description in critical_checks:
            sqlite_count = 0
            pg_count = 0
            
            # SQLite count
            try:
                sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                sqlite_count = sqlite_cursor.fetchone()[0]
            except:
                sqlite_count = 0
            
            # PostgreSQL count
            try:
                pg_cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
                pg_count = pg_cursor.fetchone()[0]
            except:
                pg_count = 0
            
            status = "✅" if pg_count >= sqlite_count else "❌" if pg_count == 0 else "⚠️"
            print(f"  {status} {description}: SQLite={sqlite_count}, PostgreSQL={pg_count}")
        
        pg_conn.close()
    
    sqlite_conn.close()
    
    print("\n🎯 Recommendations:")
    if pg_conn:
        if "campaign_contacts" not in pg_tables:
            print("🚨 URGENT: Run critical_campaign_contacts_migration.py immediately!")
            print("   Campaign creation is broken without this table.")
        print("📋 Run complete_database_migration.py for full migration")
    else:
        print("🔑 Set POSTGRES_PASSWORD to check Azure database status")
    
    print("🧪 Test campaign creation after migration at: https://app.chaknal.com")


if __name__ == "__main__":
    check_database_status()
