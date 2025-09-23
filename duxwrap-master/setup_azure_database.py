"""
Azure Database Setup Script

This script helps set up and configure Azure PostgreSQL Database
for Chaknal.
"""

import os
import sys
import logging
from azure_database import AzureDatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_connection_string():
    """Get database connection string from environment or user input"""
    
    # Check environment variables first
    connection_string = os.getenv('AZURE_POSTGRES_CONNECTION_STRING')
    
    if connection_string:
        logger.info("✅ Found connection string in environment variables")
        return connection_string
    
    # Prompt user for connection details
    print("\n" + "="*60)
    print("🔧 AZURE POSTGRESQL DATABASE SETUP")
    print("="*60)
    print("\nPlease provide your Azure PostgreSQL connection details:")
    
    server = input("Server name (e.g., your-server.postgres.database.azure.com): ").strip()
    database = input("Database name: ").strip()
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    port = input("Port (default 5432): ").strip() or "5432"
    
    # Build connection string
    connection_string = f"postgresql://{username}:{password}@{server}:{port}/{database}"
    
    # Save to environment file for future use
    save_connection_string(connection_string)
    
    return connection_string

def save_connection_string(connection_string: str):
    """Save connection string to .env file"""
    try:
        with open('.env', 'w') as f:
            f.write(f"AZURE_POSTGRES_CONNECTION_STRING={connection_string}\n")
        logger.info("✅ Connection string saved to .env file")
    except Exception as e:
        logger.warning(f"⚠️ Could not save connection string: {e}")

def test_connection(connection_string: str):
    """Test database connection"""
    try:
        logger.info("🔍 Testing database connection...")
        db_manager = AzureDatabaseManager(connection_string)
        
        # Test basic operations
        test_webhook = {
            "type": "test",
            "event": "connection_test",
            "userid": "setup_test",
            "timestamp": "2025-07-02T19:00:00Z",
            "data": {
                "test": True,
                "message": "Connection test successful"
            }
        }
        
        event_id = db_manager.store_webhook_event(test_webhook)
        logger.info(f"✅ Connection test successful! Event ID: {event_id}")
        
        # Clean up test data
        db_manager.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        return False

def create_sample_data(connection_string: str):
    """Create sample campaign and contact data"""
    try:
        logger.info("📝 Creating sample data...")
        db_manager = AzureDatabaseManager(connection_string)
        
        # Sample webhook events
        sample_events = [
            {
                "type": "visit",
                "event": "create",
                "userid": "117833704731893145427",
                "timestamp": "2025-07-02T19:22:30.449Z",
                "data": {
                    "Company": "LevelBlue",
                    "CompanyProfile": "https://www.linkedin.com/company/102069244/",
                    "CompanyWebsite": "http://www.levelblue.com/",
                    "Connections": "7256",
                    "Degree": "1",
                    "Email": "shannon@brewster.cloud",
                    "First Name": "Shannon",
                    "Last Name": "Brewster",
                    "Industry": "Computer and Network Security",
                    "Location": "United States",
                    "Profile": "https://www.linkedin.com/in/shannon-brewster/",
                    "ProfilePicture": "https://media.licdn.com/dms/image/C4E03AQH...",
                    "ProfileUrl": "https://www.linkedin.com/in/shannon-brewster/",
                    "Title": "Chief Executive Officer at LevelBlue"
                }
            },
            {
                "type": "message",
                "event": "received",
                "userid": "117833704731893145427",
                "timestamp": "2025-07-02T19:30:09.138Z",
                "data": {
                    "from": "https://www.linkedin.com/in/ACoAAFo0e68BEDr2GROQQH4fKCau2QmHFE0C2-Y",
                    "fromFirstName": "Sergio",
                    "fromId": "id.1513388975",
                    "fromLastName": "Campos",
                    "text": "testing messaging",
                    "timestamp": "2025-07-03T02:28:55.043Z",
                    "type": "MEMBER_TO_MEMBER",
                    "url": "https://www.linkedin.com/messaging/thread/2-NWI2MGVjZmItYWVjYS00NmJjLWFiOWYtYThmYzMwZWQyOTczXzEwMA==/",
                    "tags": [
                        "AMPED",
                        "🦆-default-followup-1",
                        "🦆-default-followup-2",
                        "🦆-default-followup-3",
                        "🦆-default-followup-4",
                        "🦆-default-followup-5",
                        "🦆-default-followup-6",
                        "🦆-default-followup-7",
                        "🦆-default-followup-8",
                        "🦆-testing a message sent -enrolled",
                        "testing a message sent",
                        "🦆-testing a message sent -accepted",
                        "🦆-Testing a message sent -followup-1"
                    ]
                }
            }
        ]
        
        # Store sample events
        for event in sample_events:
            event_id = db_manager.store_webhook_event(event)
            logger.info(f"✅ Stored sample event: {event_id}")
        
        db_manager.close()
        logger.info("✅ Sample data created successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to create sample data: {e}")

def main():
    """Main setup function"""
    print("\n🚀 CHAKNAL - AZURE DATABASE SETUP")
    print("="*60)
    
    # Check if psycopg2 is installed
    try:
        import psycopg2
    except ImportError:
        print("❌ psycopg2 is not installed. Please install it first:")
        print("   pip install psycopg2-binary")
        sys.exit(1)
    
    # Get connection string
    connection_string = get_connection_string()
    
    # Test connection
    if not test_connection(connection_string):
        print("\n❌ Database connection failed. Please check your credentials.")
        sys.exit(1)
    
    # Create sample data
    create_sample = input("\nWould you like to create sample data? (y/n): ").strip().lower()
    if create_sample == 'y':
        create_sample_data(connection_string)
    
    print("\n" + "="*60)
    print("✅ AZURE DATABASE SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Your database is ready to receive webhook data")
    print("2. Update your webhook_data_collector.py to use this database")
    print("3. Start your LinkedIn campaigns")
    print("4. Monitor data via the database queries")
    print("\nConnection string saved to .env file for future use.")
    print("="*60)

if __name__ == "__main__":
    main() 