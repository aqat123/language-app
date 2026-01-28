"""
Grammar Exercise Schemas.

Pydantic models for grammar question generation and answer evaluation.
Supports multiple-choice grammar exercises with explanations.

Models:
    GrammarQuestionResponse: Grammar exercise question with options
    GrammarAnswerRequest: User's grammar answer submission
    GrammarAnswerResponse: Evaluation result with explanation
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class ValidationMetadata(BaseModel):
    """Metadata about content validation."""
    is_validated: bool
    confidence_score: Optional[float] = None
    primary_check_passed: Optional[bool] = None
    secondary_check_passed: Optional[bool] = None


class GrammarQuestionResponse(BaseModel):
    """
    Grammar Question Response Model.

    Returns a grammar exercise question with multiple-choice options and
    educational explanation of the grammar rule.
    """
    question_id: str = Field(..., description="Unique question identifier")
    question_text: str = Field(..., description="Grammar question prompt")
    options: List[str] = Field(..., description="Four answer options for multiple-choice")
    correct_option_index: int = Field(..., description="Index of correct answer (0-3)")
    explanation: Optional[str] = Field(None, description="Grammar rule explanation")
    validation: Optional[ValidationMetadata] = None


class GrammarAnswerRequest(BaseModel):
    """
    Grammar Answer Submission Model.

    Captures user's response to a grammar question with the question ID and
    both selected and correct answers for validation and learning.
    """
    user_id: str = Field(..., description="User identifier (username)")
    question_id: str = Field(..., description="ID of question being answered")
    selected_option_index: int = Field(..., description="User's selected answer (0-3)")
    correct_option_index: int = Field(..., description="Correct answer index (0-3)")
    explanation: Optional[str] = Field(None, description="Optional grammar rule explanation")


class GrammarAnswerResponse(BaseModel):
    """
    Grammar Answer Evaluation Response Model.

    Returns evaluation result with the correct answer and detailed explanation
    to help user understand the grammar concept.
    """
    is_correct: bool = Field(..., description="Whether answer was correct")
    correct_option_index: int = Field(..., description="Index of correct answer")
    explanation: str = Field(..., description="Detailed explanation of grammar rule")
