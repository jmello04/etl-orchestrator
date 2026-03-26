"""Repository classes for database access — PipelineRun and Cotacao."""

from datetime import datetime
from typing import Optional

from loguru import logger

from app.infra.database.connection import get_session
from app.infra.database.models import Cotacao, PipelineRun


class PipelineRunRepository:
    """Data access layer for pipeline execution records."""

    def criar_run(self, status: str, iniciado_em: datetime) -> int:
        """Persist a new pipeline run record and return its generated ID.

        Args:
            status: Initial status string (typically "running").
            iniciado_em: UTC datetime when the run was started.

        Returns:
            The auto-generated primary key of the new run record.
        """
        session = get_session()
        try:
            run = PipelineRun(status=status, iniciado_em=iniciado_em)
            session.add(run)
            session.commit()
            session.refresh(run)
            logger.debug(f"PipelineRun created with id={run.id}")
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
    ) -> None:
        """Update the outcome fields of an existing pipeline run.

        Args:
            run_id: Primary key of the run to update.
            status: Final status string ("success" or "failed").
            finalizado_em: UTC datetime when the run finished.
            duracao_segundos: Total wall-clock duration in seconds.
            registros_processados: Number of records processed in the load step.
            erro: Error message if the run failed; None on success.
        """
        session = get_session()
        try:
            run = session.query(PipelineRun).filter(PipelineRun.id == run_id).first()
            if not run:
                logger.warning(f"PipelineRun id={run_id} not found for update.")
                return
            run.status = status
            run.finalizado_em = finalizado_em
            run.duracao_segundos = duracao_segundos
            run.registros_processados = registros_processados
            run.erro = erro
            session.commit()
            logger.debug(f"PipelineRun id={run_id} updated to status={status}")
        finally:
            session.close()

    def listar_runs(self, limite: int = 50) -> list:
        """Return the most recent pipeline runs ordered by start time descending.

        Args:
            limite: Maximum number of records to return.

        Returns:
            List of run dictionaries serialised via PipelineRun.to_dict().
        """
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
        """Fetch a single pipeline run by its primary key.

        Args:
            run_id: Primary key of the run to retrieve.

        Returns:
            Run dictionary serialised via PipelineRun.to_dict(), or None if
            no matching record exists.
        """
        session = get_session()
        try:
            run = session.query(PipelineRun).filter(PipelineRun.id == run_id).first()
            return run.to_dict() if run else None
        finally:
            session.close()


class CotacaoRepository:
    """Data access layer for exchange rate records."""

    def listar_cotacoes(
        self,
        par_moeda: Optional[str] = None,
        limite: int = 100,
    ) -> list:
        """Return processed exchange rate records, newest first.

        Args:
            par_moeda: Optional currency pair filter (e.g. "USD-BRL").
                       When omitted all pairs are returned.
            limite: Maximum number of records to return.

        Returns:
            List of cotacao dictionaries serialised via Cotacao.to_dict().
        """
        session = get_session()
        try:
            query = session.query(Cotacao)
            if par_moeda:
                query = query.filter(Cotacao.par_moeda == par_moeda)
            cotacoes = (
                query.order_by(Cotacao.data_referencia.desc()).limit(limite).all()
            )
            return [c.to_dict() for c in cotacoes]
        finally:
            session.close()
