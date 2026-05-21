import logging
from typing import Optional, Dict

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

from app.services.java_api_client import api_get
from app.tools.auth_utils import extract_auth, handle_api_error

logger = logging.getLogger(__name__)


@tool
async def get_dashboard(
    config: RunnableConfig,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
) -> Dict:
    """Obtiene el dashboard principal con los KPIs de la empresa (Ventas, Inventario, Mejores Clientes y Mejores Productos).
    
    Args:
        from_date: Fecha de inicio opcional en formato YYYY-MM-DD (ej: 2026-01-01). Por defecto desde inicio de año.
        to_date: Fecha de fin opcional en formato YYYY-MM-DD (ej: 2026-12-31). Por defecto hasta hoy.
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación para ver el dashboard."}
    
    try:
        params = {}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
            
        data = await api_get("/v1/reports/dashboard", token=auth.token, params=params)
        logger.info(f"get_dashboard retrieved (from={from_date}, to={to_date})")
        return data.get("data", data)
    except Exception as e:
        return handle_api_error(e, "obtener dashboard")


@tool
async def get_sales_summary(
    config: RunnableConfig,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
) -> Dict:
    """Obtiene un resumen de ventas (total de ingresos, ticket promedio y cantidad de ventas por estado).
    
    Args:
        from_date: Fecha de inicio opcional en formato YYYY-MM-DD (ej: 2026-01-01).
        to_date: Fecha de fin opcional en formato YYYY-MM-DD (ej: 2026-12-31).
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación para ver el resumen de ventas."}
    
    try:
        params = {}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
            
        data = await api_get("/v1/reports/sales-summary", token=auth.token, params=params)
        logger.info(f"get_sales_summary retrieved")
        return data.get("data", data)
    except Exception as e:
        return handle_api_error(e, "obtener resumen de ventas")


@tool
async def get_revenue_over_time(
    period: str,
    config: RunnableConfig,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
) -> Dict:
    """Obtiene los ingresos a lo largo del tiempo para generar gráficos.
    
    Args:
        period: El periodo de agrupación. Opciones válidas: 'DAILY', 'WEEKLY', 'MONTHLY'.
        from_date: Fecha de inicio opcional en formato YYYY-MM-DD.
        to_date: Fecha de fin opcional en formato YYYY-MM-DD.
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación para ver los ingresos a lo largo del tiempo."}
    
    try:
        params = {"period": period.upper()}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
            
        data = await api_get("/v1/reports/revenue-over-time", token=auth.token, params=params)
        logger.info(f"get_revenue_over_time retrieved for period={period}")
        return data.get("data", data)
    except Exception as e:
        return handle_api_error(e, "obtener ingresos en el tiempo")
