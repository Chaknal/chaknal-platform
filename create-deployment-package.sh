#!/bin/bash

# 🚀 Create Deployment Package for Azure App Service
# This script creates a clean deployment package for Azure

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Creating Azure Deployment Package${NC}"
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
DEPLOY_DIR="deployment-package"
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

# Create .deployment file for Azure
print_status "Creating Azure deployment configuration..."
cat > "$DEPLOY_DIR/.deployment" << EOF
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
ENABLE_ORYX_BUILD=true
PYTHON_VERSION=3.11
EOF

# Create web.config for Azure (if needed)
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
DEPLOY_ZIP="chaknal-backend-deployment-$(date +%Y%m%d-%H%M%S).zip"
print_status "Creating deployment zip: $DEPLOY_ZIP"

cd "$DEPLOY_DIR"
zip -r "../$DEPLOY_ZIP" . -x "*.pyc" "__pycache__/*" "*.git*"
cd ..

print_status "Deployment package created successfully!"
echo ""
echo -e "${BLUE}📦 Deployment Package: $DEPLOY_ZIP${NC}"
echo -e "${BLUE}📁 Size: $(du -h $DEPLOY_ZIP | cut -f1)${NC}"
echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo -e "${YELLOW}   1. Run: ./fix-azure-deployment.sh${NC}"
echo -e "${YELLOW}   2. Deploy the zip file to Azure App Service${NC}"
echo -e "${YELLOW}   3. Or use Azure CLI: az webapp deployment source config-zip${NC}"
echo ""
echo -e "${GREEN}🎉 Ready for deployment!${NC}"

# Clean up deployment directory
print_status "Cleaning up temporary files..."
rm -rf "$DEPLOY_DIR"
