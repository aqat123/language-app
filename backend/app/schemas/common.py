"""
Common API Schemas and Response Wrappers.

Shared Pydantic models for standard API responses and error handling.
Provides consistent response structure across all API endpoints.

Models:
    APIError: Standardized error response structure
    APIResponse: Generic wrapper for success and error responses
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, TypeVar, Generic

T = TypeVar('T')


class APIError(BaseModel):
    """
    Standard Error Response Model.

    Provides consistent error information across all API endpoints including
    error code, message, and optional details for debugging.
    """
    code: str = Field(..., description="Error code identifier (e.g., 'VALIDATION_ERROR')")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error context and debugging info")


class APIResponse(BaseModel, Generic[T]):
    """
    Generic API Response Wrapper Model.

    Wraps all API responses (success or error) in a consistent structure for
    predictable client-side handling. Supports generic type parameter for
    type-safe success data.
    """
    success: bool = Field(..., description="Whether request succeeded (true) or failed (false)")
    data: Optional[T] = Field(None, description="Response data on success (null on error)")
    error: Optional[APIError] = Field(None, description="Error details on failure (null on success)")

    @classmethod
    def success_response(cls, data: T):
        """
        Create a success response.

        Convenience method to create a properly formatted success response with data.

        Args:
            data: The response data to wrap (type T)

        Returns:
            APIResponse[T]: Success response with data and no error
        """
        return cls(success=True, data=data, error=None)

    @classmethod
    def error_response(cls, code: str, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Create an error response.

        Convenience method to create a properly formatted error response with
        error code, message, and optional details.

        Args:
            code: Error code identifier (VALIDATION_ERROR, NOT_FOUND, etc.)
            message: Human-readable error message
            details: Optional dict with additional error context

        Returns:
            APIResponse[T]: Error response with error object and no data
        """
        return cls(
            success=False,
            data=None,
            error=APIError(code=code, message=message, details=details)
        )
