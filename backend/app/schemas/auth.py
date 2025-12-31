from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    """Request to create a new user."""
    external_id: str
    target_language: Optional[str] = None
    level: Optional[str] = None


class UserResponse(BaseModel):
    """Response containing user information."""
    id: str
    external_id: str
    target_language: Optional[str] = None
    level: Optional[str] = None


class UserProgressResponse(BaseModel):
    """Response containing user progress for a module."""
    module: str
    score: Optional[float] = None
    total_attempts: int
    correct_attempts: int
