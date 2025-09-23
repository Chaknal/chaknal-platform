#!/bin/bash

# Setup GitHub Secrets for Chaknal Platform Deployment
echo "🔐 Setting up GitHub Secrets for Chaknal Platform..."

# Get the deployment token
DEPLOYMENT_TOKEN=$(az staticwebapp secrets list --name chaknal-frontend --resource-group Chaknal-Platform --query "properties.apiKey" --output tsv)

if [ -z "$DEPLOYMENT_TOKEN" ]; then
    echo "❌ Failed to get deployment token"
    exit 1
fi

echo "✅ Deployment token retrieved: ${DEPLOYMENT_TOKEN:0:20}..."

# Instructions for setting up GitHub secrets
echo ""
echo "📋 GitHub Secrets Setup Instructions:"
echo "====================================="
echo ""
echo "1. Go to your GitHub repository: https://github.com/Chaknal/chaknal-platform"
echo "2. Click on 'Settings' tab"
echo "3. Click on 'Secrets and variables' → 'Actions'"
echo "4. Click 'New repository secret' and add these secrets:"
echo ""
echo "   Secret Name: AZURE_STATIC_WEB_APPS_API_TOKEN"
echo "   Secret Value: $DEPLOYMENT_TOKEN"
echo ""
echo "   Secret Name: AZURE_WEBAPP_PUBLISH_PROFILE"
echo "   Secret Value: [Get from Azure App Service → Deployment Center → Download publish profile]"
echo ""
echo "5. After adding the secrets, push this commit to trigger the deployment:"
echo "   git add .github/workflows/deploy.yml"
echo "   git commit -m 'Update GitHub Actions for automated frontend deployment'"
echo "   git push origin main"
echo ""
echo "🚀 Once secrets are added, the workflow will automatically deploy both backend and frontend!"
