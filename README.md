# ETL Orchestrator — Cotações Financeiras

Pipeline ETL orquestrado para coleta, transformação e armazenamento de cotações financeiras USD-BRL e EUR-BRL, com agendamento automático via Prefect, logs estruturados e execução containerizada com Docker.

---

## Diagrama do Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                     PIPELINE ETL — FLUXO COMPLETO               │
└─────────────────────────────────────────────────────────────────┘

  ┌──────────────────────┐
  │   APIs Externas      │
  │  USD-BRL / EUR-BRL   │
  │  (AwesomeAPI)        │
  └──────────┬───────────┘
             │  httpx + retry (3x)
             ▼
  ┌──────────────────────┐
  │  [1] EXTRACT         │  ← Busca dados das APIs
  │  flows/extract.py    │  ← Valida resposta HTTP
  │                      │  ← Retry automático (3x)
  └──────────┬───────────┘
             │  dados brutos (JSON)
             ▼
  ┌──────────────────────┐
  │  [2] TRANSFORM       │  ← Normaliza com Pandas
  │  flows/transform.py  │  ← Calcula média, mín, máx
  │                      │  ← Remove duplicatas
  └──────────┬───────────┘
             │  DataFrame normalizado
             ▼
  ┌──────────────────────┐
  │  [3] LOAD            │  ← Upsert no PostgreSQL
  │  flows/load.py       │  ← Evita duplicatas
  │                      │  ← SQLAlchemy + psycopg2
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────┐
  │  PostgreSQL          │
  │  tabela: cotacoes    │
  │  tabela: pipeline_   │
  │          runs        │
  └──────────────────────┘

  ┌──────────────────────────────────────────┐
  │  Prefect Scheduler (a cada 12h)          │
  │  → agenda e monitora o pipeline          │
  └──────────────────────────────────────────┘

  ┌──────────────────────────────────────────┐
  │  FastAPI (REST)                           │
  │  POST /pipeline/run     → disparo manual │
  │  GET  /pipeline/runs    → histórico      │
  │  GET  /pipeline/runs/id → detalhes       │
  │  GET  /data/cotacoes    → dados salvos   │
  └──────────────────────────────────────────┘
```

---

## Estrutura do Projeto

```
etl-orchestrator/
├── flows/                  # Tarefas Prefect do pipeline ETL
│   ├── extract.py          # Extração via httpx com retry
│   ├── transform.py        # Transformação com Pandas/NumPy
│   ├── load.py             # Carga no PostgreSQL com upsert
│   └── pipeline.py         # Orquestrador principal (Flow)
├── app/
│   ├── main.py             # Aplicação FastAPI
│   ├── api/
│   │   └── routes/
│   │       ├── pipeline.py # Endpoints do pipeline
│   │       └── data.py     # Endpoints dos dados
│   ├── core/
│   │   ├── config.py       # Configurações via .env
│   │   └── logging.py      # Configuração loguru
│   └── infra/
│       └── database/
│           ├── models.py       # Modelos SQLAlchemy
│           ├── connection.py   # Engine e sessão
│           └── repository.py   # Repositórios de dados
├── tests/                  # Testes com pytest
├── logs/                   # Logs rotativos (gerados em runtime)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/)
- Python 3.12+ (para execução local sem Docker)

---

## Subindo o Projeto com Docker

### 1. Clone o repositório

```bash
git clone https://github.com/jmello04/etl-orchestrator.git
cd etl-orchestrator
```

### 2. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` conforme necessário.

### 3. Suba os containers

```bash
docker compose up -d --build
```

### 4. Verifique os serviços

| Serviço         | URL                          |
|-----------------|------------------------------|
| API (FastAPI)   | http://localhost:8000        |
| Docs (Swagger)  | http://localhost:8000/docs   |
| Prefect UI      | http://localhost:4200        |
| PostgreSQL      | localhost:5432               |

---

## Execução Local (sem Docker)

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows

pip install -r requirements.txt

cp .env.example .env

uvicorn app.main:app --reload
```

---

## Endpoints da API

### Executar o pipeline manualmente

```http
POST /pipeline/run
```

**Resposta:**
```json
{
  "mensagem": "Pipeline iniciado com sucesso.",
  "run_id": 1,
  "status": "running",
  "iniciado_em": "2024-01-15T10:30:00"
}
```

### Listar histórico de execuções

```http
GET /pipeline/runs
```

### Detalhe de uma execução

```http
GET /pipeline/runs/{id}
```

### Consultar cotações processadas

```http
GET /data/cotacoes?par_moeda=USD-BRL&limite=30
```

---

## Agendamento Automático (Prefect)

O pipeline executa automaticamente a cada **12 horas** via Prefect.

Para iniciar o agendamento manualmente:

```bash
python flows/pipeline.py
```

---

## Testes

```bash
pytest tests/ -v
```

---

## Logs

Os logs são gravados em:

- `logs/etl_YYYY-MM-DD.log` — log completo rotativo por dia
- `logs/etl_errors.log` — apenas erros (retenção de 60 dias)

---

## Variáveis de Ambiente

| Variável          | Padrão                                              | Descrição                    |
|-------------------|-----------------------------------------------------|------------------------------|
| `DATABASE_URL`    | `postgresql://etl_user:etl_password@localhost/etl_db` | String de conexão PostgreSQL |
| `APP_ENV`         | `development`                                       | Ambiente da aplicação        |
| `LOG_LEVEL`       | `INFO`                                              | Nível de log                 |
| `PREFECT_API_URL` | `http://localhost:4200/api`                         | URL do servidor Prefect      |

---

## Tecnologias

| Tecnologia      | Uso                              |
|-----------------|----------------------------------|
| Python 3.12     | Linguagem principal              |
| FastAPI         | API REST                         |
| Prefect 3       | Orquestração e agendamento       |
| Pandas / NumPy  | Transformação de dados           |
| SQLAlchemy 2    | ORM e acesso ao banco            |
| PostgreSQL 16   | Banco de dados relacional        |
| loguru          | Logs estruturados                |
| httpx           | Requisições HTTP assíncronas     |
| Docker Compose  | Containerização                  |
| pytest          | Testes automatizados             |

---

## Licença

MIT
