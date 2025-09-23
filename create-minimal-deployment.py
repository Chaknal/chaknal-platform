#!/usr/bin/env python3
"""
Create minimal API deployment package
This script creates a clean deployment package with only essential files
"""

import os
import shutil
import zipfile
from datetime import datetime

def create_minimal_deployment():
    """Create minimal deployment package"""
    print("🚀 Creating minimal API deployment package...")
    
    # Create temporary directory
    temp_dir = "/tmp/minimal-api-deployment"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    # Essential directories to copy
    essential_dirs = [
        "app",
        "config", 
        "database",
        "migrations"
    ]
    
    # Essential files to copy
    essential_files = [
        "requirements.txt",
        "alembic.ini",
        "app-settings.json"
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
    
    # Create minimal requirements.txt
    print("📦 Creating minimal requirements.txt...")
    minimal_requirements = """fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
httpx==0.25.2
aiofiles==23.2.1
jinja2==3.1.2
email-validator==2.0.0
bcrypt==4.1.2
pandas==2.1.3
numpy==1.25.2"""
    
    with open(os.path.join(temp_dir, "requirements.txt"), "w") as f:
        f.write(minimal_requirements)
    
    # Create minimal Dockerfile
    print("🐳 Creating minimal Dockerfile...")
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
*.tar"""
    
    with open(os.path.join(temp_dir, ".dockerignore"), "w") as f:
        f.write(dockerignore_content)
    
    # Create startup script
    print("🚀 Creating startup script...")
    startup_script = """#!/bin/bash
echo "Starting Chaknal Platform API..."

# Wait for database to be ready
echo "Waiting for database connection..."
python -c "
import time
import psycopg2
import os
from sqlalchemy import create_engine

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/chaknal')

# Try to connect to database
max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute('SELECT 1')
        print('Database connection successful!')
        break
    except Exception as e:
        print(f'Database connection failed (attempt {retry_count + 1}/{max_retries}): {e}')
        time.sleep(2)
        retry_count += 1

if retry_count >= max_retries:
    print('Failed to connect to database after maximum retries')
    exit(1)
"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting FastAPI application..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"""
    
    startup_path = os.path.join(temp_dir, "startup.sh")
    with open(startup_path, "w") as f:
        f.write(startup_script)
    os.chmod(startup_path, 0o755)
    
    # Create deployment package
    print("📦 Creating deployment package...")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    zip_filename = f"chaknal-minimal-api-{timestamp}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
    
    # Clean up temporary directory
    shutil.rmtree(temp_dir)
    
    print(f"✅ Minimal API deployment package created: {zip_filename}")
    print("📋 Package includes only essential files for API endpoints")
    print("🚫 No system files or unnecessary permissions required")
    print("🎯 Ready for Azure deployment!")
    
    return zip_filename

if __name__ == "__main__":
    create_minimal_deployment()
