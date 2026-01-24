from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.phonetics import evaluate_pronunciation, generate_target_phrase
from app.schemas.phonetics import PhoneticsEvaluationResponse, PhoneticsPracticeSession

router = APIRouter()


@router.get("/phrase", response_model=PhoneticsPracticeSession)  # Endpoint to get the random phrase
async def get_practice_phrase(
        target_language: str,
        level: str,
):
    result = await generate_target_phrase(target_language, level)
    return result


@router.post("/evaluate", response_model=PhoneticsEvaluationResponse)
async def evaluate_audio(
        user_id: str = Form(...),
        target_language: str = Form(...),
        target_phrase: str = Form(...),
        audio_file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    # Read the audio bytes from the uploaded file
    audio_bytes = await audio_file.read()

    # Call the service logic
    result = await evaluate_pronunciation(
        user_id=user_id,
        target_language=target_language,
        target_phrase=target_phrase,
        audio_bytes=audio_bytes,
        db=db
    )
    return result