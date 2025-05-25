import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Adicionar diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Base, get_engine

# Configuração de logging
fileConfig(context.config.config_file_name)

# Metadados alvo para autogeração
target_metadata = Base.metadata

# Função para rodar as migrations
def run_migrations_offline():
    url = 'postgresql://postgres:postgres@autocred-db:5432/autocred'
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, compare_type=True
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = get_engine('postgresql://postgres:postgres@autocred-db:5432/autocred')
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
