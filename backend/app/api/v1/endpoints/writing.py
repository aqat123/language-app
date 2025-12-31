from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.writing import WritingFeedbackRequest, WritingFeedbackResponse
from app.services.writing import get_writing_feedback

router = APIRouter()


@router.post("/feedback", response_model=WritingFeedbackResponse)
async def get_feedback(
    request: WritingFeedbackRequest,
    db: Session = Depends(get_db)
):
    """Get writing feedback."""
    try:
        return await get_writing_feedback(request, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
