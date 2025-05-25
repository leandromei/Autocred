from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, extract
from typing import List, Optional
from datetime import datetime, timedelta
import calendar

from database import get_db
# Importar modelos necessários
from models import User, Lead, Contact, Proposal, Contract, Commission
# Importar dependência de autenticação JWT
from core_security import get_current_active_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Função auxiliar para formatar moeda
def format_currency(value):
    if value is None:
        return "R$ 0,00"
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Função auxiliar para formatar data
def format_date(value):
    if value is None:
        return "-"
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y %H:%M")
    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")
    return str(value)

# Rota para a página de contatos (protegida)
@router.get("/contacts", response_class=HTMLResponse)
async def contacts_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    contacts = db.query(Contact).order_by(desc(Contact.created_at)).all()
    
    # Formatar dados para exibição, se necessário
    formatted_contacts = [
        {
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "phone": c.phone,
            "source": c.source,
            "created_at": format_date(c.created_at),
            "status": c.status
        }
        for c in contacts
    ]
    
    return templates.TemplateResponse(
        "contacts.html", 
        {
            "request": request, 
            "contacts": formatted_contacts,
            "user": current_user # Passar usuário autenticado
        }
    )

# Rota para a página de simulação (protegida)
@router.get("/simulation", response_class=HTMLResponse)
async def simulation_page(request: Request, current_user: User = Depends(get_current_active_user)):
    # Esta página pode não precisar de dados do DB inicialmente
    return templates.TemplateResponse(
        "simulation.html", 
        {
            "request": request,
            "user": current_user
        }
    )

# Rota para a página de propostas (protegida)
@router.get("/proposals", response_class=HTMLResponse)
async def proposals_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    proposals = db.query(Proposal).order_by(desc(Proposal.created_at)).all()
    
    formatted_proposals = [
        {
            "id": p.id,
            "client_name": p.client_name, # Assumindo que existe esse campo ou relação
            "loan_type": p.loan_type,
            "amount": format_currency(p.amount),
            "term": f"{p.term} meses",
            "interest_rate": f"{p.interest_rate:.2f}% a.m.".replace(".", ","),
            "created_at": format_date(p.created_at),
            "status": p.status
        }
        for p in proposals
    ]
    
    return templates.TemplateResponse(
        "proposals.html", 
        {
            "request": request, 
            "proposals": formatted_proposals,
            "user": current_user
        }
    )

# Rota para a página de prospecção (protegida)
@router.get("/prospecting", response_class=HTMLResponse)
async def prospecting_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    all_leads = db.query(Lead).order_by(desc(Lead.created_at)).all()
    
    # Filtrar por status
    new_leads = [l for l in all_leads if l.status == "novo"]
    contacted_leads = [l for l in all_leads if l.status == "contato"]
    qualified_leads = [l for l in all_leads if l.status == "qualificado"]
    
    # Formatar dados
    def format_lead(lead):
        return {
            "id": lead.id,
            "name": lead.name,
            "email": lead.email,
            "phone": lead.phone,
            "source": lead.source,
            "created_at": format_date(lead.created_at),
            "status": lead.status
        }

    return templates.TemplateResponse(
        "prospecting.html", 
        {
            "request": request, 
            "all_leads": [format_lead(l) for l in all_leads],
            "new_leads": [format_lead(l) for l in new_leads],
            "contacted_leads": [format_lead(l) for l in contacted_leads],
            "qualified_leads": [format_lead(l) for l in qualified_leads],
            "user": current_user
        }
    )

# Rota para a página de contratos (protegida)
@router.get("/contracts", response_class=HTMLResponse)
async def contracts_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    contracts = db.query(Contract).order_by(desc(Contract.created_at)).all()
    
    formatted_contracts = [
        {
            "id": c.id,
            "number": c.number,
            "client_name": c.client_name, # Assumindo campo ou relação
            "amount": format_currency(c.amount),
            "institution": c.institution,
            "created_at": format_date(c.created_at),
            "status": c.status
        }
        for c in contracts
    ]
    
    return templates.TemplateResponse(
        "contracts.html", 
        {
            "request": request, 
            "contracts": formatted_contracts,
            "user": current_user
        }
    )

# Rota para a página de comissões (protegida)
@router.get("/commissions", response_class=HTMLResponse)
async def commissions_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    commissions = db.query(Commission).order_by(desc(Commission.created_at)).all()
    
    pending_commissions_list = [c for c in commissions if c.status == "pendente"]
    paid_commissions_list = [c for c in commissions if c.status == "pago"]
    
    # Calcular valores para os cards de resumo
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    monthly_commissions_val = db.query(func.sum(Commission.commission_amount)).filter(
        extract('month', Commission.payment_date) == current_month, # Assumindo payment_date
        extract('year', Commission.payment_date) == current_year,
        Commission.status == 'pago'
    ).scalar() or 0
    
    pending_commissions_val = db.query(func.sum(Commission.commission_amount)).filter(
        Commission.status == 'pendente'
    ).scalar() or 0
    
    paid_commissions_val = db.query(func.sum(Commission.commission_amount)).filter(
        Commission.status == 'pago'
    ).scalar() or 0
    
    total_paid_count = len(paid_commissions_list)
    average_commission_val = (paid_commissions_val / total_paid_count) if total_paid_count > 0 else 0
    
    # Formatar dados das tabelas
    def format_commission(comm):
         return {
            "id": comm.id,
            "contract_number": comm.contract_number, # Assumindo campo ou relação
            "client_name": comm.client_name, # Assumindo campo ou relação
            "contract_amount": format_currency(comm.contract_amount), # Assumindo campo
            "commission_amount": format_currency(comm.commission_amount),
            "created_at": format_date(comm.created_at),
            "status": comm.status
        }

    return templates.TemplateResponse(
        "commissions.html", 
        {
            "request": request, 
            "commissions": [format_commission(c) for c in commissions],
            "pending_commissions_list": [format_commission(c) for c in pending_commissions_list],
            "paid_commissions_list": [format_commission(c) for c in paid_commissions_list],
            "monthly_commissions": format_currency(monthly_commissions_val),
            "pending_commissions": format_currency(pending_commissions_val),
            "paid_commissions": format_currency(paid_commissions_val),
            "average_commission": format_currency(average_commission_val),
            "pending_count": len(pending_commissions_list),
            "paid_count": total_paid_count,
            "total_count": len(commissions),
            "current_month": calendar.month_name[current_month],
            "current_year": current_year,
            "user": current_user
        }
    )

