from app.agents.profiles.base import AgentProfile
from app.prompts.templates import ANONYMOUS_PROMPT
from app.tools.products import search_products, get_product_details

anonymous_profile = AgentProfile(
    name="anonymous",
    system_prompt_template=ANONYMOUS_PROMPT,
    tools=[search_products, get_product_details],
)
