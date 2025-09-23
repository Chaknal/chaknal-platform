from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_session
from database.base import Base

router = APIRouter()

@router.post("/migrate", tags=["Database"])
async def run_migrations(session: AsyncSession = Depends(get_session)):
    """Run database migrations to create tables"""
    try:
        # Get the engine from the session
        engine = session.bind
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        return {"message": "Database migrations completed successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")
