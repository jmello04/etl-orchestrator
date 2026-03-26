"""Prefect extract task: fetches raw exchange rate data from AwesomeAPI."""

import time
from typing import Any

import httpx
from loguru import logger
from prefect import task

APIS: dict[str, str] = {
    "USD-BRL": "https://economia.awesomeapi.com.br/json/daily/USD-BRL/30",
    "EUR-BRL": "https://economia.awesomeapi.com.br/json/daily/EUR-BRL/30",
}


def _buscar_par(par: str, url: str) -> list[dict[str, Any]]:
    """Fetch raw JSON records for a single currency pair from the external API.

    Args:
        par: Currency pair label used for logging (e.g. "USD-BRL").
        url: AwesomeAPI endpoint URL for the requested pair.

    Returns:
        Non-empty list of raw record dictionaries returned by the API.

    Raises:
        httpx.HTTPStatusError: If the API responds with a non-2xx status code.
        ValueError: If the response body is empty or not a list.
    """
    with httpx.Client(timeout=15.0) as client:
        response = client.get(url)
        response.raise_for_status()
        dados = response.json()

    if not dados or not isinstance(dados, list):
        raise ValueError(f"Resposta inválida da API para {par}: {dados}")

    return dados


def extrair_cotacoes_logica() -> dict[str, list[dict[str, Any]]]:
    """Extract daily exchange rate records for all configured currency pairs.

    Iterates over the :data:`APIS` registry, calls each endpoint and
    collects the results. Intended to be called directly in tests.

    Returns:
        Dictionary mapping each currency pair label to its list of raw
        API records (e.g. ``{"USD-BRL": [...], "EUR-BRL": [...]}``)

    Raises:
        httpx.HTTPStatusError: If any API call returns a non-2xx status.
        ValueError: If any API response is empty or malformed.
    """
    inicio = time.perf_counter()
    resultados: dict[str, list[dict[str, Any]]] = {}

    logger.info("Starting extraction of exchange rate data from external APIs.")

    for par, url in APIS.items():
        logger.info(f"Fetching data for {par}.")
        dados = _buscar_par(par, url)
        resultados[par] = dados
        logger.success(f"Pair {par}: {len(dados)} records extracted successfully.")

    duracao = time.perf_counter() - inicio
    logger.info(
        f"Extraction completed in {duracao:.2f}s — {len(resultados)} pairs processed."
    )
    return resultados


@task(
    name="extrair-cotacoes",
    retries=3,
    retry_delay_seconds=10,
)
def extrair_cotacoes() -> dict[str, list[dict[str, Any]]]:
    """Prefect task wrapper for :func:`extrair_cotacoes_logica`.

    Returns:
        Dictionary mapping each currency pair label to its list of raw
        API records.
    """
    return extrair_cotacoes_logica()
