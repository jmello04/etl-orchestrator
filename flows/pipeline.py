"""Prefect flow orchestrating the full ETL pipeline for exchange rate data."""

import time
from datetime import datetime, timedelta, timezone
from typing import Optional

from loguru import logger
from prefect import flow

from app.infra.database.connection import init_db
from app.infra.database.repository import PipelineRunRepository
from flows.extract import extrair_cotacoes
from flows.load import carregar_cotacoes
from flows.transform import transformar_cotacoes


@flow(
    name="pipeline-cotacoes-financeiras",
    description="Pipeline ETL para cotações de moedas USD-BRL e EUR-BRL",
    retries=1,
    retry_delay_seconds=30,
)
def pipeline_cotacoes(run_id: Optional[int] = None) -> dict:
    """Execute the full ETL pipeline: extract, transform, load.

    Orchestrates the three Prefect tasks in sequence, persists execution
    metadata via PipelineRunRepository, and returns a summary dictionary.
    If ``run_id`` is provided the existing run record is updated; otherwise
    a new one is created.

    Args:
        run_id: Optional primary key of an existing PipelineRun record.
                When None a new run is registered before execution begins.

    Returns:
        Summary dictionary with keys: status, run_id, duracao_segundos,
        registros_processados, iniciado_em, finalizado_em.

    Raises:
        Exception: Any unhandled error from the extract, transform or load
                   step after all Prefect retries are exhausted. The run
                   record is updated to "failed" before re-raising.
    """
    inicio_total = time.perf_counter()
    inicio_dt = datetime.now(timezone.utc).replace(tzinfo=None)

    logger.info("=" * 60)
    logger.info("PIPELINE ETL — FINANCIAL EXCHANGE RATES — STARTED")
    logger.info(f"Start time: {inicio_dt.isoformat()}")
    logger.info("=" * 60)

    init_db()
    repo = PipelineRunRepository()

    if run_id is None:
        run_id = repo.criar_run(status="running", iniciado_em=inicio_dt)

    try:
        logger.info("[1/3] Starting EXTRACT stage")
        t0 = time.perf_counter()
        dados_brutos = extrair_cotacoes()
        logger.info(f"[1/3] EXTRACT completed in {time.perf_counter() - t0:.2f}s")

        logger.info("[2/3] Starting TRANSFORM stage")
        t0 = time.perf_counter()
        df_transformado = transformar_cotacoes(dados_brutos)
        logger.info(f"[2/3] TRANSFORM completed in {time.perf_counter() - t0:.2f}s")

        logger.info("[3/3] Starting LOAD stage")
        t0 = time.perf_counter()
        total_registros = carregar_cotacoes(df_transformado)
        logger.info(f"[3/3] LOAD completed in {time.perf_counter() - t0:.2f}s")

        duracao_total = time.perf_counter() - inicio_total
        fim_dt = datetime.now(timezone.utc).replace(tzinfo=None)

        repo.atualizar_run(
            run_id=run_id,
            status="success",
            finalizado_em=fim_dt,
            duracao_segundos=duracao_total,
            registros_processados=total_registros,
        )

        logger.success("=" * 60)
        logger.success("PIPELINE COMPLETED SUCCESSFULLY")
        logger.success(f"Total duration: {duracao_total:.2f}s")
        logger.success(f"Records processed: {total_registros}")
        logger.success("=" * 60)

        return {
            "status": "success",
            "run_id": run_id,
            "duracao_segundos": round(duracao_total, 2),
            "registros_processados": total_registros,
            "iniciado_em": inicio_dt.isoformat(),
            "finalizado_em": fim_dt.isoformat(),
        }

    except Exception as exc:
        duracao_total = time.perf_counter() - inicio_total
        fim_dt = datetime.now(timezone.utc).replace(tzinfo=None)

        repo.atualizar_run(
            run_id=run_id,
            status="failed",
            finalizado_em=fim_dt,
            duracao_segundos=duracao_total,
            erro=str(exc),
        )

        logger.error("=" * 60)
        logger.error("PIPELINE FAILED AFTER ALL RETRIES")
        logger.error(f"Error: {exc}")
        logger.error(f"Duration until failure: {duracao_total:.2f}s")
        logger.error("=" * 60)
        raise


def iniciar_agendamento() -> None:
    """Register the pipeline flow with Prefect for scheduled execution.

    Deploys the flow with a 12-hour interval using Prefect's serve API.
    This function is the entry point when running the scheduler process.
    """
    pipeline_cotacoes.serve(
        name="agendamento-12h",
        interval=timedelta(hours=12),
    )


if __name__ == "__main__":
    iniciar_agendamento()
