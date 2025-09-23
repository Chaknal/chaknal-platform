#!/usr/bin/env python3
"""
Migration Script: Add end_date column to campaigns table
"""

import os
import sys
import psycopg2
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_database_connection():
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL not found in environment variables")
        sys.exit(1)
    try:
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        sys.exit(1)

def check_column_exists(conn, table_name, column_name):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s AND column_name = %s
        """, (table_name, column_name))
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    except Exception as e:
        logger.error(f"Error checking column existence: {e}")
        return False

def add_end_date_column():
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        # Check if campaigns table exists
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'campaigns'
        """)
        if not cursor.fetchone():
            logger.error("Campaigns table does not exist. Please run setup_azure_auto.py first.")
            return False
        # Check if end_date column already exists
        if check_column_exists(conn, 'campaigns', 'end_date'):
            logger.info("✅ end_date column already exists in campaigns table")
            return True
        # Add the end_date column
        logger.info("🔄 Adding end_date column to campaigns table...")
        cursor.execute("""
            ALTER TABLE campaigns 
            ADD COLUMN end_date TIMESTAMP WITH TIME ZONE
        """)
        # Add a comment to document the column
        cursor.execute("""
            COMMENT ON COLUMN campaigns.end_date IS 
            'Scheduled end date/time for the campaign. If NULL, campaign never ends.'
        """)
        conn.commit()
        logger.info("✅ Successfully added end_date column to campaigns table")
        # Show the updated table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'campaigns' 
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        logger.info("📋 Updated campaigns table structure:")
        for col in columns:
            logger.info(f"   - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error adding end_date column: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def main():
    logger.info("🚀 Starting migration: Add end_date to campaigns table")
    if not add_end_date_column():
        logger.error("❌ Migration failed")
        sys.exit(1)
    logger.info("✅ Migration completed successfully!")
    logger.info("")
    logger.info("📋 Next steps:")
    logger.info("   1. Update your backend logic to use the end_date field")
    logger.info("   2. Test campaign scheduling end functionality")

if __name__ == "__main__":
    main() 