<div align="center">

# ETL Orchestrator

### Pipeline ETL de cotações financeiras com orquestração automática, retry, logs estruturados e CI/CD

[![CI](https://github.com/jmello04/etl-orchestrator/actions/workflows/ci.yml/badge.svg)](https://github.com/jmello04/etl-orchestrator/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Prefect](https://img.shields.io/badge/Prefect-3.x-1D4ED8?logo=prefect&logoColor=white)](https://prefect.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Changelog](https://img.shields.io/badge/Changelog-v1.0.0-informational)](CHANGELOG.md)

<br/>

> Coleta · Transforma · Armazena · Agenda · Monitora

</div>

---

## Sumário

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Stack Tecnológica](#stack-tecnológica)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Início Rápido](#início-rápido)
- [Endpoints da API](#endpoints-da-api)
- [Agendamento com Prefect](#agendamento-com-prefect)
- [Testes](#testes)
- [Migrações de Banco](#migrações-de-banco)
- [CI/CD](#cicd)
- [Logs](#logs)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

---

## Visão Geral

O **ETL Orchestrator** é um pipeline de engenharia de dados de nível produção para coleta e análise de cotações financeiras **USD-BRL** e **EUR-BRL**.

O sistema coleta dados históricos de 30 dias via API pública, normaliza e calcula estatísticas com Pandas/NumPy, e persiste no PostgreSQL com upsert seguro — tudo orquestrado pelo Prefect com agendamento automático, retry em falhas e alertas por log.

**O que o projeto demonstra na prática:**

- Separação clara entre lógica de negócio e infraestrutura (testabilidade real)
- Padrões de engenharia de dados: extração, transformação, carga, idempotência
- Boas práticas de API: schemas tipados, status codes, middleware, exceptions customizadas
- Operações profissionais: CI/CD, migrações versionadas, logs rotativos, Docker multi-stage

---

## Arquitetura

```
╔══════════════════════════════════════════════════════════════════════════╗
║                    PIPELINE ETL — VISÃO DE ALTO NÍVEL                   ║
╚══════════════════════════════════════════════════════════════════════════╝

  ┌──────────────────────┐     httpx + retry (3x)     ┌──────────────────┐
  │   AwesomeAPI (ext.)  │ ──────────────────────────▶ │  [1] EXTRACT     │
  │   USD-BRL · EUR-BRL  │                             │  flows/extract   │
  └──────────────────────┘                             └────────┬─────────┘
                                                                │ JSON bruto
                                                                ▼
                                                       ┌──────────────────┐
                                                       │  [2] TRANSFORM   │
                                                       │  flows/transform │
                                                       │                  │
                                                       │  • normalização  │
                                                       │  • média/mín/máx │
                                                       │  • deduplicação  │
                                                       └────────┬─────────┘
                                                                │ DataFrame
                                                                ▼
  ┌──────────────────────────────┐    upsert (ON CONFLICT)   ┌──────────────────┐
  │         PostgreSQL 16        │ ◀──────────────────────── │  [3] LOAD        │
  │  ┌────────────────────────┐  │                           │  flows/load      │
  │  │  cotacoes              │  │                           └──────────────────┘
  │  │  pipeline_runs         │  │
  │  └────────────────────────┘  │
  └──────────────────────────────┘

  ┌──────────────────────────────────────────────────────────────────────┐
  │  Prefect Scheduler  →  dispara o pipeline a cada 12 horas            │
  │  Prefect UI         →  http://localhost:4200                          │
  └──────────────────────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────────────────────┐
  │  FastAPI REST API   →  http://localhost:8000                          │
  │                                                                       │
  │  POST /pipeline/run         Disparo manual do pipeline               │
  │  GET  /pipeline/runs        Histórico de execuções com status        │
  │  GET  /pipeline/runs/{id}   Detalhes de uma execução específica      │
  │  GET  /data/cotacoes        Cotações processadas com filtros          │
  └──────────────────────────────────────────────────────────────────────┘
```

---

## Stack Tecnológica

| Camada            | Tecnologia                    | Versão     | Função                                      |
|-------------------|-------------------------------|------------|---------------------------------------------|
| Linguagem         | Python                        | 3.12       | Base do projeto                             |
| API REST          | FastAPI + Uvicorn             | 0.115      | Endpoints, schemas, middleware              |
| Orquestração      | Prefect                       | 3.x        | Flow, tasks, retry, agendamento             |
| Transformação     | Pandas + NumPy                | 2.x / 1.x  | Normalização e cálculo de estatísticas      |
| ORM               | SQLAlchemy                    | 2.0        | Mapeamento objeto-relacional, upsert        |
| Banco de dados    | PostgreSQL                    | 16         | Persistência com constraints e índices      |
| Migrações         | Alembic                       | 1.13       | Versionamento do schema do banco            |
| HTTP Client       | httpx                         | 0.27       | Requisições síncronas às APIs externas      |
| Logs              | loguru                        | 0.7        | Logs estruturados, rotativos, por nível     |
| Validação         | Pydantic v2                   | 2.9        | Schemas de request/response tipados         |
| Testes            | pytest + respx + pytest-mock  | 8.x        | Testes unitários com mocks de HTTP e DB     |
| Linting           | ruff                          | 0.4        | Análise estática e formatação               |
| Containers        | Docker + Compose              | —          | Build multi-stage, usuário não-root         |
| CI/CD             | GitHub Actions                | —          | Lint → Testes → Build automáticos           |

---

## Estrutura do Projeto

```
etl-orchestrator/
│
├── .github/
│   └── workflows/
│       └── ci.yml                  # Pipeline CI: lint → testes → docker build
│
├── alembic/                        # Migrações versionadas do banco de dados
│   ├── versions/
│   │   └── 001_initial_schema.py   # Schema inicial: cotacoes + pipeline_runs
│   ├── env.py
│   └── script.py.mako
│
├── app/                            # Aplicação FastAPI
│   ├── main.py                     # Entry point: middlewares, routers, lifespan
│   │
│   ├── api/
│   │   └── routes/
│   │       ├── pipeline.py         # POST /pipeline/run · GET /pipeline/runs
│   │       └── data.py             # GET /data/cotacoes
│   │
│   ├── schemas/                    # Contratos de entrada e saída (Pydantic v2)
│   │   ├── cotacao.py
│   │   └── pipeline.py
│   │
│   ├── core/                       # Configurações e utilitários transversais
│   │   ├── config.py               # Settings via pydantic-settings + .env
│   │   ├── logging.py              # Configuração do loguru
│   │   ├── middleware.py           # Request ID + tempo de resposta
│   │   └── exceptions.py           # Exceções HTTP customizadas
│   │
│   └── infra/
│       └── database/
│           ├── models.py           # Modelos SQLAlchemy ORM
│           ├── connection.py       # Engine e session factory
│           └── repository.py       # Repository pattern (acesso a dados)
│
├── flows/                          # Pipeline ETL com Prefect
│   ├── extract.py                  # Task: coleta via httpx + retry automático
│   ├── transform.py                # Task: normalização com Pandas/NumPy
│   ├── load.py                     # Task: upsert no PostgreSQL
│   └── pipeline.py                 # Flow principal + agendamento 12h
│
├── tests/                          # Suíte de testes automatizados
│   ├── conftest.py                 # Fixtures compartilhadas
│   ├── test_extract.py             # Testes com mock HTTP (respx)
│   ├── test_transform.py           # Testes da lógica de transformação
│   └── test_load.py                # Testes com mock de banco (pytest-mock)
│
├── logs/                           # Logs rotativos (gerados em runtime)
│
├── scheduler.py                    # Entry point do agendador Prefect
├── alembic.ini                     # Configuração do Alembic
├── pyproject.toml                  # Config centralizada: ruff, mypy, pytest
├── Makefile                        # Comandos do desenvolvedor
├── Dockerfile                      # Build multi-stage com usuário não-root
├── docker-compose.yml              # API + PostgreSQL + Prefect Server
├── requirements.txt                # Dependências Python
├── .env.example                    # Variáveis de ambiente documentadas
├── .pre-commit-config.yaml         # Hooks de qualidade de código
├── CHANGELOG.md                    # Histórico de versões
├── CONTRIBUTING.md                 # Guia para contribuidores
└── README.md
```

---

## Início Rápido

### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/)
- Python 3.12+ (apenas para execução local sem Docker)

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

Aguarde o boot completo (~15s) e acesse:

| Serviço          | URL                          | Descrição                    |
|------------------|------------------------------|------------------------------|
| API (FastAPI)    | http://localhost:8000        | REST API principal           |
| Swagger UI       | http://localhost:8000/docs   | Documentação interativa      |
| ReDoc            | http://localhost:8000/redoc  | Documentação alternativa     |
| Prefect UI       | http://localhost:4200        | Dashboard de orquestração    |
| PostgreSQL       | localhost:5432               | Banco de dados               |

### Execução Local (sem Docker)

```bash
# 1. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
.venv\Scripts\activate          # Windows

# 2. Instale as dependências
make install

# 3. Configure o ambiente
cp .env.example .env

# 4. Suba apenas o banco de dados
docker compose up postgres -d

# 5. Execute as migrações
make migrate

# 6. Inicie a API
make run
```

---

## Endpoints da API

### `POST /pipeline/run` — Disparar o pipeline

Executa o pipeline em background e retorna imediatamente com o `run_id`.

```bash
curl -X POST http://localhost:8000/pipeline/run
```

```json
{
  "mensagem": "Pipeline iniciado com sucesso. Acompanhe pelo run_id.",
  "run_id": 1,
  "status": "running",
  "iniciado_em": "2024-03-24T10:30:00"
}
```

### `GET /pipeline/runs` — Histórico de execuções

```bash
curl "http://localhost:8000/pipeline/runs?limite=10"
```

```json
{
  "total": 2,
  "execucoes": [
    {
      "id": 2,
      "status": "success",
      "iniciado_em": "2024-03-24T22:30:00",
      "finalizado_em": "2024-03-24T22:30:14",
      "duracao_segundos": 14.2,
      "registros_processados": 60,
      "erro": null
    }
  ]
}
```

### `GET /pipeline/runs/{id}` — Detalhes de uma execução

```bash
curl http://localhost:8000/pipeline/runs/1
```

### `GET /data/cotacoes` — Consultar cotações processadas

```bash
# Todas as cotações (padrão: últimas 100)
curl http://localhost:8000/data/cotacoes

# Filtrar por par de moeda e limitar resultados
curl "http://localhost:8000/data/cotacoes?par_moeda=USD-BRL&limite=30"
```

```json
{
  "total": 30,
  "par_moeda": "USD-BRL",
  "cotacoes": [
    {
      "id": 1,
      "par_moeda": "USD-BRL",
      "data_referencia": "2024-03-24",
      "compra": 5.1234,
      "venda": 5.1350,
      "maximo": 5.1500,
      "minimo": 5.1100,
      "media_compra_periodo": 5.0987,
      "media_venda_periodo": 5.1102,
      "minimo_periodo": 4.9800,
      "maximo_periodo": 5.1500,
      "processado_em": "2024-03-24T10:30:12"
    }
  ]
}
```

---

## Agendamento com Prefect

O pipeline executa **automaticamente a cada 12 horas** via Prefect.

```bash
# Ativar o agendador
python scheduler.py
```

```bash
# Executar o pipeline uma vez manualmente pelo terminal
make pipeline
```

Acesse o dashboard do Prefect em **http://localhost:4200** para:
- Visualizar o histórico completo de execuções
- Monitorar logs em tempo real por etapa
- Configurar notificações de falha
- Pausar ou ajustar o agendamento

---

## Testes

```bash
# Executar todos os testes
make test

# Com relatório de cobertura
pytest tests/ -v --cov=app --cov=flows --cov-report=term-missing

# Apenas um arquivo de testes
pytest tests/test_transform.py -v
```

Os testes são totalmente isolados de serviços externos:
- Chamadas HTTP mockadas com **respx**
- Banco de dados mockado com **pytest-mock**
- Nenhuma dependência de Docker ou rede externa

---

## Migrações de Banco

```bash
# Aplicar todas as migrações pendentes
make migrate

# Criar uma nova migração a partir dos modelos
alembic revision --autogenerate -m "adiciona_coluna_x"

# Reverter a última migração
alembic downgrade -1

# Ver histórico de migrações
alembic history
```

---

## CI/CD

O pipeline de CI executa automaticamente em todo push para `main` ou `develop`
e em todo Pull Request aberto para `main`.

```
push → main / develop
         │
         ├── [1] Lint         ruff check . (análise estática)
         │
         ├── [2] Tests        pytest com PostgreSQL real no GitHub Actions
         │        └── needs: lint
         │
         └── [3] Docker Build validação do Dockerfile multi-stage
                  └── needs: tests
```

---

## Logs

| Arquivo                        | Conteúdo                          | Rotação   | Retenção  |
|--------------------------------|-----------------------------------|-----------|-----------|
| `logs/etl_YYYY-MM-DD.log`      | Log completo de todas as etapas   | Diária    | 30 dias   |
| `logs/etl_errors.log`          | Apenas erros e alertas críticos   | 50 MB     | 60 dias   |

Cada requisição HTTP registra automaticamente:
- Método e path
- Status code e tempo de resposta
- `X-Request-ID` único por requisição

---

## Variáveis de Ambiente

Copie `.env.example` para `.env` e ajuste conforme o ambiente:

| Variável          | Padrão                                                  | Descrição                              |
|-------------------|---------------------------------------------------------|----------------------------------------|
| `DATABASE_URL`    | `postgresql://etl_user:etl_password@localhost/etl_db`   | String de conexão do PostgreSQL        |
| `POSTGRES_USER`   | `etl_user`                                              | Usuário do banco (Docker Compose)      |
| `POSTGRES_PASSWORD`| `etl_password`                                         | Senha do banco (Docker Compose)        |
| `POSTGRES_DB`     | `etl_db`                                                | Nome do banco (Docker Compose)         |
| `APP_ENV`         | `development`                                           | Ambiente: `development` ou `production`|
| `LOG_LEVEL`       | `INFO`                                                  | `DEBUG` · `INFO` · `WARNING` · `ERROR` |
| `PREFECT_API_URL` | `http://localhost:4200/api`                             | URL do servidor Prefect                |
| `CORS_ORIGINS`    | `["http://localhost:3000","http://localhost:8000"]`      | Origens permitidas (lista JSON)        |

---

## Contribuindo

Contribuições são bem-vindas! Leia o [Guia de Contribuição](CONTRIBUTING.md) para entender o fluxo de trabalho, convenção de commits e padrões de código adotados.

---

## Licença

Distribuído sob a licença **MIT**. Consulte [LICENSE](LICENSE) para mais informações.

---

<div align="center">
<sub>Feito com foco em qualidade, organização e boas práticas de engenharia de dados.</sub>
</div>
