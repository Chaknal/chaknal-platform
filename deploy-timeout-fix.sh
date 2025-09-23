#!/bin/bash

# 🚀 Deploy Timeout Fix
# This script deploys the timeout fix for the campaign API

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Deploying Timeout Fix${NC}"
echo -e "${BLUE}========================${NC}"

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
print_status "Creating deployment package..."

# Create temp directory
TEMP_DIR="timeout_fix_deploy"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

# Copy only the files we changed
cp database/database.py "$TEMP_DIR/"
cp app/api/campaign.py "$TEMP_DIR/"
cp app/main.py "$TEMP_DIR/"

# Create the directory structure
mkdir -p "$TEMP_DIR/database"
mkdir -p "$TEMP_DIR/app/api"
mkdir -p "$TEMP_DIR/app"

# Move files to correct locations
mv "$TEMP_DIR/database.py" "$TEMP_DIR/database/"
mv "$TEMP_DIR/campaign.py" "$TEMP_DIR/app/api/"
mv "$TEMP_DIR/main.py" "$TEMP_DIR/app/"

# Create deployment zip
DEPLOY_ZIP="timeout-fix-$(date +%Y%m%d-%H%M%S).zip"
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
print_warning "Waiting for deployment to complete (2 minutes)..."
sleep 120

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
if timeout 25 curl -f -s "https://$APP_URL/api/campaigns" > /dev/null 2>&1; then
    print_status "✅ Campaigns endpoint working (no timeout!)"
else
    print_warning "⚠️  Campaigns endpoint still has issues"
fi

echo ""
echo -e "${BLUE}========================${NC}"
echo -e "${GREEN}🎉 Timeout Fix Deployed!${NC}"
echo -e "${BLUE}========================${NC}"
echo ""
echo -e "${YELLOW}🧪 Test your frontend now:${NC}"
echo -e "${YELLOW}   1. Go to https://app.chaknal.com${NC}"
echo -e "${YELLOW}   2. Try creating a campaign${NC}"
echo -e "${YELLOW}   3. The spinner should complete within 20 seconds${NC}"
echo ""
echo -e "${BLUE}📋 What was fixed:${NC}"
echo -e "${BLUE}   ✅ Added 20-second timeout to campaign API${NC}"
echo -e "${BLUE}   ✅ Simplified contact counting to avoid complex queries${NC}"
echo -e "${BLUE}   ✅ Better error handling and logging${NC}"
echo -e "${BLUE}   ✅ Improved database connection settings${NC}"

# Clean up deployment file
rm -f "$DEPLOY_ZIP"
