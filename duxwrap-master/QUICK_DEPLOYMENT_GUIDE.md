# 🚀 Quick Azure Deployment Guide

## Prerequisites

### 1. Install Azure CLI
```bash
# macOS
brew install azure-cli

# Windows
# Download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### 2. Login to Azure
```bash
az login
```

### 3. Install Python Dependencies
```bash
pip install -r requirements_azure.txt
```

## 🚀 Deploy to Azure

### Option 1: Automated Deployment (Recommended)
```bash
python deploy_to_azure.py
```

This script will:
- ✅ Create Azure resource group
- ✅ Create PostgreSQL database
- ✅ Create App Service
- ✅ Deploy webhook server
- ✅ Configure environment variables
- ✅ Setup database schema

### Option 2: Manual Deployment
Follow the steps in `AZURE_DEPLOYMENT_GUIDE.md`

## 📊 What Gets Deployed

### Azure Resources Created:
- **Resource Group**: `duxwrap-testing-rg`
- **PostgreSQL Database**: `duxwrap-testing-db`
- **App Service**: `duxwrap-testing-app`
- **Database**: `duxwrap_testing`

### URLs Generated:
- **Webhook URL**: `https://duxwrap-testing-app.azurewebsites.net/webhook`
- **Health Check**: `https://duxwrap-testing-app.azurewebsites.net/health`
- **API Docs**: `https://duxwrap-testing-app.azurewebsites.net/`

## 🔧 After Deployment

### 1. Update Dux-Soup Webhook URL
In your Dux-Soup settings, update the webhook URL to:
```
https://duxwrap-testing-app.azurewebsites.net/webhook
```

### 2. Test the Deployment
```bash
# Test health endpoint
curl https://duxwrap-testing-app.azurewebsites.net/health

# Test webhook endpoint
curl -X POST https://duxwrap-testing-app.azurewebsites.net/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### 3. Monitor Logs
```bash
# View App Service logs
az webapp log tail --resource-group duxwrap-testing-rg --name duxwrap-testing-app
```

### 4. Check Database
```bash
# Connect to database (if needed)
az postgres flexible-server connect --resource-group duxwrap-testing-rg --name duxwrap-testing-db
```

## 🧪 Testing Checklist

- [ ] App Service is running
- [ ] Database connection works
- [ ] Webhook endpoint responds
- [ ] Dux-Soup webhook URL updated
- [ ] LinkedIn automation data flowing
- [ ] Database storing webhook events
- [ ] Campaign management working

## 🗑️ Cleanup (When Done Testing)

```bash
# Delete all resources
az group delete --name duxwrap-testing-rg --yes
```

## 📞 Troubleshooting

### Common Issues:

1. **Azure CLI not found**
   - Install Azure CLI first
   - Run `az login`

2. **Permission denied**
   - Check Azure subscription permissions
   - Ensure you're logged in

3. **Database connection failed**
   - Check firewall rules
   - Verify connection string

4. **App Service deployment failed**
   - Check file permissions
   - Verify Python runtime

### Get Help:
- Check Azure portal for resource status
- View App Service logs
- Test endpoints manually
- Review deployment script output

## 🎯 Next Steps

Once testing is successful:
1. ✅ Confirm API functionality
2. ✅ Validate data flow
3. ✅ Test all endpoints
4. 🚀 Build platform UI
5. 🔄 Add more integrations (Outreach.io, Apollo.io, etc.) 