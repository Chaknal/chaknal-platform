#!/usr/bin/env python3
"""
Azure Deployment Script for DuxWrap Testing

This script automates the deployment of the DuxWrap LinkedIn automation
platform to Azure for testing purposes.
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return None

def check_azure_cli():
    """Check if Azure CLI is installed and logged in"""
    print("🔍 Checking Azure CLI...")
    
    # Check if az CLI is installed
    result = subprocess.run("az --version", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Azure CLI not found. Please install it first:")
        print("   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        return False
    
    # Check if logged in
    result = subprocess.run("az account show", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Not logged into Azure. Please run: az login")
        return False
    
    print("✅ Azure CLI is ready")
    return True

def create_resource_group():
    """Create Azure resource group"""
    resource_group = "duxwrap-testing-rg"
    location = "eastus"
    
    print(f"\n🏗️ Creating resource group: {resource_group}")
    
    # Check if resource group exists
    result = subprocess.run(f"az group show --name {resource_group}", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Resource group {resource_group} already exists")
        return resource_group
    
    # Create resource group
    command = f"az group create --name {resource_group} --location {location}"
    result = run_command(command, f"Creating resource group {resource_group}")
    
    if result:
        print(f"✅ Resource group {resource_group} created successfully")
        return resource_group
    else:
        print("❌ Failed to create resource group")
        return None

def create_postgresql_database(resource_group):
    """Create Azure PostgreSQL database"""
    server_name = "duxwrap-testing-db"
    admin_user = "duxwrapadmin"
    admin_password = "DuxWrap2024!Secure"
    database_name = "duxwrap_testing"
    
    print(f"\n🗄️ Creating PostgreSQL database: {server_name}")
    
    # Check if server exists
    result = subprocess.run(f"az postgres flexible-server show --resource-group {resource_group} --name {server_name}", 
                           shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ PostgreSQL server {server_name} already exists")
    else:
        # Create PostgreSQL server
        command = f"""az postgres flexible-server create \
            --resource-group {resource_group} \
            --name {server_name} \
            --admin-user {admin_user} \
            --admin-password "{admin_password}" \
            --sku-name Standard_D2ds_v4 \
            --version 14 \
            --storage-size 32 \
            --yes"""
        
        result = run_command(command, f"Creating PostgreSQL server {server_name}")
        if not result:
            print("❌ Failed to create PostgreSQL server")
            return None
    
    # Create database
    command = f"""az postgres flexible-server db create \
        --resource-group {resource_group} \
        --server-name {server_name} \
        --database-name {database_name}"""
    
    result = run_command(command, f"Creating database {database_name}")
    if not result:
        print("❌ Failed to create database")
        return None
    
    # Get connection string
    command = f"""az postgres flexible-server show-connection-string \
        --server-name {server_name} \
        --admin-user {admin_user} \
        --admin-password "{admin_password}" \
        --database-name {database_name}"""
    
    result = run_command(command, "Getting database connection string")
    if result:
        connection_string = result.strip().replace('"', '')
        return {
            "server_name": server_name,
            "database_name": database_name,
            "connection_string": connection_string
        }
    
    return None

def create_app_service(resource_group):
    """Create Azure App Service for webhook server"""
    app_name = "duxwrap-testing-app"
    runtime = "python:3.11"
    
    print(f"\n🌐 Creating App Service: {app_name}")
    
    # Check if app service exists
    result = subprocess.run(f"az webapp show --resource-group {resource_group} --name {app_name}", 
                           shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ App Service {app_name} already exists")
        return app_name
    
    # Create App Service plan
    plan_name = "duxwrap-testing-plan"
    command = f"""az appservice plan create \
        --resource-group {resource_group} \
        --name {plan_name} \
        --sku B1 \
        --is-linux"""
    
    result = run_command(command, f"Creating App Service plan {plan_name}")
    if not result:
        print("❌ Failed to create App Service plan")
        return None
    
    # Create App Service
    command = f"""az webapp create \
        --resource-group {resource_group} \
        --plan {plan_name} \
        --name {app_name} \
        --runtime {runtime} \
        --deployment-local-git"""
    
    result = run_command(command, f"Creating App Service {app_name}")
    if not result:
        print("❌ Failed to create App Service")
        return None
    
    print(f"✅ App Service {app_name} created successfully")
    return app_name

def setup_database_schema(connection_string):
    """Setup database schema using the existing setup script"""
    print(f"\n🗄️ Setting up database schema...")
    
    # Create .env file with connection string
    env_content = f"""AZURE_POSTGRES_CONNECTION_STRING={connection_string}
