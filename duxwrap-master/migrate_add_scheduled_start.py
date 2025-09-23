#!/usr/bin/env python3
"""
Migration Script: Add scheduled_start column to campaigns table
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
    """Get database connection from environment variables"""
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
    """Check if a column exists in a table"""
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

def add_scheduled_start_column():
    """Add scheduled_start column to campaigns table"""
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
        
        # Check if scheduled_start column already exists
        if check_column_exists(conn, 'campaigns', 'scheduled_start'):
            logger.info("✅ scheduled_start column already exists in campaigns table")
            return True
        
        # Add the scheduled_start column
        logger.info("🔄 Adding scheduled_start column to campaigns table...")
        cursor.execute("""
            ALTER TABLE campaigns 
            ADD COLUMN scheduled_start TIMESTAMP WITH TIME ZONE
        """)
        
        # Add a comment to document the column
        cursor.execute("""
            COMMENT ON COLUMN campaigns.scheduled_start IS 
            'Scheduled start date/time for the campaign. If NULL, campaign starts immediately.'
        """)
        
        conn.commit()
        logger.info("✅ Successfully added scheduled_start column to campaigns table")
        
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
        logger.error(f"❌ Error adding scheduled_start column: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def create_campaign_scheduler_index():
    """Create an index for efficient campaign scheduling queries"""
    conn = get_database_connection()
    
    try:
        cursor = conn.cursor()
        
        # Check if index already exists
        cursor.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'campaigns' AND indexname = 'idx_campaigns_scheduled_start'
        """)
        
        if cursor.fetchone():
            logger.info("✅ Index on scheduled_start already exists")
            return True
        
        # Create index for efficient scheduling queries
        logger.info("🔄 Creating index on scheduled_start column...")
        cursor.execute("""
            CREATE INDEX idx_campaigns_scheduled_start 
            ON campaigns (scheduled_start) 
            WHERE scheduled_start IS NOT NULL
        """)
        
        conn.commit()
        logger.info("✅ Successfully created index on scheduled_start column")
        return True
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error creating index: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def main():
    """Run the migration"""
    logger.info("🚀 Starting migration: Add scheduled_start to campaigns table")
    
    # Add the column
    if not add_scheduled_start_column():
        logger.error("❌ Migration failed")
        sys.exit(1)
    
    # Create the index
    if not create_campaign_scheduler_index():
        logger.warning("⚠️  Index creation failed, but column was added")
    
    logger.info("✅ Migration completed successfully!")
    logger.info("")
    logger.info("📋 Next steps:")
    logger.info("   1. Update your backend logic to use the scheduled_start field")
    logger.info("   2. Create a campaign scheduler service")
    logger.info("   3. Test campaign scheduling functionality")

if __name__ == "__main__":
    main() 