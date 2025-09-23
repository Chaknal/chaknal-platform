from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config.settings import settings
import logging
from app.api import campaign, contact_import, campaign_scheduler, campaign_contacts, contact_assignment, messages, send_message, contacts
from database.database import engine
from database.base import Base
import asyncio

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    debug=settings.DEBUG
)

# Initialize database tables on startup
@app.on_event("startup")
async def startup_event():
    """Create database tables on startup if they don't exist"""
    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(campaign.router, prefix="/api", tags=["Campaigns"])
app.include_router(contact_import.router, prefix="/api", tags=["Contact Import"])
app.include_router(campaign_scheduler.router, prefix="/api", tags=["Campaign Scheduler"])
app.include_router(campaign_contacts.router, prefix="/api", tags=["Campaign Contacts"])
app.include_router(contact_assignment.router, prefix="/api", tags=["Contact Assignment"])
app.include_router(messages.router, prefix="/api", tags=["Messages"])
app.include_router(send_message.router, prefix="/api", tags=["Messages"])
app.include_router(contacts.router, prefix="/api", tags=["Contacts"])

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Chaknal Platform API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)