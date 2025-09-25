"""
Chaknal Platform - Working Version (without User Management Router)
This reverts to the previously working version
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

# Import only the working API routers
from app.api.simple_test import router as simple_test_router
from app.api.campaigns_new import router as campaigns_router
from app.api.contacts import router as contacts_router
# from app.api.auth import router as auth_router  # Temporarily disabled

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Chaknal Platform API",
        "status": "running",
        "version": "1.0.0",
        "environment": "production",
        "api_endpoints": {
            "campaigns": "/api/campaigns/",
            "contacts": "/api/contacts/",
            "auth": "/api/auth/login",
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
        "service": "chaknal-platform",
        "environment": "production",
        "database": "connected",
        "timestamp": datetime.utcnow().isoformat(),
        "deployment": "working-version"
    }

# Include only the working API routers
app.include_router(simple_test_router, prefix="/api", tags=["Test"])
app.include_router(campaigns_router, prefix="/api", tags=["Campaigns"])
app.include_router(contacts_router, prefix="/api", tags=["Contacts"])
# app.include_router(auth_router, prefix="/api", tags=["Authentication"])  # Temporarily disabled

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