DUX_SOUP_WEBHOOK_URL=https://your-webhook-url.azurewebsites.net/webhook
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ Created .env file with database connection")
    
    # Run database setup
    command = "python setup_azure_database.py"
    result = run_command(command, "Setting up database schema")
    
    if result:
        print("✅ Database schema setup completed")
        return True
    else:
        print("❌ Database schema setup failed")
        return False

def deploy_webhook_server(resource_group, app_name):
    """Deploy webhook server to App Service"""
    print(f"\n🚀 Deploying webhook server to {app_name}...")
    
    # Create deployment files
    deployment_files = [
        "webhook_data_collector_azure.py",
        "azure_database.py", 
        "startup.py",
        "requirements_azure.txt"
    ]
    
    # Check if files exist
    for file in deployment_files:
        if not os.path.exists(file):
            print(f"❌ Required file not found: {file}")
            return False
    
    # Deploy using Azure CLI
    command = f"az webapp up --resource-group {resource_group} --name {app_name} --html"
    result = run_command(command, f"Deploying to App Service {app_name}")
    
    if result:
        print("✅ Webhook server deployed successfully")
        return True
    else:
        print("❌ Webhook server deployment failed")
        return False

def configure_app_settings(resource_group, app_name, connection_string):
    """Configure App Service environment variables"""
    print(f"\n⚙️ Configuring App Service settings...")
    
    command = f"""az webapp config appsettings set \
        --resource-group {resource_group} \
        --name {app_name} \
        --settings AZURE_POSTGRES_CONNECTION_STRING="{connection_string}" \
        DUX_SOUP_WEBHOOK_URL="https://{app_name}.azurewebsites.net/webhook" """
    
    result = run_command(command, "Setting environment variables")
    
    if result:
        print("✅ App Service settings configured")
        return True
    else:
        print("❌ Failed to configure App Service settings")
        return False

def get_deployment_info(resource_group, app_name, db_info):
    """Get deployment information and next steps"""
    print(f"\n📊 Deployment Information")
    print("=" * 50)
    print(f"Resource Group: {resource_group}")
    print(f"App Service: {app_name}")
    print(f"Database: {db_info['server_name']}")
    print(f"Webhook URL: https://{app_name}.azurewebsites.net/webhook")
    print(f"Health Check: https://{app_name}.azurewebsites.net/health")
    print("\n🔧 Next Steps:")
    print("1. Update your Dux-Soup webhook URL to point to the Azure App Service")
    print("2. Test the webhook endpoint")
    print("3. Monitor the application logs")
    print("4. Check database for webhook data")

def main():
    """Main deployment function"""
    print("🚀 DuxWrap Azure Deployment for Testing")
    print("=" * 50)
    
    # Check prerequisites
    if not check_azure_cli():
        sys.exit(1)
    
    # Create resource group
    resource_group = create_resource_group()
    if not resource_group:
        sys.exit(1)
    
    # Create PostgreSQL database
    db_info = create_postgresql_database(resource_group)
    if not db_info:
        sys.exit(1)
    
    # Setup database schema
    if not setup_database_schema(db_info['connection_string']):
        sys.exit(1)
    
    # Create App Service
    app_name = create_app_service(resource_group)
    if not app_name:
        sys.exit(1)
    
    # Configure App Service settings
    if not configure_app_settings(resource_group, app_name, db_info['connection_string']):
        sys.exit(1)
    
    # Deploy webhook server
    if not deploy_webhook_server(resource_group, app_name):
        sys.exit(1)
    
    # Show deployment info
    get_deployment_info(resource_group, app_name, db_info)
    
    print(f"\n✅ DuxWrap deployment completed successfully!")
    print("🎉 Your testing environment is ready in Azure!")

if __name__ == "__main__":
    main() 