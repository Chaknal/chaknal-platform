#!/bin/bash

# 🚀 Create Minimal Working Deployment for Azure App Service
# This script creates a simple, reliable deployment package

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Creating Minimal Working Deployment${NC}"
echo -e "${BLUE}====================================${NC}"

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

# Create deployment directory
DEPLOY_DIR="deployment-minimal"
print_status "Creating deployment directory: $DEPLOY_DIR"

if [ -d "$DEPLOY_DIR" ]; then
    print_warning "Removing existing deployment directory..."
    rm -rf "$DEPLOY_DIR"
fi

mkdir -p "$DEPLOY_DIR"

# Copy essential files
print_status "Copying application files..."

# Core application files
cp -r app "$DEPLOY_DIR/"
cp -r config "$DEPLOY_DIR/"
cp -r database "$DEPLOY_DIR/"

# Configuration files
cp requirements.txt "$DEPLOY_DIR/"
cp alembic.ini "$DEPLOY_DIR/"

# Create minimal requirements.txt (only essential packages)
print_status "Creating minimal requirements.txt..."
cat > "$DEPLOY_DIR/requirements.txt" << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
pydantic-settings==2.1.0
httpx==0.25.2
aiohttp==3.9.1
google-auth==2.23.4
google-auth-oauthlib==1.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
email-validator==2.1.0
pandas==2.1.4
numpy==1.26.2
python-dateutil==2.8.2
openpyxl==3.1.2
EOF

# Create a simple startup script
print_status "Creating simple startup script..."
cat > "$DEPLOY_DIR/startup.sh" << 'EOF'
#!/bin/bash

echo "🚀 Starting Chaknal Platform..."

# Set environment variables
export PYTHONPATH=/home/site/wwwroot
export PYTHONUNBUFFERED=1

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Start the application
echo "🌟 Starting FastAPI application..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
EOF

chmod +x "$DEPLOY_DIR/startup.sh"

# Create .deployment file
print_status "Creating .deployment file..."
cat > "$DEPLOY_DIR/.deployment" << EOF
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
ENABLE_ORYX_BUILD=true
PYTHON_VERSION=3.11
EOF

# Create deployment zip
DEPLOY_ZIP="chaknal-backend-minimal-$(date +%Y%m%d-%H%M%S).zip"
print_status "Creating deployment zip: $DEPLOY_ZIP"

cd "$DEPLOY_DIR"
zip -r "../$DEPLOY_ZIP" . -x "*.pyc" "__pycache__/*" "*.git*"
cd ..

print_status "Minimal deployment package created successfully!"
echo ""
echo -e "${BLUE}📦 Deployment Package: $DEPLOY_ZIP${NC}"
echo -e "${BLUE}📁 Size: $(du -h $DEPLOY_ZIP | cut -f1)${NC}"

# Clean up deployment directory
print_status "Cleaning up temporary files..."
rm -rf "$DEPLOY_DIR"

echo -e "${GREEN}🎉 Ready for minimal deployment!${NC}"
