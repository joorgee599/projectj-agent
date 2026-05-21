from app.agents.profiles.base import AgentProfile
from app.prompts.templates import INVENTORY_PROMPT
from app.tools.products import (
    search_products,
    get_product_details,
    get_categories,
    get_brands,
    get_low_stock_products,
)
from app.tools.inventory import (
    get_inventory_movements,
    create_inventory_movement,
    confirm_inventory_movement,
    cancel_inventory_movement,
    search_providers,
)
from app.tools.reports import get_dashboard

inventory_profile = AgentProfile(
    name="inventory",
    system_prompt_template=INVENTORY_PROMPT,
    tools=[
        # Productos y catálogo (lectura)
        search_products,
        get_product_details,
        get_categories,
        get_brands,
        # Alertas de stock
        get_low_stock_products,
        # Proveedores
        search_providers,
        # Movimientos de inventario
        get_inventory_movements,
        create_inventory_movement,
        confirm_inventory_movement,
        cancel_inventory_movement,
        # Reportes
        get_dashboard,
    ],
)
