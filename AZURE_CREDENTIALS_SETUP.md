# Azure Credentials Setup for GitHub Actions

## 🔐 Setting up Azure Service Principal for GitHub Actions

### Step 1: Create Azure Service Principal

Run this command in your terminal (replace with your subscription ID):

```bash
az ad sp create-for-rbac --name "chaknal-github-actions" \
  --role contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/chaknal-platform \
  --sdk-auth
```

### Step 2: Copy the JSON Output

The command will output JSON like this:
```json
{
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

### Step 3: Add to GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `AZURE_CREDENTIALS`
5. Value: Paste the entire JSON output from Step 2
6. Click **Add secret**

### Step 4: Verify Setup

The GitHub Actions workflow will automatically use these credentials to deploy to your Azure App Service.

## 🚀 Manual Deployment (Alternative)

If you prefer to deploy manually without GitHub Actions:

```bash
# Make sure you're logged in
az login

# Run the deployment script
./deploy-to-azure.sh
```

## 🔍 Troubleshooting

### If deployment fails:
1. Check Azure login: `az account show`
2. Check app service status: `az webapp show --name chaknal-backend-container --resource-group chaknal-platform`
3. Check logs: `az webapp log tail --name chaknal-backend-container --resource-group chaknal-platform`

### If GitHub Actions fails:
1. Verify `AZURE_CREDENTIALS` secret is set correctly
2. Check the Actions tab in GitHub for detailed error logs
3. Ensure the service principal has the correct permissions
