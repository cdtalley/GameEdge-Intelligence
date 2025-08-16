from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from .config import settings

# Async database engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Sync database engine (for migrations and testing)
sync_engine = create_engine(
    settings.DATABASE_SYNC_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Async session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Sync session factory
SyncSessionLocal = sessionmaker(
    sync_engine, expire_on_commit=False
)

# Base class for models
Base = declarative_base()


# Dependency to get async database session
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Dependency to get sync database session
def get_sync_db():
    with SyncSessionLocal() as session:
        try:
            yield session
        finally:
            session.close()


# Database initialization
async def init_db():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


# Database cleanup
async def close_db():
    await engine.dispose()
