from fastapi import APIRouter, BackgroundTasks, status
from loguru import logger
from datetime import datetime

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
    from flows.pipeline import pipeline_cotacoes
    try:
        pipeline_cotacoes(run_id=run_id)
    except Exception as exc:
        logger.error(f"Pipeline run_id={run_id} encerrado com falha em background: {exc}")


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
    init_db()
    repo = PipelineRunRepository()
    agora = datetime.utcnow()
    run_id = repo.criar_run(status="running", iniciado_em=agora)

    background_tasks.add_task(_executar_pipeline_em_background, run_id)

    logger.info(f"Pipeline disparado manualmente — run_id={run_id}")
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
    init_db()
    repo = PipelineRunRepository()
    run = repo.buscar_run_por_id(run_id)
    if not run:
        raise PipelineRunNaoEncontrado(run_id)
    return run
