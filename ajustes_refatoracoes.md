# Ajustes e Refatorações no Código

## Estrutura do Projeto

### Reorganização de Arquivos
Para melhorar a organização e manutenibilidade do código, a estrutura de arquivos foi reorganizada seguindo um padrão mais modular:

```
sistema_revisado/
├── src/
│   ├── api/
│   │   ├── auth.py
│   │   ├── leads.py
│   │   ├── users.py
│   │   ├── proposals.py
│   │   ├── contracts.py
│   │   ├── commissions.py
│   │   └── prospecting.py
│   ├── models/
│   │   ├── user.py
│   │   ├── lead.py
│   │   ├── proposal.py
│   │   ├── contract.py
│   │   ├── commission.py
│   │   └── plan.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── lead.py
│   │   ├── proposal.py
│   │   ├── contract.py
│   │   ├── commission.py
│   │   └── plan.py
│   ├── crud/
│   │   ├── user.py
│   │   ├── lead.py
│   │   ├── proposal.py
│   │   ├── contract.py
│   │   ├── commission.py
│   │   └── plan.py
│   ├── core/
│   │   ├── security.py
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── exceptions.py
│   ├── utils/
│   │   ├── validators.py
│   │   ├── csv_handler.py
│   │   ├── notifications.py
│   │   └── calculations.py
│   ├── static/
│   │   ├── css/
│   │   │   ├── main.css
│   │   │   └── dark-mode.css
│   │   ├── js/
│   │   │   ├── main.js
│   │   │   ├── dark-mode.js
│   │   │   ├── form-validation.js
│   │   │   └── charts.js
│   │   └── img/
│   ├── templates/
│   │   ├── base.html
│   │   ├── components/
│   │   │   ├── header.html
│   │   │   ├── sidebar.html
│   │   │   ├── footer.html
│   │   │   └── modals.html
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── reset-password.html
│   │   ├── dashboard/
│   │   │   └── index.html
│   │   ├── leads/
│   │   │   ├── index.html
│   │   │   └── detail.html
│   │   ├── proposals/
│   │   │   ├── index.html
│   │   │   └── detail.html
│   │   ├── contracts/
│   │   │   ├── index.html
│   │   │   └── detail.html
│   │   ├── commissions/
│   │   │   ├── index.html
│   │   │   └── tables.html
│   │   ├── prospecting/
│   │   │   ├── index.html
│   │   │   └── campaigns.html
│   │   ├── simulation/
│   │   │   └── index.html
│   │   └── admin/
│   │       ├── users.html
│   │       ├── logs.html
│   │       └── settings.html
│   ├── database.py
│   └── main.py
├── tests/
│   ├── test_api/
│   ├── test_models/
│   └── test_utils/
├── alembic/
│   └── versions/
├── requirements.txt
├── README.md
└── CHANGELOG.md
```

### Correção de Importações
As importações no arquivo main.py foram corrigidas para usar caminhos absolutos:

```python
# Antes
from .api.api_plans import router as leads_router, admin_router as reports_router
from .api.api_user import router as users_router
from api_lead import router as admin_leads_router
from api_auth import router as auth_router

# Depois
from src.api.plans import router as leads_router, admin_router as reports_router
from src.api.users import router as users_router
from src.api.leads import router as admin_leads_router
from src.api.auth import router as auth_router
```

## Implementação de Modelos

### Modelo de Usuário Expandido
O modelo de usuário foi expandido para incluir permissões granulares:

```python
# src/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from passlib.context import CryptContext
from src.database import Base

# Tabela de associação para permissões
user_permissions = Table(
    'user_permissions',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
)

class Permission(Base):
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    
    users = relationship("User", secondary=user_permissions, back_populates="permissions")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    permissions = relationship("Permission", secondary=user_permissions, back_populates="users")
    leads = relationship("Lead", back_populates="assigned_to")
    proposals = relationship("Proposal", back_populates="created_by")
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    @classmethod
    def get_password_hash(cls, password):
        return cls.pwd_context.hash(password)
    
    def verify_password(self, plain_password):
        return self.pwd_context.verify(plain_password, self.hashed_password)
    
    def has_permission(self, permission_name):
        if self.is_superuser:
            return True
        return any(p.name == permission_name for p in self.permissions)
```

### Modelo de Lead Expandido
O modelo de lead foi expandido para incluir campos adicionais:

