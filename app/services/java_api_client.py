import httpx
import logging
import asyncio
from typing import Optional, Dict, Any
from cachetools import TTLCache

from app.config.config import settings

logger = logging.getLogger(__name__)

_BASE_URL = settings.API_URL_SERVER.strip().rstrip("/")
_TIMEOUT = 15.0

# Singleton Client for connection pooling
_client: Optional[httpx.AsyncClient] = None
# Cache for client resolution (email -> {client_id, user_id})
# TTL of 5 minutes to avoid stale data while reducing API calls
_client_cache = TTLCache(maxsize=100, ttl=300)

async def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            base_url=_BASE_URL,
            timeout=_TIMEOUT,
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            headers={"Accept": "application/json"}
        )
    return _client

def _build_headers(token: Optional[str] = None) -> dict:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

async def _request(method: str, endpoint: str, **kwargs) -> dict:
    client = await get_client()
    headers = kwargs.pop("headers", {})
    token = kwargs.pop("token", None)
    headers.update(_build_headers(token))
    
    try:
        resp = await client.request(method, endpoint, headers=headers, **kwargs)
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error {e.response.status_code} for {method} {endpoint}: {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"Request error for {method} {endpoint}: {e}")
        raise

async def api_get(endpoint: str, token: Optional[str] = None, params: Optional[dict] = None) -> dict:
    return await _request("GET", endpoint, token=token, params=params)

async def api_post(endpoint: str, data: dict, token: Optional[str] = None) -> dict:
    return await _request("POST", endpoint, json=data, token=token)

async def api_patch(endpoint: str, token: Optional[str] = None, data: Optional[dict] = None, params: Optional[dict] = None) -> dict:
    return await _request("PATCH", endpoint, json=data, token=token, params=params)

async def api_delete(endpoint: str, token: Optional[str] = None) -> dict:
    return await _request("DELETE", endpoint, token=token)

async def resolve_client(token: str, email: str) -> Optional[dict]:
    """Resolves client_id and user_id using the dedicated /api/v1/clients/by-email endpoint."""
    if email in _client_cache:
        return _client_cache[email]
        
    try:
        data = await api_get("/v1/clients/by-email", token=token, params={"email": email})
        client = data.get("data")
        if client:
            result = {
                "client_id": client.get("id"),
                "user_id": client.get("userId"),
            }
            _client_cache[email] = result
            return result
            
        logger.warning(f"No client found for email: {email}")
        return None
    except Exception as e:
        logger.error(f"resolve_client error: {e}")
        return None
