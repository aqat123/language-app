"""
User Authentication and Management Schemas.

Pydantic models for user registration, authentication, and progress tracking.
Used for request/response validation in auth endpoints.

Models:
    UserCreate: Request model for user registration
    UserResponse: Response model with user information
    UserProgressResponse: Response model for module progress statistics
"""

from pydantic import BaseModel, Field
from typing import Optional


class UserCreate(BaseModel):
    """
    User Registration Request Model.

    Captures required and optional information for creating a new user account.
    The external_id must be unique and is used to link with auth systems.
    """
    external_id: str = Field(..., description="Unique identifier from auth system (required)")
    target_language: Optional[str] = Field(None, description="Target language (Spanish, French, etc.)")
    level: Optional[str] = Field(None, description="CEFR proficiency level (A1, A2, B1, B2, C1, C2)")


class UserResponse(BaseModel):
    """
    User Information Response Model.

    Returns user account details and language learning preferences.
    Used in endpoints that retrieve user profile information.
    """
    id: str = Field(..., description="Internal user ID (UUID)")
    external_id: str = Field(..., description="External identifier from auth system")
    target_language: Optional[str] = Field(None, description="Target language for learning")
    level: Optional[str] = Field(None, description="Current proficiency level")


class UserProgressResponse(BaseModel):
    """
    Module Progress Statistics Response Model.

    Provides learning metrics for a specific module. Used to track and display
    user's progress across all learning modules (vocabulary, grammar, etc.).
    """
    module: str = Field(..., description="Learning module name (vocabulary, grammar, conversation, etc.)")
    score: Optional[float] = Field(None, description="Current module score or performance metric")
    total_attempts: int = Field(..., description="Total exercises completed in module")
    correct_attempts: int = Field(..., description="Number of correctly answered exercises")
