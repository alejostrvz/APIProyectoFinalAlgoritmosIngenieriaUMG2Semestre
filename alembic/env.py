import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.models import Base

# Este es el objeto de configuración de Alembic, que proporciona acceso a los valores dentro del archivo .ini.
config = context.config

# Interpretar el archivo de configuración para el registro de Python.
# Esta línea configura básicamente los registradores.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Definir los metadatos de tu modelo aquí para el soporte de 'autogenerate'.
target_metadata = Base.metadata

# Construir la URL de la base de datos a partir de las variables de entorno
DATABASE_URL = f"postgresql+psycopg2://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
config.set_main_option("sqlalchemy.url", DATABASE_URL)

def run_migrations_offline() -> None:
    """Ejecutar migraciones en modo 'offline'."""

    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Ejecutar migraciones en modo 'online'."""

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
