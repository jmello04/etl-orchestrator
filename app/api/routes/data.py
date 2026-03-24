from fastapi import APIRouter, Query
from typing import Optional

from app.infra.database.connection import init_db
from app.infra.database.repository import CotacaoRepository
from app.schemas.cotacao import ListaCotacoesResponse

router = APIRouter(prefix="/data", tags=["Dados"])


@router.get(
    "/cotacoes",
    response_model=ListaCotacoesResponse,
    summary="Cotações processadas salvas no banco",
    description=(
        "Retorna cotações financeiras processadas pelo pipeline ETL. "
        "Filtre por `par_moeda` (USD-BRL ou EUR-BRL) e controle o volume com `limite`."
    ),
)
def listar_cotacoes(
    par_moeda: Optional[str] = Query(
        default=None,
        description="Par de moeda (ex: USD-BRL, EUR-BRL)",
        examples=["USD-BRL"],
    ),
    limite: int = Query(default=100, ge=1, le=500, description="Máximo de registros retornados"),
) -> ListaCotacoesResponse:
    init_db()
    repo = CotacaoRepository()
    cotacoes = repo.listar_cotacoes(par_moeda=par_moeda, limite=limite)
    return ListaCotacoesResponse(
        total=len(cotacoes),
        par_moeda=par_moeda or "todos",
        cotacoes=cotacoes,
    )
