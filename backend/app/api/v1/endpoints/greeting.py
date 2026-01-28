"""
Greeting and Health Check Endpoints.

Provides basic endpoints for verifying backend availability and connectivity.
Used by frontend/mobile app to check if API is running.

Main Functions:
    health_check: Server health status
    greeting: Welcome message from backend

Usage:
    GET /api/v1/greeting/health -> {"status": "ok"}
    GET /api/v1/greeting/ -> {"message": "Hello..."}
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint for backend availability.

    Returns basic status to verify API is running and responsive.
    Used by frontend to ensure backend connectivity.

    Returns:
        Dict with status field

    Example:
        >>> response = GET /api/v1/greeting/health
        >>> response.json()
        {"status": "ok"}
    """
    return {"status": "ok"}


@router.get("/")
async def greeting():
    """
    Welcome message endpoint.

    Returns a greeting message from the backend. Useful for testing
    that the API is accessible and responding to requests.

    Returns:
        Dict with greeting message

    Example:
        >>> response = GET /api/v1/greeting/
        >>> response.json()
        {"message": "Hello from the Language Learning Backend!"}
    """
    return {"message": "Hello from the Language Learning Backend!"}
