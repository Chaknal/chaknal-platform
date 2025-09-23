# Azure Deployment Guide - Chaknal Platform

## 🎯 Overview
This guide walks through deploying the Chaknal Platform to Azure with GitHub Actions CI/CD.

## 📋 Prerequisites
- Azure subscription
- GitHub account
- Azure CLI installed locally
- Git configured locally

## 🏗️ Azure Resources Required

### 1. Resource Group
```bash
az group create --name chaknal-platform --location "East US"
```

### 2. App Service Plan
```bash
az appservice plan create \
  --name chaknal-platform-plan \
  --resource-group chaknal-platform \
  --sku B1 \
  --is-linux
```

### 3. Backend App Service (Python)
```bash
az webapp create \
  --resource-group chaknal-platform \
  --plan chaknal-platform-plan \
  --name chaknal-backend \
  --runtime "PYTHON|3.9" \
  --deployment-source-url https://github.com/sercio1/chaknal-platform.git \
  --deployment-source-branch main
```

### 4. Frontend App Service (Node.js)
```bash
az webapp create \
  --resource-group chaknal-platform \
  --plan chaknal-platform-plan \
  --name chaknal-frontend \
  --runtime "NODE|16-lts" \
  --deployment-source-url https://github.com/sercio1/chaknal-platform.git \
  --deployment-source-branch main
```

### 5. PostgreSQL Database
```bash
az postgres server create \
  --resource-group chaknal-platform \
  --name chaknal-db-server \
  --location "East US" \
  --admin-user chaknaladmin \
  --admin-password "YourSecurePassword123!" \
  --sku-name GP_Gen5_1 \
  --version 11

az postgres db create \
  --resource-group chaknal-platform \
  --server-name chaknal-db-server \
  --name chaknal_platform
```

### 6. Storage Account
```bash
az storage account create \
  --name chaknalstorage \
  --resource-group chaknal-platform \
  --location "East US" \
  --sku Standard_LRS
```

### 7. Key Vault
```bash
az keyvault create \
  --name chaknal-keyvault \
  --resource-group chaknal-platform \
  --location "East US"
```

## 🔐 Environment Variables

### Backend App Service Configuration
```bash
# Database
az webapp config appsettings set \
  --resource-group chaknal-platform \
  --name chaknal-backend \
  --settings DATABASE_URL="postgresql://chaknaladmin:YourSecurePassword123!@chaknal-db-server.postgres.database.azure.com:5432/chaknal_platform"

# JWT Secret
az webapp config appsettings set \
  --resource-group chaknal-platform \
  --name chaknal-backend \
  --settings JWT_SECRET_KEY="your-super-secure-jwt-secret-key-here"

# CORS Origins
az webapp config appsettings set \
  --resource-group chaknal-platform \
  --name chaknal-backend \
  --settings CORS_ORIGINS="https://chaknal-frontend.azurewebsites.net"

# Azure Storage
az webapp config appsettings set \
  --resource-group chaknal-platform \
  --name chaknal-backend \
  --settings AZURE_STORAGE_CONNECTION_STRING="your-storage-connection-string"
```

### Frontend App Service Configuration
```bash
# API Base URL
az webapp config appsettings set \
  --resource-group chaknal-platform \
  --name chaknal-frontend \
  --settings REACT_APP_API_BASE_URL="https://chaknal-backend.azurewebsites.net"

# Mock Data (Production)
az webapp config appsettings set \
  --resource-group chaknal-platform \
  --name chaknal-frontend \
  --settings REACT_APP_USE_MOCK_DATA="false"

# Environment
az webapp config appsettings set \
  --resource-group chaknal-platform \
  --name chaknal-frontend \
  --settings REACT_APP_ENVIRONMENT="production"
```

## 🚀 GitHub Actions Setup

### 1. GitHub Secrets
Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

```
AZURE_CREDENTIALS: {
  "clientId": "your-client-id",
  "clientSecret": "your-client-secret", 
  "subscriptionId": "your-subscription-id",
  "tenantId": "your-tenant-id"
}

DATABASE_URL: postgresql://chaknaladmin:YourSecurePassword123!@chaknal-db-server.postgres.database.azure.com:5432/chaknal_platform
JWT_SECRET_KEY: your-super-secure-jwt-secret-key-here
AZURE_STORAGE_CONNECTION_STRING: your-storage-connection-string
```

