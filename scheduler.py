"""
Ponto de entrada dedicado para o agendador do pipeline ETL.

Uso:
    python scheduler.py

O pipeline será executado automaticamente a cada 12 horas via Prefect.
Acesse o dashboard em http://localhost:4200 para monitorar as execuções.
"""

from flows.pipeline import iniciar_agendamento

if __name__ == "__main__":
    iniciar_agendamento()
