# Changelog

Todas as mudanças relevantes deste projeto serão documentadas neste arquivo.

O formato segue o padrão [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [1.0.0] — 2024-03-24

### Adicionado
- Pipeline ETL completo para cotações USD-BRL e EUR-BRL via AwesomeAPI
- Etapa de **Extração** com `httpx`, retry automático (3x) e validação de resposta
- Etapa de **Transformação** com `Pandas`/`NumPy`: normalização, cálculo de média, mínimo e máximo do período
- Etapa de **Carga** com `SQLAlchemy` e upsert via `ON CONFLICT DO UPDATE` no PostgreSQL
- Orquestração com **Prefect 3** e agendamento automático a cada 12 horas
- **FastAPI** com 4 endpoints REST: `POST /pipeline/run`, `GET /pipeline/runs`, `GET /pipeline/runs/{id}`, `GET /data/cotacoes`
- Schemas de resposta tipados com **Pydantic v2**
- Logs estruturados com **loguru**: rotação diária, retenção de 30 dias, arquivo de erros separado
- Middleware de logging com `X-Request-ID` e `X-Process-Time` em cada requisição
- Exceções customizadas por domínio (`PipelineRunNaoEncontrado`, `ErroBancoDeDados`)
- Migrações versionadas com **Alembic** (`001_initial_schema`)
- CORS configurável via variável de ambiente `CORS_ORIGINS`
- **Dockerfile** multi-stage (`builder` + `runtime`) com usuário não-root e HEALTHCHECK
- **Docker Compose** com PostgreSQL, API e Prefect Server integrados em rede dedicada
- **GitHub Actions CI/CD**: lint com `ruff` → testes com PostgreSQL real → build Docker
- **Makefile** com comandos: `install`, `run`, `test`, `lint`, `format`, `docker-up`, `docker-down`, `migrate`, `pipeline`
- Configuração centralizada com **pyproject.toml** (ruff, mypy, pytest)
- Hooks de qualidade de código com **pre-commit** (ruff, trailing-whitespace, detect-private-key)
- Suíte de testes com **pytest**, **respx** (mock HTTP) e **pytest-mock** (mock de banco)
- `scheduler.py` como ponto de entrada dedicado para o agendador
- Documentação completa no `README.md` com diagrama de arquitetura, exemplos e tabelas

### Corrigido
- Import inexistente `task_input_hash` do módulo `prefect.tasks` (incompatível com Prefect 3.x)
- Import `from prefect.schedules import Interval` removido (módulo não existe no Prefect 3.x)
- `build-backend` inválido no `pyproject.toml` (`setuptools.backends.legacy:build` → `setuptools.build_meta`)
- Healthcheck do container usando `httpx` (terceiro) substituído por `urllib.request` (stdlib)
- `datetime.utcnow()` depreciado no Python 3.12 substituído por `datetime.now(timezone.utc)`
- `default=datetime.utcnow` nos models SQLAlchemy substituído por lambda com `timezone.utc`
- Lógica de `rowcount` no upsert corrigida usando `RETURNING (xmax::text::int > 0)` do PostgreSQL
- Multi-stage Docker build: pacotes copiados para `/usr/local` (sem `PYTHONPATH` manual)
- Testes usavam `.fn()` em tasks do Prefect (API inexistente no Prefect 3) — substituídos por funções de lógica pura

---

[1.0.0]: https://github.com/jmello04/etl-orchestrator/releases/tag/v1.0.0
