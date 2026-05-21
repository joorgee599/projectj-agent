"""Shared authentication utilities for all tool modules."""

import logging
from dataclasses import dataclass
from typing import Optional

import httpx
from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__name__)


@dataclass
class AuthContext:
    """Holds authentication context extracted from RunnableConfig."""
    token: Optional[str]
    client_id: Optional[int]
    user_id: Optional[int]

    @property
    def is_authenticated(self) -> bool:
        return bool(self.token)

    @property
    def has_client(self) -> bool:
        return bool(self.client_id)


def extract_auth(config: RunnableConfig) -> AuthContext:
    """Extracts token, client_id and user_id from RunnableConfig."""
    cfg = config.get("configurable", {})
    return AuthContext(
        token=cfg.get("auth_token"),
        client_id=cfg.get("client_id"),
        user_id=cfg.get("user_id"),
    )


def handle_api_error(e: Exception, action: str) -> dict:
    """Standardized error handling for all tools.

    Returns a user-friendly error dict based on exception type.
    """
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        if status == 404:
            return {"error": f"No se encontró el recurso solicitado al {action}."}
        elif status in (401, 403):
            return {"error": f"No tienes permisos para {action}. ¿Sesión expirada?"}
        elif status == 400:
            # Try to extract the backend's error message
            try:
                body = e.response.json()
                msg = body.get("message", str(e))
            except Exception:
                msg = str(e)
            return {"error": f"Datos inválidos al {action}: {msg}"}
        else:
            return {"error": f"Error del servidor (HTTP {status}) al {action}."}
    elif isinstance(e, httpx.TimeoutException):
        return {"error": f"El servidor tardó demasiado al {action}. Intenta de nuevo."}
    else:
        logger.error(f"{action} error: {e}")
        return {"error": f"Error al {action}: {str(e)}"}
