import sys
from pathlib import Path
from loguru import logger
from app.core.config import get_settings


def configurar_logger():
    settings = get_settings()

    logger.remove()

    logger.add(
        sys.stdout,
        level=settings.log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        colorize=True,
        enqueue=True,
    )

    Path("logs").mkdir(exist_ok=True)
    logger.add(
        "logs/etl_{time:YYYY-MM-DD}.log",
        level=settings.log_level,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        ),
        rotation="00:00",
        retention="30 days",
        compression="zip",
        enqueue=True,
        serialize=False,
    )

    logger.add(
        "logs/etl_errors.log",
        level="ERROR",
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        ),
        rotation="50 MB",
        retention="60 days",
        enqueue=True,
    )

    return logger