### 2. Workflow Files
Create `.github/workflows/` directory with deployment workflows.

## 📊 Database Migration

### 1. Export Current SQLite Data
```bash
# Export users
sqlite3 chaknal.db ".mode csv" ".output users.csv" "SELECT * FROM user;"

# Export companies  
sqlite3 chaknal.db ".mode csv" ".output companies.csv" "SELECT * FROM company;"

# Export contacts
sqlite3 chaknal.db ".mode csv" ".output contacts.csv" "SELECT * FROM contacts;"

# Export campaigns
sqlite3 chaknal.db ".mode csv" ".output campaigns.csv" "SELECT * FROM campaigns_new;"

# Export campaign_contacts
sqlite3 chaknal.db ".mode csv" ".output campaign_contacts.csv" "SELECT * FROM campaign_contacts;"
```

### 2. PostgreSQL Schema Creation
Run Alembic migrations on PostgreSQL:
```bash
alembic upgrade head
```

### 3. Data Import
Import CSV data into PostgreSQL tables.

## 🔒 Security Configuration

### 1. Enable HTTPS Only
```bash
az webapp update \
  --resource-group chaknal-platform \
  --name chaknal-backend \
  --https-only true

az webapp update \
  --resource-group chaknal-platform \
  --name chaknal-frontend \
  --https-only true
```

### 2. Configure Custom Domain (Optional)
```bash
az webapp config hostname add \
  --webapp-name chaknal-backend \
  --resource-group chaknal-platform \
  --hostname api.yourdomain.com

az webapp config hostname add \
  --webapp-name chaknal-frontend \
  --resource-group chaknal-platform \
  --hostname app.yourdomain.com
```

## 📈 Monitoring Setup

### 1. Application Insights
```bash
az monitor app-insights component create \
  --app chaknal-insights \
  --location "East US" \
  --resource-group chaknal-platform \
  --application-type web
```

### 2. Configure App Services
```bash
# Backend monitoring
az webapp config appsettings set \
  --resource-group chaknal-platform \
  --name chaknal-backend \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY="your-instrumentation-key"

# Frontend monitoring  
az webapp config appsettings set \
  --resource-group chaknal-platform \
  --name chaknal-frontend \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY="your-instrumentation-key"
```

## 🧪 Testing Deployment

### 1. Health Checks
- Backend: `https://chaknal-backend.azurewebsites.net/health`
- Frontend: `https://chaknal-frontend.azurewebsites.net`
- API Docs: `https://chaknal-backend.azurewebsites.net/docs`

### 2. Functionality Tests
- User authentication
- Campaign creation
- Contact management  
- DuxSoup integration
- File uploads
- Database operations

## 🔄 Continuous Deployment

GitHub Actions will automatically deploy on push to main branch:
1. **Backend**: Build Python app → Deploy to Azure App Service
2. **Frontend**: Build React app → Deploy to Azure App Service  
3. **Database**: Run migrations if schema changes

## 💰 Cost Estimation

**Monthly Costs (Approximate):**
- App Service Plan (B1): $15
- PostgreSQL (GP_Gen5_1): $30
- Storage Account: $5
- Key Vault: $1
- Application Insights: $5
- **Total: ~$56/month**

## 🆘 Troubleshooting

### Common Issues
1. **Database Connection**: Check firewall rules and connection strings
2. **CORS Errors**: Verify CORS_ORIGINS configuration
3. **Build Failures**: Check Node.js/Python versions
4. **Environment Variables**: Verify all required settings are configured

### Logs Access
```bash
# Backend logs
az webapp log tail --name chaknal-backend --resource-group chaknal-platform

# Frontend logs  
az webapp log tail --name chaknal-frontend --resource-group chaknal-platform
```

## 📞 Support

For deployment issues, check:
1. Azure portal for resource status
2. GitHub Actions logs for CI/CD issues
3. Application Insights for runtime errors
4. App Service logs for detailed error information
