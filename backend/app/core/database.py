"""
Database configuration and connection management
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Create async engine with connection pooling
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session.
    Used with FastAPI's Depends() for dependency injection.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database connection and create tables if needed.
    This should be called on application startup.
    """
    try:
        # Test the connection
        async with engine.begin() as conn:
            logger.info("Database connection established successfully")
            
        # Note: In production, use Alembic migrations instead of create_all()
        # This is just for development/testing
        if settings.ENVIRONMENT == "development":
            from app.models.base import Base
            async with engine.begin() as conn:
                # Uncomment the next line only for initial development
                # await conn.run_sync(Base.metadata.create_all)
                pass
                
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_db() -> None:
    """
    Close database connections.
    This should be called on application shutdown.
    """
    await engine.dispose()
    logger.info("Database connections closed")


# Database health check
async def check_db_health() -> bool:
    """
    Check if database is accessible and healthy.
    Returns True if healthy, False otherwise.
    """
    try:
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            # Simple query to test connection
            result = await session.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False