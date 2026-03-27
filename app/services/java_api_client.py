import httpx
import logging
from typing import Optional

from app.config.config import settings

logger = logging.getLogger(__name__)

_BASE_URL = settings.API_URL_SERVER.strip().rstrip("/")
_TIMEOUT = 15.0


def _build_headers(token: Optional[str] = None) -> dict:
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


async def api_get(
    endpoint: str,
    token: Optional[str] = None,
    params: Optional[dict] = None,
) -> dict:
    url = f"{_BASE_URL}{endpoint}"
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.get(url, headers=_build_headers(token), params=params)
        resp.raise_for_status()
        return resp.json()


async def api_post(
    endpoint: str,
    data: dict,
    token: Optional[str] = None,
) -> dict:
    url = f"{_BASE_URL}{endpoint}"
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(url, json=data, headers=_build_headers(token))
        resp.raise_for_status()
        return resp.json()


async def api_patch(
    endpoint: str,
    token: Optional[str] = None,
    data: Optional[dict] = None,
    params: Optional[dict] = None,
) -> dict:
    url = f"{_BASE_URL}{endpoint}"
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.patch(
            url, json=data, headers=_build_headers(token), params=params
        )
        resp.raise_for_status()
        return resp.json()


async def api_delete(
    endpoint: str,
    token: Optional[str] = None,
) -> dict:
    url = f"{_BASE_URL}{endpoint}"
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.delete(url, headers=_build_headers(token))
        resp.raise_for_status()
        return resp.json()


async def resolve_client(token: str, email: str) -> Optional[dict]:
    """Resolves client_id and user_id by matching email in /api/v1/clients."""
    try:
        data = await api_get("/v1/clients", token=token)
        clients = data.get("data", [])
        for client in clients:
            if client.get("email", "").lower() == email.lower():
                return {
                    "client_id": client.get("id"),
                    "user_id": client.get("userId"),
                }
        logger.warning(f"No client found for email: {email}")
        return None
    except Exception as e:
        logger.error(f"resolve_client error: {e}")
        return None
