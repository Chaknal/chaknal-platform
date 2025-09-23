#!/usr/bin/env python3
"""
Fixed Backend Deployment Script
==============================

This script creates a proper deployment package and deploys it to Azure App Service
with the correct configuration to fix the uvicorn dependency issue.
"""

import os
import subprocess
import shutil
import zipfile
import sys

def create_deployment_package():
    """Create a clean deployment package"""
    
    print("📦 Creating deployment package...")
    
    # Clean up previous attempts
    if os.path.exists("deployment"):
        shutil.rmtree("deployment")
    if os.path.exists("deployment.zip"):
        os.remove("deployment.zip")
    
    # Create deployment directory
    os.makedirs("deployment", exist_ok=True)
    
    # Copy essential files
    files_to_copy = [
        "app/",
        "config/", 
        "database/",
        "migrations/",
        "requirements.txt",
        "app-settings.json"
    ]
    
    for item in files_to_copy:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.copytree(item, f"deployment/{item}")
                print(f"  ✅ Copied directory: {item}")
            else:
                shutil.copy2(item, f"deployment/{item}")
                print(f"  ✅ Copied file: {item}")
        else:
            print(f"  ⚠️  Skipped missing: {item}")
    
    # Create a startup script
    startup_content = """#!/bin/bash
echo "🚀 Starting Chaknal Platform..."
echo "📦 Installing dependencies..."
python -m pip install --upgrade pip --no-cache-dir
python -m pip install -r requirements.txt --no-cache-dir
echo "🌟 Starting application..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
"""
    
    with open("deployment/startup.sh", "w") as f:
        f.write(startup_content)
    
    # Make startup script executable
    os.chmod("deployment/startup.sh", 0o755)
    print("  ✅ Created startup script")
    
    # Create ZIP file
    with zipfile.ZipFile("deployment.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("deployment"):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, "deployment")
                zipf.write(file_path, arcname)
    
    print("  ✅ Created deployment.zip")
    return True

def deploy_to_azure():
    """Deploy to Azure App Service"""
    
    resource_group = "Chaknal-Platform"
    app_name = "chaknal-backend-1758294239"
    
    print(f"🚀 Deploying to Azure App Service: {app_name}")
    
    try:
        # Deploy using the newer az webapp deploy command
        result = subprocess.run([
            "az", "webapp", "deploy",
            "--resource-group", resource_group,
            "--name", app_name,
            "--src-path", "deployment.zip",
            "--type", "zip"
        ], capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("✅ Deployment successful!")
            print(result.stdout)
        else:
            print("❌ Deployment failed!")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Deployment timed out but may still be in progress")
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return False
    
    return True

def configure_app_service():
    """Configure the app service settings"""
    
    resource_group = "Chaknal-Platform"
    app_name = "chaknal-backend-1758294239"
    
    print("⚙️  Configuring app service...")
    
    # Set startup command
    subprocess.run([
        "az", "webapp", "config", "set",
        "--resource-group", resource_group,
        "--name", app_name,
        "--startup-file", "startup.sh"
    ])
    
    # Enable build during deployment
    subprocess.run([
        "az", "webapp", "config", "appsettings", "set",
        "--resource-group", resource_group,
        "--name", app_name,
        "--settings", "SCM_DO_BUILD_DURING_DEPLOYMENT=true"
    ])
    
    print("✅ App service configured!")

def main():
    """Main deployment process"""
    
    print("🚀 Chaknal Backend Deployment Fix")
    print("=" * 40)
    
    if not create_deployment_package():
        sys.exit(1)
    
    if not deploy_to_azure():
        sys.exit(1)
    
    configure_app_service()
    
    print("\n🎉 Deployment completed!")
    print("⏳ Waiting for app to start...")
    
    # Restart the app
    subprocess.run([
        "az", "webapp", "restart",
        "--resource-group", "Chaknal-Platform",
        "--name", "chaknal-backend-1758294239"
    ])
    
    print("✅ App restarted!")
    print("\n🧪 Test the backend at:")
    print("   Health: https://chaknal-backend-1758294239.azurewebsites.net/health")
    print("   Docs: https://chaknal-backend-1758294239.azurewebsites.net/docs")
    print("   Campaigns: https://chaknal-backend-1758294239.azurewebsites.net/api/campaigns")

if __name__ == "__main__":
    main()
