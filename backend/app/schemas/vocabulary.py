"""
Vocabulary Learning Schemas.

Pydantic models for flashcard vocabulary exercises. Includes request and response
models for flashcard generation and answer evaluation.

Models:
    FlashcardResponse: Vocabulary flashcard with word and multiple-choice options
    VocabularyAnswerRequest: User's answer submission for a flashcard
    VocabularyAnswerResponse: Evaluation result with feedback
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ValidationMetadata(BaseModel):
    """Metadata about content validation."""
    is_validated: bool
    confidence_score: Optional[float] = None
    primary_check_passed: Optional[bool] = None
    secondary_check_passed: Optional[bool] = None


class FlashcardResponse(BaseModel):
    """
    Vocabulary Flashcard Response Model.

    Returns a complete flashcard with word definition, example sentence, and
    multiple-choice options. Includes optional image data for visual learning.
    """
    word: str = Field(..., description="Target vocabulary word")
    definition: str = Field(..., description="Word definition or explanation")
    example_sentence: str = Field(..., description="Example sentence using the word")
    options: Optional[List[str]] = Field(None, description="Multiple-choice answer options (4 options)")
    correct_option_index: Optional[int] = Field(None, description="Index of correct answer (0-3)")
    image_data: Optional[str] = Field(None, description="Base64-encoded image for word visualization")
    validation: Optional[ValidationMetadata] = None


class VocabularyAnswerRequest(BaseModel):
    """
    Vocabulary Answer Submission Model.

    Captures user's answer to a flashcard exercise including the selected option
    and correct answer for validation.
    """
    user_id: str = Field(..., description="User identifier (username)")
    word: str = Field(..., description="Vocabulary word being answered")
    selected_option_index: int = Field(..., description="User's selected answer index (0-3)")
    correct_option_index: int = Field(..., description="Correct answer index (0-3)")


class VocabularyAnswerResponse(BaseModel):
    """
    Vocabulary Answer Evaluation Response Model.

    Returns whether the answer was correct and provides educational feedback.
    """
    is_correct: bool = Field(..., description="Whether selected answer matches correct answer")
    correct_option_index: int = Field(..., description="Index of correct answer")
    explanation: Optional[str] = Field(None, description="Explanation of correct answer and word usage")
