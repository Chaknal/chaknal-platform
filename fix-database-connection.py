#!/usr/bin/env python3

"""
Quick database connection test and fix script
This will help identify and fix the database connection issue
"""

import asyncio
import asyncpg
import sys
from urllib.parse import urlparse

# Database URL from app-settings.json
DATABASE_URL = "postgresql+asyncpg://chaknaladmin:Chaknal2024!@chaknal-db-server.postgres.database.azure.com/chaknal_platform"

def parse_database_url(url):
    """Parse the database URL to extract connection parameters"""
    # Convert SQLAlchemy URL to asyncpg format
    url = url.replace("postgresql+asyncpg://", "postgresql://")
    parsed = urlparse(url)
    
    return {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'database': parsed.path.lstrip('/'),
        'user': parsed.username,
        'password': parsed.password
    }

async def test_database_connection():
    """Test the database connection with proper timeout settings"""
    print("🔍 Testing database connection...")
    
    try:
        # Parse connection parameters
        conn_params = parse_database_url(DATABASE_URL)
        print(f"📍 Connecting to: {conn_params['host']}:{conn_params['port']}/{conn_params['database']}")
        print(f"👤 User: {conn_params['user']}")
        
        # Test connection with timeout
        conn = await asyncio.wait_for(
            asyncpg.connect(
                host=conn_params['host'],
                port=conn_params['port'],
                database=conn_params['database'],
                user=conn_params['user'],
                password=conn_params['password'],
                ssl='require',  # Azure PostgreSQL requires SSL
                command_timeout=10  # 10 second timeout
            ),
            timeout=15  # 15 second overall timeout
        )
        
        print("✅ Database connection successful!")
        
        # Test a simple query
        result = await conn.fetchval("SELECT COUNT(*) FROM campaigns")
        print(f"📊 Campaigns in database: {result}")
        
        # Test another query
        result = await conn.fetchval("SELECT COUNT(*) FROM contacts")
        print(f"📊 Contacts in database: {result}")
        
        await conn.close()
        print("✅ Database test completed successfully!")
        return True
        
    except asyncio.TimeoutError:
        print("❌ Database connection timed out!")
        print("💡 This suggests the database server is not responding or network issues")
        return False
    except asyncpg.exceptions.InvalidPasswordError:
        print("❌ Invalid database password!")
        return False
    except asyncpg.exceptions.ConnectionDoesNotExistError:
        print("❌ Database does not exist!")
        return False
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def main():
    print("🚀 Chaknal Platform Database Connection Test")
    print("=" * 50)
    
    success = await test_database_connection()
    
    if success:
        print("\n✅ Database connection is working!")
        print("💡 The issue might be in the FastAPI app configuration")
    else:
        print("\n❌ Database connection failed!")
        print("💡 Need to fix database connection settings")
    
    print("\n🔧 Next steps:")
    print("1. Check if the database server is accessible")
    print("2. Verify the connection string format")
    print("3. Check Azure firewall rules")
    print("4. Update FastAPI database configuration")

if __name__ == "__main__":
    asyncio.run(main())
