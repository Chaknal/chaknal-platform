# GitHub Actions Deployment Setup

## 🚀 Automated Frontend & Backend Deployment

Your Chaknal Platform is now configured for automated deployment via GitHub Actions!

## 📋 Required GitHub Secrets

### 1. Azure Static Web Apps Token
- **Secret Name**: `AZURE_STATIC_WEB_APPS_API_TOKEN`
- **Secret Value**: `46e2f965763042719dcac3bbe961db677d407b54faef6298f7c239bcc542194f01-fd653293-cebf-4aa0-9ad6-e68ad827a39600f143001890e00f`

### 2. Azure App Service Publish Profile
- **Secret Name**: `AZURE_WEBAPP_PUBLISH_PROFILE`
- **How to get it**:
  1. Go to [Azure Portal](https://portal.azure.com)
  2. Navigate to your App Service: `chaknal-backend-container`
  3. Go to "Deployment Center" → "Download publish profile"
  4. Copy the entire XML content and paste it as the secret value

## 🔧 Setup Steps

1. **Add GitHub Secrets**:
   - Go to: https://github.com/Chaknal/chaknal-platform/settings/secrets/actions
   - Click "New repository secret"
   - Add both secrets listed above

2. **Commit and Push**:
   ```bash
   git add .github/workflows/deploy.yml
   git commit -m "Update GitHub Actions for automated frontend deployment"
   git push origin main
   ```

3. **Monitor Deployment**:
   - Go to: https://github.com/Chaknal/chaknal-platform/actions
   - Watch the deployment progress

## 🎯 What Happens on Push

When you push to the `main` branch:

1. **Backend Deployment**:
   - Installs Python dependencies
   - Runs tests
   - Deploys to Azure App Service
   - URL: https://chaknal-backend-container.azurewebsites.net

2. **Frontend Deployment**:
   - Installs Node.js dependencies
   - Builds React app with production settings
   - Deploys to Azure Static Web Apps
   - URL: https://agreeable-bush-01890e00f.1.azurestaticapps.net

## 🔄 Workflow Features

- ✅ **Automatic**: Deploys on every push to main
- ✅ **Parallel**: Backend and frontend deploy simultaneously
- ✅ **Environment Variables**: Production settings applied
- ✅ **CORS**: Properly configured for frontend-backend communication
- ✅ **Testing**: Runs tests before deployment

## 🚨 Troubleshooting

If deployment fails:
1. Check GitHub Actions logs
2. Verify secrets are correctly set
3. Ensure Azure resources are running
4. Check CORS settings if frontend can't reach backend

## 📱 Your Live URLs

- **Frontend**: https://agreeable-bush-01890e00f.1.azurestaticapps.net
- **Backend API**: https://chaknal-backend-container.azurewebsites.net
- **API Docs**: https://chaknal-backend-container.azurewebsites.net/docs
