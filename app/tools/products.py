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
        data = await api_get("/v1/products")
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
