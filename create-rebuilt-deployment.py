#!/usr/bin/env python3
"""
Create rebuilt API deployment package
This script creates a deployment package with the rebuilt API routers
"""

import os
import shutil
import zipfile
from datetime import datetime

def create_rebuilt_deployment():
    """Create rebuilt deployment package with working API routers"""
    print("🚀 Creating rebuilt API deployment package...")
    
    # Create temporary directory
    temp_dir = "/tmp/rebuilt-api-deployment"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    # Create app directory structure
    app_dir = os.path.join(temp_dir, "app")
    os.makedirs(app_dir, exist_ok=True)
    os.makedirs(os.path.join(app_dir, "api"), exist_ok=True)
    
    # Copy essential files
    essential_files = [
        "requirements.txt",
        "alembic.ini",
        "app-settings.json"
    ]
    
    print("📄 Copying essential files...")
    for file_name in essential_files:
        if os.path.exists(file_name):
            shutil.copy2(file_name, temp_dir)
            print(f"   ✅ Copied {file_name}")
        else:
            print(f"   ⚠️ File {file_name} not found")
    
    # Copy config directory
    if os.path.exists("config"):
        shutil.copytree("config", os.path.join(temp_dir, "config"))
        print("   ✅ Copied config/")
    
    # Copy database directory
    if os.path.exists("database"):
        shutil.copytree("database", os.path.join(temp_dir, "database"))
        print("   ✅ Copied database/")
    
    # Copy migrations directory
    if os.path.exists("migrations"):
        shutil.copytree("migrations", os.path.join(temp_dir, "migrations"))
        print("   ✅ Copied migrations/")
    
    # Copy the rebuilt API files
    print("📁 Copying rebuilt API files...")
    api_files = [
        "app/api/campaigns_new.py",
        "app/api/contacts_new.py", 
        "app/api/messages_new.py",
        "app/main_rebuilt.py"
    ]
    
    for api_file in api_files:
        if os.path.exists(api_file):
            dest_file = os.path.join(temp_dir, api_file)
            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            shutil.copy2(api_file, dest_file)
            print(f"   ✅ Copied {api_file}")
        else:
            print(f"   ⚠️ File {api_file} not found")
    
    # Create __init__.py files
    init_files = [
        "app/__init__.py",
        "app/api/__init__.py"
    ]
    
    for init_file in init_files:
        init_path = os.path.join(temp_dir, init_file)
        os.makedirs(os.path.dirname(init_path), exist_ok=True)
        with open(init_path, "w") as f:
            f.write("")
        print(f"   ✅ Created {init_file}")
    
    # Create Dockerfile
    print("🐳 Creating Dockerfile...")
    dockerfile_content = """FROM python:3.11-slim

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    libffi-dev \\
    libssl-dev \\
    libpq-dev \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \\
    chown -R app:app /app

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Start command - use the rebuilt main file
CMD ["python", "-m", "uvicorn", "app.main_rebuilt:app", "--host", "0.0.0.0", "--port", "8000"]"""
    
    with open(os.path.join(temp_dir, "Dockerfile"), "w") as f:
        f.write(dockerfile_content)
    
    # Create .dockerignore
    print("🚫 Creating .dockerignore...")
    dockerignore_content = """__pycache__/
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
.git/
.mypy_cache/
.pytest_cache/
.hypothesis/
.DS_Store
*.db
*.sqlite
*.sqlite3
chaknal-venv/
node_modules/
*.zip
*.tar.gz
*.tar
test_*
temp_*
deployment_temp/
minimal-deployment/
platform-deployment/
fresh-deployment/
deployment/
"""
    
    with open(os.path.join(temp_dir, ".dockerignore"), "w") as f:
        f.write(dockerignore_content)
    
    # Create deployment package
    print("📦 Creating deployment package...")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    zip_filename = f"chaknal-rebuilt-api-{timestamp}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
    
    # Clean up temporary directory
    shutil.rmtree(temp_dir)
    
    print(f"✅ Rebuilt API deployment package created: {zip_filename}")
    print("📋 Package includes rebuilt API routers that should work")
    print("🎯 Ready for Azure deployment!")
    
    return zip_filename

if __name__ == "__main__":
    create_rebuilt_deployment()
