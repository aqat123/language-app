"""
Phonetics Module Endpoints.

REST API for pronunciation practice and evaluation.
Provides endpoints for generating practice phrases and evaluating audio recordings.

Main Functions:
    get_practice_phrase: Retrieve a phrase to practice pronunciation
    evaluate_audio: Submit audio recording for pronunciation evaluation

Workflow:
    1. GET /phrase -> Receive target phrase with pronunciation guide
    2. User records themselves pronouncing the phrase
    3. POST /evaluate -> Submit audio file for analysis
    4. Receive: transcription, similarity score, detailed feedback

Features:
    - Speech-to-text transcription (Google Cloud Speech-to-Text)
    - Pronunciation similarity calculation (phonetic matching)
    - Detailed feedback on pronunciation quality
    - Confidence scoring for recognized words

Usage:
    GET /api/v1/phonetics/phrase?target_language=...&level=...
    POST /api/v1/phonetics/evaluate (multipart form data with audio file)
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.phonetics import evaluate_pronunciation, generate_target_phrase
from app.schemas.phonetics import PhoneticsEvaluationResponse, PhoneticsPracticeSession

router = APIRouter()


@router.get("/phrase", response_model=PhoneticsPracticeSession)
async def get_practice_phrase(
        target_language: str,
        level: str,
):
    """
    Get a practice phrase for pronunciation training.

    Generates a target phrase tailored to user's language level.
    Phrase includes pronunciation guide and vocabulary context.

    Args:
        target_language: Language for phrase (Spanish, French, etc.)
        level: CEFR level (A1, A2, B1, B2, C1, C2)

    Returns:
        PhoneticsPracticeSession with:
        - phrase: The target phrase to pronounce
        - pronunciation_guide: IPA or phonetic representation
        - vocabulary: Key words and their meanings
        - context: Sentence or scenario using the phrase
        - level: CEFR level of phrase

    Raises:
        HTTPException(500): If generation error

    Example:
        GET /api/v1/phonetics/phrase?target_language=Spanish&level=A1
        Response:
        {
            "phrase": "Buenos días, ¿cómo estás?",
            "pronunciation_guide": "[BWEH-nos DEE-ahs, KOH-moh es-TAHS]",
            "vocabulary": {
                "buenos": "good",
                "días": "days/mornings",
                "cómo": "how"
            },
            "context": "Greeting someone in the morning",
            "level": "A1"
        }
    """


@router.post("/evaluate", response_model=PhoneticsEvaluationResponse)
async def evaluate_audio(
        user_id: str = Form(...),
        target_language: str = Form(...),
        target_phrase: str = Form(...),
        audio_file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    """
    Evaluate pronunciation in submitted audio file.

    Transcribes audio using Google Cloud Speech-to-Text, compares to target
    phrase, and provides detailed pronunciation feedback. Supports MP3, WAV, OGG.

    Args:
        user_id: User identifier (form field)
        target_language: Language of audio (form field)
        target_phrase: Expected phrase pronunciation (form field)
        audio_file: Audio file upload (MP3, WAV, OGG - max 10MB)
        db: Database session (injected)

    Returns:
        PhoneticsEvaluationResponse with:
        - transcription: What the speech-to-text recognized
        - target_phrase: The target phrase (echoed)
        - similarity_score: Pronunciation match (0.0-1.0)
        - confidence: Confidence in transcription (0.0-1.0)
        - word_breakdown: Per-word pronunciation analysis
        - feedback: Detailed improvement suggestions
        - overall_score: Pronunciation quality (0-100)

    Raises:
        HTTPException(400): If file format unsupported or file too large
        HTTPException(500): If transcription or comparison error

    Side Effects:
        - Records evaluation in database
        - Updates user's phonetics module progress
        - Stores audio transcription for later review

    Example:
        POST /api/v1/phonetics/evaluate
        Form data:
        - user_id: "maria"
        - target_language: "Spanish"
        - target_phrase: "Buenos días, ¿cómo estás?"
        - audio_file: [binary audio data]

        Response:
        {
            "transcription": "Buenos días, cómo estás",
            "target_phrase": "Buenos días, ¿cómo estás?",
            "similarity_score": 0.92,
            "confidence": 0.88,
            "word_breakdown": [
                {
                    "word": "Buenos",
                    "match": true,
                    "confidence": 0.95
                },
                {
                    "word": "días",
                    "match": true,
                    "confidence": 0.90
                }
            ],
            "feedback": "Good pronunciation! Remember the upside-down ¿ at start.",
            "overall_score": 92
        }
    """