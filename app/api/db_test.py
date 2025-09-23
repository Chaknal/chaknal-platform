from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database.database import get_session

router = APIRouter()

@router.get("/db-test", tags=["Database Test"])
async def test_database_connection(session: AsyncSession = Depends(get_session)):
    """Test database connection and list tables"""
    try:
        # Test basic connection
        result = await session.execute(text("SELECT 1 as test"))
        test_value = result.scalar()
        
        # List all tables
        tables_result = await session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        tables = [row[0] for row in tables_result.fetchall()]
        
        return {
            "connection_test": test_value,
            "tables": tables,
            "table_count": len(tables)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database test failed: {str(e)}")
