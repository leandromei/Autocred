from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Path, Body
from sqlalchemy.orm import Session
from datetime import datetime, date
from pydantic import BaseModel, Field
from database import get_db
from models_plans import Plan, Client, LeadUsage, LeadPurchase
import sqlalchemy as sa

router = APIRouter(prefix="/leads", tags=["leads"])
admin_router = APIRouter(prefix="/admin", tags=["admin"])

# Modelos Pydantic para API
class LeadUsageResponse(BaseModel):
    """Modelo Pydantic para resposta de uso de leads"""
    date: date
    total_consumed: int
    daily_limit: int
    extra_leads_available: int
    
    class Config:
        orm_mode = True

class LeadPurchaseCreate(BaseModel):
    """Modelo Pydantic para criação de compra de leads"""
    quantity: int = Field(..., description="Quantidade de leads a comprar", example=10, gt=0)

class LeadPurchaseResponse(BaseModel):
    """Modelo Pydantic para resposta de compra de leads"""
    id: int
    quantity: int
    amount: float
    status: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class FinancialReportResponse(BaseModel):
    """Modelo Pydantic para resposta de relatório financeiro"""
    total_revenue: float
    total_leads_sold: int
    purchases_by_status: dict
    revenue_by_client: List[dict]

# Função auxiliar para obter cliente pelo ID
def get_client_by_id(db: Session, client_id: int):
    """Obtém um cliente pelo ID ou lança exceção se não encontrado"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return client

# Função auxiliar para obter ou criar registro de uso de leads
def get_or_create_lead_usage(db: Session, client_id: int, usage_date: date = None):
    """Obtém ou cria um registro de uso de leads para o cliente na data especificada"""
    if usage_date is None:
        usage_date = date.today()
    
    # Buscar registro existente
    lead_usage = db.query(LeadUsage).filter(
        LeadUsage.client_id == client_id,
        LeadUsage.date == usage_date
    ).first()
    
    # Criar novo registro se não existir
    if not lead_usage:
        lead_usage = LeadUsage(
            client_id=client_id,
            date=usage_date,
            total_consumed=0
        )
        db.add(lead_usage)
        db.commit()
        db.refresh(lead_usage)
    
    return lead_usage

# Rota para obter uso atual de leads
@router.get("/usage", response_model=LeadUsageResponse, summary="Obter uso de leads",
           description="Retorna informações sobre o uso atual de leads e limites do cliente")
def get_lead_usage(
    client_id: int = Query(..., description="ID do cliente"),
    db: Session = Depends(get_db)
):
    """
    Retorna informações sobre o uso atual de leads e limites do cliente.
    
    Args:
        client_id: ID do cliente
        db: Sessão do banco de dados
        
    Returns:
        LeadUsageResponse: Informações de uso de leads
    """
    # Obter cliente e verificar se existe
    client = get_client_by_id(db, client_id)
    
    # Obter plano do cliente
    plan = client.plan
    
    # Obter ou criar registro de uso para hoje
    today = date.today()
    lead_usage = get_or_create_lead_usage(db, client_id, today)
    
    # Calcular leads extras disponíveis
    # Soma todas as compras aprovadas
    extra_leads = db.query(sa.func.sum(LeadPurchase.quantity)).filter(
        LeadPurchase.client_id == client_id,
        LeadPurchase.status == "aprovado"
    ).scalar() or 0
    
    # Calcular total já consumido (histórico)
    total_consumed_all_time = db.query(sa.func.sum(LeadUsage.total_consumed)).filter(
        LeadUsage.client_id == client_id
    ).scalar() or 0
    
    # Calcular limite diário total (plano + extras disponíveis)
    daily_limit = plan.daily_limit
    
    # Calcular extras ainda disponíveis
    # Se o cliente já consumiu mais que o limite do plano multiplicado pelos dias desde a adesão,
    # então ele está usando leads extras
    extra_leads_available = max(0, extra_leads - max(0, total_consumed_all_time - (daily_limit * 30)))  # Simplificação: 30 dias
    
    return LeadUsageResponse(
        date=today,
        total_consumed=lead_usage.total_consumed,
        daily_limit=daily_limit,
        extra_leads_available=extra_leads_available
    )

# Rota para comprar leads adicionais
@router.post("/purchase", response_model=LeadPurchaseResponse, status_code=201,
            summary="Comprar leads adicionais",
            description="Permite a compra de leads adicionais além do limite do plano")
def purchase_leads(
    purchase_data: LeadPurchaseCreate,
    client_id: int = Query(..., description="ID do cliente"),
    db: Session = Depends(get_db)
):
    """
    Registra uma compra de leads adicionais.
    
    Args:
        purchase_data: Dados da compra
        client_id: ID do cliente
        db: Sessão do banco de dados
        
    Returns:
        LeadPurchaseResponse: Informações da compra registrada
    """
    # Obter cliente e verificar se existe
    client = get_client_by_id(db, client_id)
    
    # Calcular valor da compra
    quantity = purchase_data.quantity
    price_per_lead = client.plan.extra_lead_price
    amount = quantity * price_per_lead
    
    # Criar registro de compra
    purchase = LeadPurchase(
        client_id=client_id,
        quantity=quantity,
        amount=amount,
        status="pendente"  # Status inicial
    )
    
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    
    return purchase

# Rota para relatório financeiro (admin)
@admin_router.get("/reports", response_model=FinancialReportResponse,
                 summary="Relatório financeiro",
                 description="Retorna relatório financeiro de vendas de leads")
def get_financial_report(
    start_date: Optional[date] = Query(None, description="Data inicial"),
    end_date: Optional[date] = Query(None, description="Data final"),
    db: Session = Depends(get_db)
):
    """
    Gera um relatório financeiro de vendas de leads.
    
    Args:
        start_date: Data inicial para filtro
        end_date: Data final para filtro
        db: Sessão do banco de dados
        
    Returns:
        FinancialReportResponse: Relatório financeiro
    """
    # Definir datas padrão se não fornecidas
    if not end_date:
        end_date = date.today()
    if not start_date:
        # Padrão: último mês
        start_date = date(end_date.year, end_date.month - 1 if end_date.month > 1 else 12, 1)
    
    # Consulta base para compras no período
    query = db.query(LeadPurchase).filter(
        sa.func.date(LeadPurchase.created_at) >= start_date,
        sa.func.date(LeadPurchase.created_at) <= end_date
    )
    
    # Total de receita (apenas compras aprovadas)
    total_revenue = db.query(sa.func.sum(LeadPurchase.amount)).filter(
        sa.func.date(LeadPurchase.created_at) >= start_date,
        sa.func.date(LeadPurchase.created_at) <= end_date,
        LeadPurchase.status == "aprovado"
    ).scalar() or 0
    
    # Total de leads vendidos
    total_leads_sold = db.query(sa.func.sum(LeadPurchase.quantity)).filter(
        sa.func.date(LeadPurchase.created_at) >= start_date,
        sa.func.date(LeadPurchase.created_at) <= end_date,
        LeadPurchase.status == "aprovado"
    ).scalar() or 0
    
    # Compras por status
    purchases_by_status = {}
    status_counts = db.query(
        LeadPurchase.status,
        sa.func.count(LeadPurchase.id).label('count'),
        sa.func.sum(LeadPurchase.amount).label('total')
    ).filter(
        sa.func.date(LeadPurchase.created_at) >= start_date,
        sa.func.date(LeadPurchase.created_at) <= end_date
    ).group_by(LeadPurchase.status).all()
    
    for status, count, total in status_counts:
        purchases_by_status[status] = {
            "count": count,
            "total": float(total) if total else 0
        }
    
    # Receita por cliente
    revenue_by_client = []
    client_revenues = db.query(
        Client.id,
        Client.name,
        sa.func.sum(LeadPurchase.amount).label('revenue'),
        sa.func.sum(LeadPurchase.quantity).label('leads_purchased')
    ).join(LeadPurchase).filter(
        sa.func.date(LeadPurchase.created_at) >= start_date,
        sa.func.date(LeadPurchase.created_at) <= end_date,
        LeadPurchase.status == "aprovado"
    ).group_by(Client.id, Client.name).order_by(sa.desc('revenue')).all()
    
    for client_id, client_name, revenue, leads_purchased in client_revenues:
        revenue_by_client.append({
            "client_id": client_id,
            "client_name": client_name,
            "revenue": float(revenue) if revenue else 0,
            "leads_purchased": int(leads_purchased) if leads_purchased else 0
        })
    
    return FinancialReportResponse(
        total_revenue=float(total_revenue),
        total_leads_sold=int(total_leads_sold) if total_leads_sold else 0,
        purchases_by_status=purchases_by_status,
        revenue_by_client=revenue_by_client
    )
