from pydantic import BaseModel
from typing import Optional, List


class GrammarQuestionResponse(BaseModel):
    """Response containing a grammar question."""
    question_id: str
    question_text: str
    options: List[str]
    correct_option_index: int
    explanation: Optional[str] = None


class GrammarAnswerRequest(BaseModel):
    """Request to submit a grammar answer."""
    user_id: str
    question_id: str
    selected_option_index: int
    correct_option_index: int
    explanation: Optional[str] = None


class GrammarAnswerResponse(BaseModel):
    """Response to a grammar answer submission."""
    is_correct: bool
    correct_option_index: int
    explanation: str
