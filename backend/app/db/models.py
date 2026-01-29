from sqlalchemy import Column, String, DateTime, Float, Integer, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from uuid import uuid4
from app.db.database import Base

"""Modified to work on SQLite which does not support UUID type natively.
If you are on pgsql, remove the getter and use UUID type directly."""

# Helper to ensure we always get a string
def get_uuid_str():
    return str(uuid4())

class User(Base):
    """User model for storing user information."""
    __tablename__ = "users"

    # CHANGE: explicitly use String type
    id = Column(String, primary_key=True, default=get_uuid_str)
    external_id = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    target_language = Column(String, nullable=True)
    level = Column(String, nullable=True)


class UserProgress(Base):
    """Track per-module learning progress for users."""
    __tablename__ = "user_progress"

    id = Column(String, primary_key=True, default=get_uuid_str)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    module = Column(String, nullable=False)
    score = Column(Float, nullable=True)
    total_attempts = Column(Integer, default=0)
    correct_attempts = Column(Integer, default=0)
    last_activity_at = Column(DateTime, server_default=func.now())


class ConversationSession(Base):
    """Store conversation session data and chat history."""
    __tablename__ = "conversation_sessions"

    id = Column(String, primary_key=True, default=get_uuid_str)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    context_json = Column(JSON, nullable=False, default=dict)
    target_language = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_active = Column(Boolean, default=True)


class ContentLog(Base):
    """Log all AI-generated content for auditing and improvement."""
    __tablename__ = "content_logs"

    id = Column(String, primary_key=True, default=get_uuid_str)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    module = Column(String, nullable=False)
    input_payload = Column(JSON, nullable=False)
    generated_content = Column(JSON, nullable=False)
    checker_result = Column(JSON, nullable=True)
    secondary_validation = Column(JSON, nullable=True)
    is_validated = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())