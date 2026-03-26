"""Endpoints for triggering and monitoring ETL pipeline executions."""

from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, status
from loguru import logger

from app.core.exceptions import PipelineRunNaoEncontrado
from app.infra.database.connection import init_db
from app.infra.database.repository import PipelineRunRepository
from app.schemas.pipeline import (
    IniciarPipelineResponse,
    ListaRunsResponse,
    PipelineRunSchema,
    StatusPipeline,
)

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])


def _executar_pipeline_em_background(run_id: int) -> None:
    """Execute the ETL pipeline flow in a background thread.

    Wraps the Prefect flow invocation so that any unhandled exception is
    logged without crashing the FastAPI process.

    Args:
        run_id: Primary key of the PipelineRun record tracking this execution.
    """
    from flows.pipeline import pipeline_cotacoes

    try:
        pipeline_cotacoes(run_id=run_id)
    except Exception as exc:
        logger.error(
            f"Pipeline run_id={run_id} terminated with error in background: {exc}"
        )


@router.post(
    "/run",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=IniciarPipelineResponse,
    summary="Executa o pipeline ETL manualmente",
    description=(
        "Dispara o pipeline em background e retorna imediatamente com o `run_id`. "
        "Use `GET /pipeline/runs/{run_id}` para acompanhar o status."
    ),
)
def executar_pipeline(background_tasks: BackgroundTasks) -> IniciarPipelineResponse:
    """Trigger a manual ETL pipeline run asynchronously.

    Creates a new PipelineRun record, schedules the pipeline flow as a
    background task, and returns immediately with the run ID so the caller
    can poll for completion.

    Args:
        background_tasks: FastAPI background task manager.

    Returns:
        Response containing the run ID, initial status and start timestamp.
    """
    init_db()
    repo = PipelineRunRepository()
    agora = datetime.utcnow()
    run_id = repo.criar_run(status="running", iniciado_em=agora)

    background_tasks.add_task(_executar_pipeline_em_background, run_id)

    logger.info(f"Pipeline triggered manually — run_id={run_id}")
    return IniciarPipelineResponse(
        mensagem="Pipeline iniciado com sucesso. Acompanhe pelo run_id.",
        run_id=run_id,
        status=StatusPipeline.RUNNING,
        iniciado_em=agora,
    )


@router.get(
    "/runs",
    response_model=ListaRunsResponse,
    summary="Histórico de execuções do pipeline",
)
def listar_execucoes(limite: int = 50) -> ListaRunsResponse:
    """Return the most recent pipeline execution records.

    Args:
        limite: Maximum number of records to return (default 50).

    Returns:
        List of pipeline run summaries with total count.
    """
    init_db()
    repo = PipelineRunRepository()
    runs = repo.listar_runs(limite=limite)
    return ListaRunsResponse(total=len(runs), execucoes=runs)


@router.get(
    "/runs/{run_id}",
    response_model=PipelineRunSchema,
    summary="Detalhes de uma execução específica",
)
def detalhe_execucao(run_id: int) -> PipelineRunSchema:
    """Return details for a single pipeline run.

    Args:
        run_id: Primary key of the execution to retrieve.

    Raises:
        PipelineRunNaoEncontrado: If no run with the given ID exists.

    Returns:
        Full pipeline run schema including status, duration and record count.
    """
    init_db()
    repo = PipelineRunRepository()
    run = repo.buscar_run_por_id(run_id)
    if not run:
        raise PipelineRunNaoEncontrado(run_id)
    return run
