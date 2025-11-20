from typing import Optional, Literal, MutableMapping

from alembic import context

from core.db.models import Base
from core.db.postgres import get_engine, init_db

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
# config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
# if config.config_file_name is not None:
#     fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
init_db()


def include_name(
        name: Optional[str],
        type_: Literal[
            "schema",
            "table",
            "column",
            "index",
            "unique_constraint",
            "foreign_key_constraint",
        ],
        parent_names: MutableMapping[
            Literal["schema_name", "table_name", "schema_qualified_table_name"],
            Optional[str],
        ]
):
    langgraph_tables = [
        "checkpoint_blobs",
        "checkpoint_migrations",
        "checkpoint_writes",
        "checkpoints",
        "store",
        "store_migrations"
    ]
    if type_ == "table" and name in langgraph_tables:
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
    context.configure(
        url=get_engine().url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_name=include_name
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
