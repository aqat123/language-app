"""
SQLAlchemy ORM Data Models.

Defines database table structures for the language learning application.
All models use String type for IDs (SQLite compatibility) with UUID values.
Automatically tracked with timestamps for audit purposes.

Models:
    User: User account and language preferences
    UserProgress: Per-module learning statistics
    ConversationSession: Chat history and session context
    ContentLog: Audit log of AI-generated content

Database Features:
    - All IDs are UUID strings (compatible with SQLite)
    - Automatic timestamp tracking (created_at, updated_at)
    - Foreign key relationships with cascading behavior
    - JSON fields for storing flexible data structures
    - Indexes on frequently queried fields for performance

Usage:
    from app.db.models import User, UserProgress
    from app.db.database import SessionLocal

    db = SessionLocal()
    user = db.query(User).filter(User.external_id == "user123").first()
    progress = db.query(UserProgress).filter(UserProgress.user_id == user.id).all()
"""

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
    """
    User Account Model.

    Represents a user account in the language learning application. Stores user
    identity, target language preference, and proficiency level. Uses external_id
    for linking to auth systems while maintaining internal UUID primary key.

    Attributes:
        id: Primary key (UUID string)
        external_id: External user identifier from auth system (unique, indexed)
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        target_language: Target language for learning (e.g., Spanish, French)
        level: CEFR proficiency level (A1, A2, B1, B2, C1, C2)
    """
    __tablename__ = "users"

    # CHANGE: explicitly use String type
    id = Column(String, primary_key=True, default=get_uuid_str)
    external_id = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    target_language = Column(String, nullable=True)
    level = Column(String, nullable=True)


class UserProgress(Base):
    """
    User Module Progress Model.

    Tracks learning progress for each module (vocabulary, grammar, etc.) per user.
    Maintains statistics on attempts and correct answers to measure proficiency
    and generate appropriate challenge levels.

    Attributes:
        id: Primary key (UUID string)
        user_id: Foreign key referencing User.id
        module: Learning module name (vocabulary, grammar, conversation, etc.)
        score: Current module score or performance metric (optional)
        total_attempts: Total number of exercises completed
        correct_attempts: Number of correctly answered exercises
        last_activity_at: Timestamp of most recent activity in module
    """
    __tablename__ = "user_progress"

    id = Column(String, primary_key=True, default=get_uuid_str)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    module = Column(String, nullable=False)
    score = Column(Float, nullable=True)
    total_attempts = Column(Integer, default=0)
    correct_attempts = Column(Integer, default=0)
    last_activity_at = Column(DateTime, server_default=func.now())


class ConversationSession(Base):
    """
    Conversation Session Model.

    Stores conversation session data including message context, target language,
    and activity status. Enables multi-turn conversations with AI by persisting
    context across messages.

    Attributes:
        id: Primary key (UUID string)
        user_id: Foreign key referencing User.id
        context_json: Full conversation context including message history (dict)
        target_language: Language for this conversation session
        created_at: Session creation timestamp
        updated_at: Last message timestamp
        is_active: Whether session is currently active (boolean)
    """
    __tablename__ = "conversation_sessions"

    id = Column(String, primary_key=True, default=get_uuid_str)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    context_json = Column(JSON, nullable=False, default=dict)
    target_language = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_active = Column(Boolean, default=True)


class ContentLog(Base):
    """
    Content Generation Audit Log Model.

    Logs all AI-generated content for quality assurance, learning analytics,
    and compliance auditing. Stores input prompts, generated content, and
    validation results from the "Generate then Verify" pattern.

    Attributes:
        id: Primary key (UUID string)
        user_id: Foreign key referencing User.id (nullable for system-generated content)
        module: Learning module that generated the content (vocabulary, grammar, etc.)
        input_payload: Original request parameters (dict)
        generated_content: AI-generated response content (dict)
        checker_result: Validation result from content checker (dict, optional)
        is_validated: Whether content passed validation checks (boolean)
        created_at: Timestamp when content was generated

    Purpose:
        - Track all AI content generation for compliance
        - Enable quality analysis and model improvement
        - Provide audit trail of user interactions
        - Support analytics on content generation patterns
    """
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