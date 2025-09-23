#!/bin/bash

# Setup Azure Environment Variables with Secrets
# This script sets up the Azure App Service with proper environment variables

# Configuration
RESOURCE_GROUP="Chaknal-Platform"
APP_NAME="chaknal-backend-container"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Azure CLI is installed and user is logged in
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed. Please install it first."
    exit 1
fi

# Check if user is logged in
if ! az account show &> /dev/null; then
    print_error "You are not logged in to Azure CLI. Please run 'az login' first."
    exit 1
fi

print_status "Setting up Azure App Service environment variables..."

# Set environment variables for Azure App Service
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
    ENVIRONMENT=production \
    DEBUG=false \
    LOG_LEVEL=INFO \
    SECRET_KEY="${SECRET_KEY:-$(openssl rand -hex 32)}" \
    GOOGLE_CLIENT_ID="${GOOGLE_CLIENT_ID}" \
    GOOGLE_CLIENT_SECRET="${GOOGLE_CLIENT_SECRET}" \
    GOOGLE_REDIRECT_URI="${GOOGLE_REDIRECT_URI:-https://platform.chaknal.com/auth/auth/google/callback}" \
    FRONTEND_URL="${FRONTEND_URL:-https://app.chaknal.com}" \
    CORS_ORIGINS="${CORS_ORIGINS:-https://app.chaknal.com,https://platform.chaknal.com,https://agreeable-bush-01890e00f.1.azurestaticapps.net}" \
    DUXSOUP_API_BASE_URL="${DUXSOUP_API_BASE_URL:-https://app.dux-soup.com/xapi/remote/control}" \
    DUXSOUP_RATE_LIMIT_DELAY="${DUXSOUP_RATE_LIMIT_DELAY:-1.0}" \
    DUXSOUP_USER_ID="${DUXSOUP_USER_ID}" \
    DUXSOUP_API_KEY="${DUXSOUP_API_KEY}" \
    DATABASE_URL="${DATABASE_URL}"

if [ $? -eq 0 ]; then
    print_status "✅ Environment variables set successfully!"
    print_status "Your Azure App Service is now configured with proper secrets."
    print_warning "⚠️  Remember to keep these secrets secure and never commit them to version control."
else
    print_error "Failed to set environment variables."
    exit 1
fi

print_status "Environment variables configured successfully!"
print_status "Your Chaknal Platform is ready for deployment."
