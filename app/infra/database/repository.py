from datetime import datetime
from typing import Optional
from loguru import logger

from app.infra.database.connection import get_session
from app.infra.database.models import PipelineRun, Cotacao


class PipelineRunRepository:
    def criar_run(self, status: str, iniciado_em: datetime) -> int:
        session = get_session()
        try:
            run = PipelineRun(status=status, iniciado_em=iniciado_em)
            session.add(run)
            session.commit()
            session.refresh(run)
            logger.debug(f"PipelineRun criado com id={run.id}")
            return run.id
        finally:
            session.close()

    def atualizar_run(
        self,
        run_id: int,
        status: str,
        finalizado_em: datetime,
        duracao_segundos: float,
        registros_processados: Optional[int] = None,
        erro: Optional[str] = None,
    ):
        session = get_session()
        try:
            run = session.query(PipelineRun).filter(PipelineRun.id == run_id).first()
            if not run:
                logger.warning(f"PipelineRun id={run_id} não encontrado para atualização.")
                return
            run.status = status
            run.finalizado_em = finalizado_em
            run.duracao_segundos = duracao_segundos
            run.registros_processados = registros_processados
            run.erro = erro
            session.commit()
            logger.debug(f"PipelineRun id={run_id} atualizado para status={status}")
        finally:
            session.close()

    def listar_runs(self, limite: int = 50) -> list:
        session = get_session()
        try:
            runs = (
                session.query(PipelineRun)
                .order_by(PipelineRun.iniciado_em.desc())
                .limit(limite)
                .all()
            )
            return [r.to_dict() for r in runs]
        finally:
            session.close()

    def buscar_run_por_id(self, run_id: int) -> Optional[dict]:
        session = get_session()
        try:
            run = session.query(PipelineRun).filter(PipelineRun.id == run_id).first()
            return run.to_dict() if run else None
        finally:
            session.close()


class CotacaoRepository:
    def listar_cotacoes(
        self,
        par_moeda: Optional[str] = None,
        limite: int = 100,
    ) -> list:
        session = get_session()
        try:
            query = session.query(Cotacao)
            if par_moeda:
                query = query.filter(Cotacao.par_moeda == par_moeda)
            cotacoes = query.order_by(Cotacao.data_referencia.desc()).limit(limite).all()
            return [c.to_dict() for c in cotacoes]
        finally:
            session.close()
