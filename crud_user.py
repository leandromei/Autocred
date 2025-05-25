from sqlalchemy.orm import Session
from models_user import User
from passlib.context import CryptContext

# Configuração do hashing de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int):
    """Obtém um usuário pelo ID."""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """Obtém um usuário pelo email."""
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Obtém uma lista de usuários."""
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user):
    """Cria um novo usuário."""
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_active=True,
        is_superuser=user.is_superuser if hasattr(user, 'is_superuser') else False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user, user_in):
    """Atualiza um usuário existente."""
    update_data = user_in.dict(exclude_unset=True)
    
    # Se a senha estiver sendo atualizada, hash ela
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = pwd_context.hash(update_data["password"])
        del update_data["password"]
    
    # Atualiza os atributos do usuário
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, db_user):
    """Exclui um usuário."""
    db.delete(db_user)
    db.commit()
    return db_user

def verify_password(plain_password, hashed_password):
    """Verifica se a senha está correta."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Gera um hash para a senha."""
    return pwd_context.hash(password)