```python
# src/models/lead.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from src.database import Base

class LeadStatus(enum.Enum):
    NEW = "novo"
    CONTACTED = "contatado"
    QUALIFIED = "qualificado"
    CONVERTED = "convertido"
    REJECTED = "rejeitado"

class LeadSource(enum.Enum):
    MANUAL = "manual"
    IMPORT = "importação"
    SMS = "sms"
    URA = "ura"
    WEBSITE = "website"

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    phone = Column(String)
    cpf = Column(String, index=True)
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW)
    source = Column(Enum(LeadSource), default=LeadSource.MANUAL)
    notes = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    assigned_to = relationship("User", back_populates="leads")
    
    proposals = relationship("Proposal", back_populates="lead")
    activities = relationship("LeadActivity", back_populates="lead")

class LeadActivity(Base):
    __tablename__ = "lead_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    activity_type = Column(String)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    lead = relationship("Lead", back_populates="activities")
    user = relationship("User")
```

### Modelo de Proposta
Foi criado um modelo para propostas:

```python
# src/models/proposal.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from src.database import Base

class ProposalStatus(enum.Enum):
    DRAFT = "rascunho"
    SUBMITTED = "enviada"
    UNDER_ANALYSIS = "em análise"
    APPROVED = "aprovada"
    REJECTED = "rejeitada"
    CANCELLED = "cancelada"

class Proposal(Base):
    __tablename__ = "proposals"
    
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, unique=True, index=True)
    product = Column(String)
    value = Column(Float)
    installment = Column(Float)
    installment_count = Column(Integer)
    commission = Column(Float)
    status = Column(Enum(ProposalStatus), default=ProposalStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    lead_id = Column(Integer, ForeignKey("leads.id"))
    lead = relationship("Lead", back_populates="proposals")
    
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_by = relationship("User", back_populates="proposals")
    
    contract = relationship("Contract", back_populates="proposal", uselist=False)
    commission_record = relationship("Commission", back_populates="proposal", uselist=False)
    documents = relationship("ProposalDocument", back_populates="proposal")
    history = relationship("ProposalHistory", back_populates="proposal")

class ProposalDocument(Base):
    __tablename__ = "proposal_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"))
    name = Column(String)
    file_path = Column(String)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    proposal = relationship("Proposal", back_populates="documents")

class ProposalHistory(Base):
    __tablename__ = "proposal_history"
    
    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    old_status = Column(Enum(ProposalStatus))
    new_status = Column(Enum(ProposalStatus))
    notes = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    proposal = relationship("Proposal", back_populates="history")
    user = relationship("User")
```

### Outros Modelos
Foram criados modelos para contratos, comissões e prospecção, seguindo a mesma estrutura e relacionamentos.

## Implementação de Segurança

### Configuração de CORS
A configuração de CORS foi ajustada para ser mais segura em produção:

```python
# src/core/config.py
from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Autocred API"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "insecure-secret-key-for-dev")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost", "http://localhost:8000"]
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./autocred.db")
    
    class Config:
        env_file = ".env"

settings = Settings()

# src/main.py
from src.core.config import settings

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### Proteção CSRF
Foi implementada proteção CSRF para formulários:

```python
# src/core/security.py
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime, timedelta
import secrets
from src.core.config import settings

security = HTTPBearer()

def create_csrf_token():
    return secrets.token_hex(32)

def verify_csrf_token(request: Request, form_csrf_token: str):
    session_csrf_token = request.session.get("csrf_token")
    if not session_csrf_token or session_csrf_token != form_csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token validation failed"
        )
```

### Validação de Força de Senha
Foi implementada validação de força de senha:

```python
# src/utils/validators.py
import re

def validate_password_strength(password: str) -> bool:
    """
    Validate password strength.
    Password must:
    - Be at least 8 characters long
    - Contain at least one uppercase letter
    - Contain at least one lowercase letter
    - Contain at least one digit
    - Contain at least one special character
    """
    if len(password) < 8:
        return False
    
    if not re.search(r'[A-Z]', password):
        return False
    
    if not re.search(r'[a-z]', password):
        return False
    
    if not re.search(r'[0-9]', password):
        return False
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    
    return True
