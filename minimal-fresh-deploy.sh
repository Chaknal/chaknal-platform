#!/bin/bash

# 🚀 Minimal Fresh Deployment - Focus on Contact Import
# This script creates the simplest possible deployment

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

echo -e "${BLUE}🚀 Minimal Fresh Deployment - Contact Import Focus${NC}"
echo -e "${BLUE}===============================================${NC}"

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

# Step 1: Create minimal deployment package
print_status "Creating minimal deployment package..."
MINIMAL_DIR="minimal-deployment"
if [ -d "$MINIMAL_DIR" ]; then
    rm -rf "$MINIMAL_DIR"
fi
mkdir -p "$MINIMAL_DIR"

# Copy only essential files
cp app/main.py "$MINIMAL_DIR/"
cp app/api/contact_import.py "$MINIMAL_DIR/"
cp -r app/api "$MINIMAL_DIR/"
cp -r app/models "$MINIMAL_DIR/"
cp -r app/schemas "$MINIMAL_DIR/"
cp -r app/core "$MINIMAL_DIR/"
cp -r app/auth "$MINIMAL_DIR/"
cp -r app/middleware "$MINIMAL_DIR/"
cp -r app/services "$MINIMAL_DIR/"
cp -r app/utils "$MINIMAL_DIR/"
cp -r database "$MINIMAL_DIR/"
cp -r config "$MINIMAL_DIR/"
cp requirements.txt "$MINIMAL_DIR/"

# Create minimal main.py that only includes contact import
cat > "$MINIMAL_DIR/main.py" << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Chaknal Platform - Contact Import API",
    description="Minimal API focused on contact import functionality",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "chaknal-contact-import"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Chaknal Platform - Contact Import API",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "contact_import_preview": "/api/campaigns/{campaign_id}/contacts/import/preview",
            "contact_import": "/api/campaigns/{campaign_id}/contacts/import"
        }
    }

# Import and include contact import router
try:
    from app.api.contact_import import router as contact_import_router
    app.include_router(contact_import_router, prefix="/api", tags=["Contact Import"])
    logger.info("✅ Contact Import router loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Could not load Contact Import router: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Create requirements.txt with only essential packages
cat > "$MINIMAL_DIR/requirements.txt" << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
psycopg2-binary==2.9.9
pandas==2.1.4
numpy==1.26.2
python-multipart==0.0.6
python-dotenv==1.0.0
pydantic-settings==2.1.0
EOF

# Create startup script
cat > "$MINIMAL_DIR/startup.sh" << 'EOF'
#!/bin/bash
echo "🚀 Starting Chaknal Contact Import API..."
python main.py
EOF
chmod +x "$MINIMAL_DIR/startup.sh"

# Create .deployment file
cat > "$MINIMAL_DIR/.deployment" << 'EOF'
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
ENABLE_ORYX_BUILD=true
PYTHON_VERSION=3.11
EOF

# Create deployment zip
DEPLOY_ZIP="chaknal-minimal-$(date +%Y%m%d-%H%M%S).zip"
cd "$MINIMAL_DIR"
zip -r "../$DEPLOY_ZIP" . -x "*.pyc" "__pycache__/*" "*.git*"
cd ..

print_status "Minimal deployment package created: $DEPLOY_ZIP"

# Step 2: Deploy to Azure
print_status "Deploying minimal package to Azure..."
az webapp deployment source config-zip \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --src "$DEPLOY_ZIP"

# Step 3: Restart the app
print_status "Restarting App Service..."
az webapp restart --resource-group $RESOURCE_GROUP --name $APP_NAME

print_status "Minimal deployment completed!"
echo ""
echo -e "${BLUE}🌐 App URL: https://$APP_NAME.azurewebsites.net${NC}"
echo -e "${BLUE}📊 Health check: https://$APP_NAME.azurewebsites.net/health${NC}"
echo -e "${BLUE}📚 API docs: https://$APP_NAME.azurewebsites.net/docs${NC}"
echo -e "${BLUE}🎯 Contact Import: https://$APP_NAME.azurewebsites.net/api/campaigns/{campaign_id}/contacts/import/preview${NC}"

# Step 4: Wait and test
print_warning "⏳ Waiting for app to build and start (2 minutes)..."
sleep 120

print_status "Testing minimal deployment..."
for i in {1..3}; do
    echo "Health check attempt $i/3..."
    if curl -f -s "https://$APP_NAME.azurewebsites.net/health" > /dev/null 2>&1; then
        print_status "✅ Minimal deployment successful! Contact import API is responding."
        break
    else
        if [ $i -eq 3 ]; then
            print_warning "⚠️  Backend is not responding yet. Check app logs:"
            print_warning "   az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME"
        else
            echo "   Still building/starting up... waiting 30 seconds..."
            sleep 30
        fi
    fi
done

# Clean up
rm -rf "$MINIMAL_DIR"
rm -f "$DEPLOY_ZIP"

echo ""
echo -e "${GREEN}🎉 Minimal Contact Import API Deployed!${NC}"
echo -e "${YELLOW}🧪 Test your contact import functionality now!${NC}"
