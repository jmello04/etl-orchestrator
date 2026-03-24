from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class CotacaoSchema(BaseModel):
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
    total: int
    par_moeda: str
    cotacoes: list[CotacaoSchema]