```

## Implementação de Templates

### Template Base
Foi criado um template base com suporte a Dark Mode:

```html
<!-- src/templates/base.html -->
<!DOCTYPE html>
<html lang="pt-BR" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Autocred{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', path='/css/main.css') }}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <div class="app-container">
        {% include "components/header.html" %}
        
        <div class="main-content">
            {% include "components/sidebar.html" %}
            
            <div class="content">
                {% block content %}{% endblock %}
            </div>
        </div>
        
        {% include "components/footer.html" %}
    </div>
    
    <div id="toast-container"></div>
    
    <script src="{{ url_for('static', path='/js/main.js') }}"></script>
    <script src="{{ url_for('static', path='/js/dark-mode.js') }}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### Template de Dashboard
Foi criado um template para o Dashboard:

```html
<!-- src/templates/dashboard/index.html -->
{% extends "base.html" %}

{% block title %}Dashboard - Autocred{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', path='/css/dashboard.css') }}">
{% endblock %}

{% block content %}
<div class="dashboard">
    <h1 class="page-title">Dashboard</h1>
    
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-icon">
                <i class="fas fa-file-contract"></i>
            </div>
            <div class="kpi-content">
                <h3 class="kpi-title">Propostas</h3>
                <p class="kpi-value">{{ kpi_data.proposals_count }}</p>
                <p class="kpi-trend {% if kpi_data.proposals_trend > 0 %}positive{% elif kpi_data.proposals_trend < 0 %}negative{% endif %}">
                    {% if kpi_data.proposals_trend > 0 %}+{% endif %}{{ kpi_data.proposals_trend }}% em relação ao mês anterior
                </p>
            </div>
        </div>
        
        <div class="kpi-card">
            <div class="kpi-icon">
                <i class="fas fa-money-bill-wave"></i>
            </div>
            <div class="kpi-content">
                <h3 class="kpi-title">Comissões</h3>
                <p class="kpi-value">R$ {{ kpi_data.commissions_total|number_format(2, ',', '.') }}</p>
                <p class="kpi-trend {% if kpi_data.commissions_trend > 0 %}positive{% elif kpi_data.commissions_trend < 0 %}negative{% endif %}">
                    {% if kpi_data.commissions_trend > 0 %}+{% endif %}{{ kpi_data.commissions_trend }}% em relação ao mês anterior
                </p>
            </div>
        </div>
        
        <div class="kpi-card">
            <div class="kpi-icon">
                <i class="fas fa-users"></i>
            </div>
            <div class="kpi-content">
                <h3 class="kpi-title">Leads</h3>
                <p class="kpi-value">{{ kpi_data.leads_count }}</p>
                <p class="kpi-trend {% if kpi_data.leads_trend > 0 %}positive{% elif kpi_data.leads_trend < 0 %}negative{% endif %}">
                    {% if kpi_data.leads_trend > 0 %}+{% endif %}{{ kpi_data.leads_trend }}% em relação ao mês anterior
                </p>
            </div>
        </div>
    </div>
    
    <div class="charts-container">
        <div class="chart-card">
            <h3 class="chart-title">Propostas por Status</h3>
            <div class="chart" id="proposals-by-status-chart"></div>
        </div>
        
        <div class="chart-card">
            <h3 class="chart-title">Comissões por Mês</h3>
            <div class="chart" id="commissions-by-month-chart"></div>
        </div>
    </div>
    
    <div class="recent-activities">
        <h3 class="section-title">Atividades Recentes</h3>
        <div class="activities-list">
            {% for activity in recent_activities %}
            <div class="activity-item">
                <div class="activity-icon">
                    <i class="fas fa-{{ activity.icon }}"></i>
                </div>
                <div class="activity-content">
                    <p class="activity-text">{{ activity.description }}</p>
                    <p class="activity-time">{{ activity.created_at|time_ago }}</p>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="{{ url_for('static', path='/js/charts.js') }}"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Dados para o gráfico de propostas por status
        const proposalStatusData = {
            labels: {{ proposal_status_labels|tojson }},
            data: {{ proposal_status_data|tojson }}
        };
        
        // Dados para o gráfico de comissões por mês
        const commissionsByMonthData = {
            labels: {{ commissions_by_month_labels|tojson }},
            data: {{ commissions_by_month_data|tojson }}
        };
        
        // Inicializar gráficos
        initProposalsByStatusChart('proposals-by-status-chart', proposalStatusData);
        initCommissionsByMonthChart('commissions-by-month-chart', commissionsByMonthData);
    });
</script>
{% endblock %}
```

### Outros Templates
Foram criados templates para todas as outras páginas do sistema, seguindo o mesmo padrão e aplicando as diretrizes de design e usabilidade.

## Implementação de CSS e JavaScript

### CSS Principal
Foi criado um arquivo CSS principal com suporte a Dark Mode:

```css
/* src/static/css/main.css */
:root {
  /* Variáveis de cores para modo claro */
  --color-primary: #2563EB;
  --color-secondary: #10B981;
  --color-background: #FFFFFF;
  --color-text: #1F2937;
  --color-alert: #EF4444;
  --color-warning: #F59E0B;
  --color-success: #10B981;
  --color-border: #E5E7EB;
  
  /* Variáveis de espaçamento */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 2rem;
  
  /* Variáveis de tipografia */
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.25rem;
  --font-size-xl: 1.5rem;
}

[data-theme="dark"] {
  /* Variáveis de cores para modo escuro */
  --color-primary: #3B82F6;
  --color-secondary: #34D399;
  --color-background: #111827;
  --color-text: #F9FAFB;
  --color-alert: #F87171;
  --color-warning: #FBBF24;
  --color-success: #34D399;
  --color-border: #374151;
}

/* Reset e estilos base */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background-color: var(--color-background);
  color: var(--color-text);
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  font-size: var(--font-size-base);
  line-height: 1.5;
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* Layout principal */
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  display: flex;
  flex: 1;
}

.content {
  flex: 1;
  padding: var(--space-lg);
}

/* Componentes comuns */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
  border: none;
}

.btn-primary:hover {
  background-color: var(--color-primary-dark, #1d4ed8);
}

.btn-secondary {
  background-color: transparent;
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
}

.btn-secondary:hover {
  background-color: rgba(37, 99, 235, 0.1);
}

.btn-danger {
  background-color: var(--color-alert);
  color: white;
  border: none;
}

.btn-danger:hover {
  background-color: var(--color-alert-dark, #dc2626);
}

/* Formulários */
.form-group {
  margin-bottom: var(--space-md);
}

.form-label {
  display: block;
  margin-bottom: var(--space-xs);
  font-weight: 500;
}

.form-control {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  background-color: var(--color-background);
  color: var(--color-text);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-control:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  outline: none;
}

.form-error {
  color: var(--color-alert);
  font-size: var(--font-size-sm);
  margin-top: var(--space-xs);
}

/* Tabelas */
.table-container {
  overflow-x: auto;
  margin-bottom: var(--space-lg);
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  text-align: left;
}

.table th {
  background-color: rgba(0, 0, 0, 0.02);
  font-weight: 600;
}

.table tr:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

/* Responsividade */
@media (max-width: 639px) {
  .content {
    padding: var(--space-md);
  }
  
  .kpi-container {
    flex-direction: column;
  }
  
  .kpi-card {
    width: 100%;
    margin-bottom: var(--space-md);
  }
  
  .charts-container {
    flex-direction: column;
  }
  
  .chart-card {
    width: 100%;
    margin-bottom: var(--space-md);
  }
}
```

### JavaScript para Dark Mode
Foi implementado JavaScript para controle do Dark Mode:

```javascript
// src/static/js/dark-mode.js
// Função para alternar entre modo claro e escuro
function toggleDarkMode() {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  
  // Atualizar ícone do toggle
  const toggleIcon = document.getElementById('theme-toggle-icon');
  if (toggleIcon) {
    toggleIcon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
  }
}

// Inicializar tema baseado na preferência salva ou do sistema
function initTheme() {
  const savedTheme = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const theme = savedTheme || (prefersDark ? 'dark' : 'light');
  
  document.documentElement.setAttribute('data-theme', theme);
  
  // Atualizar ícone do toggle
  const toggleIcon = document.getElementById('theme-toggle-icon');
  if (toggleIcon) {
    toggleIcon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
  }
}

// Adicionar event listener ao botão de toggle
function setupThemeToggle() {
  const themeToggle = document.querySelector('.theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', toggleDarkMode);
  }
}

// Executar ao carregar a página
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  setupThemeToggle();
});
```

### JavaScript para Validação de Formulários
Foi implementado JavaScript para validação de formulários:

```javascript
// src/static/js/form-validation.js
// Validação em tempo real
function initFormValidation() {
  const forms = document.querySelectorAll('form[data-validate]');
  
  forms.forEach(form => {
    const inputs = form.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
      // Validar ao perder foco
      input.addEventListener('blur', () => validateInput(input));
      
      // Validar ao digitar (com debounce)
      let timeout;
      input.addEventListener('input', () => {
        clearTimeout(timeout);
        timeout = setTimeout(() => validateInput(input), 500);
      });
    });
    
    // Validar ao enviar
    form.addEventListener('submit', e => {
      let isValid = true;
      
      inputs.forEach(input => {
        if (!validateInput(input)) {
          isValid = false;
        }
      });
      
      if (!isValid) {
        e.preventDefault();
        showFeedback('error', 'Por favor, corrija os erros no formulário.');
      }
    });
  });
}

function validateInput(input) {
  const value = input.value.trim();
  const validations = input.dataset.validations ? JSON.parse(input.dataset.validations) : {};
  const errorContainer = input.nextElementSibling?.classList.contains('input-error') 
    ? input.nextElementSibling 
    : null;
  
  let isValid = true;
  let errorMessage = '';
  
  // Validar obrigatório
  if (validations.required && value === '') {
    isValid = false;
    errorMessage = validations.requiredMessage || 'Este campo é obrigatório';
  }
  
  // Validar email
  else if (validations.email && value !== '' && !isValidEmail(value)) {
    isValid = false;
    errorMessage = validations.emailMessage || 'Email inválido';
  }
  
  // Validar CPF
  else if (validations.cpf && value !== '' && !isValidCPF(value)) {
    isValid = false;
    errorMessage = validations.cpfMessage || 'CPF inválido';
  }
  
  // Validar tamanho mínimo
  else if (validations.minLength && value.length < validations.minLength) {
    isValid = false;
    errorMessage = validations.minLengthMessage || `Mínimo de ${validations.minLength} caracteres`;
  }
  
  // Exibir ou limpar erro
  if (!isValid) {
    input.classList.add('input-invalid');
    
    if (!errorContainer) {
      const newErrorContainer = document.createElement('div');
      newErrorContainer.className = 'input-error';
      newErrorContainer.textContent = errorMessage;
      input.insertAdjacentElement('afterend', newErrorContainer);
    } else {
      errorContainer.textContent = errorMessage;
    }
  } else {
    input.classList.remove('input-invalid');
    if (errorContainer) {
      errorContainer.textContent = '';
    }
  }
  
  return isValid;
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function isValidCPF(cpf) {
  // Implementação de validação de CPF
  cpf = cpf.replace(/[^\d]/g, '');
  
  if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) return false;
  
  let sum = 0;
  let remainder;
  
  for (let i = 1; i <= 9; i++) {
    sum += parseInt(cpf.substring(i-1, i)) * (11 - i);
  }
  
  remainder = (sum * 10) % 11;
  if (remainder === 10 || remainder === 11) remainder = 0;
  if (remainder !== parseInt(cpf.substring(9, 10))) return false;
  
  sum = 0;
  for (let i = 1; i <= 10; i++) {
    sum += parseInt(cpf.substring(i-1, i)) * (12 - i);
  }
  
  remainder = (sum * 10) % 11;
  if (remainder === 10 || remainder === 11) remainder = 0;
  if (remainder !== parseInt(cpf.substring(10, 11))) return false;
  
  return true;
}

// Inicializar validação
document.addEventListener('DOMContentLoaded', initFormValidation);
```

## Conclusão dos Ajustes e Refatorações

Os ajustes e refatorações realizados no código do Sistema Autocred incluíram:

1. **Reorganização da estrutura de arquivos** para melhor modularidade e manutenibilidade
2. **Correção de importações** para usar caminhos absolutos
3. **Expansão dos modelos de dados** para incluir todos os campos e relacionamentos necessários
4. **Implementação de segurança** com configuração adequada de CORS, proteção CSRF e validação de senhas
5. **Criação de templates HTML** para todas as páginas do sistema, seguindo as diretrizes de design
6. **Implementação de CSS e JavaScript** para suporte a Dark Mode, validação de formulários e feedback visual

Estas melhorias tornam o sistema mais robusto, seguro e alinhado com as melhores práticas de desenvolvimento web moderno.
