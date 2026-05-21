import logging

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

from app.services.java_api_client import api_get, api_post, api_patch, api_delete
from app.tools.auth_utils import extract_auth, handle_api_error

logger = logging.getLogger(__name__)


@tool
async def get_cart(config: RunnableConfig) -> dict:
    """Obtiene el carrito de compras actual del cliente autenticado.
    Muestra los productos, cantidades y el total acumulado.
    """
    auth = extract_auth(config)
    if not auth.is_authenticated or not auth.has_client:
        return {"error": "Se requiere autenticación para acceder al carrito."}
    try:
        data = await api_get(
            "/v1/sales/cart/current",
            token=auth.token,
            params={"clientId": auth.client_id},
        )
        logger.info(f"get_cart: client_id={auth.client_id}")
        return data.get("data") if data.get("data") else {"message": "No tienes un carrito activo actualmente."}
    except Exception as e:
        return handle_api_error(e, "obtener el carrito")


@tool
async def checkout_cart(config: RunnableConfig) -> dict:
    """Confirma el carrito de compras actual y finaliza la compra (Checkout).
    Esto convierte el carrito en un pedido confirmado y descuenta el stock.
    Debe llamarse cuando el usuario quiera 'pagar' o 'finalizar' su compra.
    """
    auth = extract_auth(config)
    if not auth.is_authenticated or not auth.has_client:
        return {"error": "Se requiere autenticación para finalizar la compra."}
    try:
        cart_data = await api_get("/v1/sales/cart/current", token=auth.token, params={"clientId": auth.client_id})
        cart = cart_data.get("data")
        if not cart:
            return {"error": "No tienes un carrito activo para finalizar."}

        sale_id = cart.get("id")
        if not cart.get("details"):
            return {"error": "Tu carrito está vacío. Agrega productos antes de finalizar la compra."}

        result = await api_patch(f"/v1/sales/{sale_id}/confirm", token=auth.token, data={})
        logger.info(f"checkout_cart: sale_confirmed={sale_id}")
        return {"message": "Compra finalizada con éxito. ¡Gracias por tu pedido!", "order_details": result.get("data", result)}
    except Exception as e:
        return handle_api_error(e, "finalizar la compra")


@tool
async def get_my_orders(config: RunnableConfig) -> dict:
    """Obtiene el historial de compras y pedidos anteriores del cliente.
    Muestra pedidos confirmados, entregados o cancelados.
    """
    auth = extract_auth(config)
    if not auth.is_authenticated or not auth.has_client:
        return {"error": "Se requiere autenticación para ver tu historial."}
    try:
        data = await api_get(f"/v1/sales/client/{auth.client_id}", token=auth.token)
        orders = data.get("data", [])

        completed_orders = [o for o in orders if o.get("status") != "PENDING"]
        completed_orders.sort(key=lambda x: x.get("createdAt", ""), reverse=True)

        return {"orders": completed_orders if completed_orders else "No tienes pedidos anteriores."}
    except Exception as e:
        return handle_api_error(e, "obtener el historial de pedidos")


@tool
async def add_to_cart(product_id: int, quantity: int, config: RunnableConfig) -> dict:
    """Agrega un producto al carrito de compras del cliente.

    Args:
        product_id: ID del producto a agregar.
        quantity: Cantidad a agregar (mínimo 1).
    """
    auth = extract_auth(config)
    if not auth.is_authenticated or not auth.has_client:
        return {"error": "Se requiere autenticación para modificar el carrito."}
    try:
        cart_data = await api_get(
            "/v1/sales/cart",
            token=auth.token,
            params={"clientId": auth.client_id, "userId": auth.user_id},
        )
        cart = cart_data.get("data", cart_data)
        sale_id = cart.get("id")

        if not sale_id:
            return {"error": "No se pudo obtener o crear el carrito."}

        result = await api_post(
            f"/v1/sales/{sale_id}/items",
            data={"productId": product_id, "quantity": quantity},
            token=auth.token,
        )
        logger.info(f"add_to_cart: product={product_id}, qty={quantity}, sale={sale_id}")
        return result.get("data", result)
    except Exception as e:
        return handle_api_error(e, "agregar al carrito")


@tool
async def update_cart_item(
    sale_id: int, detail_id: int, quantity: int, config: RunnableConfig
) -> dict:
    """Actualiza la cantidad de un producto en el carrito.

    Args:
        sale_id: ID de la venta/carrito.
        detail_id: ID del detalle/línea del producto en el carrito.
        quantity: Nueva cantidad deseada.
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación para modificar el carrito."}
    try:
        result = await api_patch(
            f"/v1/sales/{sale_id}/items/{detail_id}",
            token=auth.token,
            params={"quantity": quantity},
        )
        logger.info(f"update_cart_item: sale={sale_id}, detail={detail_id}, qty={quantity}")
        return result.get("data", result)
    except Exception as e:
        return handle_api_error(e, "actualizar el carrito")


@tool
async def remove_cart_item(sale_id: int, detail_id: int, config: RunnableConfig) -> dict:
    """Elimina un producto del carrito de compras.

    Args:
        sale_id: ID de la venta/carrito.
        detail_id: ID del detalle/línea del producto a eliminar.
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación para modificar el carrito."}
    try:
        result = await api_delete(
            f"/v1/sales/{sale_id}/items/{detail_id}", token=auth.token
        )
        logger.info(f"remove_cart_item: sale={sale_id}, detail={detail_id}")
        return result.get("data", result)
    except Exception as e:
        return handle_api_error(e, "eliminar del carrito")
