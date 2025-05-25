import os
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models_user import User
from core_security import get_password_hash

def init_db():
    """Inicializa o banco de dados e cria o usuário admin se não existir."""
    # Cria as tabelas se não existirem
    Base.metadata.create_all(bind=engine)
    
    # Cria uma sessão
    db = SessionLocal()
    
    try:
        # Verifica se o usuário admin já existe
        admin_user = db.query(User).filter(User.email == "admin@autocred.com").first()
        
        if not admin_user:
            # Cria o usuário admin
            hashed_password = get_password_hash("admin123")
            admin_user = User(
                email="admin@autocred.com",
                hashed_password=hashed_password,
                full_name="Administrador",
                is_active=True,
                is_superuser=True
            )
            db.add(admin_user)
            db.commit()
            print("Usuário admin criado com sucesso!")
        else:
            print("Usuário admin já existe.")
    
    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
        db.rollback()
    finally:
        db.close()

# Executa a inicialização se este script for executado diretamente
if __name__ == "__main__":
    init_db()
