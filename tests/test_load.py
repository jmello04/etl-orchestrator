import pandas as pd
import pytest
from datetime import date, datetime
from unittest.mock import MagicMock

from flows.load import carregar_cotacoes_logica


def _df_exemplo() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "par_moeda": "USD-BRL",
            "data_referencia": date(2024, 1, 1),
            "compra": 5.1234,
            "venda": 5.1350,
            "maximo": 5.1500,
            "minimo": 5.1100,
            "media_compra_periodo": 5.15,
            "media_venda_periodo": 5.16,
            "minimo_periodo": 5.10,
            "maximo_periodo": 5.20,
            "processado_em": datetime.utcnow(),
        }
    ])


def _montar_mock_engine(foi_atualizado: bool = False):
    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_row = MagicMock()
    mock_row.foi_atualizado = foi_atualizado
    mock_resultado = MagicMock()
    mock_resultado.fetchone.return_value = mock_row
    mock_conn.execute.return_value = mock_resultado
    mock_engine.begin.return_value.__enter__ = MagicMock(return_value=mock_conn)
    mock_engine.begin.return_value.__exit__ = MagicMock(return_value=False)
    return mock_engine


def test_carrega_retorna_contagem_de_inseridos(mocker):
    mocker.patch("flows.load.get_engine", return_value=_montar_mock_engine(foi_atualizado=False))
    total = carregar_cotacoes_logica(_df_exemplo())
    assert total == 1


def test_carrega_retorna_contagem_de_atualizados(mocker):
    mocker.patch("flows.load.get_engine", return_value=_montar_mock_engine(foi_atualizado=True))
    total = carregar_cotacoes_logica(_df_exemplo())
    assert total == 1


def test_carrega_dataframe_vazio_retorna_zero(mocker):
    mocker.patch("flows.load.get_engine", return_value=_montar_mock_engine())
    df_vazio = pd.DataFrame(columns=["par_moeda", "data_referencia", "compra", "venda",
                                      "maximo", "minimo", "media_compra_periodo",
                                      "media_venda_periodo", "minimo_periodo",
                                      "maximo_periodo", "processado_em"])
    total = carregar_cotacoes_logica(df_vazio)
    assert total == 0


def test_carrega_multiplos_registros(mocker):
    mocker.patch("flows.load.get_engine", return_value=_montar_mock_engine(foi_atualizado=False))
    df = pd.concat([_df_exemplo(), _df_exemplo().assign(data_referencia=date(2024, 1, 2))],
                   ignore_index=True)
    total = carregar_cotacoes_logica(df)
    assert total == 2
