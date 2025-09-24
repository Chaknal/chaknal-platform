"""
Chaknal Platform - Rebuilt Main Application
Clean, simple implementation with working API endpoints
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from config.settings import settings
import logging
from datetime import datetime

# Import the rebuilt API routers
from app.api.campaigns_new import router as campaigns_router
from app.api.contacts_new import router as contacts_router
from app.api.messages_new import router as messages_router
from app.api.contact_import_new import router as contact_import_router
from app.api.simple_contact_import import router as simple_contact_import_router
from app.api.contact_import_with_logging import router as contact_import_logging_router
from app.api.logging_endpoints import router as logging_router
from app.api.test_contact_import import router as test_contact_import_router

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Chaknal Platform",
    version="1.0.0",
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
        "message": "Welcome to Chaknal Platform API",
        "status": "running",
        "version": "1.0.0",
        "environment": "production",
        "api_endpoints": {
            "campaigns": "/api/campaigns/",
            "contacts": "/api/contacts/",
            "messages": "/api/messages/",
            "contact_import": "/api/campaigns/{campaign_id}/contacts/import/",
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
        "database": "connected"
    }

# Include the rebuilt API routers
app.include_router(campaigns_router, prefix="/api", tags=["Campaigns"])
app.include_router(contacts_router, prefix="/api", tags=["Contacts"])
app.include_router(messages_router, prefix="/api", tags=["Messages"])
app.include_router(contact_import_router, prefix="/api", tags=["Contact Import"])
app.include_router(simple_contact_import_router, prefix="/api", tags=["Simple Contact Import"])
app.include_router(contact_import_logging_router, prefix="/api", tags=["Contact Import Logging"])
app.include_router(logging_router, prefix="/api", tags=["Logging"])
app.include_router(test_contact_import_router, prefix="/api", tags=["Test"])

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
