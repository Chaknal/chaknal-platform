#!/usr/bin/env python3
"""
Azure App Service startup script for Chaknal Platform
This script starts the FastAPI application for Azure deployment
"""

import os
import sys
import logging

# Add the current directory to Python path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main startup function for Azure App Service"""
    try:
        logger.info("🚀 Chaknal Platform Backend Starting...")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        
        # List files in directory for debugging
        files = os.listdir(current_dir)
        logger.info(f"Files in directory: {files}")
        
        # Install dependencies
        logger.info("🔧 Installing dependencies...")
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True)
        logger.info(f"✅ Pip install completed with return code: {result.returncode}")
        if result.stdout:
            logger.info(f"STDOUT: {result.stdout}")
        if result.stderr:
            logger.info(f"STDERR: {result.stderr}")
        
        # Import and start the FastAPI app
        logger.info("🚀 Starting FastAPI application...")
        from app.main import app
        import uvicorn
        
        # Get port from environment (Azure sets this)
        port = int(os.environ.get('PORT', 8000))
        logger.info(f"🌐 Starting server on port {port}")
        
        # Start the server
        uvicorn.run(app, host="0.0.0.0", port=port)
        
    except Exception as e:
        logger.error(f"❌ Error starting app: {e}")
        raise

if __name__ == "__main__":
    main()
