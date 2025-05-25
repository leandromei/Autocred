from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Plan(Base):
    __tablename__ = 'plans'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    daily_limit = Column(Integer, default=10)
    extra_lead_price = Column(Float, default=10.0)
    
    # Relacionamentos
    clients = relationship("Client", back_populates="plan")

class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    plan_id = Column(Integer, ForeignKey('plans.id'))
    
    # Relacionamentos
    plan = relationship("Plan", back_populates="clients")
    lead_usages = relationship("LeadUsage", back_populates="client")
    lead_purchases = relationship("LeadPurchase", back_populates="client")

class LeadUsage(Base):
    __tablename__ = 'lead_usages'
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    date = Column(Date, default=func.current_date())
    total_consumed = Column(Integer, default=0)
    
    # Relacionamentos
    client = relationship("Client", back_populates="lead_usages")

class LeadPurchase(Base):
    __tablename__ = 'lead_purchases'
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    quantity = Column(Integer, default=0)
    amount = Column(Float, default=0.0)
    status = Column(String, default="pendente")  # pendente, aprovado, rejeitado
    created_at = Column(DateTime, default=func.now())
    
    # Relacionamentos
    client = relationship("Client", back_populates="lead_purchases")
