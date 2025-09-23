# 🚀 Azure App Service Deployment Fix Guide

## Problem Summary
The Chaknal Platform backend API is failing to start on Azure App Service due to:
- Missing `uvicorn` dependency installation
- Incorrect startup command configuration
- Port mismatch issues
- Container startup failures

## ✅ Fixes Applied

### 1. Fixed Requirements.txt
- ✅ Pinned all dependency versions for stability
- ✅ Removed duplicate `httpx` entry
- ✅ Added proper PostgreSQL dependencies

### 2. Updated Dockerfile
- ✅ Fixed port configuration (8000 for Azure App Service)
- ✅ Added system dependencies for PostgreSQL
- ✅ Improved security with non-root user
- ✅ Added health check
- ✅ Simplified startup command

### 3. Fixed Startup Script
- ✅ Proper environment variable setup
- ✅ Dependency installation with retry logic
- ✅ Better logging and debugging
- ✅ Correct uvicorn startup command

### 4. Created Deployment Scripts
- ✅ `fix-azure-deployment.sh` - Fixes Azure configuration
- ✅ `create-deployment-package.sh` - Creates clean deployment package

## 🚀 Deployment Steps

### Step 1: Fix Azure App Service Configuration
```bash
# Make script executable
chmod +x fix-azure-deployment.sh

# Run the fix script
./fix-azure-deployment.sh
```

This script will:
- Stop the current app
- Configure proper startup command
- Set Python version to 3.11
- Configure all environment variables
- Enable "Always On"
- Restart the app service

### Step 2: Create Deployment Package
```bash
# Make script executable
chmod +x create-deployment-package.sh

# Create deployment package
./create-deployment-package.sh
```

This creates a clean zip file with only necessary files.

### Step 3: Deploy to Azure
You can deploy using any of these methods:

#### Option A: Azure CLI
```bash
# Deploy the zip file
az webapp deployment source config-zip \
  --resource-group Chaknal-Platform \
  --name chaknal-backend-1758294239 \
  --src chaknal-backend-deployment-YYYYMMDD-HHMMSS.zip
```

#### Option B: Azure Portal
1. Go to Azure Portal → App Services → chaknal-backend-1758294239
2. Go to Deployment Center
3. Upload the deployment zip file
4. Deploy

#### Option C: GitHub Actions (Recommended)
Set up continuous deployment from your GitHub repository.

## 🔧 Configuration Details

### Environment Variables Set
- `ENVIRONMENT=production`
- `DEBUG=false`
- `SECRET_KEY=...`
- `DATABASE_URL=postgresql+asyncpg://chaknaladmin:Chaknal2024!@chaknal-db-server.postgres.database.azure.com/chaknal_platform`
- `CORS_ORIGINS=https://app.chaknal.com,https://platform.chaknal.com,https://agreeable-bush-01890e00f.1.azurestaticapps.net`
- `PYTHONPATH=/home/site/wwwroot`
- `PYTHONUNBUFFERED=1`

### Startup Command
```bash
startup.sh
```

The startup script runs:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 --log-level info
```

## 🧪 Testing After Deployment

### 1. Health Check
```bash
curl https://chaknal-backend-1758294239.azurewebsites.net/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-XX...",
  "version": "2.0.0",
  "services": {
    "database": "connected",
    "authentication": "active",
    "automation": "ready",
    "multi_tenancy": "enabled"
  }
}
```

### 2. API Documentation
Visit: https://chaknal-backend-1758294239.azurewebsites.net/docs

### 3. Campaign API Test
```bash
# Test campaign endpoint
curl https://chaknal-backend-1758294239.azurewebsites.net/api/campaigns
```

### 4. Root Endpoint
```bash
curl https://chaknal-backend-1758294239.azurewebsites.net/
```

## 🐛 Troubleshooting

### If App Still Won't Start

1. **Check Azure Logs**
```bash
az webapp log tail --resource-group Chaknal-Platform --name chaknal-backend-1758294239
```

2. **Restart App Service**
```bash
az webapp restart --resource-group Chaknal-Platform --name chaknal-backend-1758294239
```

3. **Check Startup Command**
```bash
az webapp config show --resource-group Chaknal-Platform --name chaknal-backend-1758294239 --query "siteConfig.appCommandLine"
```

4. **Verify Environment Variables**
```bash
az webapp config appsettings list --resource-group Chaknal-Platform --name chaknal-backend-1758294239
```

### Common Issues

1. **ModuleNotFoundError: No module named 'uvicorn'**
   - ✅ Fixed by updating startup script and requirements.txt

2. **Port binding issues**
   - ✅ Fixed by using port 8000 consistently

3. **Database connection issues**
   - ✅ Fixed by setting proper DATABASE_URL

4. **CORS issues**
   - ✅ Fixed by setting proper CORS_ORIGINS

## 📊 Expected Results

After successful deployment:
- ✅ https://chaknal-backend-1758294239.azurewebsites.net/health returns JSON
- ✅ https://chaknal-backend-1758294239.azurewebsites.net/docs shows API documentation
- ✅ Campaign creation at https://app.chaknal.com works
- ✅ /api/campaigns endpoint responds properly
- ✅ All API endpoints are accessible
- ✅ Frontend can communicate with backend

## 🎯 Success Criteria

The deployment is successful when:
1. Health endpoint returns 200 OK
2. API docs are accessible
3. Campaign creation works from frontend
4. All environment variables are properly set
5. Database connection is established
6. CORS is properly configured

## 📞 Support

If you encounter issues:
1. Check Azure App Service logs
2. Verify all environment variables are set
3. Ensure startup command is correct
4. Check database connectivity
5. Verify CORS configuration

The fixes in this guide address all the identified issues and should resolve the deployment problems.
