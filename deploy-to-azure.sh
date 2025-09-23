#!/bin/bash

# Chaknal Platform - Direct Deployment to Azure App Service
# This script deploys the code directly to the working chaknal-backend-container service

set -e

echo "🚀 Starting Chaknal Platform deployment to Azure..."

# Configuration
APP_NAME="chaknal-backend-container"
RESOURCE_GROUP="chaknal-platform"
PACKAGE_NAME="chaknal-deployment-$(date +%Y%m%d-%H%M%S).zip"

# Check if we're logged into Azure
echo "🔐 Checking Azure login status..."
if ! az account show &> /dev/null; then
    echo "❌ Not logged into Azure. Please run 'az login' first."
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
    -x "minimal_deployment_temp/*" \
    -x "full_deployment_temp/*" \
    -x "fixed_deployment_temp/*" \
    -x "rebuilt_deployment_temp/*" \
    -x "quick_fix_deployment_temp/*" \
    -x "fresh_deployment_temp/*"

echo "✅ Package created: $PACKAGE_NAME"

# Deploy to Azure App Service
echo "🚀 Deploying to Azure App Service..."
az webapp deploy \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --src-path "$PACKAGE_NAME" \
    --type zip

echo "✅ Code deployed successfully"

# Configure app settings
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

echo "✅ App settings configured"

# Restart the app service
echo "🔄 Restarting app service..."
az webapp restart --name "$APP_NAME" --resource-group "$RESOURCE_GROUP"

echo "✅ App service restarted"

# Wait for app to start
echo "⏳ Waiting for app to start..."
sleep 30

# Health check
echo "🏥 Performing health check..."
if curl -f "https://$APP_NAME.azurewebsites.net/health" > /dev/null 2>&1; then
    echo "✅ Health check passed!"
    echo "🌐 App is available at: https://$APP_NAME.azurewebsites.net"
    echo "📊 API docs at: https://$APP_NAME.azurewebsites.net/docs"
else
    echo "❌ Health check failed!"
    echo "🔍 Check logs with: az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
    exit 1
fi

# Clean up
echo "🧹 Cleaning up..."
rm -f "$PACKAGE_NAME"

echo "🎉 Deployment completed successfully!"
echo "🔗 Frontend: https://agreeable-bush-01890e00f.1.azurestaticapps.net"
echo "🔗 Backend: https://$APP_NAME.azurewebsites.net"
echo "📚 API Docs: https://$APP_NAME.azurewebsites.net/docs"
