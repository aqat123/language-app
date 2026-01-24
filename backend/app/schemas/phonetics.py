from pydantic import BaseModel
from typing import Optional, List, Dict

class PhoneticsPracticeSession(BaseModel):
    """Response model for generating a practice phrase."""
    session_id: str
    target_phrase: str

class WordIssue(BaseModel):
    """Details about pronunciation issues for a specific word."""
    word: str
    issue: str
    tip: str

class PhoneticsEvaluationResponse(BaseModel):
    """Response with pronunciation evaluation results."""
    transcript: str
    stt_confidence: float # Gemini returns 'confidence' inside the JSON now
    score: float
    feedback: str
    # Changed from Dict to List[WordIssue] to match STTClient output
    word_level_feedback: Optional[List[WordIssue]] = None