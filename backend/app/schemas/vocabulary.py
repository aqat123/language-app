from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ValidationMetadata(BaseModel):
    """Metadata about content validation."""
    is_validated: bool
    confidence_score: Optional[float] = None
    primary_check_passed: Optional[bool] = None
    secondary_check_passed: Optional[bool] = None


class FlashcardResponse(BaseModel):
    """Response containing a vocabulary flashcard."""
    word: str
    definition: str
    example_sentence: str
    options: Optional[List[str]] = None
    correct_option_index: Optional[int] = None
    image_data: Optional[str] = None
    validation: Optional[ValidationMetadata] = None


class VocabularyAnswerRequest(BaseModel):
    """Request to submit a vocabulary answer."""
    user_id: str
    word: str
    selected_option_index: int
    correct_option_index: int


class VocabularyAnswerResponse(BaseModel):
    """Response to a vocabulary answer submission."""
    is_correct: bool
    correct_option_index: int
    explanation: Optional[str] = None
