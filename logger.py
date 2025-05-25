"""
Autocred - Sistema de Gestão de Leads para Correspondentes Bancários
Módulo de logs estruturados

Este módulo implementa um sistema de logs estruturados para facilitar
o diagnóstico e monitoramento da aplicação em produção.
"""

import logging
import json
import os
import sys
import time
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, Union

# Configuração básica do logger
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")  # 'json' ou 'text'
LOG_FILE = os.getenv("LOG_FILE", "")  # Se vazio, logs vão para stdout

# Mapeamento de níveis de log
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

# Criar logger raiz
logger = logging.getLogger("autocred")
logger.setLevel(LOG_LEVELS.get(LOG_LEVEL, logging.INFO))

# Remover handlers existentes para evitar duplicação
if logger.handlers:
    logger.handlers.clear()

# Configurar handler baseado nas variáveis de ambiente
if LOG_FILE:
    handler = logging.FileHandler(LOG_FILE)
else:
    handler = logging.StreamHandler(sys.stdout)

# Classe de formatador personalizado para logs JSON
class JsonFormatter(logging.Formatter):
    """
    Formatador personalizado para logs em formato JSON
    """
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Adicionar exceção se existir
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
            
        # Adicionar dados extras
        if hasattr(record, "data") and record.data:
            log_data["data"] = record.data
            
        return json.dumps(log_data)

# Classe de formatador para logs em texto
class TextFormatter(logging.Formatter):
    """
    Formatador personalizado para logs em formato texto
    """
    def format(self, record):
        log_message = f"[{datetime.utcnow().isoformat()}] {record.levelname} - {record.getMessage()} "
        log_message += f"({record.module}.{record.funcName}:{record.lineno})"
        
        # Adicionar dados extras
        if hasattr(record, "data") and record.data:
            log_message += f" - Data: {json.dumps(record.data)}"
            
        # Adicionar exceção se existir
        if record.exc_info:
            log_message += f"\nException: {record.exc_info[0].__name__}: {str(record.exc_info[1])}"
            log_message += f"\nTraceback: {''.join(traceback.format_exception(*record.exc_info))}"
            
        return log_message

# Configurar formatador baseado na variável de ambiente
if LOG_FORMAT.lower() == "json":
    formatter = JsonFormatter()
else:
    formatter = TextFormatter()

handler.setFormatter(formatter)
logger.addHandler(handler)


# Função para adicionar dados extras ao log
def log_with_data(level: str, message: str, data: Optional[Dict[str, Any]] = None, exc_info=None):
    """
    Registra uma mensagem de log com dados extras
    
    Args:
        level: Nível do log (debug, info, warning, error, critical)
        message: Mensagem do log
        data: Dados extras para incluir no log
        exc_info: Informações de exceção
    """
    log_method = getattr(logger, level.lower())
    
    # Criar um LogRecord personalizado
    extra = {"data": data} if data else {}
    log_method(message, extra=extra, exc_info=exc_info)


# Funções de conveniência para diferentes níveis de log
def debug(message: str, data: Optional[Dict[str, Any]] = None):
    """Log de nível DEBUG com dados opcionais"""
    log_with_data("debug", message, data)


def info(message: str, data: Optional[Dict[str, Any]] = None):
    """Log de nível INFO com dados opcionais"""
    log_with_data("info", message, data)


def warning(message: str, data: Optional[Dict[str, Any]] = None):
    """Log de nível WARNING com dados opcionais"""
    log_with_data("warning", message, data)


def error(message: str, data: Optional[Dict[str, Any]] = None, exc_info=None):
    """Log de nível ERROR com dados opcionais e informações de exceção"""
    log_with_data("error", message, data, exc_info)


def critical(message: str, data: Optional[Dict[str, Any]] = None, exc_info=None):
    """Log de nível CRITICAL com dados opcionais e informações de exceção"""
    log_with_data("critical", message, data, exc_info)


# Decorador para logging de funções
def log_function(level: str = "info"):
    """
    Decorador para registrar entrada e saída de funções
    
    Args:
        level: Nível do log (debug, info, warning, error)
        
    Returns:
        Decorador configurado
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            function_name = func.__name__
            module_name = func.__module__
            
            # Log de entrada na função
            log_with_data(level, f"Iniciando {module_name}.{function_name}", {
                "args_count": len(args),
                "kwargs": list(kwargs.keys())
            })
            
            start_time = time.time()
            try:
                # Executar a função
                result = func(*args, **kwargs)
                
                # Log de saída bem-sucedida
                execution_time = time.time() - start_time
                log_with_data(level, f"Concluído {module_name}.{function_name}", {
                    "execution_time_ms": round(execution_time * 1000),
                    "success": True
                })
                
                return result
            except Exception as e:
                # Log de erro
                execution_time = time.time() - start_time
                log_with_data("error", f"Erro em {module_name}.{function_name}: {str(e)}", {
                    "execution_time_ms": round(execution_time * 1000),
                    "success": False,
                    "error_type": e.__class__.__name__
                }, exc_info=True)
                
                # Re-lançar a exceção
                raise
                
        return wrapper
    return decorator


# Middleware para logging de requisições FastAPI
class RequestLoggingMiddleware:
    """
    Middleware para logging de requisições HTTP
    """
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
            
        # Extrair informações da requisição
        method = scope.get("method", "")
        path = scope.get("path", "")
        query_string = scope.get("query_string", b"").decode("utf-8")
        client = scope.get("client", ("", 0))
        
        # Log de início da requisição
        request_id = f"{int(time.time() * 1000)}-{os.urandom(4).hex()}"
        start_time = time.time()
        
        info(f"Requisição iniciada: {method} {path}", {
            "request_id": request_id,
            "method": method,
            "path": path,
            "query": query_string,
            "client_ip": client[0] if client else None
        })
        
        # Processar a requisição
        try:
            await self.app(scope, receive, send)
            
            # Log de conclusão da requisição
            execution_time = time.time() - start_time
            info(f"Requisição concluída: {method} {path}", {
                "request_id": request_id,
                "execution_time_ms": round(execution_time * 1000)
            })
        except Exception as e:
            # Log de erro na requisição
            execution_time = time.time() - start_time
            error(f"Erro na requisição: {method} {path} - {str(e)}", {
                "request_id": request_id,
                "execution_time_ms": round(execution_time * 1000)
            }, exc_info=True)
            
            # Re-lançar a exceção
            raise


# Inicialização do módulo
info("Sistema de logs estruturados inicializado", {
    "log_level": LOG_LEVEL,
    "log_format": LOG_FORMAT,
    "log_file": LOG_FILE or "stdout"
})
