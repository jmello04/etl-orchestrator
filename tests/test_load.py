import pytest
import pandas as pd
from datetime import date, datetime
from unittest.mock import patch, MagicMock


def test_carrega_retorna_contagem(mocker):
    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_resultado = MagicMock()
    mock_resultado.rowcount = 1
    mock_conn.execute.return_value = mock_resultado
    mock_engine.begin.return_value.__enter__ = MagicMock(return_value=mock_conn)
    mock_engine.begin.return_value.__exit__ = MagicMock(return_value=False)

    mocker.patch("flows.load.get_engine", return_value=mock_engine)

    from flows.load import carregar_cotacoes

    df = pd.DataFrame([
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

    total = carregar_cotacoes.fn(df)
    assert total == 1
