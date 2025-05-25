from sqlalchemy.ext.declarative import declarative_base

# Compartilhar a mesma Base do database.py
from database import Base

# Importar e reexportar todos os modelos
from models_user import User
from models_plans import *  # Importa todos os modelos de planos

# Adicione aqui outros modelos que possam existir no sistema
# from models_lead import Lead  # Se existir

# Este arquivo serve como ponto central para importação de todos os modelos
# Facilita a criação de tabelas e migrações
