from fastapi import APIRouter
from app.api.v1.endpoints import (
    greeting,
    auth,
    conversation,
    vocabulary,
    grammar,
    writing,
    phonetics
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(greeting.router, tags=["health"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(conversation.router, prefix="/conversation", tags=["conversation"])
api_router.include_router(vocabulary.router, prefix="/vocabulary", tags=["vocabulary"])
api_router.include_router(grammar.router, prefix="/grammar", tags=["grammar"])
api_router.include_router(writing.router, prefix="/writing", tags=["writing"])
api_router.include_router(phonetics.router, prefix="/phonetics", tags=["phonetics"])
