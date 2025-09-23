#!/bin/bash

# Deploy Frontend to Azure Static Web Apps
echo "🚀 Deploying Chaknal Frontend to Azure Static Web Apps..."

# Navigate to frontend directory
cd /Users/lacomp/Desktop/chaknal-platform/chaknal-frontend

# Build the frontend
echo "📦 Building frontend..."
npm run build

# Get deployment token
echo "🔑 Getting deployment token..."
DEPLOYMENT_TOKEN=$(az staticwebapp secrets list --name chaknal-frontend --resource-group Chaknal-Platform --query "properties.deploymentToken" --output tsv)

if [ -z "$DEPLOYMENT_TOKEN" ]; then
    echo "❌ Failed to get deployment token"
    exit 1
fi

# Deploy using Azure Static Web Apps CLI
echo "🚀 Deploying to Azure..."
npx @azure/static-web-apps-cli deploy ./build --deployment-token "$DEPLOYMENT_TOKEN"

echo "✅ Frontend deployment completed!"
echo "🌐 Frontend URL: https://agreeable-bush-01890e00f.1.azurestaticapps.net"
