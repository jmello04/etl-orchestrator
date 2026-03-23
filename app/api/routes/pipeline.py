from fastapi import APIRouter, HTTPException, BackgroundTasks
from loguru import logger
from datetime import datetime

from app.infra.database.connection import init_db
from app.infra.database.repository import PipelineRunRepository

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])


def _executar_pipeline_background(run_id: int):
    from flows.pipeline import pipeline_cotacoes
    try:
        pipeline_cotacoes(run_id=run_id)
    except Exception as exc:
        logger.error(f"Pipeline run_id={run_id} falhou em background: {exc}")


@router.post("/run", summary="Executa o pipeline ETL manualmente")
def executar_pipeline(background_tasks: BackgroundTasks):
    init_db()
    repo = PipelineRunRepository()
    run_id = repo.criar_run(status="running", iniciado_em=datetime.utcnow())

    background_tasks.add_task(_executar_pipeline_background, run_id)

    logger.info(f"Pipeline iniciado manualmente — run_id={run_id}")
    return {
        "mensagem": "Pipeline iniciado com sucesso.",
        "run_id": run_id,
        "status": "running",
        "iniciado_em": datetime.utcnow().isoformat(),
    }


@router.get("/runs", summary="Lista o histórico de execuções do pipeline")
def listar_execucoes(limite: int = 50):
    init_db()
    repo = PipelineRunRepository()
    runs = repo.listar_runs(limite=limite)
    return {
        "total": len(runs),
        "execucoes": runs,
    }


@router.get("/runs/{run_id}", summary="Retorna detalhes de uma execução específica")
def detalhe_execucao(run_id: int):
    init_db()
    repo = PipelineRunRepository()
    run = repo.buscar_run_por_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Execução id={run_id} não encontrada.")
    return run
