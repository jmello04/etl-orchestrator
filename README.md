<div align="center">

# ETL Orchestrator

**Pipeline ETL orquestrado para cotações financeiras USD-BRL e EUR-BRL**

[![CI](https://github.com/jmello04/etl-orchestrator/actions/workflows/ci.yml/badge.svg)](https://github.com/jmello04/etl-orchestrator/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Prefect](https://img.shields.io/badge/Prefect-3.x-1D4ED8?logo=prefect&logoColor=white)](https://prefect.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## Sobre

ETL Orchestrator é um pipeline de engenharia de dados para coleta e análise de cotações financeiras **USD-BRL** e **EUR-BRL**. O sistema busca dados históricos de 30 dias via API pública, normaliza e calcula estatísticas com Pandas/NumPy, e persiste no PostgreSQL com upsert idempotente — tudo orquestrado pelo Prefect com agendamento automático a cada 12 horas, retry em falhas e logs estruturados.

---

## Funcionalidades

| Recurso | Descrição |
|---------|-----------|
| Extração automática | Busca diária de 30 dias de cotações USD-BRL e EUR-BRL via AwesomeAPI |
| Transformação tipada | Normalização, renomeação de colunas, cálculo de médias e extremos do período |
| Carga idempotente | Upsert via `ON CONFLICT DO UPDATE` — re-executar o pipeline não duplica dados |
| Orquestração Prefect | Retry automático (3x por task, 1x por flow), UI de monitoramento em localhost:4200 |
| API REST | Disparar pipeline manualmente, consultar histórico de runs e cotações processadas |
| Logs estruturados | Console colorido + arquivo rotativo diário + log de erros persistente |
| Docker ready | App + PostgreSQL + Prefect Server com um único comando |
| Testes isolados | Testes unitários sem dependência de banco externo ou de rede |

---

## Arquitetura

```
  AwesomeAPI (ext.)  --httpx+retry-->  [1] EXTRACT  (flows/extract)
                                              |
                                         JSON bruto
                                              v
                                       [2] TRANSFORM (flows/transform)
                                         normalização / médias / deduplicação
                                              |
                                          DataFrame
                                              v
  PostgreSQL 16  <--upsert ON CONFLICT--  [3] LOAD  (flows/load)
    cotacoes
    pipeline_runs

  Prefect Scheduler -> dispara o pipeline a cada 12 horas
  Prefect UI        -> http://localhost:4200

  FastAPI REST API  -> http://localhost:8000
    POST /pipeline/run         Disparo manual
    GET  /pipeline/runs        Histórico de execuções
    GET  /pipeline/runs/{id}   Detalhes de uma execução
    GET  /data/cotacoes        Cotações processadas com filtros
```

---

## Stack

| Camada | Tecnologia | Motivo |
|--------|-----------|--------|
| Orquestração | Prefect 3.x | Retry nativo por task, UI de observabilidade e agendamento com serve() |
| API REST | FastAPI + Uvicorn | Validação automática, OpenAPI nativo, performance assíncrona |
| Banco de dados | PostgreSQL 16 + SQLAlchemy | Upsert nativo, tipagem forte, migrações versionadas via Alembic |
| Transformação | Pandas + NumPy | Manipulação eficiente de séries temporais e cálculo vetorizado |
| Extração HTTP | httpx | Cliente moderno com suporte a timeout e context manager |
| Logging | loguru | API fluente, rotação de arquivos e formatação colorida sem configuração extra |
| Testes | Pytest + respx + pytest-mock | Mocking de HTTP, banco e engine sem dependências externas |
| Infra | Docker + Docker Compose | Ambiente reproduzível com Prefect Server incluso |

---

## Como executar

### Pré-requisitos

- [Docker](https://www.docker.com/) e [Docker Compose](https://docs.docker.com/compose/) **ou** Python 3.12+ com PostgreSQL

---

### Opção 1 — Docker Compose (recomendado)

```bash
git clone https://github.com/jmello04/etl-orchestrator.git
cd etl-orchestrator

cp .env.example .env

docker compose up --build
```

Serviços disponíveis:
- **API:** http://localhost:8000/docs
- **Prefect UI:** http://localhost:4200

---

### Opção 2 — Execução local

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

pip install -r requirements.txt

cp .env.example .env

uvicorn app.main:app --reload
```

Para rodar o agendamento Prefect localmente:

```bash
python flows/pipeline.py
```

---

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/health` | Status da aplicação |
| `POST` | `/pipeline/run` | Dispara o pipeline ETL manualmente (async, 202) |
| `GET` | `/pipeline/runs` | Histórico de execuções com status e duração |
| `GET` | `/pipeline/runs/{id}` | Detalhes de uma execução específica |
| `GET` | `/data/cotacoes` | Cotações processadas (filtro por par e limite) |

**Exemplo — disparar pipeline:**

```bash
curl -X POST http://localhost:8000/pipeline/run
```

**Exemplo — consultar cotações USD-BRL:**

```bash
curl "http://localhost:8000/data/cotacoes?par_moeda=USD-BRL&limite=10"
```

---

## Variáveis de ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `DATABASE_URL` | URL de conexão PostgreSQL | `postgresql://etl_user:etl_password@localhost:5432/etl_db` |
| `APP_ENV` | Ambiente de execução | `development` |
| `LOG_LEVEL` | Nível mínimo de log | `INFO` |
| `PREFECT_API_URL` | URL da API do Prefect Server | `http://localhost:4200/api` |
| `CORS_ORIGINS` | Lista JSON de origens permitidas | `["http://localhost:3000","http://localhost:8000"]` |

---

## Testes

```bash
pytest tests/ -v
```

Os testes usam mocks de HTTP (respx) e de engine de banco (pytest-mock) — sem necessidade de PostgreSQL ou Prefect Server em execução.

---

## Estrutura de pastas

```
etl-orchestrator/
├── .github/workflows/ci.yml
├── app/
│   ├── main.py
│   ├── api/routes/
│   │   ├── data.py
│   │   └── pipeline.py
│   ├── core/
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   ├── logging.py
│   │   └── middleware.py
│   ├── infra/database/
│   │   ├── connection.py
│   │   ├── models.py
│   │   └── repository.py
│   └── schemas/
│       ├── cotacao.py
│       └── pipeline.py
├── flows/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── pipeline.py
├── alembic/
├── tests/
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── pyproject.toml
```

---

## Licença

Distribuído sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
