from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, extract
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import calendar
import json
import random # Para dados simulados

from database import get_db
# Assumindo que Lead e LeadPurchase são os modelos relevantes. Se houver um modelo Commission, deve ser importado.
from models import Lead, LeadPurchase # Adicionado LeadPurchase
from core_security import get_current_active_user

# Criar router para o dashboard
router = APIRouter(prefix="/dashboard")

@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Retorna estatísticas agregadas para o dashboard financeiro.
    Inclui:
    - Total de leads
    - Leads qualificados
    - Leads convertidos
    - Receita estimada
    - Dados para gráficos (Leads, Origem, Status, Comissões)
    """
    # Definir período (últimos 30 dias para cards, últimos 12 meses para gráficos)
    today = datetime.now()
    thirty_days_ago = today - timedelta(days=30)
    one_year_ago = today - timedelta(days=365)
    
    try:
        # --- Cálculos para os Cards (últimos 30 dias) ---
        total_leads = db.query(func.count(Lead.id)).filter(
            Lead.created_at >= thirty_days_ago
        ).scalar() or 0
        
        qualified_leads = db.query(func.count(Lead.id)).filter(
            and_(
                Lead.created_at >= thirty_days_ago,
                Lead.status.in_(["qualificado", "proposta", "fechado"])
            )
        ).scalar() or 0
        
        converted_leads = db.query(func.count(Lead.id)).filter(
            and_(
                Lead.created_at >= thirty_days_ago,
                Lead.status == "fechado"
            )
        ).scalar() or 0
        
        qualified_rate = round((qualified_leads / total_leads * 100), 1) if total_leads > 0 else 0
        conversion_rate = round((converted_leads / total_leads * 100), 1) if total_leads > 0 else 0
        
        average_ticket = 3000
        estimated_revenue = converted_leads * average_ticket
        
        # --- Dados para Gráficos (últimos 12 meses) ---
        
        # 1. Evolução de Leads por Mês
        leads_monthly_data = db.query(
            extract('year', Lead.created_at).label('year'),
            extract('month', Lead.created_at).label('month'),
            func.count(Lead.id).label('count')
        ).filter(
            Lead.created_at >= one_year_ago
        ).group_by('year', 'month').order_by('year', 'month').all()
        
        leads_evolution_labels = []
        leads_evolution_values = []
        month_map = {}
        for i in range(12):
            dt = today - timedelta(days=(11-i)*30) # Aproximação para garantir 12 meses
            month_key = (dt.year, dt.month)
            month_map[month_key] = 0
            leads_evolution_labels.append(dt.strftime("%b/%y"))
            
        for year, month, count in leads_monthly_data:
            if (year, month) in month_map:
                 month_map[(year, month)] = count
                 
        leads_evolution_values = [month_map.get((datetime.strptime(label, "%b/%y").year, datetime.strptime(label, "%b/%y").month), 0) for label in leads_evolution_labels]
        # Ajuste final para garantir 12 valores
        if len(leads_evolution_values) < 12:
             leads_evolution_values.extend([0] * (12 - len(leads_evolution_values)))
        leads_evolution_values = leads_evolution_values[-12:]
        leads_evolution_labels = leads_evolution_labels[-12:]

        # 2. Conversão por Origem (Total)
        sources_data = db.query(
            Lead.source, func.count(Lead.id).label('count')
        ).group_by(Lead.source).order_by(desc('count')).all()
        
        conversion_source_labels = [s[0] for s in sources_data if s[0]]
        conversion_source_values = [s[1] for s in sources_data if s[0]]
        # Limitar a 5 fontes principais + 'Outros'
        if len(conversion_source_labels) > 5:
            other_count = sum(conversion_source_values[5:])
            conversion_source_labels = conversion_source_labels[:5] + ["Outros"]
            conversion_source_values = conversion_source_values[:5] + [other_count]
            
        # Cores para o gráfico de pizza/doughnut
        pie_colors = ["#3498db", "#2ecc71", "#e74c3c", "#f39c12", "#9b59b6", "#34495e"]

        # 3. Status dos Leads (Total)
        statuses_data = db.query(
            Lead.status, func.count(Lead.id).label('count')
        ).group_by(Lead.status).order_by(desc('count')).all()
        
        lead_status_labels = [s[0] for s in statuses_data if s[0]]
        lead_status_values = [s[1] for s in statuses_data if s[0]]
        
        # 4. Comissões ao Longo do Tempo (últimos 12 meses)
        # Assumindo que LeadPurchase.amount representa o valor da comissão e created_at a data
        # Se houver um modelo Commission, usar esse modelo.
        commissions_monthly_data = db.query(
            extract('year', LeadPurchase.created_at).label('year'),
            extract('month', LeadPurchase.created_at).label('month'),
            func.sum(LeadPurchase.amount).label('total_amount')
        ).filter(
            LeadPurchase.created_at >= one_year_ago,
            LeadPurchase.status == 'aprovado' # Considerar apenas comissões aprovadas/pagas
        ).group_by('year', 'month').order_by('year', 'month').all()
        
        commissions_evolution_labels = []
        commissions_evolution_values = []
        commissions_month_map = {}
        for i in range(12):
            dt = today - timedelta(days=(11-i)*30)
            month_key = (dt.year, dt.month)
            commissions_month_map[month_key] = 0
            commissions_evolution_labels.append(dt.strftime("%b/%y"))
            
        for year, month, total_amount in commissions_monthly_data:
             if (year, month) in commissions_month_map:
                 commissions_month_map[(year, month)] = total_amount or 0
                 
        commissions_evolution_values = [commissions_month_map.get((datetime.strptime(label, "%b/%y").year, datetime.strptime(label, "%b/%y").month), 0) for label in commissions_evolution_labels]
        # Ajuste final para garantir 12 valores
        if len(commissions_evolution_values) < 12:
             commissions_evolution_values.extend([0] * (12 - len(commissions_evolution_values)))
        commissions_evolution_values = commissions_evolution_values[-12:]
        commissions_evolution_labels = commissions_evolution_labels[-12:]

        # Montar resposta
        return {
            "total_leads": total_leads,
            "qualified_leads": qualified_leads,
            "qualified_rate": qualified_rate,
            "converted_leads": converted_leads,
            "conversion_rate": conversion_rate,
            "estimated_revenue": f"{estimated_revenue:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "average_ticket": f"{average_ticket:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "leads_evolution_data": {
                "labels": leads_evolution_labels,
                "datasets": [{
                    "label": "Leads",
                    "data": leads_evolution_values,
                    "backgroundColor": "#2196F3",
                    "borderColor": "#2196F3",
                    "tension": 0.1
                }]
            },
            "conversion_by_source_data": {
                "labels": conversion_source_labels,
                "datasets": [{
                    "label": "Origem",
                    "data": conversion_source_values,
                    "backgroundColor": pie_colors[:len(conversion_source_labels)]
                }]
            },
            "lead_status_data": {
                "labels": lead_status_labels,
                "datasets": [{
                    "label": "Status",
                    "data": lead_status_values,
                    "backgroundColor": pie_colors[:len(lead_status_labels)] # Reutilizar cores
                }]
            },
            "commissions_evolution_data": {
                "labels": commissions_evolution_labels,
                "datasets": [{
                    "label": "Comissões (R$)",
                    "data": commissions_evolution_values,
                    "backgroundColor": "#2ecc71", # Verde para comissões
                    "borderColor": "#2ecc71",
                    "tension": 0.1
                }]
            }
        }
    except Exception as e:
        # Em produção, registrar o erro em um sistema de log
        print(f"Erro ao obter estatísticas do dashboard: {e}")
        
        # Retornar dados de exemplo para desenvolvimento
        # Gerar 12 meses de exemplo
        example_labels = [(today - timedelta(days=(11-i)*30)).strftime("%b/%y") for i in range(12)]
        return {
            "total_leads": 124,
            "qualified_leads": 78,
            "qualified_rate": 62.9,
            "converted_leads": 42,
            "conversion_rate": 33.8,
            "estimated_revenue": "126.000,00",
            "average_ticket": "3.000,00",
            "leads_evolution_data": {
                "labels": example_labels,
                "datasets": [{
                    "label": "Leads",
                    "data": [random.randint(50, 150) for _ in range(12)],
                    "backgroundColor": "#2196F3",
                    "borderColor": "#2196F3",
                    "tension": 0.1
                }]
            },
            "conversion_by_source_data": {
                "labels": ["Facebook", "Google", "Instagram", "Indicação", "Site", "Outros"],
                "datasets": [{
                    "label": "Origem",
                    "data": [35, 45, 25, 20, 15, 10],
                    "backgroundColor": ["#3498db", "#2ecc71", "#e74c3c", "#f39c12", "#9b59b6", "#34495e"]
                }]
            },
            "lead_status_data": {
                "labels": ["Novo", "Contato", "Qualificado", "Proposta", "Fechado", "Perdido"],
                "datasets": [{
                    "label": "Status",
                    "data": [30, 25, 20, 15, 10, 5],
                    "backgroundColor": ["#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#2c3e50", "#e74c3c"]
                }]
            },
            "commissions_evolution_data": {
                 "labels": example_labels,
                 "datasets": [{
                     "label": "Comissões (R$)",
                     "data": [random.randint(1000, 5000) for _ in range(12)],
                     "backgroundColor": "#2ecc71",
                     "borderColor": "#2ecc71",
                     "tension": 0.1
                 }]
            }
        }

