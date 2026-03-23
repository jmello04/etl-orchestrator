from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger
from functools import lru_cache

from app.core.config import get_settings
from app.infra.database.models import Base


@lru_cache
def get_engine():
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
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return SessionLocal()


def init_db():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    logger.info("Banco de dados inicializado — tabelas criadas/verificadas.")
