"""
Vocabulary Module Endpoints.

REST API for vocabulary learning flashcards.
Provides endpoints to generate vocabulary flashcards and submit answers.

Main Functions:
    get_flashcard: Generate new vocabulary flashcard
    submit_answer: Submit flashcard answer and get feedback

Workflow:
    1. GET /next -> Receive flashcard with word and options
    2. User selects answer in frontend
    3. POST /answer -> Submit answer, get score and explanation

Usage:
    GET /api/v1/vocabulary/next?user_id=maria&target_language=Spanish&level=A1
    POST /api/v1/vocabulary/answer
"""

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
    """
    Generate next vocabulary flashcard for user.

    Creates an AI-generated vocabulary word with definition and 4 multiple-choice options.
    Avoids recently shown words to prevent repetition.

    Args:
        user_id: User identifier (username)
        target_language: Target language (Spanish, French, German, etc.)
        level: CEFR level (A1, A2, B1, B2, C1, C2) - optional, defaults to A1
        db: Database session (injected)

    Returns:
        FlashcardResponse containing:
        - word: Target language vocabulary word
        - definition: English definition
        - example_sentence: Example usage in target language
        - options: 4 English definitions (1 correct, 3 distractors)
        - correct_option_index: Index of correct answer (0-3)
        - image_data: Base64 encoded vocabulary image (optional)

    Raises:
        HTTPException(500): If AI generation fails or service error

    Example:
        GET /api/v1/vocabulary/next?user_id=maria&target_language=Spanish&level=A1
        Response:
        {
            "word": "Gato",
            "definition": "Cat",
            "example_sentence": "El gato es muy bonito.",
            "options": ["Cat", "Dog", "Bird", "Fish"],
            "correct_option_index": 0,
            "image_data": "base64_image_string"
        }
    """
    try:
        return await get_next_flashcard(user_id, target_language, level, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answer", response_model=VocabularyAnswerResponse)
async def submit_answer(
    request: VocabularyAnswerRequest,
    db: Session = Depends(get_db)
):
    """
    Submit vocabulary answer and receive feedback.

    Records user's answer choice and updates progress statistics.
    Returns whether answer was correct with explanation.

    Args:
        request: VocabularyAnswerRequest containing:
            - user_id: User identifier
            - selected_option_index: Index of selected answer (0-3)
            - correct_option_index: Index of correct answer (for validation)
        db: Database session (injected)

    Returns:
        VocabularyAnswerResponse with:
        - is_correct: Whether answer was correct (bool)
        - correct_option_index: Index of correct answer
        - explanation: Brief feedback (correct message or hint)

    Raises:
        HTTPException(404): If user not found
        HTTPException(500): If service error

    Side Effects:
        Updates user_progress table with new statistics

    Example:
        POST /api/v1/vocabulary/answer
        {
            "user_id": "maria",
            "selected_option_index": 0,
            "correct_option_index": 0
        }
        Response:
        {
            "is_correct": true,
            "correct_option_index": 0,
            "explanation": "Correct!"
        }
    """
    try:
        return await submit_vocabulary_answer(request, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
