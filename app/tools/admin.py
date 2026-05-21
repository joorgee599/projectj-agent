"""Admin-only tools for full system management (CRUD operations)."""

import logging
from typing import Optional, Union, List, Dict

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

from app.services.java_api_client import api_get, api_post, api_patch, api_delete
from app.tools.auth_utils import extract_auth, handle_api_error

logger = logging.getLogger(__name__)


# ─── PRODUCTS CRUD ────────────────────────────────────────────────

@tool
async def create_product(
    name: str,
    price: float,
    category_id: int,
    brand_id: int,
    config: RunnableConfig,
    description: Optional[str] = None,
    code: Optional[str] = None,
    stock: Optional[int] = 0,
    min_stock: Optional[int] = 0,
    max_stock: Optional[int] = 0,
) -> Dict:
    """Crea un nuevo producto en el catálogo.

    Args:
        name: Nombre del producto.
        price: Precio del producto.
        category_id: ID de la categoría.
        brand_id: ID de la marca.
        description: Descripción opcional del producto.
        code: Código opcional del producto (SKU).
        stock: Stock inicial (por defecto 0).
        min_stock: Stock mínimo para alertas (por defecto 0).
        max_stock: Stock máximo (por defecto 0).
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación de administrador."}
    try:
        product_data = {
            "name": name,
            "price": price,
            "categoryId": category_id,
            "brandId": brand_id,
            "stock": stock,
            "minStock": min_stock,
            "maxStock": max_stock,
            "status": 1,
        }
        if description:
            product_data["description"] = description
        if code:
            product_data["code"] = code

        data = await api_post("/v1/products", product_data, token=auth.token)
        logger.info(f"create_product: name={name}")
        return data.get("data", data)
    except Exception as e:
        return handle_api_error(e, "crear producto")


@tool
async def update_product(
    product_id: int,
    config: RunnableConfig,
    name: Optional[str] = None,
    price: Optional[float] = None,
    description: Optional[str] = None,
    category_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    stock: Optional[int] = None,
    min_stock: Optional[int] = None,
    max_stock: Optional[int] = None,
) -> Dict:
    """Actualiza un producto existente. Solo los campos proporcionados serán actualizados.

    Args:
        product_id: ID del producto a actualizar.
        name: Nuevo nombre (opcional).
        price: Nuevo precio (opcional).
        description: Nueva descripción (opcional).
        category_id: Nueva categoría (opcional).
        brand_id: Nueva marca (opcional).
        stock: Nuevo stock (opcional).
        min_stock: Nuevo stock mínimo (opcional).
        max_stock: Nuevo stock máximo (opcional).
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación de administrador."}
    try:
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if price is not None:
            update_data["price"] = price
        if description is not None:
            update_data["description"] = description
        if category_id is not None:
            update_data["categoryId"] = category_id
        if brand_id is not None:
            update_data["brandId"] = brand_id
        if stock is not None:
            update_data["stock"] = stock
        if min_stock is not None:
            update_data["minStock"] = min_stock
        if max_stock is not None:
            update_data["maxStock"] = max_stock

        if not update_data:
            return {"error": "Debe especificar al menos un campo para actualizar."}

        data = await api_patch(f"/v1/products/{product_id}", token=auth.token, data=update_data)
        logger.info(f"update_product: product_id={product_id}")
        return data.get("data", data)
    except Exception as e:
        return handle_api_error(e, "actualizar producto")


@tool
async def update_product_status(product_id: int, status: int, config: RunnableConfig) -> Dict:
    """Activa o desactiva un producto.

    Args:
        product_id: ID del producto.
        status: 1 para activar, 0 para desactivar.
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación de administrador."}
    try:
        data = await api_patch(
            f"/v1/products/{product_id}/status", token=auth.token, params={"status": status}
        )
        logger.info(f"update_product_status: product_id={product_id}, status={status}")
        return data.get("data", data)
    except Exception as e:
        return handle_api_error(e, "cambiar estado del producto")


@tool
async def delete_product(product_id: int, config: RunnableConfig) -> Dict:
    """Elimina un producto del catálogo.

    Args:
        product_id: ID del producto a eliminar.
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación de administrador."}
    try:
        data = await api_delete(f"/v1/products/{product_id}", token=auth.token)
        logger.info(f"delete_product: product_id={product_id}")
        return {"message": "Producto eliminado exitosamente."}
    except Exception as e:
        return handle_api_error(e, "eliminar producto")


