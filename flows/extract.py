import time

import httpx
from loguru import logger
from prefect import task

APIS = {
    "USD-BRL": "https://economia.awesomeapi.com.br/json/daily/USD-BRL/30",
    "EUR-BRL": "https://economia.awesomeapi.com.br/json/daily/EUR-BRL/30",
}


def _buscar_par(par: str, url: str) -> list:
    with httpx.Client(timeout=15.0) as client:
        resposta = client.get(url)
        resposta.raise_for_status()
        dados = resposta.json()

    if not dados or not isinstance(dados, list):
        raise ValueError(f"Resposta inválida da API para {par}: {dados}")

    return dados


def extrair_cotacoes_logica() -> dict:
    inicio = time.perf_counter()
    resultados = {}

    logger.info("Iniciando extração de cotações das APIs externas.")

    for par, url in APIS.items():
        logger.info(f"Buscando dados para {par}.")
        dados = _buscar_par(par, url)
        resultados[par] = dados
        logger.success(f"Par {par}: {len(dados)} registros extraídos com sucesso.")

    duracao = time.perf_counter() - inicio
    logger.info(f"Extração concluída em {duracao:.2f}s — {len(resultados)} pares processados.")
    return resultados


@task(
    name="extrair-cotacoes",
    retries=3,
    retry_delay_seconds=10,
)
def extrair_cotacoes() -> dict:
    return extrair_cotacoes_logica()
