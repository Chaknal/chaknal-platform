#!/bin/bash

# 🧪 Local Docker Testing Script for Chaknal Platform
# This script builds and tests the Docker container locally

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="chaknal-backend"
TAG="latest"
CONTAINER_NAME="chaknal-local-test"
PORT="8000"

echo -e "${BLUE}🧪 Local Docker Testing for Chaknal Platform${NC}"
echo -e "${BLUE}===========================================${NC}"

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

# Clean up any existing container
print_status "Cleaning up existing containers..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# Build the Docker image
print_status "Building Docker image..."
docker build -t $IMAGE_NAME:$TAG .

# Run the container
print_status "Starting container..."
docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:8000 \
    -e ENVIRONMENT=development \
    -e DEBUG=true \
    -e DATABASE_URL="postgresql+asyncpg://chaknaladmin:Chaknal2024!@chaknal-db-server.postgres.database.azure.com/chaknal_platform" \
    -e CORS_ORIGINS="http://localhost:3000,http://localhost:3001,https://app.chaknal.com" \
    $IMAGE_NAME:$TAG

# Wait for container to start
print_status "Waiting for container to start..."
sleep 15

# Check if container is running
if docker ps | grep -q $CONTAINER_NAME; then
    print_status "Container is running"
else
    print_error "Container failed to start"
    print_error "Container logs:"
    docker logs $CONTAINER_NAME
    exit 1
fi

# Test health endpoint
print_status "Testing health endpoint..."
for i in {1..10}; do
    echo "Health check attempt $i/10..."
    if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
        print_status "✅ Health check passed!"
        break
    else
        if [ $i -eq 10 ]; then
            print_error "❌ Health check failed after 10 attempts"
            print_error "Container logs:"
            docker logs $CONTAINER_NAME
            exit 1
        else
            echo "   Still starting up... waiting 5 seconds..."
            sleep 5
        fi
    fi
done

# Test API endpoints
print_status "Testing API endpoints..."

# Test root endpoint
echo "Testing root endpoint..."
curl -s http://localhost:$PORT/ | head -5

# Test API status
echo "Testing API status..."
curl -s http://localhost:$PORT/api/status | head -5

# Test contact import endpoints (should return 404 for missing campaign_id, but endpoint should exist)
echo "Testing contact import endpoints..."
curl -s -X POST http://localhost:$PORT/api/campaigns/test-campaign/contacts/import/preview \
    -F "file=@test_contacts.csv" \
    -F "source=duxsoup" || echo "Expected error (no test file)"

print_status "✅ All tests completed!"

echo ""
echo -e "${BLUE}🌐 Local App URL: http://localhost:$PORT${NC}"
echo -e "${BLUE}📊 Health check: http://localhost:$PORT/health${NC}"
echo -e "${BLUE}📚 API docs: http://localhost:$PORT/docs${NC}"
echo ""
echo -e "${YELLOW}📋 To stop the container: docker stop $CONTAINER_NAME${NC}"
echo -e "${YELLOW}📋 To view logs: docker logs $CONTAINER_NAME${NC}"
echo -e "${YELLOW}📋 To remove container: docker rm $CONTAINER_NAME${NC}"
echo ""
print_status "🎉 Local testing complete! Ready for Azure deployment."
