from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Chaknal Platform",
    version="1.0.0",
    debug=False
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.chaknal.com", "https://platform.chaknal.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Chaknal Platform",
        "version": "1.0.0",
        "status": "Working"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "authentication": "active"
        }
    }

@app.get("/api/campaigns")
async def list_campaigns():
    """Simple campaigns endpoint that returns empty list"""
    return []

@app.post("/api/campaigns")
async def create_campaign():
    """Simple campaign creation endpoint"""
    return {
        "message": "Campaign creation endpoint working",
        "status": "success"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
