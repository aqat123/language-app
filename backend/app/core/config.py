from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

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
