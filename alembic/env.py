from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from src.infra.database.base import Base

# Precisa importar os models explicitamente ANTES de capturar
# target_metadata — sem isso, Base.metadata fica vazio (nenhuma classe
# registrada ainda) e o autogenerate não enxerga nenhuma tabela existente,
# o que faz o Alembic gerar uma migração tentando DROPAR tudo. Mesma lista
# de imports que init_db.py usa.
from src.infra.database.models.campaign_model import CampanhaModel  # noqa: F401
from src.infra.database.models.campanha_time import campanha_time  # noqa: F401
from src.infra.database.models.local_model import Local  # noqa: F401
from src.infra.database.models.time_model import TimeModel  # noqa: F401
from src.infra.database.models.user_campaign import user_campanha  # noqa: F401
from src.infra.database.models.venda_model import VendaModel  # noqa: F401
from src.infra.settings.settings import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override the hardcoded sqlalchemy.url from alembic.ini with the value
# built from environment variables (.env), so no credentials live in
# version-controlled config files.
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name in ("spatial_ref_sys", "geometry_columns", "geography_columns"):
        return False
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()