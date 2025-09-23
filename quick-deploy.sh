#!/bin/bash

# Chaknal Platform - Quick Deployment Script
# This script deploys directly to Azure App Service for fast development

set -e

echo "🚀 Quick Deploy to Chaknal Platform..."

# Configuration
APP_NAME="chaknal-backend-container"
RESOURCE_GROUP="chaknal-platform"
PACKAGE_NAME="chaknal-quick-deploy-$(date +%Y%m%d-%H%M%S).zip"

# Check Azure login
if ! az account show &> /dev/null; then
    echo "❌ Please run 'az login' first"
    exit 1
fi

echo "✅ Azure login confirmed"

# Create deployment package
echo "📦 Creating deployment package..."
zip -r "$PACKAGE_NAME" . \
    -x "*.git*" \
    -x "*.github*" \
    -x "*.pyc" \
    -x "__pycache__/*" \
    -x "*.log" \
    -x "*.db" \
    -x "*.zip" \
    -x "node_modules/*" \
    -x "*.venv*" \
    -x "chaknal-venv/*" \
    -x "*.DS_Store" \
    -x "deployment_temp/*" \
    -x "*_deployment_temp/*" \
    -x "test_*.py" \
    -x "create_*.py" \
    -x "setup_*.py" \
    -x "monitor_*.py" \
    -x "performance_*.py" \
    -x "populate_*.py"

echo "✅ Package created: $PACKAGE_NAME"

# Deploy to Azure
echo "🚀 Deploying to Azure..."
az webapp deploy \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --src-path "$PACKAGE_NAME" \
    --type zip

echo "✅ Code deployed"

# Configure settings
echo "⚙️ Configuring app settings..."
az webapp config appsettings set \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --settings \
    ENVIRONMENT=production \
    LOG_LEVEL=INFO \
    DATABASE_URL="postgresql+asyncpg://chaknal_user:Chaknal2025!@chaknal-postgres.postgres.database.azure.com:5432/chaknal_db" \
    SECRET_KEY="your-super-secret-key-here-change-in-production" \
    CORS_ORIGINS="https://app.chaknal.com,https://platform.chaknal.com,https://agreeable-bush-01890e00f.1.azurestaticapps.net" \
    WEBSITES_PORT=8000

echo "✅ Settings configured"

# Restart app
echo "🔄 Restarting app..."
az webapp restart --name "$APP_NAME" --resource-group "$RESOURCE_GROUP"

echo "⏳ Waiting for app to start..."
sleep 30

# Health check
echo "🏥 Health check..."
if curl -f "https://$APP_NAME.azurewebsites.net/health" > /dev/null 2>&1; then
    echo "✅ Health check passed!"
    echo "🌐 App: https://$APP_NAME.azurewebsites.net"
    echo "📚 API Docs: https://$APP_NAME.azurewebsites.net/docs"
    echo "🎉 Deployment successful!"
else
    echo "❌ Health check failed"
    echo "🔍 Check logs: az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
    exit 1
fi

# Cleanup
rm -f "$PACKAGE_NAME"
echo "🧹 Cleanup complete"