"""
Autocred - Sistema de Gestão de Leads para Correspondentes Bancários
Configuração do banco de dados

Este módulo configura a conexão com o banco de dados, define a sessão
e fornece funções para acesso ao banco de dados.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Configuração do banco de dados
# Prioriza variáveis de ambiente para facilitar o deploy em diferentes ambientes
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./autocred.db")

# Criar engine do SQLAlchemy com configurações específicas para SQLite
# Para outros bancos de dados, remover connect_args
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Criar sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos declarativos
Base = declarative_base()


def get_db():
    """
    Função para obter uma sessão do banco de dados
    
    Yields:
        Session: Sessão do banco de dados
        
    Note:
        Utiliza padrão de contexto para garantir que a sessão seja fechada
        mesmo em caso de exceção
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db_and_tables():
    """
    Função para criar o banco de dados e tabelas
    
    Esta função deve ser chamada durante a inicialização da aplicação
    para garantir que o banco de dados e as tabelas existam
    """
    Base.metadata.create_all(bind=engine)
    print("Banco de dados e tabelas criados com sucesso")
