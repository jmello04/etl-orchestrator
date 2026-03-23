import httpx
from loguru import logger
from prefect import task
from prefect.tasks import task_input_hash
from datetime import timedelta
import time


APIS = {
    "USD-BRL": "https://economia.awesomeapi.com.br/json/daily/USD-BRL/30",
    "EUR-BRL": "https://economia.awesomeapi.com.br/json/daily/EUR-BRL/30",
}


@task(
    name="extrair-cotacoes",
    retries=3,
    retry_delay_seconds=10,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=1),
)
def extrair_cotacoes() -> dict:
    inicio = time.perf_counter()
    resultados = {}

    logger.info("Iniciando extração de cotações das APIs externas.")

    for par, url in APIS.items():
        tentativa = 0
        while tentativa < 3:
            try:
                logger.info(f"Buscando dados para {par} — tentativa {tentativa + 1}/3.")
                with httpx.Client(timeout=15.0) as client:
                    resposta = client.get(url)
                    resposta.raise_for_status()
                    dados = resposta.json()

                if not dados or not isinstance(dados, list):
                    raise ValueError(f"Resposta inválida da API para {par}: {dados}")

                resultados[par] = dados
                logger.success(f"Par {par}: {len(dados)} registros extraídos com sucesso.")
                break

            except httpx.HTTPStatusError as exc:
                tentativa += 1
                logger.warning(
                    f"Erro HTTP ao buscar {par} (tentativa {tentativa}/3): "
                    f"status={exc.response.status_code}"
                )
                if tentativa == 3:
                    logger.error(
                        f"ALERTA: Falha definitiva na extração de {par} após 3 tentativas. "
                        f"Erro: {exc}"
                    )
                    raise

            except (httpx.RequestError, ValueError) as exc:
                tentativa += 1
                logger.warning(f"Erro ao buscar {par} (tentativa {tentativa}/3): {exc}")
                if tentativa == 3:
                    logger.error(
                        f"ALERTA: Falha definitiva na extração de {par} após 3 tentativas. "
                        f"Erro: {exc}"
                    )
                    raise
                time.sleep(5)

    duracao = time.perf_counter() - inicio
    logger.info(f"Extração concluída em {duracao:.2f}s — {len(resultados)} pares processados.")
    return resultados
