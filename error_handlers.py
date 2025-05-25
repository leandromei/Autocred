"""
Autocred - Sistema de Gestão de Leads para Correspondentes Bancários
Módulo de tratamento de erros

Este módulo implementa handlers de exceções e utilitários para
garantir um tratamento de erros robusto e consistente.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from jose.exceptions import JWTError
from typing import Dict, Any, Optional, Callable, Type

import logger


class AutocredError(Exception):
    """
    Classe base para exceções personalizadas do sistema Autocred
    """
    def __init__(
        self, 
        message: str, 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "internal_error",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(AutocredError):
    """Erro para recursos não encontrados"""
    def __init__(self, message: str, resource_type: str, resource_id: Any):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="resource_not_found",
            details={
                "resource_type": resource_type,
                "resource_id": resource_id
            }
        )


class AuthenticationError(AutocredError):
    """Erro para falhas de autenticação"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="authentication_failed",
            details=details
        )


class AuthorizationError(AutocredError):
    """Erro para falhas de autorização"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="authorization_failed",
            details=details
        )


class ValidationError(AutocredError):
    """Erro para falhas de validação"""
    def __init__(self, message: str, field_errors: Optional[Dict[str, str]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="validation_error",
            details={"field_errors": field_errors or {}}
        )


class DatabaseError(AutocredError):
    """Erro para falhas de banco de dados"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="database_error",
            details=details
        )


# Handlers para exceções específicas
async def autocred_exception_handler(request: Request, exc: AutocredError) -> JSONResponse:
    """
    Handler para exceções personalizadas do Autocred
    
    Args:
        request: Objeto Request do FastAPI
        exc: Exceção do tipo AutocredError
        
    Returns:
        JSONResponse com detalhes do erro
    """
    # Registrar erro no log
    logger.error(f"Erro da aplicação: {exc.message}", {
        "error_code": exc.error_code,
        "status_code": exc.status_code,
        "path": request.url.path,
        "details": exc.details
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "error_code": exc.error_code,
            "details": exc.details
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler para erros de validação do FastAPI
    
    Args:
        request: Objeto Request do FastAPI
        exc: Exceção de validação
        
    Returns:
        JSONResponse com detalhes dos erros de validação
    """
    # Extrair erros de validação
    field_errors = {}
    for error in exc.errors():
        # Obter o campo com erro
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        # Obter a mensagem de erro
        message = error["msg"]
        field_errors[field] = message
    
    # Registrar erro no log
    logger.warning("Erro de validação de dados", {
        "path": request.url.path,
        "field_errors": field_errors
    })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "message": "Erro de validação dos dados fornecidos",
            "error_code": "validation_error",
            "details": {
                "field_errors": field_errors
            }
        }
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handler para erros do SQLAlchemy
    
    Args:
        request: Objeto Request do FastAPI
        exc: Exceção do SQLAlchemy
        
    Returns:
        JSONResponse com detalhes do erro
    """
    # Determinar o tipo específico de erro
    if isinstance(exc, IntegrityError):
        # Erro de integridade (chave duplicada, violação de constraint, etc.)
        message = "Erro de integridade do banco de dados"
        error_code = "database_integrity_error"
    else:
        # Outros erros de banco de dados
        message = "Erro de banco de dados"
        error_code = "database_error"
    
    # Registrar erro no log
    logger.error(f"Erro de banco de dados: {str(exc)}", {
        "path": request.url.path,
        "error_type": exc.__class__.__name__
    }, exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": message,
            "error_code": error_code,
            "details": {
                "error_type": exc.__class__.__name__
            }
        }
    )


async def jwt_exception_handler(request: Request, exc: JWTError) -> JSONResponse:
    """
    Handler para erros de JWT
    
    Args:
        request: Objeto Request do FastAPI
        exc: Exceção de JWT
        
    Returns:
        JSONResponse com detalhes do erro
    """
    # Registrar erro no log
    logger.warning(f"Erro de autenticação JWT: {str(exc)}", {
        "path": request.url.path
    })
    
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error": True,
            "message": "Token de autenticação inválido ou expirado",
            "error_code": "invalid_token",
            "details": {
                "error_type": exc.__class__.__name__
            }
        },
        headers={"WWW-Authenticate": "Bearer"}
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler para exceções não tratadas
    
    Args:
        request: Objeto Request do FastAPI
        exc: Exceção genérica
        
    Returns:
        JSONResponse com detalhes do erro
    """
    # Registrar erro no log
    logger.critical(f"Erro não tratado: {str(exc)}", {
        "path": request.url.path,
        "error_type": exc.__class__.__name__
    }, exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "Erro interno do servidor",
            "error_code": "internal_server_error",
            "details": {
                "error_type": exc.__class__.__name__
            }
        }
    )


# Função para configurar todos os handlers de exceção na aplicação FastAPI
def configure_exception_handlers(app):
    """
    Configura todos os handlers de exceção na aplicação FastAPI
    
    Args:
        app: Instância da aplicação FastAPI
    """
    # Handlers para exceções personalizadas
    app.add_exception_handler(AutocredError, autocred_exception_handler)
    
    # Handlers para exceções do FastAPI
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # Handlers para exceções do SQLAlchemy
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    
    # Handlers para exceções de JWT
    app.add_exception_handler(JWTError, jwt_exception_handler)
    
    # Handler para exceções não tratadas
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Handlers de exceção configurados")


# Decorador para tratamento de erros em funções
def handle_errors(
    default_message: str = "Ocorreu um erro ao processar a solicitação",
    log_level: str = "error"
):
    """
    Decorador para tratamento de erros em funções
    
    Args:
        default_message: Mensagem padrão para erros não tratados
        log_level: Nível de log para erros (error, critical)
        
    Returns:
        Decorador configurado
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except AutocredError:
                # Exceções personalizadas já têm tratamento adequado
                raise
            except SQLAlchemyError as e:
                # Converter para DatabaseError
                log_method = getattr(logger, log_level)
                log_method(f"Erro de banco de dados em {func.__name__}: {str(e)}", exc_info=True)
                raise DatabaseError(
                    message="Erro ao acessar o banco de dados",
                    details={"function": func.__name__}
                )
            except Exception as e:
                # Registrar erro não tratado
                logger.critical(f"Erro não tratado em {func.__name__}: {str(e)}", exc_info=True)
                raise AutocredError(
                    message=default_message,
                    details={"function": func.__name__}
                )
        return wrapper
    return decorator