# ─── CATEGORIES CRUD ──────────────────────────────────────────────

@tool
async def create_category(name: str, config: RunnableConfig, description: Optional[str] = None) -> Dict:
    """Crea una nueva categoría de productos.

    Args:
        name: Nombre de la categoría.
        description: Descripción opcional.
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación de administrador."}
    try:
        cat_data = {"name": name}
        if description:
            cat_data["description"] = description
        data = await api_post("/v1/categories", cat_data, token=auth.token)
        logger.info(f"create_category: name={name}")
        return data.get("data", data)
    except Exception as e:
        return handle_api_error(e, "crear categoría")


@tool
async def update_category(category_id: int, name: str, config: RunnableConfig, description: Optional[str] = None) -> Dict:
    """Actualiza una categoría existente.

    Args:
        category_id: ID de la categoría.
        name: Nuevo nombre.
        description: Nueva descripción (opcional).
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación de administrador."}
    try:
        cat_data = {"name": name}
        if description:
            cat_data["description"] = description
        data = await api_patch(f"/v1/categories/{category_id}", token=auth.token, data=cat_data)
        logger.info(f"update_category: category_id={category_id}")
        return data.get("data", data)
    except Exception as e:
        return handle_api_error(e, "actualizar categoría")


@tool
async def delete_category(category_id: int, config: RunnableConfig) -> Dict:
    """Elimina una categoría.

    Args:
        category_id: ID de la categoría a eliminar.
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación de administrador."}
    try:
        await api_delete(f"/v1/categories/{category_id}", token=auth.token)
        logger.info(f"delete_category: category_id={category_id}")
        return {"message": "Categoría eliminada exitosamente."}
    except Exception as e:
        return handle_api_error(e, "eliminar categoría")


# ─── BRANDS CRUD ──────────────────────────────────────────────────

@tool
async def create_brand(name: str, config: RunnableConfig, description: Optional[str] = None) -> Dict:
    """Crea una nueva marca de productos.

    Args:
        name: Nombre de la marca.
        description: Descripción opcional.
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación de administrador."}
    try:
        brand_data = {"name": name}
        if description:
            brand_data["description"] = description
        data = await api_post("/v1/brands", brand_data, token=auth.token)
        logger.info(f"create_brand: name={name}")
        return data.get("data", data)
    except Exception as e:
        return handle_api_error(e, "crear marca")


@tool
async def update_brand(brand_id: int, name: str, config: RunnableConfig, description: Optional[str] = None) -> Dict:
    """Actualiza una marca existente.

    Args:
        brand_id: ID de la marca.
        name: Nuevo nombre.
        description: Nueva descripción (opcional).
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación de administrador."}
    try:
        brand_data = {"name": name}
        if description:
            brand_data["description"] = description
        data = await api_patch(f"/v1/brands/{brand_id}", token=auth.token, data=brand_data)
        logger.info(f"update_brand: brand_id={brand_id}")
        return data.get("data", data)
    except Exception as e:
        return handle_api_error(e, "actualizar marca")


@tool
async def delete_brand(brand_id: int, config: RunnableConfig) -> Dict:
    """Elimina una marca.

    Args:
        brand_id: ID de la marca a eliminar.
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación de administrador."}
    try:
        await api_delete(f"/v1/brands/{brand_id}", token=auth.token)
        logger.info(f"delete_brand: brand_id={brand_id}")
        return {"message": "Marca eliminada exitosamente."}
    except Exception as e:
        return handle_api_error(e, "eliminar marca")


# ─── CLIENTS MANAGEMENT ──────────────────────────────────────────

