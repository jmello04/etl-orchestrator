from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    Date,
    DateTime,
    Text,
    Float,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Cotacao(Base):
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
    processado_em = Column(DateTime, default=datetime.utcnow)
    criado_em = Column(DateTime, server_default=func.now())

    def to_dict(self):
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
    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String(20), nullable=False, default="running")
    iniciado_em = Column(DateTime, nullable=False, default=datetime.utcnow)
    finalizado_em = Column(DateTime, nullable=True)
    duracao_segundos = Column(Float, nullable=True)
    registros_processados = Column(Integer, nullable=True)
    erro = Column(Text, nullable=True)
    criado_em = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "iniciado_em": self.iniciado_em.isoformat() if self.iniciado_em else None,
            "finalizado_em": self.finalizado_em.isoformat() if self.finalizado_em else None,
            "duracao_segundos": self.duracao_segundos,
            "registros_processados": self.registros_processados,
            "erro": self.erro,
        }
