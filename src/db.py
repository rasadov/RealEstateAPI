from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from src.config import DATABASE_URL

# Global variables for engine and session, initialized later
engine = None
AsyncSessionLocal = None
Base = declarative_base()

async def initialize_database():
    """
    Initializes the database engine and session factory.
    This function should be called on application startup.
    """
    global engine, AsyncSessionLocal
    engine = create_async_engine(DATABASE_URL, echo=True)

    AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

async def get_db_session():
    """Dependency to provide a session for database operations."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
