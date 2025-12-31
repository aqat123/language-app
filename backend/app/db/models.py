from sqlalchemy import Column, String, DateTime, Float, Integer, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from uuid import uuid4
from app.db.database import Base


class User(Base):
    """User model for storing user information."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    external_id = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    target_language = Column(String, nullable=True)
    level = Column(String, nullable=True)  # e.g., A1, A2, B1, B2, C1, C2


class UserProgress(Base):
    """Track per-module learning progress for users."""
    __tablename__ = "user_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    module = Column(String, nullable=False)  # "conversation", "vocabulary", "grammar", "writing", "phonetics"
    score = Column(Float, nullable=True)
    total_attempts = Column(Integer, default=0)
    correct_attempts = Column(Integer, default=0)
    last_activity_at = Column(DateTime, server_default=func.now())


class ConversationSession(Base):
    """Store conversation session data and chat history."""
    __tablename__ = "conversation_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    context_json = Column(JSON, nullable=False, default=dict)  # stored chat history / system state
    target_language = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_active = Column(Boolean, default=True)


class ContentLog(Base):
    """Log all AI-generated content for auditing and improvement."""
    __tablename__ = "content_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    module = Column(String, nullable=False)
    input_payload = Column(JSON, nullable=False)  # what user asked
    generated_content = Column(JSON, nullable=False)  # main LLM output
    checker_result = Column(JSON, nullable=True)  # checker output metadata
    is_validated = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
