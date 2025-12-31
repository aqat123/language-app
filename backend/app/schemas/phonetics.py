from pydantic import BaseModel
from typing import Optional, Dict


class PhoneticsEvaluationResponse(BaseModel):
    """Response with pronunciation evaluation results."""
    transcript: str
    stt_confidence: float
    score: float
    feedback: str
    word_level_feedback: Optional[Dict[str, str]] = None
