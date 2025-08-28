import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Consolidated application settings.
    Reads settings from environment variables and .env file.
    """

    # pydantic-settings configuration (Pydantic v2 style)
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Application Config
    APP_NAME: str = "NoBroker API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Property rental platform API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # LLM Config
    GEMINI_API_KEY: str
    GROQ_API_KEY: str
    LLM_MODEL: str
    OPENAI_API_KEY: str


    # Database Config (prefer DATABASE_URL; otherwise build from parts if provided)
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DATABASE_URL: Optional[str] = None

    # Connection pool settings
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # JWT Settings
    SECRET_KEY: str  # required; supply via env/.env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ADK Web Server Config
    ADK_WEB_PORT: int  # Default to 8001 to avoid conflict with FastAPI on 8000

    def model_post_init(self, __context: object) -> None:
        # If DATABASE_URL is not supplied, try to construct it from parts
        if not self.DATABASE_URL:
            if all([self.DB_HOST, self.DB_PORT, self.DB_NAME, self.DB_USER, self.DB_PASSWORD]):
                # Prefer psycopg2 driver when targeting Postgres
                self.DATABASE_URL = (
                    f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
                    f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
                )
            else:
                # Fallback to a local SQLite DB to allow app to boot without secrets
                self.DATABASE_URL = "sqlite:///./app.db"

# Single settings instance to be used across the application
settings = Settings()