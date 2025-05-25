from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime, date

# Esquema base para lead
class LeadBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = "novo"
    notes: Optional[str] = None

# Esquema para criação de lead
class LeadCreate(LeadBase):
    pass

# Esquema para atualização de lead
class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    assigned_to_id: Optional[int] = None

# Esquema para resposta de lead
class Lead(LeadBase):
    id: int
    created_at: datetime
    assigned_to_id: Optional[int] = None
    
    class Config:
        from_attributes = True  # Anteriormente orm_mode = True

# Esquema para uso de leads
class LeadUsageResponse(BaseModel):
    date: date
    total_consumed: int
    daily_limit: int
    extra_leads_available: int
    
    class Config:
        from_attributes = True

# Esquema para compra de leads
class LeadPurchaseCreate(BaseModel):
    quantity: int = Field(..., description="Quantidade de leads a comprar", example=10, gt=0)

class LeadPurchaseResponse(BaseModel):
    id: int
    quantity: int
    amount: float
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Esquema para relatório financeiro
class FinancialReportResponse(BaseModel):
    total_revenue: float
    total_leads_sold: int
    purchases_by_status: dict
    revenue_by_client: List[dict]
