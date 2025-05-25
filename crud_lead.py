from sqlalchemy.orm import Session
from models_plans import LeadPurchase, Client
from typing import Optional, List
from datetime import date
from schemas_lead import LeadCreate, LeadUpdate

# Funções originais para compra de leads
def get_lead_purchase(db: Session, purchase_id: int):
    """Obtém uma compra de leads pelo ID."""
    return db.query(LeadPurchase).filter(LeadPurchase.id == purchase_id).first()

def get_lead_purchases(db: Session, client_id: Optional[int] = None, 
                      status: Optional[str] = None, skip: int = 0, limit: int = 100):
    """Obtém uma lista de compras de leads com filtros opcionais."""
    query = db.query(LeadPurchase)
    
    if client_id:
        query = query.filter(LeadPurchase.client_id == client_id)
    
    if status:
        query = query.filter(LeadPurchase.status == status)
    
    return query.offset(skip).limit(limit).all()

def create_lead_purchase(db: Session, client_id: int, quantity: int, amount: float):
    """Cria uma nova compra de leads."""
    db_purchase = LeadPurchase(
        client_id=client_id,
        quantity=quantity,
        amount=amount,
        status="pendente"
    )
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    return db_purchase

def update_lead_purchase_status(db: Session, purchase_id: int, status: str):
    """Atualiza o status de uma compra de leads."""
    db_purchase = get_lead_purchase(db, purchase_id)
    if not db_purchase:
        return None
    
    db_purchase.status = status
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    return db_purchase

def get_financial_report(db: Session, start_date: date, end_date: date):
    """Gera um relatório financeiro de vendas de leads."""
    # Esta função seria implementada com queries mais complexas
    # para agregar dados financeiros, mas aqui simplificamos
    return {
        "total_revenue": 0,
        "total_leads_sold": 0,
        "purchases_by_status": {},
        "revenue_by_client": []
    }

# Funções adicionadas para compatibilidade com api_lead.py
def create_lead(db: Session, lead: LeadCreate):
    """Cria um novo lead."""
    # Implementação simplificada para resolver a dependência
    # Em produção, substitua por uma implementação real
    db_lead = Client(
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        status="novo"
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

def get_leads(db: Session, skip: int = 0, limit: int = 100, assigned_to_id: Optional[int] = None):
    """Obtém uma lista de leads."""
    query = db.query(Client)
    
    if assigned_to_id:
        query = query.filter(Client.assigned_to_id == assigned_to_id)
    
    return query.offset(skip).limit(limit).all()

def get_lead(db: Session, lead_id: int):
    """Obtém um lead pelo ID."""
    return db.query(Client).filter(Client.id == lead_id).first()

def update_lead(db: Session, db_lead, lead_in: LeadUpdate):
    """Atualiza um lead."""
    for key, value in lead_in.dict(exclude_unset=True).items():
        setattr(db_lead, key, value)
    
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

def delete_lead(db: Session, db_lead):
    """Exclui um lead."""
    db.delete(db_lead)
    db.commit()
    return db_lead
