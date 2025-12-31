from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.schemas.grammar import GrammarQuestionResponse, GrammarAnswerRequest, GrammarAnswerResponse
from app.services.grammar import get_grammar_question, submit_grammar_answer

router = APIRouter()


@router.get("/question", response_model=GrammarQuestionResponse)
async def get_question(
    user_id: str = Query(...),
    target_language: str = Query(...),
    level: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get grammar question."""
    try:
        return await get_grammar_question(user_id, target_language, level, topic, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answer", response_model=GrammarAnswerResponse)
async def submit_answer(
    request: GrammarAnswerRequest,
    db: Session = Depends(get_db)
):
    """Submit grammar answer."""
    try:
        return await submit_grammar_answer(request, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
