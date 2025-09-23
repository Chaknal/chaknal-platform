#!/bin/bash

# Azure App Service Startup Script for Chaknal Platform
echo "🚀 Starting Chaknal Platform..."

# Set environment variables
export PYTHONPATH=/home/site/wwwroot
export PYTHONUNBUFFERED=1

# Update pip first
echo "📦 Updating pip..."
python -m pip install --upgrade pip --no-cache-dir

# Install system dependencies for pandas
echo "🔧 Installing system dependencies..."
apt-get update -y
apt-get install -y gcc g++ libffi-dev libssl-dev

# Install Python dependencies
echo "📦 Installing Python dependencies..."
python -m pip install -r requirements-azure.txt --no-cache-dir

# Wait for dependencies to be fully installed
echo "⏳ Waiting for dependencies to be ready..."
sleep 10

# Verify critical packages
echo "🔍 Verifying critical packages..."
python -c "import pandas; print('✅ Pandas version:', pandas.__version__)"
python -c "import numpy; print('✅ NumPy version:', numpy.__version__)"
python -c "import fastapi; print('✅ FastAPI version:', fastapi.__version__)"

# Start the application
echo "🌟 Starting FastAPI application..."
echo "📍 Working directory: $(pwd)"
echo "🐍 Python version: $(python --version)"

# Start with uvicorn
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 --log-level info
