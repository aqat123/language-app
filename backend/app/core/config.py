"""
Application Configuration Management.

Loads and manages all application settings from environment variables using
Pydantic Settings. Supports multiple environments (dev, staging, production)
with environment-specific defaults.

Configuration Categories:
    - Database: PostgreSQL/SQLite connection URL
    - LLM API: Gemini API for content generation (gemini-2.5-flash)
    - Image API: Imagen 4.0 for vocabulary image generation
    - STT API: Google Cloud Speech-to-Text configuration
    - Application: FastAPI settings, CORS, debug mode
    - Environment: Dev/production mode flags

Environment Variables:
    All settings are loaded from .env file or system environment variables.
    Required: DATABASE_URL, LLM_API_KEY, LLM_IMAGE_API_KEY, STT_API_KEY
    Optional: Defaults provided for API endpoints and models

Usage:
    from app.core.config import settings

    # Access settings anywhere in application
    db_url = settings.DATABASE_URL
    api_key = settings.LLM_API_KEY
    debug = settings.DEBUG
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application Settings Configuration.

    Centralized configuration for all environment variables. Uses Pydantic
    BaseSettings for validation and type conversion. Automatically loads from
    .env file in project root.

    Attributes:
        DATABASE_URL: SQLAlchemy database connection URL (required)
            Format: postgresql://user:pass@host:port/db or sqlite:///path
        LLM_API_KEY: Google Gemini API key for content generation (required)
        LLM_API_BASE_URL: Gemini API endpoint
        LLM_MODEL: Model version (gemini-2.5-flash)
        LLM_IMAGE_API_KEY: Google Imagen API key (required)
        LLM_IMAGE_API_BASE_URL: Imagen API endpoint
        LLM_IMAGE_MODEL: Image generation model (imagen-4.0-generate-001)
        STT_API_KEY: Google Cloud Speech-to-Text API key (required)
        STT_API_BASE_URL: Speech-to-Text API endpoint
        STT_MODEL: STT model version (gemini-2.5-flash)
        ENV: Environment name (dev, staging, prod)
        DEBUG: Enable debug logging and error details
        API_V1_PREFIX: API route prefix (/api/v1)
        PROJECT_NAME: Application name for OpenAPI docs
        BACKEND_CORS_ORIGINS: Allowed CORS origins (list)
    """

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/language_app"

    # LLM API Configuration
    LLM_API_KEY: str
    LLM_API_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"
    LLM_MODEL: str = "gemini-2.5-flash"

    # Image Generation API Configuration (Legacy - not used with Vertex AI)
    LLM_IMAGE_API_KEY: str = ""
    LLM_IMAGE_API_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"
    LLM_IMAGE_MODEL: str = "imagen-4.0-generate-001"

    # Vertex AI Configuration for Imagen
    VERTEX_AI_PROJECT_ID: Optional[str] = None
    VERTEX_AI_LOCATION: str = "us-central1"
    VERTEX_AI_CREDENTIALS_PATH: str = "credentials/service-account-key.json"
    USE_VERTEX_AI: bool = False  # Set to True to enable Vertex AI images

    # Speech-to-Text API Configuration
    STT_API_KEY: str
    STT_API_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"
    STT_MODEL: str = "gemini-2.5-flash"

    # Application Configuration
    ENV: str = "dev"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Language Learning Backend"

    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
