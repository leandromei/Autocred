"""
Autocred - Sistema de Gestão de Leads para Correspondentes Bancários
Arquivo principal da aplicação FastAPI

Este módulo configura a aplicação FastAPI, define as rotas principais
e gerencia a autenticação e autorização dos usuários.
"""

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
import json
from datetime import timedelta
from typing import Dict, Any
import os

# Importar routers e dependências
from api_lead import router as lead_router
from api_dashboard import router as dashboard_router
from api_auth import router as auth_router
from routes import router as page_router
from database import get_db, engine
import models
from core_security import (
    create_access_token,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user
)
from models import User

# Importar módulos de logs e tratamento de erros
import logger
from error_handlers import (
    configure_exception_handlers,
    handle_errors,
    AuthenticationError,
    AuthorizationError,
    NotFoundError
)
from logger import RequestLoggingMiddleware

# Configuração do aplicativo
app = FastAPI(
    title="Autocred - Sistema de Gestão de Leads",
    description="API para o sistema de gestão de leads para correspondentes bancários",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adicionar middleware de logging
app.add_middleware(RequestLoggingMiddleware)

# Configurar handlers de exceção
configure_exception_handlers(app)

# Configuração de templates e arquivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir routers na aplicação
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(lead_router, prefix="/api", tags=["leads"])
app.include_router(dashboard_router, prefix="/api", tags=["dashboard"])
app.include_router(page_router)  # Rotas das páginas HTML

# Registrar inicialização da aplicação
logger.info("Aplicação Autocred inicializada", {
    "environment": os.getenv("ENVIRONMENT", "development"),
    "version": "1.0.0"
})


@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Rota principal - redireciona para a página de login
    """
    logger.debug("Acesso à rota principal, redirecionando para login")
    return RedirectResponse(url="/login", status_code=302)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Renderiza a página de login
    """
    logger.debug("Renderizando página de login")
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login", response_class=JSONResponse)
@handle_errors(default_message="Erro ao processar login")
async def login_for_access_token_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Processa o formulário de login e retorna um token JWT
    
    Args:
        form_data: Dados do formulário de login
        db: Sessão do banco de dados
        
    Returns:
        JSONResponse com o token JWT ou mensagem de erro
    """
    logger.info("Tentativa de login", {"email": form_data.username})
    
    user = authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        logger.warning("Falha na autenticação", {"email": form_data.username})
        raise AuthenticationError(
            message="Usuário ou senha inválidos",
            details={"email": form_data.username}
        )
    
    logger.info("Login bem-sucedido", {"user_id": user.id, "email": user.email})
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/dashboard", response_class=HTMLResponse)
@handle_errors(default_message="Erro ao carregar dashboard")
async def dashboard(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Renderiza o dashboard financeiro (protegido por autenticação)
    
    Args:
        request: Objeto Request do FastAPI
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Template HTML do dashboard com dados do usuário e estatísticas
    """
    logger.info("Acesso ao dashboard", {"user_id": current_user.id})
    
    # Obter estatísticas do dashboard usando a função da API
    from api_dashboard import get_dashboard_stats
    dashboard_stats = get_dashboard_stats(db=db, current_user=current_user)

    # Preparar contexto para o template
    context = {
        "request": request,
        "user": current_user,
        "total_leads": dashboard_stats.get("total_leads", 0),
        "qualified_leads": dashboard_stats.get("qualified_leads", 0),
        "qualified_rate": dashboard_stats.get("qualified_rate", 0),
        "converted_leads": dashboard_stats.get("converted_leads", 0),
        "conversion_rate": dashboard_stats.get("conversion_rate", 0),
        "estimated_revenue": dashboard_stats.get("estimated_revenue", "0,00"),
        "average_ticket": dashboard_stats.get("average_ticket", "0,00"),
        # Converter dados dos gráficos para JSON
        "leads_evolution_data": json.dumps(dashboard_stats.get("leads_evolution_data", {})),
        "conversion_by_source_data": json.dumps(dashboard_stats.get("conversion_by_source_data", {})),
        "lead_status_data": json.dumps(dashboard_stats.get("lead_status_data", {})),
        "commissions_evolution_data": json.dumps(dashboard_stats.get("commissions_evolution_data", {}))
    }
    
    return templates.TemplateResponse("financial_dashboard.html", context)


@app.get("/admin", response_class=HTMLResponse)
@handle_errors(default_message="Erro ao carregar painel administrativo")
async def admin(
    request: Request, 
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """
    Renderiza o painel administrativo de leads (protegido por autenticação e autorização)
    
    Args:
        request: Objeto Request do FastAPI
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        Template HTML do painel administrativo com dados dos leads
        
    Raises:
        AuthorizationError: Se o usuário não tiver privilégios de administrador
    """
    logger.info("Acesso ao painel administrativo", {"user_id": current_user.id})
    
    # Verificar se o usuário é administrador
    if not current_user.is_superuser:
        logger.warning("Tentativa de acesso não autorizado ao painel admin", {
            "user_id": current_user.id,
            "is_admin": current_user.is_superuser
        })
        raise AuthorizationError(
            message="Acesso negado: Requer privilégios de administrador",
            details={"user_id": current_user.id}
        )
    
    # Buscar leads recentes
    leads = db.query(models.Lead).order_by(desc(models.Lead.created_at)).limit(20).all()
    
    # Formatar leads para exibição
    formatted_leads = [
        {
            "id": lead.id,
            "name": lead.name,
            "email": lead.email,
            "phone": lead.phone,
            "status": lead.status,
            "created_at": lead.created_at.strftime("%d/%m/%Y %H:%M") if lead.created_at else "-"
        }
        for lead in leads
    ]
    
    return templates.TemplateResponse(
        "admin_leads.html", 
        {"request": request, "user": current_user, "leads": formatted_leads}
    )


@app.get("/logout")
async def logout():
    """
    Rota para logout - redireciona para a página de login
    O token JWT é removido no frontend (localStorage)
    """
    logger.info("Logout de usuário")
    return RedirectResponse(url="/login", status_code=302)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> HTMLResponse | JSONResponse:
    """
    Tratamento global de exceções HTTP
    
    Args:
        request: Objeto Request do FastAPI
        exc: Exceção HTTP
        
    Returns:
        Redirecionamento para login (401), página de erro ou resposta JSON
    """
    logger.warning(f"Exceção HTTP: {exc.status_code} - {exc.detail}", {
        "path": request.url.path,
        "status_code": exc.status_code
    })
    
    if exc.status_code == 401:
        # Verificar se a requisição espera HTML
        accept_header = request.headers.get("accept", "")
        if "text/html" in accept_header:
            return RedirectResponse(url="/login", status_code=302)
        else:
            # Para requisições de API, retornar JSON
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
                headers=exc.headers,
            )
    
    # Para outros erros, retornar página de erro
    return templates.TemplateResponse(
        "error.html", 
        {
            "request": request, 
            "status_code": exc.status_code, 
            "detail": exc.detail
        }, 
        status_code=exc.status_code
    )


@app.on_event("startup")
async def startup_event():
    """
    Evento executado na inicialização da aplicação
    """
    logger.info("Iniciando aplicação Autocred")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento executado no encerramento da aplicação
    """
    logger.info("Encerrando aplicação Autocred")
