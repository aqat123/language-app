"""
Writing Practice Schemas.

Pydantic models for writing exercises with AI-powered feedback.
Provides correction and improvement suggestions for written text.

Models:
    WritingFeedbackRequest: Text submission for analysis and correction
    WritingFeedbackResponse: Comprehensive writing feedback and corrections
"""

from pydantic import BaseModel, Field
from typing import Optional


class WritingFeedbackRequest(BaseModel):
    """
    Writing Feedback Request Model.

    Submits text for AI analysis including grammar checking, spelling correction,
    vocabulary suggestions, and style feedback.
    """
    user_id: str = Field(..., description="User identifier (username)")
    target_language: str = Field(..., description="Language of text (Spanish, French, etc.)")
    level: Optional[str] = Field(None, description="CEFR level for context-aware feedback")
    text: str = Field(..., description="Essay or paragraph to analyze (max 5000 chars)")


class WritingFeedbackResponse(BaseModel):
    """
    Writing Feedback Response Model.

    Returns comprehensive analysis with corrections, suggestions, and overall
    quality score. Provides detailed feedback for writing improvement.
    """
    corrected_text: str = Field(..., description="Text with corrections applied")
    overall_comment: str = Field(..., description="Overall assessment of writing quality")
    inline_explanation: Optional[str] = Field(None, description="Detailed explanation of corrections")
    score: Optional[float] = Field(None, description="Writing quality score (0-100)")
