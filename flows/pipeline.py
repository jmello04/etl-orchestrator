import time
from datetime import datetime, timedelta, timezone

from loguru import logger
from prefect import flow

from flows.extract import extrair_cotacoes
from flows.transform import transformar_cotacoes
from flows.load import carregar_cotacoes
from app.infra.database.connection import init_db
from app.infra.database.repository import PipelineRunRepository


@flow(
    name="pipeline-cotacoes-financeiras",
    description="Pipeline ETL para cotações de moedas USD-BRL e EUR-BRL",
    retries=1,
    retry_delay_seconds=30,
)
def pipeline_cotacoes(run_id: int | None = None) -> dict:
    inicio_total = time.perf_counter()
    inicio_dt = datetime.now(timezone.utc).replace(tzinfo=None)

    logger.info("=" * 60)
    logger.info("PIPELINE ETL — COTAÇÕES FINANCEIRAS — INICIADO")
    logger.info(f"Data/hora de início: {inicio_dt.isoformat()}")
    logger.info("=" * 60)

    init_db()
    repo = PipelineRunRepository()

    if run_id is None:
        run_id = repo.criar_run(status="running", iniciado_em=inicio_dt)

    try:
        # ETAPA 1: EXTRAÇÃO
        logger.info("[1/3] Iniciando etapa de EXTRAÇÃO")
        t0 = time.perf_counter()
        dados_brutos = extrair_cotacoes()
        t1 = time.perf_counter()
        logger.info(f"[1/3] EXTRAÇÃO concluída em {t1 - t0:.2f}s")

        # ETAPA 2: TRANSFORMAÇÃO
        logger.info("[2/3] Iniciando etapa de TRANSFORMAÇÃO")
        t0 = time.perf_counter()
        df_transformado = transformar_cotacoes(dados_brutos)
        t1 = time.perf_counter()
        logger.info(f"[2/3] TRANSFORMAÇÃO concluída em {t1 - t0:.2f}s")

        # ETAPA 3: CARGA
        logger.info("[3/3] Iniciando etapa de CARGA")
        t0 = time.perf_counter()
        total_registros = carregar_cotacoes(df_transformado)
        t1 = time.perf_counter()
        logger.info(f"[3/3] CARGA concluída em {t1 - t0:.2f}s")

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
        logger.success("PIPELINE CONCLUÍDO COM SUCESSO")
        logger.success(f"Duração total: {duracao_total:.2f}s")
        logger.success(f"Registros processados: {total_registros}")
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
        logger.error("ALERTA: PIPELINE FALHOU APÓS TODAS AS TENTATIVAS")
        logger.error(f"Erro: {exc}")
        logger.error(f"Duração até falha: {duracao_total:.2f}s")
        logger.error("=" * 60)
        raise


def iniciar_agendamento():
    pipeline_cotacoes.serve(
        name="agendamento-12h",
        interval=timedelta(hours=12),
    )


if __name__ == "__main__":
    iniciar_agendamento()
