"""
Grammar Module Endpoints.

REST API for grammar exercise learning.
Provides endpoints for generating grammar questions and evaluating answers.

Main Functions:
    get_question: Retrieve a grammar exercise question
    submit_answer: Submit answer to grammar question

Workflow:
    1. GET /question -> Receive grammar question (multiple choice)
    2. POST /answer -> Submit selected answer, get feedback

Features:
    - AI-generated grammar questions targeted to user level
    - Instant evaluation with explanation of correct answer
    - Progress tracking integrated with user profile

Usage:
    GET /api/v1/grammar/question?user_id=...&target_language=...
    POST /api/v1/grammar/answer
"""

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
    """
    Get a grammar exercise question.

    Generates AI-created grammar question adapted to user's level.
    Question type includes multiple-choice with 4 options and explanation.

    Args:
        user_id: User identifier (username)
        target_language: Language for question (Spanish, French, etc.)
        level: Optional CEFR level (A1, A2, B1, B2, C1, C2)
            If not provided, uses user's current level from database
        topic: Optional grammar topic filter (tenses, subjunctive, etc.)
        db: Database session (injected)

    Returns:
        GrammarQuestionResponse with:
        - question_id: Unique identifier for this question
        - question_text: Grammar question in English (context)
        - example_sentence: Example sentence in target language
        - options: List of 4 answer choices
        - level: CEFR level of question
        - explanation: Grammar rule explanation

    Raises:
        HTTPException(500): If AI generation or database error

    Example:
        GET /api/v1/grammar/question?user_id=maria&target_language=Spanish&level=A2
        Response:
        {
            "question_id": "q123",
            "question_text": "Fill in the blank with correct preterite form",
            "example_sentence": "Ayer yo ____ al parque.",
            "options": ["fui", "iba", "voy", "iré"],
            "level": "A2",
            "explanation": "Preterite 'fui' indicates completed action in past"
        }
    """
    try:
        return await get_grammar_question(user_id, target_language, level, topic, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answer", response_model=GrammarAnswerResponse)
async def submit_answer(
    request: GrammarAnswerRequest,
    db: Session = Depends(get_db)
):
    """
    Submit answer to grammar question.

    Evaluates submitted answer against correct option, provides detailed
    explanation of grammar rule, and updates user progress.

    Args:
        request: GrammarAnswerRequest containing:
            - question_id: ID of the question being answered
            - user_id: User identifier (username)
            - selected_option: User's selected answer (string)
        db: Database session (injected)

    Returns:
        GrammarAnswerResponse with:
        - question_id: ID of answered question (echoed)
        - is_correct: Boolean indicating if answer was correct
        - correct_answer: The correct option
        - explanation: Detailed explanation of grammar rule
        - detailed_explanation: Extended explanation with examples

    Raises:
        HTTPException(404): If question_id not found
        HTTPException(500): If evaluation or database error

    Side Effects:
        - Records answer in database
        - Updates user's grammar module progress
        - Increments streak if correct, resets if incorrect

    Example:
        POST /api/v1/grammar/answer
        {
            "question_id": "q123",
            "user_id": "maria",
            "selected_option": "fui"
        }
        Response:
        {
            "question_id": "q123",
            "is_correct": true,
            "correct_answer": "fui",
            "explanation": "Preterite 'fui' marks completed action",
            "detailed_explanation": "Use preterite when action is finished..."
        }
    """
    try:
        return await submit_grammar_answer(request, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
