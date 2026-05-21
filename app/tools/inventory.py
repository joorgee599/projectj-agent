import logging
from typing import Optional, Union, List, Dict

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

from app.services.java_api_client import api_get, api_patch, api_post
from app.tools.auth_utils import extract_auth, handle_api_error

logger = logging.getLogger(__name__)


@tool
async def get_inventory_movements(
    limit: Optional[int] = 50, config: RunnableConfig = None
) -> Union[List[Dict], Dict]:
    """Obtiene los movimientos de inventario más recientes.

    Args:
        limit: Cantidad máxima de movimientos a obtener (por defecto 50).
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación para ver movimientos de inventario."}
    try:
        # Use paginated endpoint (already sorted by ID DESC server-side)
        size = min(limit or 50, 100)
        data = await api_get("/v1/inventories", token=auth.token, params={"page": 0, "size": size})
        movements = data.get("data", [])

        logger.info(f"get_inventory_movements: {len(movements)} movements retrieved (page=0, size={size})")
        return movements
    except Exception as e:
        return handle_api_error(e, "obtener movimientos de inventario")


@tool
async def create_inventory_movement(
    product_ids: str,
    quantities: str,
    movement_types: str,
    config: RunnableConfig,
    description: Optional[str] = None,
    unit_costs: Optional[str] = None,
) -> Dict:
    """Crea un nuevo movimiento de inventario para registrar entradas, salidas o ajustes de stock.

    Args:
        product_ids: IDs de productos separados por comas. Ejemplo: "1,2,3"
        quantities: Cantidades separadas por comas. Ejemplo: "50,20,10"
        movement_types: Tipo de movimiento por producto separado por comas. Valores: ENTRADA, SALIDA, AJUSTE. Ejemplo: "ENTRADA,ENTRADA,AJUSTE"
        description: Descripción opcional del movimiento (ej: "Reabastecimiento semanal")
        unit_costs: Costos unitarios separados por comas (opcional). Ejemplo: "15.50,20.00,0"
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación para crear movimientos de inventario."}
    if not auth.user_id:
        return {"error": "No se pudo determinar el ID del usuario."}
    if not product_ids or not quantities or not movement_types:
        return {"error": "Debe especificar product_ids, quantities y movement_types."}

    valid_types = {"ENTRADA", "SALIDA", "AJUSTE"}

    try:
        prod_list = [int(x.strip()) for x in product_ids.split(",") if x.strip()]
        qty_list = [int(x.strip()) for x in quantities.split(",") if x.strip()]
        type_list = [x.strip().upper() for x in movement_types.split(",") if x.strip()]
    except ValueError:
        return {"error": "product_ids y quantities deben ser números separados por comas."}

    if len(prod_list) != len(qty_list) or len(prod_list) != len(type_list):
        return {"error": f"product_ids ({len(prod_list)}), quantities ({len(qty_list)}) y movement_types ({len(type_list)}) deben tener la misma cantidad de elementos."}
    if len(prod_list) == 0:
        return {"error": "Debe especificar al menos un producto."}
    if any(qty < 1 for qty in qty_list):
        return {"error": "Todas las cantidades deben ser >= 1."}
    if any(t not in valid_types for t in type_list):
        invalid = [t for t in type_list if t not in valid_types]
        return {"error": f"Tipos de movimiento inválidos: {invalid}. Use: ENTRADA, SALIDA o AJUSTE."}

    # Parse optional unit costs
    cost_list = None
    if unit_costs:
        try:
            cost_list = [float(x.strip()) for x in unit_costs.split(",") if x.strip()]
            if len(cost_list) != len(prod_list):
                return {"error": f"unit_costs ({len(cost_list)}) debe tener la misma cantidad que product_ids ({len(prod_list)})."}
        except ValueError:
            return {"error": "unit_costs deben ser números separados por comas."}

    try:
        details = []
        for i, (prod_id, qty, mov_type) in enumerate(zip(prod_list, qty_list, type_list)):
            detail = {
                "productId": prod_id,
                "quantity": qty,
                "type": mov_type,
            }
            if cost_list and cost_list[i] > 0:
                detail["unitCost"] = cost_list[i]
            details.append(detail)

        inventory_data = {
            "userId": auth.user_id,
            "details": details,
        }
        if description:
            inventory_data["description"] = description

        data = await api_post("/v1/inventories", inventory_data, token=auth.token)
        logger.info(f"create_inventory_movement: {len(details)} details created")
        return data.get("data", data)
    except Exception as e:
        return handle_api_error(e, "crear movimiento de inventario")


@tool
async def confirm_inventory_movement(movement_id: int, config: RunnableConfig) -> Dict:
    """Confirma un movimiento de inventario y aplica los cambios de stock.
    - ENTRADA: Suma stock al producto.
    - SALIDA: Resta stock del producto.
    - AJUSTE: Ajusta el stock según la cantidad.

    Args:
        movement_id: ID del movimiento de inventario a confirmar.
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación para confirmar movimientos de inventario."}
    try:
        data = await api_patch(f"/v1/inventories/{movement_id}/confirm", token=auth.token, data={})
        logger.info(f"confirm_inventory_movement: movement_id={movement_id} confirmed")
        return data.get("data", data)
    except Exception as e:
        return handle_api_error(e, "confirmar movimiento de inventario")


@tool
async def cancel_inventory_movement(movement_id: int, config: RunnableConfig) -> Dict:
    """Cancela un movimiento de inventario y revierte los cambios de stock si ya estaba confirmado.

    Args:
        movement_id: ID del movimiento de inventario a cancelar.
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación para cancelar movimientos de inventario."}
    try:
        data = await api_patch(f"/v1/inventories/{movement_id}/cancel", token=auth.token, data={})
        logger.info(f"cancel_inventory_movement: movement_id={movement_id} cancelled")
        return data.get("data", data)
    except Exception as e:
        return handle_api_error(e, "cancelar movimiento de inventario")


@tool
async def search_providers(query: Optional[str] = None, config: RunnableConfig = None) -> Union[List[Dict], Dict]:
    """Busca proveedores por nombre, email o teléfono.
    Útil para encontrar el proveedor al registrar entradas de mercancía en el inventario.

    Args:
        query: Término de búsqueda opcional (nombre, email o teléfono del proveedor).
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación para buscar proveedores."}
    try:
        data = await api_get("/v1/providers/all", token=auth.token)
        providers = data.get("data", [])

        if query:
            q = query.lower()
            providers = [
                p for p in providers
                if q in str(p.get("name", "")).lower()
                or q in str(p.get("email", "")).lower()
                or q in str(p.get("phone", "")).lower()
            ]

        logger.info(f"search_providers: {len(providers)} results for query='{query}'")
        return providers
    except Exception as e:
        return handle_api_error(e, "buscar proveedores")

