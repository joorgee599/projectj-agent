from app.agents.profiles.base import AgentProfile
from app.prompts.templates import CLIENT_PROMPT
from app.tools.products import search_products, get_product_details, get_categories, get_brands
from app.tools.cart import (
    get_cart,
    add_to_cart,
    update_cart_item,
    remove_cart_item,
    checkout_cart,
    get_my_orders,
)

client_profile = AgentProfile(
    name="client",
    system_prompt_template=CLIENT_PROMPT,
    tools=[
        search_products,
        get_product_details,
        get_categories,
        get_brands,
        get_cart,
        add_to_cart,
        update_cart_item,
        remove_cart_item,
        checkout_cart,
        get_my_orders,
    ],
)
