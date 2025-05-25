"""
Autocred - Sistema de Gestão de Leads para Correspondentes Bancários
Módulo de segurança e autenticação

Este módulo implementa a autenticação JWT, hash de senhas e verificação
de permissões de usuários.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
import os
from typing import Optional

import models_user
from database import get_db

# Configuração de segurança
# Em produção, estas variáveis devem vir de variáveis de ambiente
SECRET_KEY = os.getenv(
    "SECRET_KEY", 
    "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
)
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Configuração do hash de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuração do OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto plano corresponde ao hash armazenado
    
    Args:
        plain_password: Senha em texto plano
        hashed_password: Hash da senha armazenada
        
    Returns:
        True se a senha corresponder ao hash, False caso contrário
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Gera um hash bcrypt para a senha
    
    Args:
        password: Senha em texto plano
        
    Returns:
        Hash da senha
    """
    return pwd_context.hash(password)


def authenticate_user(db: Session, email: str, password: str) -> Optional[models_user.User]:
    """
    Autentica um usuário verificando email e senha
    
    Args:
        db: Sessão do banco de dados
        email: Email do usuário
        password: Senha em texto plano
        
    Returns:
        Objeto User se a autenticação for bem-sucedida, False caso contrário
    """
    user = db.query(models_user.User).filter(models_user.User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um token JWT com os dados fornecidos
    
    Args:
        data: Dados a serem codificados no token
        expires_delta: Tempo de expiração do token
        
    Returns:
        Token JWT codificado
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> models_user.User:
    """
    Obtém o usuário atual a partir do token JWT
    
    Args:
        token: Token JWT
        db: Sessão do banco de dados
        
    Returns:
        Objeto User correspondente ao token
        
    Raises:
        HTTPException: Se o token for inválido ou o usuário não for encontrado
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models_user.User).filter(models_user.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: models_user.User = Depends(get_current_user)
) -> models_user.User:
    """
    Verifica se o usuário atual está ativo
    
    Args:
        current_user: Usuário atual obtido do token JWT
        
    Returns:
        Objeto User se o usuário estiver ativo
        
    Raises:
        HTTPException: Se o usuário estiver inativo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Usuário inativo"
        )
    return current_user


async def get_current_active_superuser(
    current_user: models_user.User = Depends(get_current_active_user)
) -> models_user.User:
    """
    Verifica se o usuário atual é um superusuário (admin) ativo
    
    Args:
        current_user: Usuário atual obtido do token JWT
        
    Returns:
        Objeto User se o usuário for um superusuário ativo
        
    Raises:
        HTTPException: Se o usuário não for um superusuário
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Permissões de administrador necessárias"
        )
    return current_user
