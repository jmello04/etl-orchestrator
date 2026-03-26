"""Application entry point and lifespan management."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.routes.data import router as data_router
from app.api.routes.pipeline import router as pipeline_router
from app.core.config import get_settings
from app.core.logging import configurar_logger
from app.core.middleware import LoggingMiddleware
from app.infra.database.connection import init_db

configurar_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown.

    On startup: logs the environment and initialises the database schema.
    On shutdown: logs the shutdown event.

    Args:
        app: The FastAPI application instance.

    Yields:
        Control to FastAPI while the application is running.
    """
    logger.info(
        f"Starting {settings.app_name} v{settings.app_version} [{settings.app_env}]"
    )
    init_db()
    yield
    logger.info(f"Shutting down {settings.app_name}")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Pipeline ETL orquestrado para cotações financeiras USD-BRL e EUR-BRL.\n\n"
        "Fontes: AwesomeAPI | Destino: PostgreSQL | Orquestrador: Prefect"
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(pipeline_router)
app.include_router(data_router)


@app.get("/health", tags=["Sistema"], summary="Verifica saúde da aplicação")
def health_check() -> dict:
    """Return a simple liveness probe response.

    Returns:
        A dict with status, application version and environment.
    """
    return {
        "status": "ok",
        "versao": settings.app_version,
        "ambiente": settings.app_env,
    }
