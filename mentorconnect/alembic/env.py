"""
alembic/env.py
-----------------
Alembic environment configuration. Pulls the database URL from our
app.core.config.settings (instead of a hardcoded value in alembic.ini) so
migrations always target whatever DB the running environment is configured
for, and imports app.models so autogenerate can detect model changes against
Base.metadata.
"""

import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Make the project root importable (so `import app.xxx` works when alembic
# is invoked from the project root, e.g. `alembic upgrade head`)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings  # noqa: E402
from app.db.base_class import Base  # noqa: E402
import app.models  # noqa: E402,F401  (imports all models so Base.metadata is fully populated)

# Alembic Config object, providing access to values within alembic.ini
config = context.config

# Override the sqlalchemy.url from alembic.ini with our app's actual configured DB URL
config.set_main_option("sqlalchemy.url", settings.SQLALCHEMY_DATABASE_URI)

# Interpret the config file for Python logging (writes log output for migrations)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# This is the metadata object autogenerate compares the DB against
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode: emits SQL to a script without a live
    DB connection. Useful for generating migration SQL to review/hand off
    to a DBA without actually executing it.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode: connects to the DB and applies changes directly."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,        # detect column type changes in autogenerate
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
