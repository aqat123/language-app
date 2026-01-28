"""
Pronunciation Practice Schemas.

Pydantic models for phonetics and pronunciation evaluation.
Includes speech-to-text transcription and pronunciation quality assessment.

Models:
    PhoneticsPracticeSession: Practice phrase with pronunciation guide
    WordIssue: Pronunciation feedback for individual words
    PhoneticsEvaluationResponse: Comprehensive pronunciation analysis
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class PhoneticsPracticeSession(BaseModel):
    """
    Pronunciation Practice Session Model.

    Contains a target phrase and session ID for pronunciation practice.
    User records themselves pronouncing the phrase for evaluation.
    """
    session_id: str = Field(..., description="Unique practice session identifier")
    target_phrase: str = Field(..., description="Phrase to practice pronouncing")


class WordIssue(BaseModel):
    """
    Word-Level Pronunciation Feedback Model.

    Provides detailed feedback on pronunciation quality for a specific word,
    including identified issues and tips for improvement.
    """
    word: str = Field(..., description="Word being evaluated")
    issue: str = Field(..., description="Description of pronunciation issue (if any)")
    tip: str = Field(..., description="Suggestion for improvement")


class PhoneticsEvaluationResponse(BaseModel):
    """
    Pronunciation Evaluation Response Model.

    Returns comprehensive pronunciation analysis including transcription,
    similarity score, and detailed word-by-word feedback.
    """
    transcript: str = Field(..., description="Speech-to-text transcription of user's audio")
    stt_confidence: float = Field(..., description="Confidence score of transcription (0.0-1.0)")
    score: float = Field(..., description="Overall pronunciation quality score (0-100)")
    feedback: str = Field(..., description="Overall feedback and suggestions for improvement")
    word_level_feedback: Optional[List[WordIssue]] = Field(None, description="Per-word pronunciation analysis")