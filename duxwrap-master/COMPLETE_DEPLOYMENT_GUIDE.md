# Complete Deployment Guide for Dux-Soup LinkedIn Automation Platform

## 🚀 Overview

This guide provides everything you need to deploy the Dux-Soup LinkedIn automation platform to any environment. The platform includes a comprehensive database schema and Python application that handles all Dux-Soup webhook events for LinkedIn automation campaigns.

## 📁 Files Included

### Core Database Files
- **`complete_database_schema.sql`** - Complete PostgreSQL schema with all tables, indexes, and logic
- **`complete_database_manager.py`** - Python database manager with all webhook processing logic

### Supporting Files
- **`azure_database.py`** - Original Azure-specific database manager (for reference)
- **`setup_azure_database.py`** - Azure database setup script
- **`requirements_azure.txt`** - Python dependencies

## 🗄️ Database Schema Overview

The platform uses a PostgreSQL database with the following core tables:

### 1. **campaigns** - Campaign Management
- Stores LinkedIn automation campaigns
- Includes scheduling, targeting, and status tracking
- Uses UUID primary keys and campaign_key for API access

### 2. **contacts** - LinkedIn Contact Profiles
- Extracted from Dux-Soup webhook data
- Stores comprehensive profile information
- Links to LinkedIn profiles via linkedin_id

### 3. **campaign_contacts** - Campaign-Contact Relationships
- Junction table linking contacts to campaigns
- Tracks engagement status (enrolled, accepted, replied, blacklisted)
- Manages messaging sequences and tags

### 4. **messages** - Message History
- Complete conversation tracking
- Stores both sent and received messages
- Links to campaign_contacts for context

### 5. **webhook_events** - Raw Webhook Data
- Stores all incoming Dux-Soup webhook events
- Preserves complete raw data for processing
- Tracks processing status

## 🔧 Deployment Steps

### Step 1: Set Up PostgreSQL Database

#### Option A: Local PostgreSQL
```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres createdb linkedin_automation
sudo -u postgres createuser linkedin_user
sudo -u postgres psql -c "ALTER USER linkedin_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE linkedin_automation TO linkedin_user;"
```

#### Option B: Cloud PostgreSQL (Azure, AWS, GCP)
```bash
# Azure PostgreSQL example
az postgres flexible-server create \
  --resource-group your-rg \
  --name linkedin-automation-db \
  --admin-user linkedinadmin \
  --admin-password "YourSecurePassword123!" \
  --sku-name Standard_B1ms \
  --version 14 \
  --storage-size 32

az postgres flexible-server db create \
  --resource-group your-rg \
  --server-name linkedin-automation-db \
  --database-name linkedin_automation
```

### Step 2: Create Database Schema

```bash
# Connect to your database and run the schema
psql -h your-host -U your-user -d linkedin_automation -f complete_database_schema.sql
```

Or using Python:
```python
import psycopg2

# Read and execute schema
with open('complete_database_schema.sql', 'r') as f:
    schema_sql = f.read()

conn = psycopg2.connect("postgresql://user:password@host:port/database")
cur = conn.cursor()
cur.execute(schema_sql)
conn.commit()
conn.close()
```

### Step 3: Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements_azure.txt

# Additional dependencies for complete deployment
pip install psycopg2-binary python-dotenv flask
```

### Step 4: Configure Environment Variables

Create a `.env` file:
```env
# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database
AZURE_POSTGRES_CONNECTION_STRING=postgresql://user:password@host:port/database

# Dux-Soup Configuration
DUX_SOUP_WEBHOOK_SECRET=your_webhook_secret
DUX_SOUP_USER_ID=your_dux_user_id

