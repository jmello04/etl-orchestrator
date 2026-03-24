from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
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
    return Settings()
