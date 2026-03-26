"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings object populated from the environment or .env file.

    Attributes:
        database_url: SQLAlchemy-compatible PostgreSQL connection string.
        app_env: Deployment environment label (development / production).
        log_level: Minimum log severity level forwarded to loguru.
        prefect_api_url: Base URL of the Prefect server API.
        cors_origins: List of allowed CORS origins for the FastAPI middleware.
        app_name: Human-readable application name used in API metadata.
        app_version: Semantic version string surfaced in /health and OpenAPI.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    database_url: str = "postgresql://etl_user:etl_password@localhost:5432/etl_db"
    app_env: str = "development"
    log_level: str = "INFO"
    prefect_api_url: str = "http://localhost:4200/api"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    app_name: str = "ETL Orchestrator"
    app_version: str = "1.0.0"


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings singleton.

    Returns:
        A fully populated Settings instance.
    """
    return Settings()
