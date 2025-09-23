#!/bin/bash

# 🚀 Chaknal Platform Production Deployment Script
# This script deploys the platform with DuxSoup integration to production

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="chaknal-platform"
DOCKER_IMAGE="chaknal-platform:latest"
CONTAINER_NAME="chaknal-platform-prod"
NETWORK_NAME="chaknal-network"
VOLUME_NAME="chaknal-data"

# Environment variables (should be set in production)
export POSTGRES_HOST=${POSTGRES_HOST:-"localhost"}
export POSTGRES_PORT=${POSTGRES_PORT:-"5432"}
export POSTGRES_DB=${POSTGRES_DB:-"chaknal_prod"}
export POSTGRES_USER=${POSTGRES_USER:-"chaknal_user"}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-"CHANGE_ME_IN_PRODUCTION"}
export DUXSOUP_API_BASE_URL=${DUXSOUP_API_BASE_URL:-"https://app.dux-soup.com/xapi/remote/control"}
export JWT_SECRET_KEY=${JWT_SECRET_KEY:-"CHANGE_ME_IN_PRODUCTION"}
export ENVIRONMENT=${ENVIRONMENT:-"production"}

echo -e "${BLUE}🚀 Starting Chaknal Platform Production Deployment${NC}"
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

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_status "Docker is running"

# Check if required environment variables are set
if [ "$POSTGRES_PASSWORD" = "CHANGE_ME_IN_PRODUCTION" ]; then
    print_warning "POSTGRES_PASSWORD is set to default value. Please set a secure password."
fi

if [ "$JWT_SECRET_KEY" = "CHANGE_ME_IN_PRODUCTION" ]; then
    print_warning "JWT_SECRET_KEY is set to default value. Please set a secure secret key."
fi

# Create Docker network if it doesn't exist
if ! docker network ls | grep -q "$NETWORK_NAME"; then
    print_status "Creating Docker network: $NETWORK_NAME"
    docker network create "$NETWORK_NAME"
else
    print_status "Docker network $NETWORK_NAME already exists"
fi

# Create Docker volume if it doesn't exist
if ! docker volume ls | grep -q "$VOLUME_NAME"; then
    print_status "Creating Docker volume: $VOLUME_NAME"
    docker volume create "$VOLUME_NAME"
else
    print_status "Docker volume $VOLUME_NAME already exists"
fi

# Build the Docker image
print_status "Building Docker image: $DOCKER_IMAGE"
docker build -t "$DOCKER_IMAGE" .

# Stop and remove existing container if it exists
if docker ps -a | grep -q "$CONTAINER_NAME"; then
    print_status "Stopping existing container: $CONTAINER_NAME"
    docker stop "$CONTAINER_NAME" || true
    docker rm "$CONTAINER_NAME" || true
fi

# Run database migrations
print_status "Running database migrations"
docker run --rm \
    --network "$NETWORK_NAME" \
    --env-file .env \
    -v "$VOLUME_NAME:/app/data" \
    "$DOCKER_IMAGE" \
    python -m alembic upgrade head

# Start the application container
print_status "Starting application container: $CONTAINER_NAME"
docker run -d \
    --name "$CONTAINER_NAME" \
    --network "$NETWORK_NAME" \
    --restart unless-stopped \
    -p 8000:8000 \
    -p 8001:8001 \
    --env-file .env \
    -v "$VOLUME_NAME:/app/data" \
    -v "$(pwd)/logs:/app/logs" \
    "$DOCKER_IMAGE"

# Wait for the application to start
print_status "Waiting for application to start..."
sleep 10

# Check if the application is running
if docker ps | grep -q "$CONTAINER_NAME"; then
    print_status "Application container is running"
else
    print_error "Failed to start application container"
    docker logs "$CONTAINER_NAME"
    exit 1
fi

# Check application health
print_status "Checking application health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "Application is healthy and responding"
else
    print_warning "Application health check failed, but container is running"
fi

# Show container status
print_status "Container status:"
docker ps | grep "$CONTAINER_NAME"

# Show logs
print_status "Recent application logs:"
docker logs --tail 20 "$CONTAINER_NAME"

echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}🎉 Chaknal Platform Production Deployment Complete!${NC}"
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}✅ Application is running on port 8000${NC}"
echo -e "${GREEN}✅ Health check endpoint: http://localhost:8000/health${NC}"
echo -e "${GREEN}✅ API documentation: http://localhost:8000/docs${NC}"
echo -e "${GREEN}✅ Automation dashboard: http://localhost:8000/static/automation-dashboard.html${NC}"
echo -e "${BLUE}================================================${NC}"
echo -e "${YELLOW}📋 Next steps:${NC}"
echo -e "${YELLOW}   1. Configure your DuxSoup API credentials${NC}"
echo -e "${YELLOW}   2. Set up your first LinkedIn automation campaign${NC}"
echo -e "${YELLOW}   3. Monitor the application logs: docker logs -f $CONTAINER_NAME${NC}"
echo -e "${YELLOW}   4. Set up monitoring and alerting${NC}"
echo -e "${BLUE}================================================${NC}"
