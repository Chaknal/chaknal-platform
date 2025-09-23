from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = settings.DATABASE_URL

# Configure engine with proper timeout and SSL settings
# Different configurations for PostgreSQL (Azure) vs SQLite (local)
if "postgresql" in DATABASE_URL:
    # PostgreSQL configuration for Azure
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,  # Disable SQL echo in production
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=3600,   # Recycle connections every hour
        pool_timeout=30,     # 30 second timeout for getting connection from pool
        connect_args={
            "server_settings": {
                "application_name": "chaknal_platform",
            },
            "command_timeout": 60,  # 60 second timeout for individual commands
            "prepared_statement_cache_size": 0,  # Disable prepared statement cache for Azure
        }
    )
else:
    # SQLite configuration for local development
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        connect_args={
            "timeout": 30,  # SQLite timeout
        }
    )

async_session_maker = async_sessionmaker(
    engine, 
    expire_on_commit=False, 
    class_=AsyncSession
)


async def get_session() -> AsyncSession:
    """Dependency to get database session"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
