#!/bin/bash

# 🚀 Docker Deployment Script for Chaknal Platform
# This script builds and deploys the Docker container to Azure

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RESOURCE_GROUP="Chaknal-Platform"
APP_NAME="chaknal-backend-1758294239"
REGISTRY_NAME="chaknalregistry"
IMAGE_NAME="chaknal-backend"
TAG="latest"

echo -e "${BLUE}🚀 Docker Deployment for Chaknal Platform${NC}"
echo -e "${BLUE}=======================================${NC}"

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

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker Desktop first."
    exit 1
fi

print_status "Docker is running"

# Check if Azure CLI is logged in
if ! az account show > /dev/null 2>&1; then
    print_error "Not logged into Azure CLI. Please run 'az login' first."
    exit 1
fi

print_status "Azure CLI is authenticated"

# Step 1: Build the Docker image
print_status "Building Docker image..."
docker build -t $IMAGE_NAME:$TAG .

# Step 2: Test the image locally (optional)
print_warning "Testing Docker image locally..."
if docker run --rm -d --name chaknal-test -p 8000:8000 $IMAGE_NAME:$TAG; then
    print_status "Docker image started successfully"
    sleep 10
    
    # Test health endpoint
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_status "Health check passed"
    else
        print_warning "Health check failed, but continuing with deployment"
    fi
    
    # Stop test container
    docker stop chaknal-test
else
    print_warning "Docker image test failed, but continuing with deployment"
fi

# Step 3: Create Azure Container Registry (if it doesn't exist)
print_status "Creating Azure Container Registry..."
if ! az acr show --name $REGISTRY_NAME --resource-group $RESOURCE_GROUP > /dev/null 2>&1; then
    az acr create --name $REGISTRY_NAME --resource-group $RESOURCE_GROUP --sku Basic --admin-enabled true
    print_status "Container registry created"
else
    print_status "Container registry already exists"
fi

# Step 4: Login to Azure Container Registry
print_status "Logging into Azure Container Registry..."
az acr login --name $REGISTRY_NAME

# Step 5: Tag and push the image
print_status "Tagging and pushing Docker image..."
docker tag $IMAGE_NAME:$TAG $REGISTRY_NAME.azurecr.io/$IMAGE_NAME:$TAG
docker push $REGISTRY_NAME.azurecr.io/$IMAGE_NAME:$TAG

# Step 6: Configure App Service to use Docker
print_status "Configuring App Service to use Docker..."
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --linux-fx-version "DOCKER|$REGISTRY_NAME.azurecr.io/$IMAGE_NAME:$TAG"

# Step 7: Set app settings
print_status "Setting app settings..."
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
    DOCKER_REGISTRY_SERVER_URL="https://$REGISTRY_NAME.azurecr.io" \
    DOCKER_REGISTRY_SERVER_USERNAME="$REGISTRY_NAME" \
    DOCKER_REGISTRY_SERVER_PASSWORD="$(az acr credential show --name $REGISTRY_NAME --query passwords[0].value -o tsv)" \
    WEBSITES_ENABLE_APP_SERVICE_STORAGE=false

# Step 8: Restart the app
print_status "Restarting App Service..."
az webapp restart --resource-group $RESOURCE_GROUP --name $APP_NAME

print_status "Docker deployment completed!"
echo ""
echo -e "${BLUE}🌐 App URL: https://$APP_NAME.azurewebsites.net${NC}"
echo -e "${BLUE}📊 Health check: https://$APP_NAME.azurewebsites.net/health${NC}"
echo -e "${BLUE}📚 API docs: https://$APP_NAME.azurewebsites.net/docs${NC}"
echo ""
print_warning "⏳ Waiting for app to start up (this may take 2-3 minutes)..."
sleep 60

# Test the deployment
print_status "Testing deployment..."
for i in {1..5}; do
    echo "Attempt $i/5..."
    if curl -f -s "https://$APP_NAME.azurewebsites.net/health" > /dev/null 2>&1; then
        print_status "✅ Deployment successful! App is responding."
        break
    else
        if [ $i -eq 5 ]; then
            print_warning "⚠️  App is not responding yet. Check Azure Portal for logs."
        else
            echo "   Still starting up... waiting 30 seconds..."
            sleep 30
        fi
    fi
done

echo ""
echo -e "${GREEN}🎉 Docker deployment complete!${NC}"
echo -e "${YELLOW}🧪 Test your contact import functionality now!${NC}"
