from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.phonetics import PhoneticsEvaluationResponse
from app.services.phonetics import evaluate_pronunciation

router = APIRouter()


@router.post("/evaluate", response_model=PhoneticsEvaluationResponse)
async def evaluate_pronunciation_endpoint(
    user_id: str = Form(...),
    target_language: str = Form(...),
    target_phrase: str = Form(...),
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Evaluate pronunciation from audio file."""
    try:
        # Read audio bytes
        audio_bytes = await audio_file.read()

        return await evaluate_pronunciation(
            user_id=user_id,
            target_language=target_language,
            target_phrase=target_phrase,
            audio_bytes=audio_bytes,
            db=db
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
