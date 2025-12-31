from pydantic import BaseModel
from typing import Optional


class ConversationStartRequest(BaseModel):
    """Request to start a new conversation session."""
    user_id: str
    target_language: str
    level: Optional[str] = None
    topic: Optional[str] = None


class ConversationStartResponse(BaseModel):
    """Response when starting a new conversation."""
    session_id: str
    opening_message: str


class ConversationMessageRequest(BaseModel):
    """Request to send a message in a conversation."""
    user_id: str
    message: str


class ConversationMessageResponse(BaseModel):
    """Response to a conversation message."""
    reply: str
    corrected_user_message: Optional[str] = None
    tips: Optional[str] = None
    session_id: str
