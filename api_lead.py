"""
Autocred - Sistema de Gestão de Leads para Correspondentes Bancários
API de gerenciamento de leads

Este módulo define as rotas da API para operações CRUD de leads,
incluindo criação, leitura, atualização e exclusão.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

# Importar funções CRUD
from crud_lead import (
    create_lead as crud_create_lead,
    get_leads as crud_get_leads,
    get_lead as crud_get_lead,
    update_lead as crud_update_lead,
    delete_lead as crud_delete_lead
)

# Importar schemas e dependências
from schemas_lead import Lead as LeadSchema, LeadCreate, LeadUpdate
from database import get_db
from core_security import get_current_active_user

# Criar router com prefixo
router = APIRouter(prefix="/leads")


@router.post("/", response_model=LeadSchema, status_code=status.HTTP_201_CREATED)
def create_lead(
    lead_in: LeadCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Cria um novo lead no sistema
    
    Args:
        lead_in: Dados do lead a ser criado
        db: Sessão do banco de dados
        current_user: Usuário autenticado que está criando o lead
        
    Returns:
        O lead criado
    """
    # Adicionar o ID do usuário atual como criador do lead
    return crud_create_lead(db=db, lead=lead_in, created_by_id=current_user.id)


@router.get("/", response_model=List[LeadSchema])
def read_leads(
    skip: int = Query(0, ge=0, description="Número de registros para pular (paginação)"),
    limit: int = Query(100, ge=1, le=200, description="Número máximo de registros a retornar"),
    assigned_to_id: Optional[int] = Query(None, description="Filtrar leads por ID do usuário responsável"),
    status: Optional[str] = Query(None, description="Filtrar leads por status"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Recupera uma lista de leads com opções de filtragem e paginação
    
    Args:
        skip: Número de registros para pular (paginação)
        limit: Número máximo de registros a retornar
        assigned_to_id: ID do usuário responsável para filtrar
        status: Status do lead para filtrar
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        Lista de leads que correspondem aos critérios de filtragem
    """
    # Se não for admin, mostrar apenas leads atribuídos ao usuário
    if not current_user.is_superuser and assigned_to_id is None:
        assigned_to_id = current_user.id
        
    return crud_get_leads(
        db, 
        skip=skip, 
        limit=limit, 
        assigned_to_id=assigned_to_id,
        status=status
    )


@router.get("/{lead_id}", response_model=LeadSchema)
def read_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Recupera um lead específico pelo ID
    
    Args:
        lead_id: ID do lead a ser recuperado
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        O lead solicitado
        
    Raises:
        HTTPException: Se o lead não for encontrado ou o usuário não tiver permissão
    """
    db_lead = crud_get_lead(db, lead_id=lead_id)
    if db_lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Lead não encontrado"
        )
    
    # Verificar permissão: apenas admin ou usuário responsável pode ver o lead
    if not current_user.is_superuser and db_lead.assigned_to_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar este lead"
        )
        
    return db_lead


@router.put("/{lead_id}", response_model=LeadSchema)
def update_lead(
    lead_id: int,
    lead_in: LeadUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Atualiza um lead existente
    
    Args:
        lead_id: ID do lead a ser atualizado
        lead_in: Dados atualizados do lead
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        O lead atualizado
        
    Raises:
        HTTPException: Se o lead não for encontrado ou o usuário não tiver permissão
    """
    db_lead = crud_get_lead(db, lead_id=lead_id)
    if db_lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Lead não encontrado"
        )
    
    # Verificar permissão: apenas admin ou usuário responsável pode atualizar o lead
    if not current_user.is_superuser and db_lead.assigned_to_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para atualizar este lead"
        )
        
    return crud_update_lead(db=db, db_lead=db_lead, lead_in=lead_in)


@router.delete("/{lead_id}", response_model=LeadSchema)
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Remove um lead do sistema
    
    Args:
        lead_id: ID do lead a ser removido
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        O lead removido
        
    Raises:
        HTTPException: Se o lead não for encontrado ou o usuário não tiver permissão
    """
    db_lead = crud_get_lead(db, lead_id=lead_id)
    if db_lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Lead não encontrado"
        )
    
    # Verificar permissão: apenas admin pode excluir leads
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem excluir leads"
        )
        
    return crud_delete_lead(db=db, db_lead=db_lead)
