from fastapi import APIRouter, Query
from typing import Optional

from app.infra.database.connection import init_db
from app.infra.database.repository import CotacaoRepository

router = APIRouter(prefix="/data", tags=["Dados"])


@router.get("/cotacoes", summary="Retorna as cotações processadas salvas no banco")
def listar_cotacoes(
    par_moeda: Optional[str] = Query(
        default=None,
        description="Filtrar por par de moeda (ex: USD-BRL, EUR-BRL)",
    ),
    limite: int = Query(default=100, ge=1, le=500),
):
    init_db()
    repo = CotacaoRepository()
    cotacoes = repo.listar_cotacoes(par_moeda=par_moeda, limite=limite)
    return {
        "total": len(cotacoes),
        "par_moeda": par_moeda or "todos",
        "cotacoes": cotacoes,
    }
