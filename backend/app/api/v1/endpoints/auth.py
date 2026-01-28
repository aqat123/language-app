"""
User Authentication and Management Endpoints.

Handles user registration, retrieval, and progress tracking.
Provides REST endpoints for:
- User account creation
- User profile retrieval
- User progress across all modules

Main Functions:
    create_user: Register new user
    get_user: Fetch user profile
    get_user_progress: Get user statistics across modules

Usage:
    POST /api/v1/users -> Create user
    GET /api/v1/users/{external_id} -> Get user
    GET /api/v1/users/{external_id}/progress -> Get progress
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models import User, UserProgress
from app.schemas.auth import UserCreate, UserResponse, UserProgressResponse

router = APIRouter()


@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.

    Registers a new user for language learning. Each user is identified
    by external_id (from frontend) and learning preferences.

    Args:
        user: UserCreate schema with:
            - external_id: User identifier from frontend (username)
            - target_language: Language to learn (Spanish, French, etc.)
            - level: Initial CEFR level (A1, A2, B1, etc.)
        db: Database session (injected)

    Returns:
        UserResponse with created user details and UUID id

    Raises:
        HTTPException(400): If user with same external_id already exists

    Example:
        POST /api/v1/users
        {
            "external_id": "maria",
            "target_language": "Spanish",
            "level": "A1"
        }
        Response:
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "external_id": "maria",
            "target_language": "Spanish",
            "level": "A1"
        }
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.external_id == user.external_id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Create new user
    new_user = User(
        external_id=user.external_id,
        target_language=user.target_language,
        level=user.level
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        id=str(new_user.id),
        external_id=new_user.external_id,
        target_language=new_user.target_language,
        level=new_user.level
    )


@router.get("/users/{external_id}", response_model=UserResponse)
async def get_user(external_id: str, db: Session = Depends(get_db)):
    """
    Retrieve user profile by external ID.

    Fetches user account information including learning preferences.

    Args:
        external_id: User identifier (username from frontend)
        db: Database session (injected)

    Returns:
        UserResponse with user details

    Raises:
        HTTPException(404): If user not found

    Example:
        GET /api/v1/users/maria
        Response:
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "external_id": "maria",
            "target_language": "Spanish",
            "level": "A1"
        }
    """
    user = db.query(User).filter(User.external_id == external_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=str(user.id),
        external_id=user.external_id,
        target_language=user.target_language,
        level=user.level
    )


@router.get("/users/{external_id}/progress", response_model=List[UserProgressResponse])
async def get_user_progress(external_id: str, db: Session = Depends(get_db)):
    """
    Get user's learning progress across all modules.

    Retrieves statistics for vocabulary, conversation, grammar, writing, and phonetics.
    Includes total attempts, correct answers, and calculated scores.

    Args:
        external_id: User identifier (username from frontend)
        db: Database session (injected)

    Returns:
        List of UserProgressResponse, one per module:
        [{
            "module": "vocabulary",
            "total_attempts": 10,
            "correct_attempts": 8,
            "score": 80.0,
            "last_activity_at": "2026-01-28T10:30:00"
        }, ...]

    Raises:
        HTTPException(404): If user not found

    Example:
        GET /api/v1/users/maria/progress
        Response: [
            {
                "module": "vocabulary",
                "total_attempts": 10,
                "correct_attempts": 8,
                "score": 80.0,
                "last_activity_at": "2026-01-28T10:30:00"
            },
            {
                "module": "grammar",
                "total_attempts": 5,
                "correct_attempts": 4,
                "score": 80.0,
                "last_activity_at": "2026-01-28T11:00:00"
            }
        ]
    """
    user = db.query(User).filter(User.external_id == external_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    progress_records = db.query(UserProgress).filter(UserProgress.user_id == user.id).all()

    return [
        UserProgressResponse(
            module=p.module,
            score=p.score,
            total_attempts=p.total_attempts,
            correct_attempts=p.correct_attempts
        )
        for p in progress_records
    ]
