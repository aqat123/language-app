from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.schemas.vocabulary import FlashcardResponse, VocabularyAnswerRequest, VocabularyAnswerResponse
from app.services.vocabulary import get_next_flashcard, submit_vocabulary_answer

router = APIRouter()


@router.get("/next", response_model=FlashcardResponse)
async def get_flashcard(
    user_id: str = Query(...),
    target_language: str = Query(...),
    level: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get next vocabulary flashcard."""
    try:
        return await get_next_flashcard(user_id, target_language, level, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answer", response_model=VocabularyAnswerResponse)
async def submit_answer(
    request: VocabularyAnswerRequest,
    db: Session = Depends(get_db)
):
    """Submit vocabulary answer."""
    try:
        return await submit_vocabulary_answer(request, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
