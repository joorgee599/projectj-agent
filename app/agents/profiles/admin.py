from app.agents.profiles.base import AgentProfile
from app.prompts.templates import ADMIN_PROMPT
from app.tools.products import (
    search_products,
    get_product_details,
    get_categories,
    get_brands,
    get_low_stock_products,
)
from app.tools.sales import (
    get_recent_sales,
    get_sales_by_client,
    get_sale_details,
    search_clients,
    create_sale,
    confirm_sale,
    cancel_sale,
)
from app.tools.inventory import (
    get_inventory_movements,
    create_inventory_movement,
    confirm_inventory_movement,
    cancel_inventory_movement,
    search_providers,
)
from app.tools.reports import (
    get_dashboard,
    get_sales_summary,
    get_revenue_over_time,
)
from app.tools.admin import (
    # Productos CRUD
    create_product,
    update_product,
    delete_product,
    update_product_status,
    # Categorías CRUD
    create_category,
    update_category,
    delete_category,
    # Marcas CRUD
    create_brand,
    update_brand,
    delete_brand,
    # Clientes
    create_client,
    update_client_status,
    # Proveedores
    create_provider,
    update_provider_status,
    # Usuarios y Roles
    list_users,
    update_user_status,
    assign_user_role,
    list_roles,
)

admin_profile = AgentProfile(
    name="admin",
    system_prompt_template=ADMIN_PROMPT,
    tools=[
        # ── Catálogo (lectura) ──
        search_products,
        get_product_details,
        get_categories,
        get_brands,
        get_low_stock_products,
        # ── Clientes (lectura) ──
        search_clients,
        # ── Proveedores (lectura) ──
        search_providers,
        # ── Ventas (todo del seller) ──
        get_recent_sales,
        get_sales_by_client,
        get_sale_details,
        create_sale,
        confirm_sale,
        cancel_sale,
        # ── Inventario (todo del inventory) ──
        get_inventory_movements,
        create_inventory_movement,
        confirm_inventory_movement,
        cancel_inventory_movement,
        # ── Dashboard & Reportes ──
        get_dashboard,
        get_sales_summary,
        get_revenue_over_time,
        # ── ADMIN: Productos CRUD ──
        create_product,
        update_product,
        delete_product,
        update_product_status,
        # ── ADMIN: Categorías CRUD ──
        create_category,
        update_category,
        delete_category,
        # ── ADMIN: Marcas CRUD ──
        create_brand,
        update_brand,
        delete_brand,
        # ── ADMIN: Clientes gestión ──
        create_client,
        update_client_status,
        # ── ADMIN: Proveedores gestión ──
        create_provider,
        update_provider_status,
        # ── ADMIN: Usuarios y Roles ──
        list_users,
        update_user_status,
        assign_user_role,
        list_roles,
    ],
)
