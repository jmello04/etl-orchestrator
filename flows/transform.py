"""Prefect transform task: normalises raw API data into a typed DataFrame."""

import time
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd
from loguru import logger
from prefect import task


def transformar_cotacoes_logica(dados_brutos: dict[str, list[dict[str, Any]]]) -> pd.DataFrame:
    """Normalise raw API records into a clean DataFrame ready for loading.

    For each currency pair:
    - Renames API fields to domain column names.
    - Converts price columns to float.
    - Derives the reference date from the Unix timestamp.
    - Computes period statistics (average, min, max).

    After processing all pairs the frames are concatenated, rows with null
    prices or dates are dropped, duplicates on (par_moeda, data_referencia)
    are removed, and a processing timestamp is added.

    Args:
        dados_brutos: Dictionary mapping currency pair labels to lists of raw
                      API record dictionaries, as returned by the extract step.

    Returns:
        Clean pandas DataFrame with one row per (pair, date) combination.

    Raises:
        ValueError: If the input dictionary is empty or yields no valid rows.
    """
    inicio = time.perf_counter()
    logger.info("Starting transformation of raw data.")

    frames: list[pd.DataFrame] = []

    for par, registros in dados_brutos.items():
        df = pd.DataFrame(registros)

        colunas_necessarias = {"bid", "ask", "high", "low", "timestamp", "code", "codein"}
        faltando = colunas_necessarias - set(df.columns)
        if faltando:
            logger.warning(f"Pair {par}: columns missing from API response: {faltando}")

        df = df.rename(
            columns={
                "bid": "compra",
                "ask": "venda",
                "high": "maximo",
                "low": "minimo",
                "timestamp": "timestamp_unix",
            }
        )

        for col in ["compra", "venda", "maximo", "minimo"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        if "timestamp_unix" in df.columns:
            df["data_referencia"] = (
                pd.to_datetime(df["timestamp_unix"].astype("int64"), unit="s", utc=True)
                .dt.tz_convert("America/Sao_Paulo")
                .dt.date
            )

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
            f"Pair {par} — period statistics: "
            f"avg_buy={media_compra:.4f}, "
            f"avg_sell={media_venda:.4f}, "
            f"min={minimo_periodo:.4f}, "
            f"max={maximo_periodo:.4f}"
        )

        frames.append(df)

    if not frames:
        raise ValueError("Nenhum dado disponível para transformação.")

    df_final = pd.concat(frames, ignore_index=True)
    df_final = df_final.dropna(subset=["compra", "venda", "data_referencia"])
    df_final = df_final.drop_duplicates(subset=["par_moeda", "data_referencia"])
    df_final["processado_em"] = datetime.now(timezone.utc).replace(tzinfo=None)

    duracao = time.perf_counter() - inicio
    logger.info(
        f"Transformation completed in {duracao:.2f}s — "
        f"{len(df_final)} records ready for loading."
    )
    return df_final


@task(name="transformar-cotacoes")
def transformar_cotacoes(dados_brutos: dict[str, list[dict[str, Any]]]) -> pd.DataFrame:
    """Prefect task wrapper for :func:`transformar_cotacoes_logica`.

    Args:
        dados_brutos: Raw API data from the extract step.

    Returns:
        Clean DataFrame ready for the load step.
    """
    return transformar_cotacoes_logica(dados_brutos)
