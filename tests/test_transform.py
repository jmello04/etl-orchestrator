import pytest
import pandas as pd
from flows.transform import transformar_cotacoes


DADOS_VALIDOS = {
    "USD-BRL": [
        {
            "code": "USD",
            "codein": "BRL",
            "bid": "5.1234",
            "ask": "5.1350",
            "high": "5.1500",
            "low": "5.1100",
            "timestamp": "1700000000",
        },
        {
            "code": "USD",
            "codein": "BRL",
            "bid": "5.2000",
            "ask": "5.2150",
            "high": "5.2300",
            "low": "5.1900",
            "timestamp": "1700086400",
        },
    ]
}


def test_transforma_retorna_dataframe():
    df = transformar_cotacoes.fn(DADOS_VALIDOS)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_transforma_colunas_obrigatorias():
    df = transformar_cotacoes.fn(DADOS_VALIDOS)
    colunas = df.columns.tolist()
    assert "par_moeda" in colunas
    assert "compra" in colunas
    assert "venda" in colunas
    assert "data_referencia" in colunas
    assert "media_compra_periodo" in colunas
    assert "media_venda_periodo" in colunas
    assert "minimo_periodo" in colunas
    assert "maximo_periodo" in colunas


def test_transforma_tipos_numericos():
    df = transformar_cotacoes.fn(DADOS_VALIDOS)
    assert pd.api.types.is_float_dtype(df["compra"])
    assert pd.api.types.is_float_dtype(df["venda"])


def test_transforma_sem_duplicatas():
    df = transformar_cotacoes.fn(DADOS_VALIDOS)
    duplicatas = df.duplicated(subset=["par_moeda", "data_referencia"]).sum()
    assert duplicatas == 0


def test_transforma_levanta_erro_com_dados_vazios():
    with pytest.raises(ValueError):
        transformar_cotacoes.fn({})
