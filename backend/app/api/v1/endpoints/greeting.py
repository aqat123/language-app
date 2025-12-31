from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@router.get("/")
async def greeting():
    """Simple greeting endpoint."""
    return {"message": "Hello from the Language Learning Backend!"}
