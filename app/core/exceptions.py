"""Custom HTTP and domain exceptions for the ETL Orchestrator."""

from fastapi import HTTPException, status


class PipelineRunNaoEncontrado(HTTPException):
    """Raised when a pipeline run with the given ID does not exist.

    Args:
        run_id: The pipeline run ID that could not be found.
    """

    def __init__(self, run_id: int) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execução com id={run_id} não encontrada.",
        )


class ErroBancoDeDados(HTTPException):
    """Raised when a database operation fails unexpectedly.

    Args:
        detalhe: Human-readable description of the database error.
    """

    def __init__(self, detalhe: str = "Erro ao acessar o banco de dados.") -> None:
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detalhe,
        )


class ErroExtracaoDados(Exception):
    """Raised when the extraction step fails after exhausting all retries.

    Attributes:
        par: Currency pair that failed extraction (e.g. "USD-BRL").
        tentativas: Number of attempts made before giving up.
        causa: Underlying error message or description.
    """

    def __init__(self, par: str, tentativas: int, causa: str) -> None:
        self.par = par
        self.tentativas = tentativas
        self.causa = causa
        super().__init__(
            f"Falha ao extrair dados para {par} após {tentativas} tentativas: {causa}"
        )
