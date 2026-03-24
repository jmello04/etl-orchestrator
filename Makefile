.PHONY: help install run test lint format docker-up docker-down docker-logs migrate pipeline

help:
	@echo ""
	@echo "  ETL Orchestrator — Comandos disponíveis"
	@echo "  ─────────────────────────────────────────"
	@echo "  make install      Instala dependências"
	@echo "  make run          Inicia a API localmente"
	@echo "  make test         Executa todos os testes"
	@echo "  make lint         Analisa o código com ruff"
	@echo "  make format       Formata o código com ruff"
	@echo "  make docker-up    Sobe todos os containers"
	@echo "  make docker-down  Para todos os containers"
	@echo "  make docker-logs  Exibe logs dos containers"
	@echo "  make migrate      Executa migrações do banco"
	@echo "  make pipeline     Executa o pipeline manualmente"
	@echo ""

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --tb=short

lint:
	ruff check .

format:
	ruff format .

docker-up:
	docker compose up -d --build
	@echo ""
	@echo "  Serviços disponíveis:"
	@echo "  → API:     http://localhost:8000"
	@echo "  → Docs:    http://localhost:8000/docs"
	@echo "  → Prefect: http://localhost:4200"
	@echo ""

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

migrate:
	alembic upgrade head

pipeline:
	python -c "from flows.pipeline import pipeline_cotacoes; pipeline_cotacoes()"
