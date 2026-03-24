from fastapi import HTTPException, status


class PipelineRunNaoEncontrado(HTTPException):
    def __init__(self, run_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execução com id={run_id} não encontrada.",
        )


class ErroBancoDeDados(HTTPException):
    def __init__(self, detalhe: str = "Erro ao acessar o banco de dados."):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detalhe,
        )


class ErroExtracaoDados(Exception):
    def __init__(self, par: str, tentativas: int, causa: str):
        self.par = par
        self.tentativas = tentativas
        self.causa = causa
        super().__init__(
            f"Falha ao extrair dados para {par} após {tentativas} tentativas: {causa}"
        )
