from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from app.utils.custom_exceptions import (
    PlanilhaNaoEncontradaError,
    AbaNaoEncontradaError,
    ColunaNaoEncontradaError,
    ErroLeituraDadosError,
    LLMConnectionError
)

logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: Exception):
    """
    Manipulador genérico para exceções HTTP e outras exceções customizadas.
    """
    status_code = 500
    detail = "Ocorreu um erro interno no servidor."

    if isinstance(exc, (PlanilhaNaoEncontradaError, AbaNaoEncontradaError, ColunaNaoEncontradaError)):
        status_code = 404
        detail = str(exc)
    elif isinstance(exc, (ErroLeituraDadosError, LLMConnectionError)):
        status_code = 502 # Bad Gateway, pois o erro está em um serviço externo
        detail = str(exc)
    else:
        # Para exceções não previstas, logamos o erro completo
        logger.error(f"Erro não tratado: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status_code,
        content={"detail": detail},
    )

def add_exception_handlers(app):
    """
    Adiciona os manipuladores de exceção à aplicação FastAPI.
    """
    app.add_exception_handler(Exception, http_exception_handler)
