import logging

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

from app.services.java_api_client import api_get, api_post, api_patch, api_delete

logger = logging.getLogger(__name__)


def _auth(config: RunnableConfig) -> tuple:
    """Extracts token, client_id and user_id from RunnableConfig."""
    cfg = config.get("configurable", {})
    return cfg.get("auth_token"), cfg.get("client_id"), cfg.get("user_id")


@tool
async def get_cart(config: RunnableConfig) -> dict:
    """Obtiene el carrito de compras actual del cliente autenticado con todos sus productos."""
    token, client_id, user_id = _auth(config)
    if not token or not client_id:
        return {"error": "Se requiere autenticación para acceder al carrito."}
    try:
        data = await api_get(
            "/v1/sales/cart",
            token=token,
            params={"clientId": client_id, "userId": user_id},
        )
        logger.info(f"get_cart: client_id={client_id}")
        return data.get("data", data)
    except Exception as e:
        logger.error(f"get_cart error: {e}")
        return {"error": f"Error al obtener el carrito: {str(e)}"}


@tool
async def add_to_cart(product_id: int, quantity: int, config: RunnableConfig) -> dict:
    """Agrega un producto al carrito de compras del cliente.

    Args:
        product_id: ID del producto a agregar.
        quantity: Cantidad a agregar (mínimo 1).
    """
    token, client_id, user_id = _auth(config)
    if not token or not client_id:
        return {"error": "Se requiere autenticación para modificar el carrito."}
    try:
        # Get or create cart
        cart_data = await api_get(
            "/v1/sales/cart",
            token=token,
            params={"clientId": client_id, "userId": user_id},
        )
        cart = cart_data.get("data", cart_data)
        sale_id = cart.get("id")

        if not sale_id:
            return {"error": "No se pudo obtener o crear el carrito."}

        # Add item to cart
        result = await api_post(
            f"/v1/sales/{sale_id}/items",
            data={"productId": product_id, "quantity": quantity},
            token=token,
        )
        logger.info(f"add_to_cart: product={product_id}, qty={quantity}, sale={sale_id}")
        return result.get("data", result)

    except Exception as e:
        logger.error(f"add_to_cart error: {e}")
        return {"error": f"Error al agregar al carrito: {str(e)}"}


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
    token, _, _ = _auth(config)
    if not token:
        return {"error": "Se requiere autenticación para modificar el carrito."}
    try:
        result = await api_patch(
            f"/v1/sales/{sale_id}/items/{detail_id}",
            token=token,
            params={"quantity": quantity},
        )
        logger.info(f"update_cart_item: sale={sale_id}, detail={detail_id}, qty={quantity}")
        return result.get("data", result)
    except Exception as e:
        logger.error(f"update_cart_item error: {e}")
        return {"error": f"Error al actualizar el carrito: {str(e)}"}


@tool
async def remove_cart_item(sale_id: int, detail_id: int, config: RunnableConfig) -> dict:
    """Elimina un producto del carrito de compras.

    Args:
        sale_id: ID de la venta/carrito.
        detail_id: ID del detalle/línea del producto a eliminar.
    """
    token, _, _ = _auth(config)
    if not token:
        return {"error": "Se requiere autenticación para modificar el carrito."}
    try:
        result = await api_delete(
            f"/v1/sales/{sale_id}/items/{detail_id}", token=token
        )
        logger.info(f"remove_cart_item: sale={sale_id}, detail={detail_id}")
        return result.get("data", result)
    except Exception as e:
        logger.error(f"remove_cart_item error: {e}")
        return {"error": f"Error al eliminar del carrito: {str(e)}"}
