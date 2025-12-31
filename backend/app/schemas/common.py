from pydantic import BaseModel
from typing import Optional, Dict, Any, TypeVar, Generic

T = TypeVar('T')


class APIError(BaseModel):
    """Standard error response structure."""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    success: bool
    data: Optional[T] = None
    error: Optional[APIError] = None

    @classmethod
    def success_response(cls, data: T):
        """Create a success response."""
        return cls(success=True, data=data, error=None)

    @classmethod
    def error_response(cls, code: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Create an error response."""
        return cls(
            success=False,
            data=None,
            error=APIError(code=code, message=message, details=details)
        )
