#!/bin/bash
cd /Users/lacomp/Desktop/chaknal-platform
echo "🚀 Deploying Chaknal Platform..."
az webapp deploy --name chaknal-backend-container --resource-group chaknal-platform --src-path . --type zip
echo "✅ Deployment complete!"
