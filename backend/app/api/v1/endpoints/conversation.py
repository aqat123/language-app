"""
Conversation Module Endpoints.

REST API for conversational language learning.
Provides stateful chat endpoints for practicing target language.

Main Functions:
    start_conversation_endpoint: Initiate new conversation session
    send_message_endpoint: Send message and get AI response

Workflow:
    1. POST /start -> Create session, get opening message from AI
    2. POST /{session_id}/message -> Send message, get AI reply
    3. Repeat step 2 for multi-turn conversation

Usage:
    POST /api/v1/conversation/start
    POST /api/v1/conversation/{session_id}/message
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.conversation import (
    ConversationStartRequest,
    ConversationStartResponse,
    ConversationMessageRequest,
    ConversationMessageResponse
)
from app.services.conversation import start_conversation, send_message

router = APIRouter()


@router.post("/start", response_model=ConversationStartResponse)
async def start_conversation_endpoint(
    request: ConversationStartRequest,
    db: Session = Depends(get_db)
):
    """
    Start a new conversation session with AI tutor.

    Creates a stateful conversation session and generates opening message
    from AI tutor in the target language.

    Args:
        request: ConversationStartRequest containing:
            - user_id: User identifier (username)
            - target_language: Language for conversation (Spanish, French, etc.)
            - level: CEFR level (A1, A2, B1, B2, C1, C2)
            - topic: Optional conversation topic (food, travel, etc.)
        db: Database session (injected)

    Returns:
        ConversationStartResponse with:
        - session_id: Unique session identifier for subsequent messages
        - opening_message: AI tutor's opening message in target language

    Raises:
        HTTPException(500): If AI generation or database error

    Example:
        POST /api/v1/conversation/start
        {
            "user_id": "maria",
            "target_language": "Spanish",
            "level": "A1",
            "topic": "food"
        }
        Response:
        {
            "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
            "opening_message": "¡Hola! ¿Cuál es tu comida favorita?"
        }
    """
    try:
        return await start_conversation(request, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/message", response_model=ConversationMessageResponse)
async def send_message_endpoint(
    session_id: str,
    request: ConversationMessageRequest,
    db: Session = Depends(get_db)
):
    """
    Send a message in an active conversation session.

    Processes user message, validates session, sends to AI tutor service,
    and returns AI response. Maintains conversation context across messages
    for coherent multi-turn dialogue.

    Args:
        session_id: UUID of active conversation session (path parameter)
        request: ConversationMessageRequest containing:
            - user_message: User's message in target language (string)
        db: Database session (injected)

    Returns:
        ConversationMessageResponse with:
        - session_id: Session identifier (echoed)
        - user_message: User's original message
        - ai_response: AI tutor's reply in target language
        - message_count: Total messages in this session

    Raises:
        HTTPException(404): If session_id not found
        HTTPException(500): If AI generation or database error

    Side Effects:
        - Persists message pair to database conversation_sessions table
        - Updates user's conversation progress

    Example:
        POST /api/v1/conversation/{session_id}/message
        {
            "user_message": "Me gusta la pizza"
        }
        Response:
        {
            "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
            "user_message": "Me gusta la pizza",
            "ai_response": "¡Qué bien! ¿Con qué ingredientes la prefieres?",
            "message_count": 2
        }
    """
    try:
        return await send_message(session_id, request, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
