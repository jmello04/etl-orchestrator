# Guia de Contribuição

Obrigado pelo interesse em contribuir com o **ETL Orchestrator**!
Este guia descreve como configurar o ambiente, o fluxo de trabalho esperado e os padrões adotados no projeto.

---

## Sumário

- [Pré-requisitos](#pré-requisitos)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Executando os Testes](#executando-os-testes)
- [Padrões de Código](#padrões-de-código)
- [Fluxo de Contribuição](#fluxo-de-contribuição)
- [Convenção de Commits](#convenção-de-commits)
- [Estrutura de Branches](#estrutura-de-branches)

---

## Pré-requisitos

- Python **3.12+**
- Docker e Docker Compose
- Git

---

## Configuração do Ambiente

```bash
# 1. Fork e clone o repositório
git clone https://github.com/SEU_USUARIO/etl-orchestrator.git
cd etl-orchestrator

# 2. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows

# 3. Instale as dependências
make install

# 4. Configure o ambiente
cp .env.example .env

# 5. Instale os hooks de qualidade de código
pre-commit install

# 6. Suba o banco de dados para desenvolvimento
docker compose up postgres -d

# 7. Execute as migrações
make migrate
```

---

## Executando os Testes

```bash
# Todos os testes
make test

# Com relatório de cobertura
pytest tests/ -v --cov=app --cov=flows --cov-report=term-missing

# Um teste específico
pytest tests/test_transform.py -v
```

Os testes são independentes de serviços externos:
- Chamadas HTTP são mockadas com **respx**
- O banco de dados é mockado com **pytest-mock**

---

## Padrões de Código

Este projeto usa **ruff** para linting e formatação automática.

```bash
# Verificar problemas
make lint

# Corrigir automaticamente
make format
```

Os hooks do `pre-commit` rodam automaticamente antes de cada commit.
Se um hook falhar, corrija o problema e faça o commit novamente.

### Diretrizes gerais

- **Funções de lógica pura** devem ser separadas dos decoradores Prefect (`@task`, `@flow`)
  para garantir testabilidade. Veja `flows/extract.py` como referência.
- **Type hints** são obrigatórios em todas as funções públicas.
- **Logs** devem usar `loguru` com nível apropriado (`info`, `warning`, `error`, `success`).
- **Sem comentários óbvios** — o código deve ser autoexplicativo. Comente apenas decisões não evidentes.

---

## Fluxo de Contribuição

1. Crie uma branch a partir de `main`:

```bash
git checkout -b feat/nome-da-funcionalidade
# ou
git checkout -b fix/nome-do-bug
```

2. Faça suas alterações com commits atômicos e bem descritos.

3. Garanta que todos os testes passam:

```bash
make test
make lint
```

4. Abra um **Pull Request** para a branch `main` com:
   - Título claro e objetivo
   - Descrição do que foi alterado e por quê
   - Referência à issue relacionada (se houver)

---

## Convenção de Commits

Este projeto segue o padrão [Conventional Commits](https://www.conventionalcommits.org/pt-br/):

| Prefixo    | Uso                                          |
|------------|----------------------------------------------|
| `feat:`    | Nova funcionalidade                          |
| `fix:`     | Correção de bug                              |
| `refactor:`| Refatoração sem mudança de comportamento     |
| `test:`    | Adição ou correção de testes                 |
| `docs:`    | Apenas documentação                          |
| `chore:`   | Tarefas de manutenção (deps, config, etc.)   |
| `ci:`      | Mudanças no pipeline de CI/CD                |

**Exemplos:**

```
feat: adiciona endpoint GET /data/cotacoes com filtro por par
fix: corrige lógica de upsert no PostgreSQL com xmax
docs: atualiza README com exemplos de uso da API
test: adiciona testes de borda para transformar_cotacoes_logica
```

---

## Estrutura de Branches

| Branch    | Finalidade                              |
|-----------|-----------------------------------------|
| `main`    | Código estável, pronto para produção    |
| `develop` | Integração de features antes do merge  |
| `feat/*`  | Desenvolvimento de novas funcionalidades|
| `fix/*`   | Correções de bugs                       |

---

Dúvidas? Abra uma [issue](https://github.com/jmello04/etl-orchestrator/issues).
