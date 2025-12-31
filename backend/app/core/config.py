from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/language_app"

    # LLM API Configuration
    LLM_API_KEY: str
    LLM_API_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"
    LLM_MODEL: str = "gemini-1.5-flash"

    # Speech-to-Text API Configuration
    STT_API_KEY: str
    STT_API_BASE_URL: str = "https://speech.googleapis.com/v1"

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
