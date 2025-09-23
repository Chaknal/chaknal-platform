#!/bin/bash

# Azure Configuration Script for Chaknal Platform (no resource group/app plan creation)
# This script configures the Azure App Service for proper deployment

set -e

RESOURCE_GROUP="Chaknal-Platform"
APP_NAME="chacker"

# Set the startup command
echo "🔧 Configuring startup command..."
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --startup-file "gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000 --timeout 600 --workers 4"

# Set environment variables
echo "🔧 Configuring environment variables..."
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
    ENVIRONMENT="production" \
    DEBUG="false" \
    LOG_LEVEL="INFO" \
    RATE_LIMIT_PER_MINUTE="60" \
    SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" \
    ALGORITHM="HS256" \
    ACCESS_TOKEN_EXPIRE_MINUTES="1440" \
    ALLOWED_ORIGINS='["http://localhost:3000", "https://chaknal-frontend.azurewebsites.net"]' \
    ALLOW_CREDENTIALS="true" \
    ALLOW_METHODS='["GET", "POST", "PUT", "DELETE", "OPTIONS"]' \
    ALLOW_HEADERS='["*"]' \
    PROJECT_NAME="Chaknal Platform"

# Enable HTTPS only
echo "🔧 Enabling HTTPS only..."
az webapp update \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --https-only true

# Get the app URL
APP_URL=$(az webapp show --resource-group $RESOURCE_GROUP --name $APP_NAME --query defaultHostName --output tsv)

echo "✅ Configuration completed!"
echo "🌐 App URL: https://$APP_URL"
echo "📊 Health check: https://$APP_URL/health"
echo "🔐 Auth status: https://$APP_URL/api/auth/status"

echo ""
echo "📋 Next steps:"
echo "1. Set up your database connection string in Azure Portal if not already set."
echo "2. Configure Google OAuth credentials if needed."
echo "3. Test the deployment with: curl https://$APP_URL/health"
echo "4. Deploy the frontend to Azure Static Web Apps."

# Test the deployment
echo ""
echo "🧪 Testing deployment..."
sleep 30
if curl -f "https://$APP_URL/health" > /dev/null 2>&1; then
    echo "✅ Deployment successful! App is responding."
else
    echo "⚠️  App is not responding yet. Check Azure Portal for logs."
    echo "   You may need to restart the app or check the startup command."
fi