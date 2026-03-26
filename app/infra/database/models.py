"""SQLAlchemy ORM models for the ETL Orchestrator domain."""

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base class shared by all ORM models."""


class Cotacao(Base):
    """Stores a single daily exchange-rate observation.

    Each row is uniquely identified by the currency pair and reference date,
    enforced by the ``uq_par_data`` unique constraint.

    Attributes:
        id: Auto-incremented primary key.
        par_moeda: Currency pair label (e.g. "USD-BRL").
        data_referencia: Calendar date the observation refers to.
        compra: Buy (bid) rate for the day.
        venda: Sell (ask) rate for the day.
        maximo: Intraday high.
        minimo: Intraday low.
        media_compra_periodo: Average buy rate over the extracted window.
        media_venda_periodo: Average sell rate over the extracted window.
        minimo_periodo: Minimum rate observed in the extracted window.
        maximo_periodo: Maximum rate observed in the extracted window.
        processado_em: UTC timestamp when the ETL pipeline processed this row.
        criado_em: Database-level insertion timestamp.
    """

    __tablename__ = "cotacoes"
    __table_args__ = (
        UniqueConstraint("par_moeda", "data_referencia", name="uq_par_data"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    par_moeda = Column(String(10), nullable=False, index=True)
    data_referencia = Column(Date, nullable=False, index=True)
    compra = Column(Numeric(12, 4))
    venda = Column(Numeric(12, 4))
    maximo = Column(Numeric(12, 4))
    minimo = Column(Numeric(12, 4))
    media_compra_periodo = Column(Numeric(12, 4))
    media_venda_periodo = Column(Numeric(12, 4))
    minimo_periodo = Column(Numeric(12, 4))
    maximo_periodo = Column(Numeric(12, 4))
    processado_em = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
    criado_em = Column(DateTime, server_default=func.now())

    def to_dict(self) -> dict:
        """Serialise the instance to a plain dictionary.

        Returns:
            Dictionary representation with all fields; Decimal values are
            converted to float and datetime values to ISO 8601 strings.
        """
        return {
            "id": self.id,
            "par_moeda": self.par_moeda,
            "data_referencia": str(self.data_referencia),
            "compra": float(self.compra) if self.compra else None,
            "venda": float(self.venda) if self.venda else None,
            "maximo": float(self.maximo) if self.maximo else None,
            "minimo": float(self.minimo) if self.minimo else None,
            "media_compra_periodo": float(self.media_compra_periodo) if self.media_compra_periodo else None,
            "media_venda_periodo": float(self.media_venda_periodo) if self.media_venda_periodo else None,
            "minimo_periodo": float(self.minimo_periodo) if self.minimo_periodo else None,
            "maximo_periodo": float(self.maximo_periodo) if self.maximo_periodo else None,
            "processado_em": self.processado_em.isoformat() if self.processado_em else None,
        }


class PipelineRun(Base):
    """Records metadata for a single ETL pipeline execution.

    Attributes:
        id: Auto-incremented primary key.
        status: Execution state — one of "running", "success", or "failed".
        iniciado_em: UTC datetime when the run was triggered.
        finalizado_em: UTC datetime when the run finished; None while running.
        duracao_segundos: Wall-clock duration in seconds; None while running.
        registros_processados: Number of rows upserted in the load step.
        erro: Error message captured when the pipeline fails.
        criado_em: Database-level insertion timestamp.
    """

    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String(20), nullable=False, default="running")
    iniciado_em = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
    finalizado_em = Column(DateTime, nullable=True)
    duracao_segundos = Column(Float, nullable=True)
    registros_processados = Column(Integer, nullable=True)
    erro = Column(Text, nullable=True)
    criado_em = Column(DateTime, server_default=func.now())

    def to_dict(self) -> dict:
        """Serialise the instance to a plain dictionary.

        Returns:
            Dictionary representation with all fields; datetime values are
            converted to ISO 8601 strings.
        """
        return {
            "id": self.id,
            "status": self.status,
            "iniciado_em": self.iniciado_em.isoformat() if self.iniciado_em else None,
            "finalizado_em": self.finalizado_em.isoformat() if self.finalizado_em else None,
            "duracao_segundos": self.duracao_segundos,
            "registros_processados": self.registros_processados,
            "erro": self.erro,
        }
