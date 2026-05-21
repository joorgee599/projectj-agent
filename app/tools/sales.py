import logging
from typing import Optional, Union, List, Dict

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

from app.services.java_api_client import api_get, api_patch, api_post
from app.tools.auth_utils import extract_auth, handle_api_error

logger = logging.getLogger(__name__)


@tool
async def get_recent_sales(
    limit: Optional[int] = 50, config: RunnableConfig = None
) -> Union[List[Dict], Dict]:
    """Obtiene las ventas más recientes del sistema para reportes.

    Args:
        limit: Cantidad máxima de ventas a obtener (por defecto 50).
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación para ver ventas."}
    try:
        # Use paginated endpoint (already sorted by ID DESC server-side)
        size = min(limit or 50, 100)
        data = await api_get("/v1/sales", token=auth.token, params={"page": 0, "size": size})
        sales = data.get("data", [])

        logger.info(f"get_recent_sales: {len(sales)} sales retrieved (page=0, size={size})")
        return sales
    except Exception as e:
        return handle_api_error(e, "obtener ventas recientes")


@tool
async def get_sales_by_client(client_id: int, config: RunnableConfig) -> Union[List[Dict], Dict]:
    """Obtiene todas las ventas de un cliente específico.

    Args:
        client_id: ID del cliente.
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación para ver ventas del cliente."}
    try:
        data = await api_get(f"/v1/sales/client/{client_id}", token=auth.token)
        sales = data.get("data", [])

        logger.info(f"get_sales_by_client: {len(sales)} sales for client_id={client_id}")
        return sales
    except Exception as e:
        return handle_api_error(e, "obtener ventas del cliente")


@tool
async def get_sale_details(sale_id: int, config: RunnableConfig) -> Dict:
    """Obtiene los detalles completos de una venta específica, incluyendo
    todos los productos, cantidades, precios unitarios, subtotales y el total.

    Args:
        sale_id: ID de la venta a consultar.
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación para ver detalles de ventas."}
    try:
        data = await api_get(f"/v1/sales/{sale_id}", token=auth.token)
        logger.info(f"get_sale_details: sale_id={sale_id}")
        return data.get("data", data)
    except Exception as e:
        return handle_api_error(e, "obtener detalle de la venta")


@tool
async def search_clients(query: str, config: RunnableConfig) -> Union[List[Dict], Dict]:
    """Busca clientes por nombre o email.
    Útil para encontrar el ID del cliente al crear ventas o consultar su historial.

    Args:
        query: Término de búsqueda (nombre o email del cliente).
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación para buscar clientes."}
    try:
        data = await api_get("/v1/clients/all", token=auth.token)
        clients = data.get("data", [])

        if query:
            q = query.lower()
            clients = [
                c for c in clients
                if q in str(c.get("name", "")).lower()
                or q in str(c.get("email", "")).lower()
                or q in str(c.get("document", "")).lower()
            ]

        logger.info(f"search_clients: {len(clients)} results for query='{query}'")
        return clients
    except Exception as e:
        return handle_api_error(e, "buscar clientes")


@tool
async def create_sale(
    client_id: int,
    product_ids: str,
    quantities: str,
    config: RunnableConfig,
    payment_method: Optional[str] = None,
    description: Optional[str] = None,
) -> Dict:
    """Crea una nueva venta con productos específicos para un cliente.

    Args:
        client_id: ID del cliente para quien se crea la venta.
        product_ids: IDs de productos separados por comas. Ejemplo: "1,2,3"
        quantities: Cantidades separadas por comas. Ejemplo: "2,1,5" (debe coincidir con product_ids)
        payment_method: Método de pago opcional (Efectivo, Tarjeta, etc.)
        description: Descripción opcional de la venta
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación para crear ventas."}
    if not auth.user_id:
        return {"error": "No se pudo determinar el ID del usuario vendedor."}
    if not product_ids or not quantities:
        return {"error": "Debe especificar product_ids y quantities (formato: '1,2,3' y '2,1,5')"}

    try:
        prod_list = [int(x.strip()) for x in product_ids.split(",") if x.strip()]
        qty_list = [int(x.strip()) for x in quantities.split(",") if x.strip()]
    except ValueError:
        return {"error": "product_ids y quantities deben ser números separados por comas."}

    if len(prod_list) != len(qty_list):
        return {"error": f"product_ids tiene {len(prod_list)} elementos pero quantities tiene {len(qty_list)}. Deben coincidir."}
    if len(prod_list) == 0:
        return {"error": "Debe especificar al menos un producto."}
    if any(qty < 1 for qty in qty_list):
        return {"error": "Todas las cantidades deben ser >= 1."}

    try:
        details = [
            {"productId": prod_id, "quantity": qty}
            for prod_id, qty in zip(prod_list, qty_list)
        ]

        sale_data = {
            "clientId": client_id,
            "userId": auth.user_id,
            "details": details,
        }
        if payment_method:
            sale_data["paymentMethod"] = payment_method
        if description:
            sale_data["description"] = description

        data = await api_post("/v1/sales", sale_data, token=auth.token)
        logger.info(f"create_sale: client_id={client_id}, products_count={len(prod_list)}")
        return data.get("data", data)
    except Exception as e:
        return handle_api_error(e, "crear la venta")


@tool
async def confirm_sale(sale_id: int, config: RunnableConfig) -> Dict:
    """Confirma una venta pendiente y descuenta el stock del inventario.

    Args:
        sale_id: ID de la venta a confirmar.
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación para confirmar ventas."}
    try:
        data = await api_patch(f"/v1/sales/{sale_id}/confirm", token=auth.token, data={})
        logger.info(f"confirm_sale: sale_id={sale_id} confirmed")
        return data.get("data", data)
    except Exception as e:
        return handle_api_error(e, "confirmar la venta")


@tool
async def cancel_sale(sale_id: int, config: RunnableConfig) -> Dict:
    """Cancela una venta y restaura el stock si ya estaba confirmada.

    Args:
        sale_id: ID de la venta a cancelar.
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación para cancelar ventas."}
    try:
        data = await api_patch(f"/v1/sales/{sale_id}/cancel", token=auth.token, data={})
        logger.info(f"cancel_sale: sale_id={sale_id} cancelled")
        return data.get("data", data)
    except Exception as e:
        return handle_api_error(e, "cancelar la venta")
