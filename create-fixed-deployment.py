#!/usr/bin/env python3
"""
Create fixed API deployment package with correct requirements
This script creates a deployment package with the working requirements.txt
"""

import os
import shutil
import zipfile
from datetime import datetime

def create_fixed_deployment():
    """Create fixed deployment package with correct requirements"""
    print("🚀 Creating fixed API deployment package...")
    
    # Create temporary directory
    temp_dir = "/tmp/fixed-api-deployment"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    # Essential directories to copy
    essential_dirs = [
        "app",
        "config", 
        "database",
        "migrations",
        "static"
    ]
    
    # Essential files to copy
    essential_files = [
        "requirements.txt",  # Use the original working requirements.txt
        "alembic.ini",
        "app-settings.json",
        "startup.py",
        "startup.sh"
    ]
    
    print("📁 Copying essential directories...")
    for dir_name in essential_dirs:
        if os.path.exists(dir_name):
            dest_path = os.path.join(temp_dir, dir_name)
            shutil.copytree(dir_name, dest_path)
            print(f"   ✅ Copied {dir_name}/")
        else:
            print(f"   ⚠️ Directory {dir_name}/ not found")
    
    print("📄 Copying essential files...")
    for file_name in essential_files:
        if os.path.exists(file_name):
            shutil.copy2(file_name, temp_dir)
            print(f"   ✅ Copied {file_name}")
        else:
            print(f"   ⚠️ File {file_name} not found")
    
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

# Start command
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]"""
    
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
    zip_filename = f"chaknal-fixed-api-{timestamp}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
    
    # Clean up temporary directory
    shutil.rmtree(temp_dir)
    
    print(f"✅ Fixed API deployment package created: {zip_filename}")
    print("📋 Package uses the original working requirements.txt")
    print("🎯 Ready for Azure deployment!")
    
    return zip_filename

if __name__ == "__main__":
    create_fixed_deployment()
