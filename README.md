<div align="center">

# ETL Orchestrator

**Pipeline ETL de cotações financeiras com orquestração, retry automático e logs estruturados**

[![CI](https://github.com/jmello04/etl-orchestrator/actions/workflows/ci.yml/badge.svg)](https://github.com/jmello04/etl-orchestrator/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com)
[![Prefect](https://img.shields.io/badge/Prefect-3.x-blue.svg)](https://prefect.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## Visão Geral

O **ETL Orchestrator** é um pipeline de dados robusto que coleta cotações financeiras de USD-BRL e EUR-BRL via API pública, transforma os dados com Pandas/NumPy e armazena no PostgreSQL com upsert automático. Todo o fluxo é orquestrado pelo Prefect com agendamento a cada 12 horas, retry automático em falhas e logs estruturados com rotação diária.

---

## Arquitetura do Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PIPELINE ETL — FLUXO DE DADOS                        │
└─────────────────────────────────────────────────────────────────────────┘

   Fontes Externas                  Pipeline ETL                 Destino
  ┌─────────────────┐              ┌─────────────┐
  │  AwesomeAPI     │              │             │
  │  USD-BRL (30d)  │──────────────▶  [EXTRACT]  │  httpx + retry (3x)
  │  EUR-BRL (30d)  │              │             │
  └─────────────────┘              └──────┬──────┘
                                          │ JSON bruto
                                          ▼
                                   ┌─────────────┐
                                   │             │
                                   │ [TRANSFORM] │  Pandas · NumPy
                                   │             │  média · mín · máx
                                   └──────┬──────┘
                                          │ DataFrame normalizado
                                          ▼
                                   ┌─────────────┐          ┌─────────────────┐
                                   │             │  upsert  │   PostgreSQL 16  │
                                   │   [LOAD]    │─────────▶│   ─────────────  │
                                   │             │          │   cotacoes       │
                                   └──────┬──────┘          │   pipeline_runs  │
                                          │                 └─────────────────┘
                                          ▼
                                   ┌─────────────┐
                                   │    [LOG]    │  loguru · rotação diária
                                   │             │  status · duração · erros
                                   └─────────────┘

  ┌──────────────────────────────────────────────────────────────────┐
  │  Prefect Scheduler  →  execução automática a cada 12 horas       │
  └──────────────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────────────┐
  │  FastAPI REST API   →  disparo manual · histórico · consulta     │
  └──────────────────────────────────────────────────────────────────┘
```

---

## Stack Tecnológica

| Camada             | Tecnologia              | Versão   |
|--------------------|-------------------------|----------|
| Linguagem          | Python                  | 3.12     |
| API REST           | FastAPI + Uvicorn       | 0.115    |
| Orquestração       | Prefect                 | 3.x      |
| Transformação      | Pandas + NumPy          | 2.x      |
| ORM / Banco        | SQLAlchemy + PostgreSQL | 2.0 / 16 |
| Migrações          | Alembic                 | 1.13     |
| HTTP Client        | httpx                   | 0.27     |
| Logs               | loguru                  | 0.7      |
| Testes             | pytest + respx          | 8.x      |
| Containers         | Docker + Compose        | —        |
| CI/CD              | GitHub Actions          | —        |

---

## Estrutura do Projeto

```
etl-orchestrator/
│
├── .github/
│   └── workflows/
│       └── ci.yml              # CI/CD: lint → testes → build Docker
│
├── alembic/
│   ├── versions/
│   │   └── 001_initial_schema.py
│   ├── env.py
│   └── script.py.mako
│
├── app/
│   ├── main.py                 # Aplicação FastAPI com middleware
│   ├── schemas/
│   │   ├── cotacao.py          # Pydantic: resposta de cotações
│   │   └── pipeline.py         # Pydantic: resposta de runs
│   ├── api/
│   │   └── routes/
│   │       ├── pipeline.py     # POST /pipeline/run · GET /pipeline/runs
│   │       └── data.py         # GET /data/cotacoes
│   ├── core/
│   │   ├── config.py           # Configurações via .env (pydantic-settings)
│   │   ├── logging.py          # loguru: console + arquivo rotativo
│   │   ├── middleware.py       # Request ID + tempo de resposta
│   │   └── exceptions.py       # Exceções customizadas
│   └── infra/
│       └── database/
│           ├── models.py       # SQLAlchemy ORM
│           ├── connection.py   # Engine + session factory
│           └── repository.py   # Repository pattern
│
├── flows/
│   ├── extract.py              # Prefect task: httpx + retry
│   ├── transform.py            # Prefect task: Pandas/NumPy
│   ├── load.py                 # Prefect task: upsert PostgreSQL
│   └── pipeline.py             # Prefect flow + agendamento 12h
│
├── tests/
│   ├── conftest.py             # Fixtures e dados de teste
│   ├── test_extract.py         # Testes de extração (mock HTTP)
│   ├── test_transform.py       # Testes de transformação
│   └── test_load.py            # Testes de carga (mock DB)
│
├── logs/                       # Logs rotativos (gerados em runtime)
├── .github/workflows/ci.yml    # Pipeline CI/CD
├── .pre-commit-config.yaml     # Hooks de qualidade de código
├── alembic.ini                 # Configuração de migrações
├── pyproject.toml              # Configuração do projeto (ruff, pytest, mypy)
├── Makefile                    # Comandos do desenvolvedor
├── docker-compose.yml          # Orquestração de containers
├── Dockerfile                  # Build multi-stage (builder + runtime)
├── requirements.txt            # Dependências Python
├── .env.example                # Variáveis de ambiente de exemplo
└── README.md
```

---

## Início Rápido

### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/)
- Python 3.12+ (apenas para execução local)

### Com Docker (recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/jmello04/etl-orchestrator.git
cd etl-orchestrator

# 2. Configure as variáveis de ambiente
cp .env.example .env

# 3. Suba todos os containers
make docker-up
```

Serviços disponíveis após o boot:

| Serviço          | URL                        | Descrição                     |
|------------------|----------------------------|-------------------------------|
| API (FastAPI)    | http://localhost:8000      | REST API principal            |
| Documentação     | http://localhost:8000/docs | Swagger UI interativo         |
| ReDoc            | http://localhost:8000/redoc | Documentação alternativa     |
| Prefect UI       | http://localhost:4200      | Dashboard de orquestração     |
| PostgreSQL       | localhost:5432             | Banco de dados                |

### Execução Local

```bash
# Instalar dependências
make install

# Configurar ambiente
cp .env.example .env

# Iniciar API
make run

# Em outro terminal, executar pipeline manualmente
make pipeline
```

---

## Endpoints da API

### `POST /pipeline/run` — Disparar pipeline manualmente

```bash
curl -X POST http://localhost:8000/pipeline/run
```

```json
{
  "mensagem": "Pipeline iniciado com sucesso. Acompanhe pelo run_id.",
  "run_id": 1,
  "status": "running",
  "iniciado_em": "2024-01-15T10:30:00"
}
```

### `GET /pipeline/runs` — Histórico de execuções

```bash
curl http://localhost:8000/pipeline/runs?limite=10
```

### `GET /pipeline/runs/{id}` — Detalhes de uma execução

```bash
curl http://localhost:8000/pipeline/runs/1
```

```json
{
  "id": 1,
  "status": "success",
  "iniciado_em": "2024-01-15T10:30:00",
  "finalizado_em": "2024-01-15T10:30:12",
  "duracao_segundos": 12.4,
  "registros_processados": 60,
  "erro": null
}
```

### `GET /data/cotacoes` — Consultar cotações processadas

```bash
# Todas as cotações
curl http://localhost:8000/data/cotacoes

# Filtrar por par de moeda
curl "http://localhost:8000/data/cotacoes?par_moeda=USD-BRL&limite=30"
```

---

## Testes

```bash
# Executar todos os testes
make test

# Com cobertura
pytest tests/ -v --cov=app --cov=flows --cov-report=term-missing
```

---

## Migrações de Banco de Dados

```bash
# Aplicar todas as migrações
make migrate

# Criar nova migração
alembic revision --autogenerate -m "descricao_da_alteracao"

# Reverter última migração
alembic downgrade -1
```

---

## Agendamento Automático (Prefect)

O pipeline é agendado para rodar **automaticamente a cada 12 horas** via Prefect.

Para ativar o agendamento:

```bash
python flows/pipeline.py
```

Acesse o dashboard do Prefect em http://localhost:4200 para monitorar execuções, visualizar logs e configurar alertas.

---

## Variáveis de Ambiente

| Variável          | Padrão                                                | Descrição                    |
|-------------------|-------------------------------------------------------|------------------------------|
| `DATABASE_URL`    | `postgresql://etl_user:etl_password@localhost/etl_db` | Conexão com o PostgreSQL     |
| `APP_ENV`         | `development`                                         | Ambiente da aplicação        |
| `LOG_LEVEL`       | `INFO`                                                | Nível de log (DEBUG/INFO/WARNING/ERROR) |
| `PREFECT_API_URL` | `http://localhost:4200/api`                           | URL do servidor Prefect      |

---

## Logs

Os logs são gravados em:

| Arquivo                    | Conteúdo                       | Retenção  |
|----------------------------|--------------------------------|-----------|
| `logs/etl_YYYY-MM-DD.log`  | Log completo rotativo por dia  | 30 dias   |
| `logs/etl_errors.log`      | Apenas erros críticos          | 60 dias   |

---

## CI/CD

O pipeline de CI executa automaticamente em todo push para `main` ou `develop`:

1. **Lint** — análise estática com `ruff`
2. **Testes** — pytest com banco PostgreSQL real no GitHub Actions
3. **Docker Build** — validação do Dockerfile multi-stage

---

## Licença

Distribuído sob a licença MIT. Consulte [LICENSE](LICENSE) para mais informações.
