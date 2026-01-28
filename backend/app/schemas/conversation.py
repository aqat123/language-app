"""
Conversation Practice Schemas.

Pydantic models for conversational language learning with AI tutor.
Supports multi-turn conversations with session management.

Models:
    ConversationStartRequest: Initialize new conversation session
    ConversationStartResponse: Confirm session creation with opening message
    ConversationMessageRequest: Send message in active conversation
    ConversationMessageResponse: AI tutor's reply with corrections and tips
"""

from pydantic import BaseModel, Field
from typing import Optional


class ConversationStartRequest(BaseModel):
    """
    Conversation Session Start Request Model.

    Initiates a new conversation session with AI tutor. Specifies language,
    level, and optional topic to tailor the conversation to user's needs.
    """
    user_id: str = Field(..., description="User identifier (username)")
    target_language: str = Field(..., description="Language for conversation (Spanish, French, etc.)")
    level: Optional[str] = Field(None, description="CEFR level (A1, A2, B1, B2, C1, C2)")
    topic: Optional[str] = Field(None, description="Conversation topic (food, travel, etc.)")


class ConversationStartResponse(BaseModel):
    """
    Conversation Session Start Response Model.

    Confirms session creation and provides AI tutor's opening message in the
    target language to start the conversation.
    """
    session_id: str = Field(..., description="Unique conversation session ID")
    opening_message: str = Field(..., description="AI tutor's opening message in target language")


class ConversationMessageRequest(BaseModel):
    """
    Conversation Message Request Model.

    Sends user's message in an active conversation session. User sends text
    in the target language for practice.
    """
    user_id: str = Field(..., description="User identifier (username)")
    message: str = Field(..., description="User's message in target language")


class ConversationMessageResponse(BaseModel):
    """
    Conversation Message Response Model.

    Returns AI tutor's reply with optional corrections and learning tips.
    Provides immediate feedback to improve language learning in context.
    """
    reply: str = Field(..., description="AI tutor's response message")
    corrected_user_message: Optional[str] = Field(None, description="Corrected version of user's message")
    tips: Optional[str] = Field(None, description="Grammar, vocabulary, or pronunciation tips")
    session_id: str = Field(..., description="Session ID (echoed for verification)")
