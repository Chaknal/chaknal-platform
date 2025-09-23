#!/bin/bash

# 🚀 Create Comprehensive Deployment Package for Azure App Service
# This script creates a complete deployment package with all dependencies

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Creating Comprehensive Azure Deployment Package${NC}"
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

# Create deployment directory
DEPLOY_DIR="deployment-comprehensive"
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
cp -r migrations "$DEPLOY_DIR/"

# Configuration files
cp requirements.txt "$DEPLOY_DIR/"
cp startup.sh "$DEPLOY_DIR/"
cp Dockerfile "$DEPLOY_DIR/"
cp alembic.ini "$DEPLOY_DIR/"

# Make startup script executable
chmod +x "$DEPLOY_DIR/startup.sh"

# Create comprehensive requirements.txt for Azure
print_status "Creating comprehensive requirements.txt for Azure..."
cat > "$DEPLOY_DIR/requirements.txt" << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0
sqlalchemy==2.0.23
alembic==1.12.1
asyncpg==0.29.0
psycopg2-binary==2.9.9
aiosqlite==0.19.0
fastapi-users[sqlalchemy]==12.1.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
email-validator==2.1.0
python-dotenv==1.0.0
pydantic-settings==2.1.0
httpx==0.25.2
aiohttp==3.9.1
google-auth==2.23.4
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.2.0
pandas==2.1.4
numpy==1.26.2
python-dateutil==2.8.2
openpyxl==3.1.2
xlrd==2.0.1
EOF

# Create improved startup script for Azure
print_status "Creating improved startup script for Azure..."
cat > "$DEPLOY_DIR/startup.sh" << 'EOF'
#!/bin/bash

# Azure App Service Startup Script for Chaknal Platform
echo "🚀 Starting Chaknal Platform..."

# Set environment variables
export PYTHONPATH=/home/site/wwwroot
export PYTHONUNBUFFERED=1

# Update pip first
echo "📦 Updating pip..."
python -m pip install --upgrade pip --no-cache-dir

# Install Python dependencies
echo "📦 Installing Python dependencies..."
python -m pip install -r requirements.txt --no-cache-dir

# Wait for dependencies to be fully installed
echo "⏳ Waiting for dependencies to be ready..."
sleep 10

# Verify critical packages
echo "🔍 Verifying critical packages..."
python -c "import pandas; print('✅ Pandas version:', pandas.__version__)" || echo "❌ Pandas import failed"
python -c "import numpy; print('✅ NumPy version:', numpy.__version__)" || echo "❌ NumPy import failed"
python -c "import fastapi; print('✅ FastAPI version:', fastapi.__version__)" || echo "❌ FastAPI import failed"

# Start the application
echo "🌟 Starting FastAPI application..."
echo "📍 Working directory: $(pwd)"
echo "🐍 Python version: $(python --version)"

# Start with uvicorn
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 --log-level info
EOF

chmod +x "$DEPLOY_DIR/startup.sh"

# Create .deployment file for Azure
print_status "Creating Azure deployment configuration..."
cat > "$DEPLOY_DIR/.deployment" << EOF
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
ENABLE_ORYX_BUILD=true
PYTHON_VERSION=3.11
EOF

# Create web.config for Azure
print_status "Creating web.config..."
cat > "$DEPLOY_DIR/web.config" << EOF
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="httpPlatformHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified" />
    </handlers>
    <httpPlatform processPath="python" arguments="-m uvicorn app.main:app --host 0.0.0.0 --port %HTTP_PLATFORM_PORT%" stdoutLogEnabled="true" stdoutLogFile="D:\home\LogFiles\python.log">
      <environmentVariables>
        <environmentVariable name="PYTHONPATH" value="D:\home\site\wwwroot" />
        <environmentVariable name="PYTHONUNBUFFERED" value="1" />
      </environmentVariables>
    </httpPlatform>
  </system.webServer>
</configuration>
EOF

# Create .gitignore for deployment
print_status "Creating .gitignore for deployment..."
cat > "$DEPLOY_DIR/.gitignore" << EOF
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
.DS_Store
EOF

# Create deployment zip
DEPLOY_ZIP="chaknal-backend-comprehensive-$(date +%Y%m%d-%H%M%S).zip"
print_status "Creating deployment zip: $DEPLOY_ZIP"

cd "$DEPLOY_DIR"
zip -r "../$DEPLOY_ZIP" . -x "*.pyc" "__pycache__/*" "*.git*"
cd ..

print_status "Comprehensive deployment package created successfully!"
echo ""
echo -e "${BLUE}📦 Deployment Package: $DEPLOY_ZIP${NC}"
echo -e "${BLUE}📁 Size: $(du -h $DEPLOY_ZIP | cut -f1)${NC}"
echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo -e "${YELLOW}   1. Run: ./fix-azure-deployment-comprehensive.sh${NC}"
echo -e "${YELLOW}   2. Deploy the zip file: az webapp deployment source config-zip${NC}"
echo -e "${YELLOW}   3. Monitor logs for any issues${NC}"
echo ""
echo -e "${GREEN}🎉 Ready for comprehensive deployment!${NC}"

# Clean up deployment directory
print_status "Cleaning up temporary files..."
rm -rf "$DEPLOY_DIR"
