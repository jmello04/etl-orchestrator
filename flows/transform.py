import pandas as pd
import numpy as np
from loguru import logger
from prefect import task
import time
from datetime import datetime


@task(name="transformar-cotacoes")
def transformar_cotacoes(dados_brutos: dict) -> pd.DataFrame:
    inicio = time.perf_counter()
    logger.info("Iniciando transformação dos dados brutos.")

    frames = []

    for par, registros in dados_brutos.items():
        df = pd.DataFrame(registros)

        colunas_necessarias = {"bid", "ask", "high", "low", "timestamp", "code", "codein"}
        colunas_presentes = set(df.columns)
        faltando = colunas_necessarias - colunas_presentes
        if faltando:
            logger.warning(f"Par {par}: colunas ausentes na API: {faltando}")

        df = df.rename(columns={
            "bid": "compra",
            "ask": "venda",
            "high": "maximo",
            "low": "minimo",
            "timestamp": "timestamp_unix",
        })

        for col in ["compra", "venda", "maximo", "minimo"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        if "timestamp_unix" in df.columns:
            df["data_referencia"] = pd.to_datetime(
                df["timestamp_unix"].astype("int64"), unit="s", utc=True
            ).dt.tz_convert("America/Sao_Paulo").dt.date

        df["par_moeda"] = par

        media_compra = df["compra"].mean() if "compra" in df.columns else np.nan
        media_venda = df["venda"].mean() if "venda" in df.columns else np.nan
        minimo_periodo = df["minimo"].min() if "minimo" in df.columns else np.nan
        maximo_periodo = df["maximo"].max() if "maximo" in df.columns else np.nan

        df["media_compra_periodo"] = round(media_compra, 4)
        df["media_venda_periodo"] = round(media_venda, 4)
        df["minimo_periodo"] = round(minimo_periodo, 4)
        df["maximo_periodo"] = round(maximo_periodo, 4)

        logger.info(
            f"Par {par} — estatísticas do período: "
            f"média_compra={media_compra:.4f}, "
            f"média_venda={media_venda:.4f}, "
            f"mínimo={minimo_periodo:.4f}, "
            f"máximo={maximo_periodo:.4f}"
        )

        frames.append(df)

    if not frames:
        raise ValueError("Nenhum dado disponível para transformação.")

    df_final = pd.concat(frames, ignore_index=True)
    df_final = df_final.dropna(subset=["compra", "venda", "data_referencia"])
    df_final = df_final.drop_duplicates(subset=["par_moeda", "data_referencia"])
    df_final["processado_em"] = datetime.utcnow()

    duracao = time.perf_counter() - inicio
    logger.info(
        f"Transformação concluída em {duracao:.2f}s — "
        f"{len(df_final)} registros prontos para carga."
    )
    return df_final
