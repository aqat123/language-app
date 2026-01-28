"""
Writing Module Endpoints.

REST API for writing practice and feedback.
Provides endpoints for AI-powered writing correction and improvement.

Main Functions:
    get_feedback: Submit text for correction and receive detailed feedback

Features:
    - Grammar and spelling corrections
    - Vocabulary suggestions for natural expression
    - Style and tone analysis
    - Confidence-based feedback (identifies low/high confidence areas)

Workflow:
    1. POST /feedback -> Submit essay or paragraph
    2. Receive: corrections, suggestions, confidence ratings
    3. User revises based on feedback

Usage:
    POST /api/v1/writing/feedback
"""

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
    """
    Get writing feedback for submitted text.

    Analyzes submitted text for grammar, spelling, vocabulary, and style.
    Uses AI to identify errors, suggest corrections, and rate confidence
    in feedback. Sanitizes output to prevent injection attacks.

    Args:
        request: WritingFeedbackRequest containing:
            - user_id: User identifier (username)
            - target_language: Language for writing (Spanish, French, etc.)
            - text: The text to analyze (essay, paragraph, or sentence)
            - level: Optional CEFR level for context-aware feedback
        db: Database session (injected)

    Returns:
        WritingFeedbackResponse with:
        - original_text: User's submitted text (echoed)
        - corrected_text: Text with corrections applied
        - corrections: List of correction objects with:
            * original: Original word/phrase
            * corrected: Suggested correction
            * type: Error type (grammar, spelling, vocabulary)
            * explanation: Reason for correction
            * confidence: Confidence score (0.0-1.0)
        - suggestions: List of improvement suggestions
        - overall_score: Text quality score (0-100)

    Raises:
        HTTPException(400): If text exceeds max length (5000 chars)
        HTTPException(500): If AI analysis or database error

    Side Effects:
        - Records submission in content_logs database table
        - Updates user's writing module progress
        - Stores corrections for learning analytics

    Example:
        POST /api/v1/writing/feedback
        {
            "user_id": "maria",
            "target_language": "Spanish",
            "text": "Ayer yo fuí al parque con mis amigos",
            "level": "B1"
        }
        Response:
        {
            "original_text": "Ayer yo fuí al parque con mis amigos",
            "corrected_text": "Ayer fui al parque con mis amigos",
            "corrections": [
                {
                    "original": "fuí",
                    "corrected": "fui",
                    "type": "spelling",
                    "explanation": "Accent unnecessary on one-syllable word",
                    "confidence": 0.95
                },
                {
                    "original": "yo",
                    "corrected": "[remove]",
                    "type": "grammar",
                    "explanation": "Subject pronoun implicit in conjugation",
                    "confidence": 0.85
                }
            ],
            "suggestions": ["Consider adding object pronouns for clarity"],
            "overall_score": 82
        }
    """
    try:
        return await get_writing_feedback(request, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
