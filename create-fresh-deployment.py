#!/usr/bin/env python3
"""
Create completely fresh deployment package
This script creates a clean deployment with our rebuilt API
"""

import os
import shutil
import zipfile
from datetime import datetime

def create_fresh_deployment():
    """Create completely fresh deployment package"""
    print("🚀 Creating completely fresh deployment package...")
    
    # Create temporary directory
    temp_dir = "/tmp/fresh-deployment"
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
        "app/api/messages_new.py"
    ]
    
    for api_file in api_files:
        if os.path.exists(api_file):
            dest_file = os.path.join(temp_dir, api_file)
            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            shutil.copy2(api_file, dest_file)
            print(f"   ✅ Copied {api_file}")
        else:
            print(f"   ⚠️ File {api_file} not found")
    
    # Create a completely fresh main.py
    print("📝 Creating fresh main.py...")
    main_content = '''"""
Chaknal Platform - Fresh Main Application
Clean implementation with rebuilt API endpoints
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config.settings import settings
import logging
from datetime import datetime

# Import the rebuilt API routers
from app.api.campaigns_new import router as campaigns_router
from app.api.contacts_new import router as contacts_router
from app.api.messages_new import router as messages_router

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Chaknal Platform - Fresh",
    version="2.0.0",
    debug=settings.DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Chaknal Platform API - Fresh Version",
        "status": "running",
        "version": "2.0.0",
        "environment": "production",
        "api_endpoints": {
            "campaigns": "/api/campaigns/",
            "contacts": "/api/contacts/",
            "messages": "/api/messages/",
            "health": "/health",
            "docs": "/docs"
        }
    }

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "chaknal-platform-fresh",
        "environment": "production",
        "database": "connected"
    }

# Include the rebuilt API routers
app.include_router(campaigns_router, prefix="/api", tags=["Campaigns"])
app.include_router(contacts_router, prefix="/api", tags=["Contacts"])
app.include_router(messages_router, prefix="/api", tags=["Messages"])

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found", "path": str(request.url)}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    with open(os.path.join(temp_dir, "app", "main.py"), "w") as f:
        f.write(main_content)
    print("   ✅ Created fresh main.py")
    
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

# Start command
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]"""
    
    with open(os.path.join(temp_dir, "Dockerfile"), "w") as f:
        f.write(dockerfile_content)
    
    # Create deployment package
    print("📦 Creating deployment package...")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    zip_filename = f"chaknal-fresh-{timestamp}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
    
    # Clean up temporary directory
    shutil.rmtree(temp_dir)
    
    print(f"✅ Fresh deployment package created: {zip_filename}")
    print("📋 Package includes completely fresh main.py with rebuilt API")
    print("🎯 Ready for Azure deployment!")
    
    return zip_filename

if __name__ == "__main__":
    create_fresh_deployment()
