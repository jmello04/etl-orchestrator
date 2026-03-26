"""Pydantic schemas for pipeline execution API responses."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class StatusPipeline(str, Enum):
    """Possible execution states for a pipeline run.

    Attributes:
        RUNNING: The pipeline is currently executing.
        SUCCESS: The pipeline completed without errors.
        FAILED: The pipeline terminated with an unrecoverable error.
    """

    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class PipelineRunSchema(BaseModel):
    """Full schema for a pipeline execution record.

    Attributes:
        id: Database primary key.
        status: Current or final execution state.
        iniciado_em: UTC datetime when the run was triggered.
        finalizado_em: UTC datetime when the run finished; None while running.
        duracao_segundos: Wall-clock duration in seconds; None while running.
        registros_processados: Number of records upserted in the load step.
        erro: Error message if the run failed; None on success.
    """

    id: int
    status: StatusPipeline
    iniciado_em: datetime
    finalizado_em: Optional[datetime] = None
    duracao_segundos: Optional[float] = None
    registros_processados: Optional[int] = None
    erro: Optional[str] = None

    model_config = {"from_attributes": True}


class IniciarPipelineResponse(BaseModel):
    """Response returned when a manual pipeline run is accepted.

    Attributes:
        mensagem: Human-readable confirmation message.
        run_id: Primary key of the newly created PipelineRun record.
        status: Initial status (always RUNNING at acceptance time).
        iniciado_em: UTC datetime when the run was scheduled.
    """

    mensagem: str
    run_id: int
    status: StatusPipeline
    iniciado_em: datetime


class ListaRunsResponse(BaseModel):
    """Paginated response wrapper for a list of pipeline run records.

    Attributes:
        total: Number of records returned in this response.
        execucoes: List of pipeline run schemas.
    """

    total: int
    execucoes: list[PipelineRunSchema]
