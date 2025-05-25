#!/bin/sh
# Script de inicialização para Autocred em produção

set -e

echo "Iniciando Autocred - Sistema de Gestão de Leads para Correspondentes Bancários"
echo "Ambiente: $ENVIRONMENT"

# Verificar variáveis de ambiente essenciais
if [ -z "$SECRET_KEY" ]; then
  echo "AVISO: SECRET_KEY não definida. Usando valor padrão (não recomendado para produção)."
fi

# Carregar variáveis de ambiente do arquivo .env, se existir
if [ -f .env ]; then
  echo "Carregando variáveis de ambiente do arquivo .env"
  export $(grep -v '^#' .env | xargs)
fi

# Criar diretório de logs, se necessário
if [ ! -z "$LOG_FILE" ] && [ ! -d "$(dirname "$LOG_FILE")" ]; then
  echo "Criando diretório para logs: $(dirname "$LOG_FILE")"
  mkdir -p "$(dirname "$LOG_FILE")"
fi

# Verificar conexão com banco de dados
echo "Verificando conexão com o banco de dados..."
python -c "
import sys
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import os

# Obter URL do banco de dados
db_url = os.getenv('DATABASE_URL', 'sqlite:///./autocred.db')
print(f'Tentando conectar a: {db_url}')

# Tentar conectar ao banco de dados com retry
max_retries = 5
retry_interval = 5

for i in range(max_retries):
    try:
        engine = create_engine(db_url)
        conn = engine.connect()
        conn.close()
        print('Conexão com o banco de dados estabelecida com sucesso!')
        sys.exit(0)
    except OperationalError as e:
        print(f'Tentativa {i+1}/{max_retries}: Erro ao conectar ao banco de dados: {e}')
        if i < max_retries - 1:
            print(f'Tentando novamente em {retry_interval} segundos...')
            time.sleep(retry_interval)
        else:
            print('Falha ao conectar ao banco de dados após várias tentativas.')
            sys.exit(1)
"

# Executar migrações do banco de dados
echo "Executando migrações do banco de dados..."
python -c "
from database import engine, Base
import models
import models_user
import logger

logger.info('Criando tabelas no banco de dados')
Base.metadata.create_all(bind=engine)
logger.info('Tabelas criadas com sucesso')
"

# Verificar se é necessário criar usuário admin inicial
echo "Verificando usuário administrador..."
python -c "
from sqlalchemy.orm import Session
from database import SessionLocal
import models_user
from core_security import get_password_hash
import os
import logger

# Função para criar usuário admin se não existir
def create_admin_if_not_exists():
    db = SessionLocal()
    try:
        # Verificar se já existe algum usuário admin
        admin = db.query(models_user.User).filter(models_user.User.is_superuser == True).first()
        if not admin:
            # Obter credenciais do ambiente ou usar padrões
            admin_email = os.getenv('ADMIN_EMAIL', 'admin@autocred.com.br')
            admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
            
            # Criar usuário admin
            admin = models_user.User(
                email=admin_email,
                full_name='Administrador',
                hashed_password=get_password_hash(admin_password),
                is_active=True,
                is_superuser=True
            )
            db.add(admin)
            db.commit()
            logger.info(f'Usuário administrador criado: {admin_email}')
            print(f'Usuário administrador criado: {admin_email}')
            if admin_password == 'admin123':
                logger.warning('Usuário admin criado com senha padrão. Altere imediatamente!')
                print('AVISO: Usuário admin criado com senha padrão. Altere imediatamente!')
        else:
            logger.info(f'Usuário administrador já existe: {admin.email}')
            print(f'Usuário administrador já existe: {admin.email}')
    except Exception as e:
        logger.error(f'Erro ao verificar/criar usuário admin: {str(e)}')
        print(f'Erro ao verificar/criar usuário admin: {str(e)}')
    finally:
        db.close()

# Executar função
create_admin_if_not_exists()
"

# Iniciar servidor web
echo "Iniciando servidor web..."
if [ "$ENVIRONMENT" = "production" ]; then
  # Em produção, usar uvicorn com múltiplos workers
  exec uvicorn main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000} --workers 4
else
  # Em desenvolvimento, usar modo de reload
  exec uvicorn main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000} --reload
fi
