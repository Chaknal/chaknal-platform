#!/bin/bash

# Deploy Scheduling Services to Azure App Service
# This script deploys the new scheduling system with transaction logging

set -e

echo "🚀 Deploying Scheduling Services to Azure App Service..."

# Configuration
RESOURCE_GROUP="Chaknal-Platform"
APP_NAME="chaknal-backend-1758294239"
DEPLOYMENT_PACKAGE="chaknal-scheduling-deployment-$(date +%Y%m%d-%H%M%S).zip"

echo "📦 Creating deployment package..."

# Create temporary directory for deployment
mkdir -p temp_deployment
cd temp_deployment

# Copy all necessary files
echo "📋 Copying application files..."

# Core application files
cp -r ../app .
cp -r ../database .
cp -r ../config .
cp -r ../migrations .

# Python files
cp ../*.py .
cp ../requirements.txt .
cp ../alembic.ini .

# Configuration files
cp ../app-settings.json .
cp ../Dockerfile .
cp ../startup.sh .

# Create new requirements.txt with scheduling dependencies
echo "📝 Updating requirements.txt..."
cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
alembic==1.12.1
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
pandas==2.1.3
numpy==1.25.2
pytz==2023.3
pydantic==2.5.0
httpx==0.25.2
aiofiles==23.2.1
jinja2==3.1.2
email-validator==2.0.0
psycopg2-binary==2.9.9
EOF

# Create deployment-specific startup script
echo "🔧 Creating startup script..."
cat > startup-azure-scheduling.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting Chaknal Platform with Scheduling Services..."

# Set environment variables
export PYTHONPATH="/home/site/wwwroot"
export ENVIRONMENT="production"
export DEBUG="false"

# Install any missing dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations
echo "📊 Running database migrations..."
python -c "
import asyncio
import sys
sys.path.append('.')
from database.database import engine
from sqlalchemy import text

async def run_migrations():
    try:
        async with engine.begin() as conn:
            print('🔧 Creating transaction logs table...')
            
            # Create transaction_logs table if it doesn't exist
            await conn.execute(text('''
                CREATE TABLE IF NOT EXISTS transaction_logs (
                    transaction_id VARCHAR(36) PRIMARY KEY,
                    transaction_type VARCHAR(100) NOT NULL,
                    transaction_time TIMESTAMP WITH TIME ZONE NOT NULL,
                    user_id VARCHAR(36),
                    entity_id VARCHAR(36),
                    entity_type VARCHAR(50),
                    description TEXT,
                    transaction_metadata JSON,
                    success BOOLEAN DEFAULT TRUE,
                    error_message TEXT,
                    campaign_id VARCHAR(36),
                    contact_id VARCHAR(36),
                    dux_user_id VARCHAR(100)
                );
            '''))
            
            # Create indexes
            await conn.execute(text('''
                CREATE INDEX IF NOT EXISTS idx_transaction_logs_type ON transaction_logs(transaction_type);
                CREATE INDEX IF NOT EXISTS idx_transaction_logs_time ON transaction_logs(transaction_time);
                CREATE INDEX IF NOT EXISTS idx_transaction_logs_user_id ON transaction_logs(user_id);
                CREATE INDEX IF NOT EXISTS idx_transaction_logs_entity_id ON transaction_logs(entity_id);
                CREATE INDEX IF NOT EXISTS idx_transaction_logs_entity_type ON transaction_logs(entity_type);
                CREATE INDEX IF NOT EXISTS idx_transaction_logs_success ON transaction_logs(success);
                CREATE INDEX IF NOT EXISTS idx_transaction_logs_campaign_id ON transaction_logs(campaign_id);
                CREATE INDEX IF NOT EXISTS idx_transaction_logs_contact_id ON transaction_logs(contact_id);
                CREATE INDEX IF NOT EXISTS idx_transaction_logs_dux_user_id ON transaction_logs(dux_user_id);
            '''))
            
            print('✅ Database schema updated successfully')
            
    except Exception as e:
        print(f'❌ Error updating database: {e}')

asyncio.run(run_migrations())
"

# Start the application
echo "🌟 Starting FastAPI application..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
EOF

chmod +x startup-azure-scheduling.sh

# Create .deployment file
echo "📄 Creating .deployment file..."
cat > .deployment << EOF
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
ENABLE_ORYX_BUILD=true
PYTHON_VERSION=3.11
EOF

# Create web.config for Azure
echo "⚙️ Creating web.config..."
cat > web.config << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified"/>
    </handlers>
    <httpPlatform processPath="D:\home\Python311\python.exe"
                  arguments="D:\home\site\wwwroot\startup-azure-scheduling.sh"
                  stdoutLogEnabled="true"
                  stdoutLogFile="D:\home\LogFiles\python.log"
                  startupTimeLimit="60"
                  startupRetryCount="3">
    </httpPlatform>
  </system.webServer>
</configuration>
EOF

# Create deployment package
echo "📦 Creating deployment package..."
zip -r ../$DEPLOYMENT_PACKAGE . -x "*.pyc" "__pycache__/*" "*.git*" "*.DS_Store"

cd ..

echo "📤 Deploying to Azure App Service..."

# Deploy using Azure CLI
if command -v az &> /dev/null; then
    echo "🔧 Using Azure CLI for deployment..."
    
    # Check if logged in
    if ! az account show &> /dev/null; then
        echo "❌ Please login to Azure CLI first: az login"
        exit 1
    fi
    
    # Deploy the package
    az webapp deployment source config-zip \
        --resource-group $RESOURCE_GROUP \
        --name $APP_NAME \
        --src $DEPLOYMENT_PACKAGE
    
    echo "✅ Deployment completed successfully!"
    
    # Restart the app
    echo "🔄 Restarting application..."
    az webapp restart --resource-group $RESOURCE_GROUP --name $APP_NAME
    
    # Check deployment status
    echo "📊 Checking deployment status..."
    az webapp show --resource-group $RESOURCE_GROUP --name $APP_NAME --query "{state:state,lastModifiedTime:lastModifiedTime}" --output table
    
else
    echo "⚠️ Azure CLI not found. Please install Azure CLI or deploy manually:"
    echo "1. Upload $DEPLOYMENT_PACKAGE to Azure App Service"
    echo "2. Restart the application"
    echo "3. Check the logs for any errors"
fi

echo "🎉 Scheduling services deployment completed!"
echo "📋 Next steps:"
echo "1. Verify the application is running: https://$APP_NAME.azurewebsites.net/health"
echo "2. Check the transaction logs table was created"
echo "3. Test the scheduling endpoints"
echo "4. Configure DuxSoup accounts"

# Cleanup
rm -rf temp_deployment
echo "🧹 Cleanup completed"
