from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class StatusPipeline(str, Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class PipelineRunSchema(BaseModel):
    id: int
    status: StatusPipeline
    iniciado_em: datetime
    finalizado_em: Optional[datetime] = None
    duracao_segundos: Optional[float] = None
    registros_processados: Optional[int] = None
    erro: Optional[str] = None

    model_config = {"from_attributes": True}


class IniciarPipelineResponse(BaseModel):
    mensagem: str
    run_id: int
    status: StatusPipeline
    iniciado_em: datetime


class ListaRunsResponse(BaseModel):
    total: int
    execucoes: list[PipelineRunSchema]
