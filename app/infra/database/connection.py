"""Database engine factory and schema initialisation utilities."""

from functools import lru_cache

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.infra.database.models import Base


@lru_cache
def get_engine() -> Engine:
    """Return the cached SQLAlchemy engine instance.

    The engine is created once and reused for the lifetime of the process.
    Connection pool parameters are tuned for a small-to-medium workload.

    Returns:
        A configured SQLAlchemy Engine connected to the application database.
    """
    settings = get_settings()
    engine = create_engine(
        settings.database_url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        echo=False,
    )
    return engine


def get_session() -> Session:
    """Create and return a new database session.

    The caller is responsible for closing the session after use.

    Returns:
        An unbound SQLAlchemy Session connected to the application engine.
    """
    engine = get_engine()
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return session_factory()


def init_db() -> None:
    """Create all ORM-mapped tables if they do not already exist.

    Safe to call multiple times; existing tables are not modified.
    """
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialised — tables created/verified.")
