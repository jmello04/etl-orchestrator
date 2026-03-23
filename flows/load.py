import pandas as pd
from loguru import logger
from prefect import task
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import text
import time

from app.infra.database.connection import get_engine
from app.infra.database.models import Cotacao


@task(name="carregar-cotacoes")
def carregar_cotacoes(df: pd.DataFrame) -> int:
    inicio = time.perf_counter()
    logger.info(f"Iniciando carga de {len(df)} registros no PostgreSQL.")

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
            )
            resultado = conn.execute(stmt)
            if resultado.rowcount == 1:
                inseridos += 1
            else:
                atualizados += 1

    duracao = time.perf_counter() - inicio
    logger.success(
        f"Carga concluída em {duracao:.2f}s — "
        f"{inseridos} inseridos, {atualizados} atualizados."
    )
    return inseridos + atualizados
