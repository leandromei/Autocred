"""
Autocred - Sistema de Gestão de Leads para Correspondentes Bancários
API de autenticação

Este módulo implementa as rotas de autenticação, incluindo login, logout
e obtenção de informações do usuário atual.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel
from typing import Optional

from database import get_db
import crud_user
from schemas_user import User as UserSchema
from models_user import User
import core_security
import logger
from error_handlers import AuthenticationError, handle_errors

# Criar router
router = APIRouter()

# Schema para resposta de token
class Token(BaseModel):
    """Schema para resposta de token JWT"""
    access_token: str
    token_type: str


@router.post("/token", response_model=Token)
@handle_errors(default_message="Erro durante autenticação")
async def login_for_access_token(
    response: Response,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Autentica o usuário e retorna um token JWT
    
    Args:
        response: Objeto Response do FastAPI
        db: Sessão do banco de dados
        form_data: Dados do formulário de login
        
    Returns:
        Token JWT e tipo de token
        
    Raises:
        AuthenticationError: Se as credenciais forem inválidas ou o usuário estiver inativo
    """
    logger.info("Tentativa de autenticação via API", {"email": form_data.username})
    
    user = crud_user.get_user_by_email(db, email=form_data.username)
    if not user or not core_security.verify_password(form_data.password, user.hashed_password):
        logger.warning("Falha na autenticação via API", {"email": form_data.username})
        raise AuthenticationError(
            message="Email ou senha incorretos",
            details={"email": form_data.username}
        )
        
    if not user.is_active:
        logger.warning("Tentativa de login com usuário inativo", {"email": form_data.username, "user_id": user.id})
        raise AuthenticationError(
            message="Usuário inativo",
            details={"email": form_data.username, "user_id": user.id}
        )

    # Criar token JWT
    access_token_expires = timedelta(minutes=core_security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = core_security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    # Registrar login bem-sucedido
    logger.info("Login bem-sucedido via API", {"user_id": user.id, "email": user.email})
    
    # Definir token em cookie HTTPOnly (opcional, complementa o retorno JSON)
    # Em produção, secure deve ser True para HTTPS
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=int(access_token_expires.total_seconds()),
        expires=int(access_token_expires.total_seconds()),
        samesite="lax",
        secure=False  # Mudar para True em produção com HTTPS
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=UserSchema)
@handle_errors(default_message="Erro ao obter informações do usuário")
async def read_users_me(
    current_user: User = Depends(core_security.get_current_active_user)
):
    """
    Obtém informações do usuário autenticado atual
    
    Args:
        current_user: Usuário autenticado atual
        
    Returns:
        Informações do usuário
    """
    logger.info("Acesso às informações do usuário", {"user_id": current_user.id})
    return current_user


@router.get("/logout")
@handle_errors(default_message="Erro durante logout")
async def logout(response: Response):
    """
    Realiza logout do usuário removendo o cookie de token
    
    Args:
        response: Objeto Response do FastAPI
        
    Returns:
        Redirecionamento para a página de login
    """
    logger.info("Logout via API")
    
    # Criar resposta de redirecionamento
    redirect_response = RedirectResponse(
        url="/login", 
        status_code=status.HTTP_303_SEE_OTHER
    )
    
    # Remover cookie de token
    redirect_response.delete_cookie(
        key="access_token", 
        httponly=True, 
        samesite="lax", 
        secure=False  # Mudar para True em produção com HTTPS
    )
    
    return redirect_response


@router.post("/refresh-token", response_model=Token)
@handle_errors(default_message="Erro ao renovar token")
async def refresh_access_token(
    current_user: User = Depends(core_security.get_current_active_user),
    response: Response = None
):
    """
    Renova o token JWT do usuário autenticado
    
    Args:
        current_user: Usuário autenticado atual
        response: Objeto Response do FastAPI
        
    Returns:
        Novo token JWT e tipo de token
    """
    logger.info("Renovação de token", {"user_id": current_user.id, "email": current_user.email})
    
    # Criar novo token JWT
    access_token_expires = timedelta(minutes=core_security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = core_security.create_access_token(
        data={"sub": current_user.email}, expires_delta=access_token_expires
    )
    
    # Atualizar cookie se response for fornecido
    if response:
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=int(access_token_expires.total_seconds()),
            expires=int(access_token_expires.total_seconds()),
            samesite="lax",
            secure=False  # Mudar para True em produção com HTTPS
        )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/change-password")
@handle_errors(default_message="Erro ao alterar senha")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(core_security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Altera a senha do usuário autenticado
    
    Args:
        current_password: Senha atual
        new_password: Nova senha
        current_user: Usuário autenticado atual
        db: Sessão do banco de dados
        
    Returns:
        Mensagem de sucesso
        
    Raises:
        AuthenticationError: Se a senha atual for inválida
    """
    logger.info("Tentativa de alteração de senha", {"user_id": current_user.id})
    
    # Verificar senha atual
    if not core_security.verify_password(current_password, current_user.hashed_password):
        logger.warning("Falha na alteração de senha: senha atual incorreta", {"user_id": current_user.id})
        raise AuthenticationError(
            message="Senha atual incorreta",
            details={"user_id": current_user.id}
        )
    
    # Gerar hash da nova senha
    hashed_password = core_security.get_password_hash(new_password)
    
    # Atualizar senha no banco de dados
    current_user.hashed_password = hashed_password
    db.commit()
    
    logger.info("Senha alterada com sucesso", {"user_id": current_user.id})
    
    return {"message": "Senha alterada com sucesso"}
