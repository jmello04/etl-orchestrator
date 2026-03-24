import httpx
import pytest
import respx

from flows.extract import APIS, extrair_cotacoes_logica


@respx.mock
def test_extrai_dados_com_sucesso():
    respx.get(APIS["USD-BRL"]).mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "code": "USD",
                    "codein": "BRL",
                    "bid": "5.1234",
                    "ask": "5.1350",
                    "high": "5.1500",
                    "low": "5.1100",
                    "timestamp": "1700000000",
                }
            ],
        )
    )
    respx.get(APIS["EUR-BRL"]).mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "code": "EUR",
                    "codein": "BRL",
                    "bid": "5.5500",
                    "ask": "5.5700",
                    "high": "5.5900",
                    "low": "5.5300",
                    "timestamp": "1700000000",
                }
            ],
        )
    )

    resultado = extrair_cotacoes_logica()

    assert "USD-BRL" in resultado
    assert "EUR-BRL" in resultado
    assert len(resultado["USD-BRL"]) == 1
    assert len(resultado["EUR-BRL"]) == 1


@respx.mock
def test_extrai_levanta_erro_em_status_http_invalido():
    respx.get(APIS["USD-BRL"]).mock(return_value=httpx.Response(500))
    respx.get(APIS["EUR-BRL"]).mock(return_value=httpx.Response(500))

    with pytest.raises(httpx.HTTPStatusError):
        extrair_cotacoes_logica()


@respx.mock
def test_extrai_levanta_erro_resposta_vazia():
    respx.get(APIS["USD-BRL"]).mock(return_value=httpx.Response(200, json=[]))
    respx.get(APIS["EUR-BRL"]).mock(return_value=httpx.Response(200, json=[]))

    with pytest.raises(ValueError, match="Resposta inválida"):
        extrair_cotacoes_logica()


@respx.mock
def test_extrai_estrutura_de_cada_registro():
    respx.get(APIS["USD-BRL"]).mock(
        return_value=httpx.Response(
            200,
            json=[{"code": "USD", "codein": "BRL", "bid": "5.10", "ask": "5.12",
                   "high": "5.15", "low": "5.05", "timestamp": "1700000000"}],
        )
    )
    respx.get(APIS["EUR-BRL"]).mock(
        return_value=httpx.Response(
            200,
            json=[{"code": "EUR", "codein": "BRL", "bid": "5.50", "ask": "5.55",
                   "high": "5.60", "low": "5.45", "timestamp": "1700000000"}],
        )
    )

    resultado = extrair_cotacoes_logica()

    registro_usd = resultado["USD-BRL"][0]
    assert "bid" in registro_usd
    assert "ask" in registro_usd
    assert "timestamp" in registro_usd
