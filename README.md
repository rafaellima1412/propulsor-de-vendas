# Propulsor de Vendas — Backend

API de gestão de campanhas de vendas, times, usuários, vendas e carteira, construída com **FastAPI** e **Clean Architecture**. Serve exclusivamente como API — o frontend (React) roda como aplicação separada, consumindo essa API via HTTP.

## Stack

- **FastAPI** — API REST (100% JSON, sem páginas server-rendered)
- **PostgreSQL** com **PostGIS** (dados geoespaciais dos locais de campanha) via **SQLAlchemy 2.0**
- **Alembic** para migrations
- **dependency-injector** para injeção de dependência (Clean Architecture: `domain` / `application` / `infra`)
- **JWT** (python-jose) + **bcrypt** (passlib) para autenticação via cookie httpOnly
- **Pillow** + **qrcode** para geração de QR code e recortes de imagem sob demanda
- **pytest** com **ruff** para lint
- **Docker** / **docker-compose** para ambiente reproduzível

## Arquitetura

```
src/
├── domain/        # entidades, enums, validadores e schemas Pydantic — sem dependência de framework
├── application/    # casos de uso, DTOs e interfaces de repositório (portas)
└── infra/          # adapters: SQLAlchemy, rotas FastAPI, DI container, settings
```

O domínio não depende de infraestrutura; os casos de uso dependem apenas de **interfaces** de repositório (`IUserRepository`, `ICampanhaRepository`, `IVendaRepository`, `ITimeRepository`...), implementadas na camada `infra`. A ligação entre eles é feita pelo `Container` (`src/infra/dy/container.py`), usando [dependency-injector](https://python-dependency-injector.ets-labs.org/).

**Autorização por papel:** a maior parte das rotas usa checagem inline (`if user["role"] not in (...): raise HTTPException(403, ...)`) dentro do próprio endpoint. `time_route.py` usa um padrão de dependência reutilizável (`require_coordenador`, `require_gerente_ou_coordenador`) — vale seguir esse padrão em vez do inline ao criar rotas novas.

## Como rodar (Docker — recomendado)

```bash
cp .env.example .env   # ajuste SECRET_KEY e demais variáveis
docker compose up --build
```

A API sobe em `http://localhost:8000` (docs interativos em `/docs` e `/redoc`). O `docker-compose.yml` sobe um Postgres com PostGIS já com a extensão habilitada.

Migrations rodam automaticamente no start do container (`alembic upgrade head` antes do `uvicorn`), mas o `init_db()` chamado no `lifespan` da aplicação também cria qualquer tabela que porventura esteja faltando via `Base.metadata.create_all` — útil em dev, mas **não substitui migration** ao alterar uma tabela existente (adicionar/remover coluna): isso sempre precisa de uma revision do Alembic.

## Como rodar localmente (sem Docker)

Requer Python 3.12+, Poetry e um Postgres com PostGIS acessível.

```bash
poetry install
cp .env.example .env   # aponte para seu Postgres local

poetry run alembic upgrade head
poetry run uvicorn main:app --reload
```

### Variáveis de ambiente (`.env`)

| Variável | Descrição |
|---|---|
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Credenciais do Postgres |
| `DB_HOST` / `DB_PORT` | Host/porta do Postgres |
| `SECRET_KEY` | Chave usada pra assinar os JWTs |
| `ALGORITHM` | Algoritmo do JWT (ex: `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Validade do token de acesso |
| `CORS_ORIGINS_RAW` | URL(s) do frontend permitidas no CORS, separadas por vírgula, sem barra no final (ex: `http://localhost:5173`) |

## Testes

```bash
poetry run pytest                                     # suíte completa
poetry run pytest --cov=src --cov-report=term-missing  # com cobertura

poetry run ruff check .        # lint
poetry run ruff check --fix .  # autofix (revise o diff antes de commitar — ver nota abaixo)
```

> ⚠️ **Cuidado com `ruff --fix` neste projeto especificamente.** Alguns arquivos em `src/infra/database/models/__init__.py` e `src/infra/database/init_db.py` importam classes só pelo **efeito colateral** de registrar tabelas/mappers no SQLAlchemy — não porque o nome é usado no arquivo (`user_campanha`, `campanha_time`, etc). Um autofix de "unused import" já removeu esses imports uma vez durante o desenvolvimento e quebrou a configuração dos mappers de um jeito só visível em runtime (não no lint nem no import). O mesmo cuidado vale pro `alembic/env.py`, que importa todos os models antes de capturar `target_metadata` — sem isso, `alembic revision --autogenerate` não enxerga nenhuma tabela existente e gera uma migration tentando **dropar tudo**.

## Modelo de papéis (roles)

Quatro papéis, cada um com escopo de visibilidade diferente:

- **admin** — só cadastra usuários (`POST /user/register`). Não opera o dia a dia do sistema.
- **coordenador** — visão geral da empresa: todos os times, todas as campanhas, todas as vendas, todos os colaboradores.
- **gerente** — escopo restrito ao(s) próprio(s) time(s): só vê/associa colaboradores sem time ou do próprio time, só vê campanhas e vendas do próprio time.
- **colaborador** — vê as próprias campanhas e as do time; registra a própria carteira de resultados.

O primeiro usuário cadastrado no sistema (`POST /user/register` com o banco de usuários vazio) vira `admin` automaticamente — é o caminho de bootstrap, não exige login. Depois disso, cadastrar alguém exige estar autenticado como `admin`.

## Fluxo de campanha e QR code

Ponto importante pra quem for mexer nisso: **o QR code não é gerado (nem colado) na criação ou edição da campanha.** A imagem que fica salva na campanha é exatamente a que o gerente enviou, sem alteração.

O QR code (CPF + matrícula do colaborador) só é gerado **na hora do compartilhamento**, quando alguém chama `GET /campanhas/{id}/social/{formato}` — nesse momento a imagem é recortada pro formato pedido (feed/stories/post) e o QR é colado por cima, na hora, sem cache em disco. Cada colaborador associado à campanha gera o próprio QR, com a própria matrícula (guardada no cadastro do usuário, não na campanha — ver `matricula` em `UserModel`). Uma campanha pode ter mais de um colaborador associado (`POST /campanhas/{id}/colaboradores`); o campo `usuario_id` no retorno é só o "principal" (o primeiro associado), mas `usuario_ids` traz a lista completa.

## Endpoints

Docs completos e interativos em `/docs` (Swagger) e `/redoc`. Tabela resumida por domínio:

### Autenticação e usuários (`/user`)

| Método | Rota | Descrição | Quem acessa |
|---|---|---|---|
| POST | `/user/register` | Cadastra usuário. Primeiro usuário do sistema vira admin automaticamente (bootstrap, sem login) | admin (ou ninguém, se for o primeiro) |
| POST | `/user/login` | Login, seta cookie JWT httpOnly | público |
| POST | `/user/logout` | Remove o cookie | qualquer autenticado |
| GET | `/user/me` | Dados do usuário logado | qualquer autenticado |
| GET | `/user/` | Lista todos os usuários | qualquer autenticado |
| POST | `/user/` | Cria usuário (via DTO direto) | admin |
| POST | `/user/forgot-password` | Gera senha nova a partir do CPF | público |
| GET | `/user/gerentes` | Lista usuários com papel gerente | coordenador/admin |
| GET | `/user/colaboradores?q=` | Busca colaboradores por nome/CPF. Gerente só vê os do próprio time ou sem time; coordenador/admin veem todos | gerente/coordenador/admin |
| PUT | `/user/{user_id}/time` | Associa um usuário a um time | gerente |

### Times (`/times`)

| Método | Rota | Descrição | Quem acessa |
|---|---|---|---|
| GET | `/times/list` | Lista todos os times | gerente/coordenador/admin |
| GET | `/times/{time_id}` | Detalhe de um time | gerente/coordenador/admin |
| POST | `/times/create` | Cria time | coordenador |
| PUT | `/times/{time_id}` | Atualiza time | coordenador |
| DELETE | `/times/{time_id}` | Remove time | coordenador |
| GET | `/times/by-coo/{coo_id}` | Times de um coordenador | gerente/coordenador/admin |
| GET | `/times/by-gerente/{gerente_id}` | Times de um gerente | gerente/coordenador/admin |

### Campanhas (`/campanhas`)

| Método | Rota | Descrição | Quem acessa |
|---|---|---|---|
| POST | `/campanhas/` | Cria campanha (imagem enviada como está, sem QR) | gerente/coordenador |
| POST | `/campanhas/upload-imagem` | Upload da imagem base (multipart), devolve a URL pra usar em `folder_image` | gerente/coordenador |
| GET | `/campanhas/by-usuario` | Dashboard: campanhas + métricas de venda, escopo conforme o papel de quem chama | qualquer autenticado |
| GET | `/campanhas/de-usuario/{usuario_id}` | Campanhas de um colaborador específico | gerente/coordenador |
| GET | `/campanhas/do-time` | Campanhas do próprio time (gerente vê o time que gerencia; colaborador vê o time em que está) | gerente/colaborador |
| GET | `/campanhas/de-gerente/{gerente_id}` | Campanhas do time de um gerente específico | coordenador |
| GET | `/campanhas/{campaign_id}` | Detalhe de uma campanha | gerente/coordenador/colaborador (dono) |
| PUT | `/campanhas/{campaign_id}` | Edita campanha | gerente/coordenador |
| POST | `/campanhas/{campanha_id}/colaboradores` | Associa mais um colaborador a uma campanha já existente | gerente (só do próprio time)/coordenador |
| GET | `/campanhas/{campaign_id}/social/{formato}` | Gera a imagem recortada (`feed`/`stories`/`post`) com QR code colado na hora | colaborador associado/gerente/coordenador |

### Vendas (`/vendas`)

| Método | Rota | Descrição | Quem acessa |
|---|---|---|---|
| POST | `/vendas/` | Registra venda (payload no formato esperado pela futura integração com ERP) | gerente/coordenador |
| GET | `/vendas/` | Lista vendas — gerente só vê as do próprio time; coordenador vê todas | gerente/coordenador |

### Carteira (`/carteira`)

| Método | Rota | Descrição | Quem acessa |
|---|---|---|---|
| GET | `/carteira/me` | Resultado + esforço do próprio usuário logado | qualquer autenticado |
| GET | `/carteira/time` | Soma da carteira de todos os colaboradores do próprio time | gerente |
| GET | `/carteira/geral` | Soma da carteira de todos os colaboradores da empresa | coordenador |
| GET | `/carteira/{usuario_id}` | Carteira de um colaborador específico | gerente/coordenador |

> Os valores de comissão usados pra calcular o "saldo estimado" da carteira são fictícios (`src/domain/constants/comissoes.py`) — ajuste pros valores reais assim que a empresa definir a regra de comissão. Nada mais no sistema depende de onde esse número vem.

### Locais (`/locais`)

CRUD padrão de locais geoespaciais (PostGIS) — usado internamente, não faz parte do fluxo principal de campanha/venda.

## Decisões de projeto / coisas que parecem bug mas são intencionais

- **`POST /user/register` não exige login quando o banco de usuários está vazio.** É o caminho de bootstrap: sem isso, ninguém conseguiria criar o primeiro usuário (que vira admin automaticamente).
- **A imagem da campanha nunca tem QR code colado.** Isso é proposital (ver seção "Fluxo de campanha e QR code" acima) — não é um bug de geração faltando.
- **`usuario_id` no retorno de uma campanha é só o primeiro colaborador associado.** Se precisar saber todos, use `usuario_ids`.

## Known issues / roadmap

- **Sessão do SQLAlchemy não é verdadeiramente request-scoped.** O DI container resolve uma `Session` nova a cada resolução de repositório (`providers.Factory`). Isso já causou esgotamento real do pool de conexões em produção (`QueuePool limit ... connection timed out`) — a causa era vazamento: métodos de leitura que nunca chamavam `.close()`. Isso foi corrigido em todos os repositórios (`venda_repository.py`, `campaign_repository.py`, `user_repository.py`, `TimeRepository.py`, `local_repository.py`), com cuidado extra nos poucos métodos que precisam manter a sessão viva entre duas chamadas (ex: `get_by_id` seguido de `update` no mesmo objeto — fechar cedo demais aí quebra com `DetachedInstanceError`, isso já foi testado). Ainda assim, o modelo de "uma sessão nova por resolução de repositório" continua não sendo uma Unit of Work de verdade — criar um gerente + criar um time novo, por exemplo, acontece em duas transações separadas, não uma só atômica. A correção de raiz seria migrar pra FastAPI async + SQLAlchemy `AsyncSession` com sessão por requisição.
- Sem cache (Redis), fila (RabbitMQ/Celery) ou observabilidade (OpenTelemetry/Prometheus) ainda.
- Cobertura de testes automatizados hoje é parcial — boa parte da validação de fluxos novos (carteira, vendas, associação de colaborador a campanha, geração de QR sob demanda) foi feita manualmente/via scripts ad-hoc durante o desenvolvimento, não em `tests/`. Vale transformar em testes de integração de verdade.

## Estrutura de testes

```
tests/
├── conftest.py                  # fixtures: client (TestClient), truncate entre testes
├── test_auth.py                  # autenticação (hash/JWT)
├── test_cpf_validator.py         # validador de CPF
├── test_dashboard_usecase.py     # DashboardUseCase
├── test_user_case.py             # UserUseCase com repositórios mockados
└── test_user_flow.py             # fluxo de registro/login ponta a ponta
```