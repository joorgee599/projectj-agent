import logging
from typing import Optional, Union, List, Dict

from langchain_core.tools import tool

from app.services.java_api_client import api_get

logger = logging.getLogger(__name__)


@tool
async def search_products(query: Optional[str] = None) -> Union[List[Dict], Dict]:
    """Busca productos en el catálogo. Puede filtrar por nombre, descripción, categoría o marca.

    Args:
        query: Término de búsqueda opcional para filtrar productos.
    """
    try:
        data = await api_get("/v1/products/all")
        products = data.get("data", [])

        if query:
            q = query.lower()
            products = [
                p
                for p in products
                if q in str(p.get("name", "")).lower()
                or q in str(p.get("description", "")).lower()
                or q in str(p.get("categoryName", "")).lower()
                or q in str(p.get("brandName", "")).lower()
            ]

        logger.info(f"search_products: {len(products)} results for query='{query}'")
        return products

    except Exception as e:
        logger.error(f"search_products error: {e}")
        return {"error": f"Error al buscar productos: {str(e)}"}


@tool
async def get_categories() -> Union[List[Dict], Dict]:
    """Obtiene todas las categorías de productos disponibles en la tienda.
    Útil para ayudar al usuario a navegar por el catálogo.
    """
    try:
        data = await api_get("/v1/categories/all")
        return data.get("data", [])
    except Exception as e:
        logger.error(f"get_categories error: {e}")
        return {"error": f"Error al obtener categorías: {str(e)}"}


@tool
async def get_brands() -> Union[List[Dict], Dict]:
    """Obtiene todas las marcas de productos disponibles en la tienda.
    Útil para filtrar o buscar por fabricante.
    """
    try:
        data = await api_get("/v1/brands/all")
        return data.get("data", [])
    except Exception as e:
        logger.error(f"get_brands error: {e}")
        return {"error": f"Error al obtener marcas: {str(e)}"}


@tool
async def get_product_details(product_id: int) -> dict:
    """Obtiene información detallada de un producto específico por su ID.

    Args:
        product_id: El ID del producto a consultar.
    """
    try:
        data = await api_get(f"/v1/products/{product_id}")
        logger.info(f"get_product_details: product_id={product_id}")
        return data.get("data", data)

    except Exception as e:
        logger.error(f"get_product_details error: {e}")
        return {"error": f"Error al obtener el producto: {str(e)}"}


@tool
async def get_low_stock_products() -> Union[List[Dict], Dict]:
    """Obtiene productos con stock bajo (stock actual menor o igual al stock mínimo).
    Útil para el vendedor como alerta de productos que necesitan reabastecimiento.
    Muestra nombre, stock actual, stock mínimo y stock máximo.
    """
    try:
        data = await api_get("/v1/products/all")
        products = data.get("data", [])

        low_stock = [
            {
                "id": p.get("id"),
                "name": p.get("name"),
                "stock": p.get("stock", 0),
                "minStock": p.get("minStock", 0),
                "maxStock": p.get("maxStock", 0),
                "categoryName": p.get("categoryName"),
                "brandName": p.get("brandName"),
                "price": p.get("price"),
            }
            for p in products
            if p.get("minStock") is not None
            and p.get("stock") is not None
            and p.get("stock") <= p.get("minStock")
            and p.get("status") == 1
        ]

        logger.info(f"get_low_stock_products: {len(low_stock)} products with low stock")
        return low_stock if low_stock else {"message": "No hay productos con stock bajo. ¡Todo en orden!"}
    except Exception as e:
        logger.error(f"get_low_stock_products error: {e}")
        return {"error": f"Error al obtener productos con stock bajo: {str(e)}"}
