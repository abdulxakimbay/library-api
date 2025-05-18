from logging.config import fileConfig

from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool

from alembic import context

from src.config import settings
from src.models import *

# Это объект конфигурации Alembic, который предоставляет доступ к значениям в .ini файле.
config = context.config

# Интерпретируем файл конфигурации для Python logging.
# Эта строка настраивает логгеры.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Получаем URL базы данных из настроек (замени на свой способ получения)
config.set_main_option('sqlalchemy.url', settings.get_db_url + "?async_fallback=True")

# Мета-данные для моделей, необходимые для автоматических миграций
target_metadata = Base.metadata  # Убедись, что Base — это правильный объект для твоих моделей

def run_migrations_offline() -> None:
    """Запуск миграций в 'офлайн' режиме.

    Этот режим используется, если нужно работать с URL, не создавая соединение.
    В этом случае нет необходимости в DBAPI.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """Запуск миграций в 'онлайн' режиме.

    В этом режиме создаём движок и ассоциируем его с контекстом миграции.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.begin() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def do_run_migrations(connection):
    """Функция для запуска миграций с подключением."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_server_default=True,
    )
    context.run_migrations()

# Запуск в зависимости от того, в каком режиме работаем (онлайн или офлайн)
if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())
