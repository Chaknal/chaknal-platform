#!/bin/bash

# 🚀 Quick Fix Deployment Script
# This script deploys the database timeout fixes

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Quick Fix Deployment - Database Timeout Issues${NC}"
echo -e "${BLUE}================================================${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Configuration
RESOURCE_GROUP="Chaknal-Platform"
APP_NAME="chaknal-backend-1758294239"

# Create a minimal deployment package with just the fixes
print_status "Creating minimal deployment package..."

# Create temp directory
TEMP_DIR="temp_deploy"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

# Copy only the files we changed
cp database/database.py "$TEMP_DIR/"
cp app/api/campaign_simple.py "$TEMP_DIR/"
cp app/main.py "$TEMP_DIR/"

# Create the directory structure
mkdir -p "$TEMP_DIR/database"
mkdir -p "$TEMP_DIR/app/api"

# Move files to correct locations
mv "$TEMP_DIR/database.py" "$TEMP_DIR/database/"
mv "$TEMP_DIR/campaign_simple.py" "$TEMP_DIR/app/api/"
mv "$TEMP_DIR/main.py" "$TEMP_DIR/app/"

# Create deployment zip
DEPLOY_ZIP="quick-fix-$(date +%Y%m%d-%H%M%S).zip"
cd "$TEMP_DIR"
zip -r "../$DEPLOY_ZIP" . -q
cd ..

# Clean up temp directory
rm -rf "$TEMP_DIR"

print_status "Deployment package created: $DEPLOY_ZIP"

# Deploy to Azure
print_status "Deploying to Azure App Service..."
az webapp deployment source config-zip \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --src "$DEPLOY_ZIP"

print_status "Deployment completed!"

# Wait for deployment
print_warning "Waiting for deployment to complete (1 minute)..."
sleep 60

# Test the fix
print_status "Testing the fix..."
APP_URL="chaknal-backend-1758294239.azurewebsites.net"

# Test health endpoint
if curl -f -s "https://$APP_URL/health" > /dev/null 2>&1; then
    print_status "✅ Health endpoint working"
else
    print_error "❌ Health endpoint failed"
fi

# Test campaigns endpoint with timeout
print_status "Testing campaigns endpoint..."
if timeout 20 curl -f -s "https://$APP_URL/api/campaigns" > /dev/null 2>&1; then
    print_status "✅ Campaigns endpoint working (no timeout!)"
else
    print_warning "⚠️  Campaigns endpoint still has issues"
fi

echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}🎉 Quick Fix Deployment Complete!${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "${YELLOW}🧪 Test your frontend now:${NC}"
echo -e "${YELLOW}   1. Go to https://app.chaknal.com${NC}"
echo -e "${YELLOW}   2. Try creating a campaign${NC}"
echo -e "${YELLOW}   3. The spinner should complete quickly now${NC}"
echo ""
echo -e "${BLUE}📋 If still having issues:${NC}"
echo -e "${BLUE}   1. Check logs: az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME${NC}"
echo -e "${BLUE}   2. Restart app: az webapp restart --resource-group $RESOURCE_GROUP --name $APP_NAME${NC}"

# Clean up deployment file
rm -f "$DEPLOY_ZIP"
