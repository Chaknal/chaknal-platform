#!/bin/bash

# Chaknal Platform Local Development Runner
echo "🚀 Starting Chaknal Platform Local Development..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Set environment variables for local development
export DATABASE_URL="postgresql+asyncpg://chaknaladmin:!1homunyucatan@tziban.postgres.database.azure.com:5432/chaknal"
export SECRET_KEY="your-local-secret-key"
export ENVIRONMENT="development"
export DEBUG="true"
export FRONTEND_URL="http://localhost:3000"

# Google OAuth (optional - set these if you want to test OAuth locally)
export GOOGLE_CLIENT_ID="${GOOGLE_CLIENT_ID:-}"
export GOOGLE_CLIENT_SECRET="${GOOGLE_CLIENT_SECRET:-}"
export GOOGLE_REDIRECT_URI="http://localhost:8000/auth/google/callback"

echo "🔥 Starting FastAPI server on http://localhost:8000"
echo "📊 API docs available at http://localhost:8000/docs"
echo "🛑 Press Ctrl+C to stop"

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000



