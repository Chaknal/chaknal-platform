# Azure Deployment Guide for Chaknal

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements_azure.txt
```

### 2. Set Up Azure PostgreSQL Database

#### Option A: Azure Portal (Recommended)
1. Go to [Azure Portal](https://portal.azure.com)
2. Create a new **Azure Database for PostgreSQL - Flexible Server**
3. Choose your region and resource group
4. Set server name (e.g., `linkedin-automation-db`)
5. Set admin username and password
6. Create database (e.g., `linkedin_automation`)
7. Note down the connection details

#### Option B: Azure CLI
```bash
# Create resource group
az group create --name linkedin-automation-rg --location eastus

# Create PostgreSQL server
az postgres flexible-server create \
  --resource-group linkedin-automation-rg \
  --name linkedin-automation-db \
  --admin-user linkedinadmin \
  --admin-password "YourSecurePassword123!" \
  --sku-name Standard_B1ms \
  --version 14 \
  --storage-size 32

# Create database
az postgres flexible-server db create \
  --resource-group linkedin-automation-rg \
  --server-name linkedin-automation-db \
  --database-name linkedin_automation
```

### 3. Configure Database Connection
```bash
python setup_azure_database.py
```

Follow the prompts to enter your Azure PostgreSQL connection details.

### 4. Test the Setup
```bash
python test_database_integration.py
```

## 📊 Database Schema

The platform creates these tables automatically:

### Core Tables
- **`campaigns`** - Campaign management and metadata
- **`contacts`** - LinkedIn contact profiles and data
- **`campaign_contacts`** - Many-to-many relationship with status tracking
- **`messages`** - Complete message history for Slack integration
- **`webhook_events`** - Raw webhook data from Dux-Soup

### Key Features
- **UUID Primary Keys** for scalability
- **JSONB Fields** for flexible data storage
- **Array Fields** for tags and sequences
- **Automatic Timestamps** for audit trails
- **Foreign Key Constraints** for data integrity

## 🔧 Configuration

### Environment Variables
Create a `.env` file:
```env
AZURE_POSTGRES_CONNECTION_STRING=postgresql://username:password@server.postgres.database.azure.com:5432/database
DUX_SOUP_WEBHOOK_URL=https://your-ngrok-url.ngrok-free.app/webhook
```

### Webhook Configuration
1. Update your Dux-Soup webhook URL to point to your server
2. Ensure HTTPS is enabled (use ngrok for development)
3. Test webhook reception

## 📈 Scaling Considerations

### Database Scaling
- **Vertical Scaling**: Increase compute and memory
- **Horizontal Scaling**: Add read replicas
- **Connection Pooling**: Already implemented in the code

### Application Scaling
- **Webhook Server**: Deploy to Azure App Service
- **Background Processing**: Use Azure Functions
- **File Storage**: Azure Blob Storage for attachments

## 🔒 Security Best Practices

### Database Security
1. **Enable SSL**: Azure PostgreSQL enforces SSL by default
2. **Firewall Rules**: Restrict access to your application IPs
3. **Connection Pooling**: Prevents connection exhaustion
4. **Environment Variables**: Never hardcode credentials

### Application Security
1. **Input Validation**: Validate all webhook data
2. **Rate Limiting**: Implement webhook rate limiting
3. **Logging**: Monitor for suspicious activity
4. **Backup**: Enable automated backups

## 🚀 Production Deployment

### Option 1: Azure App Service
```bash
# Deploy webhook server to Azure App Service
az webapp up --name linkedin-webhook-server --resource-group linkedin-automation-rg
```

### Option 2: Azure Container Instances
```bash
# Build and deploy Docker container
docker build -t linkedin-automation .
az container create --resource-group linkedin-automation-rg --name linkedin-automation --image linkedin-automation
```

### Option 3: Azure Functions
- Convert webhook handler to Azure Function
- Use Event Grid for real-time processing
- Scale automatically based on demand

## 📊 Monitoring and Analytics

### Database Monitoring
- **Azure Monitor**: Track database performance
- **Query Performance**: Monitor slow queries
- **Connection Metrics**: Track connection usage

### Application Monitoring
- **Application Insights**: Monitor webhook processing
- **Custom Metrics**: Track campaign performance
- **Alerting**: Set up alerts for failures

## 🔄 Schema Modifications

The database is designed to be flexible. You can modify the schema:

### Adding New Fields
```sql
-- Add new column to existing table
ALTER TABLE campaigns ADD COLUMN target_industry VARCHAR(255);

-- Add new table
CREATE TABLE campaign_sequences (
    sequence_id UUID PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(campaign_id),
    step_order INTEGER NOT NULL,
    message_template TEXT,
    delay_days INTEGER DEFAULT 0
);
```

### Data Migration
```python
# Use the AzureDatabaseManager for safe migrations
db_manager = AzureDatabaseManager(connection_string)
# Add migration logic here
```

## 🆘 Troubleshooting

### Common Issues

#### Connection Errors
```bash
# Test connection
python -c "from azure_database import AzureDatabaseManager; AzureDatabaseManager('your_connection_string')"
```

#### Webhook Not Receiving Data
1. Check ngrok tunnel is active
2. Verify webhook URL in Dux-Soup
3. Check server logs for errors
4. Test webhook endpoint manually

#### Database Performance
1. Monitor connection pool usage
2. Check for slow queries
3. Consider adding indexes
4. Scale database if needed

## 📞 Support

For issues with:
- **Azure Setup**: Check Azure documentation
- **Database Issues**: Review PostgreSQL logs
- **Webhook Problems**: Check server logs
- **Schema Changes**: Test in development first

## 🔮 Future Enhancements

### Planned Features
- **Real-time Dashboard**: WebSocket connections for live updates
- **Advanced Analytics**: Machine learning for campaign optimization
- **Multi-tenant Support**: Database partitioning for multiple clients
- **API Gateway**: Azure API Management for external access

### Integration Options
- **Slack Bot**: Real-time notifications and replies
- **CRM Integration**: Salesforce, HubSpot connectors
- **Email Marketing**: Mailchimp, ConvertKit integration
- **Analytics**: Power BI, Tableau dashboards 