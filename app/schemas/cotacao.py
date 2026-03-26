"""Pydantic schemas for exchange rate (cotacao) API responses."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class CotacaoSchema(BaseModel):
    """Serialisation schema for a single exchange rate observation.

    Attributes:
        id: Database primary key.
        par_moeda: Currency pair label (e.g. "USD-BRL").
        data_referencia: Calendar date the observation refers to.
        compra: Buy (bid) rate.
        venda: Sell (ask) rate.
        maximo: Intraday high.
        minimo: Intraday low.
        media_compra_periodo: Average buy rate over the extracted window.
        media_venda_periodo: Average sell rate over the extracted window.
        minimo_periodo: Minimum rate in the extracted window.
        maximo_periodo: Maximum rate in the extracted window.
        processado_em: UTC timestamp when the ETL pipeline processed this row.
    """

    id: int
    par_moeda: str = Field(examples=["USD-BRL"])
    data_referencia: date
    compra: Optional[float] = None
    venda: Optional[float] = None
    maximo: Optional[float] = None
    minimo: Optional[float] = None
    media_compra_periodo: Optional[float] = None
    media_venda_periodo: Optional[float] = None
    minimo_periodo: Optional[float] = None
    maximo_periodo: Optional[float] = None
    processado_em: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ListaCotacoesResponse(BaseModel):
    """Paginated response wrapper for a list of exchange rate records.

    Attributes:
        total: Number of records returned in this response.
        par_moeda: Currency pair filter applied, or "todos" if none.
        cotacoes: List of exchange rate observation schemas.
    """

    total: int
    par_moeda: str
    cotacoes: list[CotacaoSchema]