@tool
async def create_client(
    name: str,
    email: str,
    temporary_password: str,
    config: RunnableConfig,
    document: Optional[str] = None,
    phone: Optional[str] = None,
    address: Optional[str] = None,
) -> Dict:
    """Crea un nuevo cliente (también crea automáticamente un usuario vinculado con rol CLIENT).

    Args:
        name: Nombre completo del cliente.
        email: Email del cliente (será su usuario de login).
        temporary_password: Contraseña temporal para el nuevo usuario.
        document: Documento de identidad (opcional).
        phone: Teléfono (opcional).
        address: Dirección (opcional).
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación de administrador."}
    try:
        client_data = {
            "name": name,
            "email": email,
            "temporaryPassword": temporary_password,
        }
        if document:
            client_data["document"] = document
        if phone:
            client_data["phone"] = phone
        if address:
            client_data["address"] = address

        data = await api_post("/v1/clients", client_data, token=auth.token)
        logger.info(f"create_client: email={email}")
        return data.get("data", data)
    except Exception as e:
        return handle_api_error(e, "crear cliente")


@tool
async def update_client_status(client_id: int, status: int, config: RunnableConfig) -> Dict:
    """Activa o desactiva un cliente.

    Args:
        client_id: ID del cliente.
        status: 1 para activar, 0 para desactivar.
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación de administrador."}
    try:
        data = await api_patch(
            f"/v1/clients/{client_id}/status", token=auth.token, params={"status": status}
        )
        logger.info(f"update_client_status: client_id={client_id}, status={status}")
        return data.get("data", data)
    except Exception as e:
        return handle_api_error(e, "cambiar estado del cliente")


# ─── PROVIDERS MANAGEMENT ─────────────────────────────────────────

@tool
async def create_provider(
    name: str, config: RunnableConfig,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    address: Optional[str] = None,
) -> Dict:
    """Crea un nuevo proveedor.

    Args:
        name: Nombre del proveedor.
        email: Email del proveedor (opcional).
        phone: Teléfono del proveedor (opcional).
        address: Dirección del proveedor (opcional).
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación de administrador."}
    try:
        provider_data = {"name": name}
        if email:
            provider_data["email"] = email
        if phone:
            provider_data["phone"] = phone
        if address:
            provider_data["address"] = address

        data = await api_post("/v1/providers", provider_data, token=auth.token)
        logger.info(f"create_provider: name={name}")
        return data.get("data", data)
    except Exception as e:
        return handle_api_error(e, "crear proveedor")


@tool
async def update_provider_status(provider_id: int, status: int, config: RunnableConfig) -> Dict:
    """Activa o desactiva un proveedor.

    Args:
        provider_id: ID del proveedor.
        status: 1 para activar, 0 para desactivar.
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación de administrador."}
    try:
        data = await api_patch(
            f"/v1/providers/{provider_id}/status", token=auth.token, params={"status": status}
        )
        logger.info(f"update_provider_status: provider_id={provider_id}, status={status}")
        return data.get("data", data)
    except Exception as e:
        return handle_api_error(e, "cambiar estado del proveedor")


# ─── USERS & ROLES MANAGEMENT ────────────────────────────────────

@tool
async def list_users(config: RunnableConfig) -> Union[List[Dict], Dict]:
    """Lista todos los usuarios activos del sistema con sus roles asignados."""
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación de administrador."}
    try:
        data = await api_get("/v1/users/all", token=auth.token)
        return data.get("data", [])
    except Exception as e:
        return handle_api_error(e, "listar usuarios")


@tool
async def update_user_status(user_id: int, status: int, config: RunnableConfig) -> Dict:
    """Activa o desactiva un usuario del sistema.

    Args:
        user_id: ID del usuario.
        status: 1 para activar, 0 para desactivar.
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación de administrador."}
    try:
        data = await api_patch(
            f"/v1/users/{user_id}/status", token=auth.token, params={"status": status}
        )
        logger.info(f"update_user_status: user_id={user_id}, status={status}")
        return data.get("data", data)
    except Exception as e:
        return handle_api_error(e, "cambiar estado del usuario")


@tool
async def assign_user_role(user_id: int, role_id: int, config: RunnableConfig) -> Dict:
    """Asigna un rol a un usuario.

    Args:
        user_id: ID del usuario.
        role_id: ID del rol a asignar.
    """
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación de administrador."}
    try:
        data = await api_post(f"/v1/users/{user_id}/roles/{role_id}", data={}, token=auth.token)
        logger.info(f"assign_user_role: user_id={user_id}, role_id={role_id}")
        return data.get("data", data)
    except Exception as e:
        return handle_api_error(e, "asignar rol al usuario")


@tool
async def list_roles(config: RunnableConfig) -> Union[List[Dict], Dict]:
    """Lista todos los roles disponibles en el sistema."""
    auth = extract_auth(config)
    if not auth.is_authenticated:
        return {"error": "Se requiere autenticación de administrador."}
    try:
        data = await api_get("/v1/roles/all", token=auth.token)
        return data.get("data", [])
    except Exception as e:
        return handle_api_error(e, "listar roles")
