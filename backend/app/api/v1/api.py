"""
API v1 Router Configuration Module.

Central aggregator for all v1 API endpoints. Combines routers from individual
learning modules (conversation, vocabulary, grammar, writing, phonetics) and
authentication/health endpoints into a single router with appropriate prefixes
and OpenAPI tags for documentation.

Route Structure:
    /health, /users/* -> health check & user management
    /conversation/* -> conversational practice endpoints
    /vocabulary/* -> flashcard vocabulary endpoints
    /grammar/* -> grammar exercise endpoints
    /writing/* -> writing feedback endpoints
    /phonetics/* -> pronunciation practice endpoints
"""

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

# Include all endpoint routers with their respective prefixes and OpenAPI tags
# Health check endpoint (no prefix)
api_router.include_router(greeting.router, tags=["health"])
# User authentication and management (no prefix)
api_router.include_router(auth.router, tags=["auth"])
# Learning module routers (each with /module_name prefix)
api_router.include_router(conversation.router, prefix="/conversation", tags=["conversation"])
api_router.include_router(vocabulary.router, prefix="/vocabulary", tags=["vocabulary"])
api_router.include_router(grammar.router, prefix="/grammar", tags=["grammar"])
api_router.include_router(writing.router, prefix="/writing", tags=["writing"])
api_router.include_router(phonetics.router, prefix="/phonetics", tags=["phonetics"])
