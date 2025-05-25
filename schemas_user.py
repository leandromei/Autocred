from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# Esquema base para usuário
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

# Esquema para criação de usuário
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

# Esquema para atualização de usuário
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

# Esquema para resposta de usuário
class User(UserBase):
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # Anteriormente orm_mode = True
