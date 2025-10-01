from __future__ import annotations

import os
import pkgutil
import importlib
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.shared.db import BaseModel

# --- Auto-import all feature models: app/modules/<feature>/model.py ---
FEATURES_ROOT_PKG = "app.modules"  # the package that contains feature subpackages
FEATURE_MODEL_MODULE = "model"  # we import modules.<feature>.model


def _import_feature_models(root_pkg: str, model_module_name: str = "model") -> None:
    """
    Import modules.<feature>.model for every subpackage in 'modules'.
    Example: modules.user.model, modules.product.model, modules.order.model
    """
    try:
        pkg = importlib.import_module(root_pkg)
    except ModuleNotFoundError as e:
        raise RuntimeError(
            f"Cannot import root models package '{root_pkg}'. "
            f"Ensure it exists and has an __init__.py."
        ) from e

    if not hasattr(pkg, "__path__"):
        # If 'modules' is a simple module (not a package), just importing it is enough.
        return

    for _finder, subpkg_name, ispkg in pkgutil.iter_modules(pkg.__path__):
        if not ispkg:
            continue
        mod_path = f"{root_pkg}.{subpkg_name}.{model_module_name}"
        try:
            importlib.import_module(mod_path)
        except ModuleNotFoundError:
            # Feature might not have a model.py yet; that's fine.
            pass


# Import all feature model modules so their tables register on BaseModel.metadata
_import_feature_models(FEATURES_ROOT_PKG, FEATURE_MODEL_MODULE)

# ---- Alembic config / metadata ----
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Allow DATABASE_URL from environment to override alembic.ini
env_url = os.getenv("DATABASE_URL")
if env_url:
    config.set_main_option("sqlalchemy.url", env_url)

target_metadata = BaseModel.metadata


# ---- Migration runners ----
def _configure_context_with_connection(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # detect column type changes
        compare_server_default=True,  # detect server_default changes
        render_as_batch=False,  # set True only for SQLite batch mode
    )


def do_run_migrations(connection):
    _configure_context_with_connection(connection)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


def run_migrations() -> None:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        import asyncio

        asyncio.run(run_migrations_online())


run_migrations()
