#!/bin/bash

# Redeploy Chaknal Backend to Azure App Service
# This script deploys the latest code with campaign endpoints

set -e

echo "🚀 Redeploying Chaknal Backend to Azure"
echo "======================================"

# Configuration
RESOURCE_GROUP="Chaknal-Platform"
APP_NAME="chaknal-backend-1758294239"
ZIP_FILE="chaknal-backend-deployment.zip"

echo "📦 App Service: $APP_NAME"
echo "📦 Resource Group: $RESOURCE_GROUP"
echo ""

# Step 1: Clean up any previous deployment files
echo "🧹 Cleaning up previous deployment files..."
rm -f $ZIP_FILE
rm -rf deployment_temp

# Step 2: Create deployment package
echo "📦 Creating deployment package..."
mkdir -p deployment_temp

# Copy essential files for deployment
cp -r app deployment_temp/
cp -r config deployment_temp/
cp -r database deployment_temp/
cp -r migrations deployment_temp/
cp requirements.txt deployment_temp/
cp app-settings.json deployment_temp/
cp startup.py deployment_temp/

# Copy static files if they exist
if [ -d "static" ]; then
    cp -r static deployment_temp/
fi

# Create a simple startup script for Azure
cat > deployment_temp/startup.sh << 'EOF'
#!/bin/bash
echo "Starting Chaknal Platform..."
python -m gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000 --timeout 600 --workers 2
EOF

chmod +x deployment_temp/startup.sh

# Step 3: Create ZIP package
echo "🗜️  Creating ZIP package..."
cd deployment_temp
zip -r ../$ZIP_FILE . -q
cd ..

echo "✅ Deployment package created: $ZIP_FILE"

# Step 4: Deploy to Azure App Service
echo "🚀 Deploying to Azure App Service..."
az webapp deployment source config-zip \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --src $ZIP_FILE

echo "✅ Code deployed successfully!"

# Step 5: Update app settings with latest configuration
echo "⚙️  Updating app settings..."
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings @app-settings.json

echo "✅ App settings updated!"

# Step 6: Set the startup command
echo "🔧 Setting startup command..."
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --startup-file "python -m gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000 --timeout 600 --workers 2"

echo "✅ Startup command configured!"

# Step 7: Restart the app service
echo "🔄 Restarting app service..."
az webapp restart \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME

echo "✅ App service restarted!"

# Step 8: Wait for startup and test
echo "⏳ Waiting for app to start up..."
sleep 30

# Test the health endpoint
echo "🧪 Testing health endpoint..."
APP_URL="https://${APP_NAME}.azurewebsites.net"
if curl -f "$APP_URL/health" > /dev/null 2>&1; then
    echo "✅ Health check passed!"
else
    echo "⚠️  Health check failed. App may still be starting up."
fi

# Test the campaigns endpoint
echo "🧪 Testing campaigns endpoint..."
if curl -f "$APP_URL/api/campaigns" --max-time 10 > /dev/null 2>&1; then
    echo "✅ Campaigns endpoint is available!"
else
    echo "⚠️  Campaigns endpoint test failed. This might be due to authentication requirements."
fi

# Cleanup
echo "🧹 Cleaning up..."
rm -f $ZIP_FILE
rm -rf deployment_temp

echo ""
echo "🎉 DEPLOYMENT COMPLETED!"
echo "======================================"
echo "🌐 Backend URL: $APP_URL"
echo "📊 Health Check: $APP_URL/health"
echo "📋 API Docs: $APP_URL/docs"
echo "🚀 Campaigns API: $APP_URL/api/campaigns"
echo ""
echo "🔧 Next Steps:"
echo "1. Test campaign creation at: https://app.chaknal.com"
echo "2. Check API documentation at: $APP_URL/docs"
echo "3. Monitor logs in Azure Portal if needed"
