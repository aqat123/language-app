from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models import User, UserProgress
from app.schemas.auth import UserCreate, UserResponse, UserProgressResponse

router = APIRouter()


@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
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
    """Get user by external ID."""
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
    """Get user progress across all modules."""
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
