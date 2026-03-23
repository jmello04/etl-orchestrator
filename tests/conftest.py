import pytest
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infra.database.models import Base


@pytest.fixture(scope="session")
def engine_teste():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def session_teste(engine_teste):
    Session = sessionmaker(bind=engine_teste)
    session = Session()
    yield session
    session.rollback()
    session.close()


MOCK_RESPOSTA_USD = [
    {
        "code": "USD",
        "codein": "BRL",
        "bid": "5.1234",
        "ask": "5.1350",
        "high": "5.1500",
        "low": "5.1100",
        "timestamp": "1700000000",
    },
    {
        "code": "USD",
        "codein": "BRL",
        "bid": "5.2000",
        "ask": "5.2150",
        "high": "5.2300",
        "low": "5.1900",
        "timestamp": "1700086400",
    },
]

MOCK_RESPOSTA_EUR = [
    {
        "code": "EUR",
        "codein": "BRL",
        "bid": "5.5500",
        "ask": "5.5700",
        "high": "5.5900",
        "low": "5.5300",
        "timestamp": "1700000000",
    },
]
