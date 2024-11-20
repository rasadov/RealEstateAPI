import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = "postgresql://{}:{}@{}:{}/{}".format(
    os.getenv("DB_USER"),
    os.getenv("DB_PASS"),
    os.getenv("DB_HOST"),
    os.getenv("DB_PORT"),
    os.getenv("DB_NAME"),
)

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

def get_sync_db_session():
    """Dependency to provide a synchronous session for database operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
