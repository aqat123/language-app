from pydantic import BaseModel
from typing import Optional


class WritingFeedbackRequest(BaseModel):
    """Request for writing feedback."""
    user_id: str
    target_language: str
    level: Optional[str] = None
    text: str


class WritingFeedbackResponse(BaseModel):
    """Response with writing feedback."""
    corrected_text: str
    overall_comment: str
    inline_explanation: Optional[str] = None
    score: Optional[float] = None