# Application Configuration
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5000
```

### Step 5: Deploy the Application

#### Option A: Direct Python Deployment
```python
# app.py
from flask import Flask, request, jsonify
from complete_database_manager import CompleteDatabaseManager
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
db = CompleteDatabaseManager(os.getenv('DATABASE_URL'))

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Dux-Soup webhook events"""
    try:
        webhook_data = request.json
        event_id = db.store_webhook_event(webhook_data)
        return jsonify({"status": "success", "event_id": event_id}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/campaigns', methods=['GET'])
def get_campaigns():
    """Get active campaigns"""
    try:
        campaigns = db.get_active_campaigns()
        return jsonify(campaigns), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
```

#### Option B: Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements_azure.txt .
RUN pip install -r requirements_azure.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/linkedin_automation
    depends_on:
      - db
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=linkedin_automation
      - POSTGRES_USER=linkedin_user
      - POSTGRES_PASSWORD=your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./complete_database_schema.sql:/docker-entrypoint-initdb.d/schema.sql

volumes:
  postgres_data:
```

### Step 6: Configure Dux-Soup Webhook

1. Log into your Dux-Soup account
2. Go to Settings > Webhooks
3. Add your webhook URL: `https://your-domain.com/webhook`
4. Select all event types: message, visit, action, rccommand
5. Save the webhook configuration

## 🔍 Testing the Deployment

### Test Database Connection
```python
from complete_database_manager import CompleteDatabaseManager
import os

db = CompleteDatabaseManager(os.getenv('DATABASE_URL'))
print("✅ Database connection successful")

# Test webhook event storage
test_webhook = {
    "type": "message",
    "event": "received",
    "profile": "https://www.linkedin.com/in/test-user/",
    "userid": "test_user_123",
    "data": {
        "from": "https://www.linkedin.com/in/test-user/",
        "message": "Test message",
        "timestamp": 1751508398903
    },
    "timestamp": 1751508398903
}

event_id = db.store_webhook_event(test_webhook)
print(f"✅ Webhook event stored: {event_id}")
```

### Test Webhook Endpoint
```bash
# Send test webhook
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "type": "message",
    "event": "received",
    "profile": "https://www.linkedin.com/in/test-user/",
    "userid": "test_user_123",
    "data": {
      "from": "https://www.linkedin.com/in/test-user/",
      "message": "Test message",
      "timestamp": 1751508398903
    },
    "timestamp": 1751508398903
  }'
```

## 📊 Monitoring and Analytics

### Database Queries for Insights

```sql
-- Get campaign performance
SELECT 
    c.name,
    COUNT(cc.contact_id) as total_contacts,
    COUNT(CASE WHEN cc.status = 'accepted' THEN 1 END) as accepted_count,
    COUNT(CASE WHEN cc.status = 'replied' THEN 1 END) as replied_count,
    ROUND(COUNT(CASE WHEN cc.status = 'replied' THEN 1 END) * 100.0 / COUNT(cc.contact_id), 2) as reply_rate
FROM campaigns c
LEFT JOIN campaign_contacts cc ON c.campaign_id = cc.campaign_id
GROUP BY c.campaign_id, c.name;

-- Get recent webhook events
SELECT 
    event_type,
    event_name,
    COUNT(*) as count,
    MAX(created_at) as latest_event
FROM webhook_events
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY event_type, event_name
ORDER BY count DESC;

-- Get contacts who replied
SELECT 
    c.first_name,
    c.last_name,
    c.company,
    cc.replied_at,
    m.message_text as last_reply
FROM contacts c
JOIN campaign_contacts cc ON c.contact_id = cc.contact_id
LEFT JOIN messages m ON cc.campaign_contact_id = m.campaign_contact_id
WHERE cc.status = 'replied'
AND m.direction = 'received'
ORDER BY cc.replied_at DESC;
```

### Python Analytics
```python
# Get campaign statistics
stats = db.get_campaign_stats(campaign_id)
print(f"Campaign: {stats['name']}")
print(f"Total contacts: {stats['total_contacts']}")
print(f"Accepted: {stats['accepted_count']}")
print(f"Replied: {stats['replied_count']}")

# Get contacts who replied
replied_contacts = db.get_contacts_who_replied(campaign_id)
for contact in replied_contacts:
    print(f"{contact['first_name']} {contact['last_name']} from {contact['company']}")

# Get recent webhook events
recent_events = db.get_recent_webhook_events(hours=24)
for event in recent_events:
    print(f"{event['event_type']}: {event['event_name']} - {event['created_at']}")
```

## 🔧 Advanced Configuration

### Custom Campaign Settings
```python
# Create campaign with custom settings
campaign_id = db.create_campaign(
    name="Q1 Cybersecurity Outreach",
    dux_user_id="your_user_id",
    description="Targeting CISOs for partnership discussions",
    target_title="Chief Information Security Officer",
    settings={
        "message_templates": [
            "Hi {first_name}, I noticed your work at {company}...",
            "Thanks for connecting! I'd love to discuss..."
        ],
        "delay_between_messages": 2,  # days
        "max_messages_per_contact": 3,
        "auto_follow_up": True
    }
)
```

### Message Processing
```python
# Store a message
message_id = db.store_message(
    campaign_contact_id=campaign_contact_id,
    direction="sent",
    message_text="Hi John, thanks for connecting!",
    sent_at=datetime.now(),
    tags=["initial_connection"]
)

# Update contact status when they reply
if webhook_data["type"] == "message" and webhook_data["event"] == "received":
    # Update campaign contact status to replied
    # This logic would be in your webhook processing
    pass
```

## 🚨 Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Test connection
psql -h your-host -U your-user -d your-database -c "SELECT 1;"

# Check if tables exist
psql -h your-host -U your-user -d your-database -c "\dt"
```

#### Webhook Not Receiving Data
1. Check webhook URL is accessible
2. Verify Dux-Soup webhook configuration
3. Check application logs for errors
4. Test webhook endpoint manually

#### Performance Issues
1. Monitor database indexes
2. Check connection pool usage
3. Consider database scaling
4. Optimize queries for large datasets

### Logging and Debugging
```python
import logging

# Enable detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Test database operations with logging
db = CompleteDatabaseManager(connection_string)
logger = logging.getLogger(__name__)

try:
    event_id = db.store_webhook_event(webhook_data)
    logger.info(f"Webhook stored successfully: {event_id}")
except Exception as e:
    logger.error(f"Failed to store webhook: {e}")
```

## 🔄 Migration and Updates

### Schema Updates
```sql
-- Add new columns
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS new_feature JSONB;

-- Add new indexes
CREATE INDEX IF NOT EXISTS idx_new_feature ON campaigns USING GIN (new_feature);

-- Update existing data
UPDATE campaigns SET new_feature = '{}' WHERE new_feature IS NULL;
```

### Data Migration
```python
# Migrate data between environments
def migrate_campaigns(source_db, target_db):
    campaigns = source_db.get_active_campaigns()
    for campaign in campaigns:
        target_db.create_campaign(
            name=campaign['name'],
            dux_user_id=campaign['dux_user_id'],
            description=campaign['description'],
            # ... other fields
        )
```

## 📈 Scaling Considerations

### Database Scaling
- Use read replicas for analytics queries
- Implement connection pooling
- Consider database partitioning for large datasets
- Monitor and optimize slow queries

### Application Scaling
- Use load balancers for multiple instances
- Implement caching for frequently accessed data
- Consider microservices architecture for large deployments
- Use message queues for webhook processing

## 🔐 Security Best Practices

### Database Security
- Use strong passwords and encrypted connections
- Implement row-level security (RLS)
- Regular security updates
- Backup and disaster recovery

### Application Security
- Validate all webhook data
- Implement rate limiting
- Use HTTPS for all communications
- Regular security audits

## 📞 Support and Maintenance

### Regular Maintenance Tasks
1. **Database backups** - Daily automated backups
2. **Log rotation** - Manage application and database logs
3. **Performance monitoring** - Track query performance and resource usage
4. **Security updates** - Keep dependencies updated
5. **Data cleanup** - Archive old webhook events and messages

### Monitoring Setup
```python
# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Test database connection
        db.get_active_campaigns()
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500
```

---

## 🎯 Quick Start Checklist

- [ ] Set up PostgreSQL database
- [ ] Run `complete_database_schema.sql`
- [ ] Install Python dependencies
- [ ] Configure environment variables
- [ ] Deploy application
- [ ] Configure Dux-Soup webhook
- [ ] Test webhook endpoint
- [ ] Monitor application logs
- [ ] Set up monitoring and alerts

This deployment guide provides everything needed to successfully deploy and operate the Dux-Soup LinkedIn automation platform in any environment. The complete database schema and Python manager handle all the complexity of webhook processing and campaign management. 