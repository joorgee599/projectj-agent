from app.agents.profiles.base import AgentProfile
from app.prompts.templates import SELLER_PROMPT
from app.tools.products import (
    search_products,
    get_product_details,
    get_categories,
    get_brands,
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
from app.tools.reports import (
    get_dashboard,
    get_sales_summary,
)

seller_profile = AgentProfile(
    name="seller",
    system_prompt_template=SELLER_PROMPT,
    tools=[
        # Productos y catálogo (lectura)
        search_products,
        get_product_details,
        get_categories,
        get_brands,
        # Clientes
        search_clients,
        # Ventas
        get_recent_sales,
        get_sales_by_client,
        get_sale_details,
        create_sale,
        confirm_sale,
        cancel_sale,
        # Reportes
        get_dashboard,
        get_sales_summary,
    ],
)
