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
    """Start a new conversation session."""
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
    """Send a message in a conversation session."""
    try:
        return await send_message(session_id, request, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
