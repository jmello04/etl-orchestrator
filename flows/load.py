"""Prefect load task: upserts transformed exchange rate data into PostgreSQL."""

import time

import pandas as pd
from loguru import logger
from prefect import task
from sqlalchemy import literal_column
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.types import Boolean

from app.infra.database.connection import get_engine
from app.infra.database.models import Cotacao


def carregar_cotacoes_logica(df: pd.DataFrame) -> int:
    """Upsert exchange rate records into the cotacoes table.

    Uses PostgreSQL ``ON CONFLICT DO UPDATE`` (upsert) so that re-running
    the pipeline is idempotent — existing rows are refreshed rather than
    duplicated. Tracks whether each statement resulted in an insert or an
    update via the ``xmax`` system column.

    Args:
        df: Clean DataFrame produced by the transform step. Must contain the
            columns expected by the Cotacao model.

    Returns:
        Total number of rows affected (inserts + updates).
    """
    inicio = time.perf_counter()
    logger.info(f"Starting load of {len(df)} records into PostgreSQL.")

    engine = get_engine()
    registros = df.to_dict(orient="records")

    inseridos = 0
    atualizados = 0

    with engine.begin() as conn:
        for registro in registros:
            stmt = (
                insert(Cotacao)
                .values(
                    par_moeda=registro.get("par_moeda"),
                    data_referencia=registro.get("data_referencia"),
                    compra=registro.get("compra"),
                    venda=registro.get("venda"),
                    maximo=registro.get("maximo"),
                    minimo=registro.get("minimo"),
                    media_compra_periodo=registro.get("media_compra_periodo"),
                    media_venda_periodo=registro.get("media_venda_periodo"),
                    minimo_periodo=registro.get("minimo_periodo"),
                    maximo_periodo=registro.get("maximo_periodo"),
                    processado_em=registro.get("processado_em"),
                )
                .on_conflict_do_update(
                    index_elements=["par_moeda", "data_referencia"],
                    set_={
                        "compra": registro.get("compra"),
                        "venda": registro.get("venda"),
                        "maximo": registro.get("maximo"),
                        "minimo": registro.get("minimo"),
                        "media_compra_periodo": registro.get("media_compra_periodo"),
                        "media_venda_periodo": registro.get("media_venda_periodo"),
                        "minimo_periodo": registro.get("minimo_periodo"),
                        "maximo_periodo": registro.get("maximo_periodo"),
                        "processado_em": registro.get("processado_em"),
                    },
                )
                .returning(
                    literal_column("(xmax::text::int > 0)", Boolean).label(
                        "foi_atualizado"
                    )
                )
            )
            resultado = conn.execute(stmt)
            row = resultado.fetchone()
            if row is not None and row.foi_atualizado:
                atualizados += 1
            else:
                inseridos += 1

    duracao = time.perf_counter() - inicio
    logger.success(
        f"Load completed in {duracao:.2f}s — "
        f"{inseridos} inserted, {atualizados} updated."
    )
    return inseridos + atualizados


@task(name="carregar-cotacoes")
def carregar_cotacoes(df: pd.DataFrame) -> int:
    """Prefect task wrapper for :func:`carregar_cotacoes_logica`.

    Args:
        df: Clean DataFrame from the transform step.

    Returns:
        Total number of rows affected (inserts + updates).
    """
    return carregar_cotacoes_logica(df)
