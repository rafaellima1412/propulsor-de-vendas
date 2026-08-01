# Propulsor de Vendas

API de gestão de campanhas de vendas, times e usuários, construída com **FastAPI**, **PostgreSQL/PostGIS** e **Clean Architecture**. Projeto usado como peça de portfólio para vagas de Desenvolvedor(a) Python Sênior.

[![CI](https://github.com/rafaellima1412/propulsor-de-vendas/actions/workflows/ci.yml/badge.svg)](https://github.com/rafaellima1412/propulsor-de-vendas/actions/workflows/ci.yml)

## Stack

- **FastAPI** + **Jinja2** (API + páginas server-rendered)
- **PostgreSQL** com **PostGIS** (dados geoespaciais dos locais de campanha) via **SQLAlchemy 2.0**
- **Alembic** para migrations
- **dependency-injector** para injeção de dependência (Clean Architecture: `domain` / `application` / `infra`)
- **JWT** (python-jose) + **bcrypt** (passlib) para autenticação
- **pytest** (unitário + integração contra Postgres real) com **ruff** para lint
- **Docker** / **docker-compose** para ambiente reproduzível
- **GitHub Actions** para CI

## Arquitetura

```
src/
├── domain/        # entidades, enums, validadores e schemas Pydantic — sem dependência de framework
├── application/    # casos de uso, DTOs e interfaces de repositório (portas)
└── infra/          # adapters: SQLAlchemy, rotas FastAPI, DI container, settings
```

O domínio não depende de infraestrutura; os casos de uso dependem apenas de **interfaces** de repositório (`IUserRepository`, `ITimeRepository`...), implementadas na camada `infra`. A ligação entre eles é feita pelo `Container` (`src/infra/dy/container.py`), usando [dependency-injector](https://python-dependency-injector.ets-labs.org/).

## Como rodar (Docker — recomendado)

```bash
cp .env.example .env   # ajuste SECRET_KEY se quiser
docker compose up --build
```

A API sobe em `http://localhost:8000` (docs interativos em `/docs`). O `docker-compose.yml` sobe um Postgres com PostGIS já com a extensão habilitada e cria automaticamente um segundo banco (`propulsor_vendas_test`) para a suíte de testes.

Migrations rodam automaticamente no start do container (`alembic upgrade head` antes do `uvicorn`).

## Como rodar localmente (sem Docker)

Requer Python 3.12+, Poetry e um Postgres com PostGIS acessível.

```bash
poetry install --with dev
cp .env.example .env   # aponte para seu Postgres local

poetry run alembic upgrade head
poetry run uvicorn main:app --reload
```

## Testes

```bash
poetry run pytest                                     # suíte completa
poetry run pytest tests/unit                          # só unitários (sem banco)
poetry run pytest tests/integration                   # só integração (precisa de Postgres)
poetry run pytest --cov=src --cov-report=term-missing  # com cobertura
```

Os testes de integração usam um banco isolado (`TEST_POSTGRES_DB`, padrão `propulsor_vendas_test`) e nunca tocam o banco de desenvolvimento — veja `tests/conftest.py`.

```bash
poetry run ruff check .        # lint
poetry run ruff check --fix .  # autofix (revise o diff antes de commitar — ver nota abaixo)
```

> ⚠️ **Cuidado com `ruff --fix` neste projeto especificamente.** Alguns arquivos em `src/infra/database/models/__init__.py` e `src/infra/database/init_db.py` importam classes só pelo **efeito colateral** de registrar tabelas/mappers no SQLAlchemy — não porque o nome é usado no arquivo. Um autofix de "unused import" já removeu esses imports uma vez durante o desenvolvimento deste projeto e quebrou a configuração dos mappers de um jeito só visível em runtime (não no lint nem no import). Os arquivos afetados têm `# ruff: noqa: I001` / `# noqa: F401` e comentários explicando por quê — não remova.

## Principais endpoints

| Método | Rota | Descrição | Auth |
|---|---|---|---|
| POST | `/user/register` | Cadastra um usuário (bootstrap: não exige login) | não |
| GET | `/user/register` | Formulário de cadastro | sim |
| POST | `/user/cadastro` | Login (seta cookie JWT) | não |
| GET | `/user/gerentes` | Lista gerentes (JSON) | não |
| GET | `/pagina/inicial` | Dashboard | sim |
| POST | `/campanhas/` | Cria campanha (com QR code) | sim |
| POST | `/vendas/` | Registra venda | sim |

Docs completos e interativos em `/docs` (Swagger) e `/redoc`.

## Decisões de projeto / coisas que parecem bug mas são intencionais

- **`POST /user/register` não exige login, mas `GET /user/register` exige.** É o caminho de bootstrap: sem isso, ninguém conseguiria criar o primeiro usuário. Depois do primeiro cadastro, presume-se que só um usuário já autenticado (ex.: um COO) cadastra os demais.

## Known issues / roadmap

Lista honesta do que ainda falta para este projeto ser 100% idiomático — decidido conscientemente para manter o escopo desta rodada de trabalho em "fundação testável" em vez de reescrever tudo de uma vez:

- **Sessão do SQLAlchemy não é verdadeiramente request-scoped.** O DI container resolve uma `Session` nova a cada resolução (`Factory`), não há como compartilhar uma única sessão por requisição de forma limpa com `dependency-injector` + endpoints síncronos do FastAPI (que despacha dependências síncronas para threads de um pool — uma `ContextVar` setada em uma dependência não fica visível nas outras, isso foi testado e descartado durante o desenvolvimento). Na prática isso significa que, por exemplo, criar um gerente + criar um time novo acontece em duas transações separadas, não uma só atômica. Cada repositório fecha sua própria sessão logo após cada escrita para evitar vazamento de conexões, mas o ideal seria uma sessão por requisição com um Unit of Work de verdade. **A migração para FastAPI async + SQLAlchemy `AsyncSession`** resolve isso de raiz, porque dependências async não passam por threadpool.
- **`login.html` não exibe a mensagem de erro** que a rota já envia no contexto (`error: "Credenciais inválidas"`). Bug de frontend, não afeta segurança (login realmente falha quando a senha está errada), só a UX.
- Sem cache (Redis), fila (RabbitMQ/Celery) ou observabilidade (OpenTelemetry/Prometheus) ainda.
- Cobertura de testes hoje foca no fluxo de usuários (o mais crítico nesta rodada). `campanhas`, `vendas` e `times` ainda não têm testes de integração dedicados.

## Estrutura de testes

```
tests/
├── conftest.py       # fixtures: client (TestClient), truncate entre testes
├── unit/              # sem banco: validador de CPF, auth (hash/JWT), UserUseCase com repos mockados
└── integration/        # contra Postgres real: registro, login, autenticação, listagem
```