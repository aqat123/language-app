"""
Database Configuration and Connection Management.

Handles database engine initialization, session management, and dependency injection
for FastAPI endpoints. Supports both PostgreSQL and SQLite databases with appropriate
connection pooling and session handling.

Main Components:
    engine: SQLAlchemy database engine with connection pooling
    SessionLocal: Session factory for creating ORM sessions
    Base: Declarative base class for all ORM models
    get_db(): FastAPI dependency for injecting DB sessions into endpoints
    init_db(): Initialize all database tables

Database Features:
    - Automatic schema creation from models
    - Connection pooling with pool_pre_ping for reliability
    - SQLite compatibility (requires check_same_thread=False)
    - Debug logging when DEBUG mode enabled
    - Automatic session cleanup after endpoint execution

Usage:
    # In FastAPI endpoint
    @app.get("/users/{user_id}")
    async def get_user(user_id: str, db: Session = Depends(get_db)):
        return db.query(User).filter(User.id == user_id).first()
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create database engine
# Use check_same_thread=False for SQLite (required for FastAPI async)
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG,
    connect_args=connect_args
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for declarative models
Base = declarative_base()


def get_db():
    """
    Get database session for FastAPI dependency injection.

    FastAPI dependency that provides a SQLAlchemy session to endpoint functions.
    Automatically handles session cleanup after request completion, ensuring
    resources are properly released even if exceptions occur.

    Yields:
        Session: SQLAlchemy ORM session bound to the configured database engine.
            Use this session to query and modify database records.

    Example:
        @app.get("/users/{user_id}")
        async def get_user(user_id: str, db: Session = Depends(get_db)):
            user = db.query(User).filter(User.id == user_id).first()
            return user
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.

    Creates all database tables defined in SQLAlchemy models (User, UserProgress,
    ConversationSession, ContentLog) based on their metadata. Safe to call multiple
    times - only creates tables that don't already exist.

    Should be called once during application startup to ensure database schema
    matches the current model definitions.

    Example:
        if __name__ == "__main__":
            init_db()
            print("Database tables created successfully")
    """
    Base.metadata.create_all(bind=engine)
