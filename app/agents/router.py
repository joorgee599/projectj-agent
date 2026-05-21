import logging
from typing import Optional

from app.schemas.chat_schema import UserContext
from app.agents.profiles.base import AgentProfile
from app.agents.profiles.anonymous import anonymous_profile
from app.agents.profiles.client import client_profile
from app.agents.profiles.seller import seller_profile
from app.agents.profiles.inventory import inventory_profile
from app.agents.profiles.admin import admin_profile

logger = logging.getLogger(__name__)


def resolve_profile(
    auth_token: Optional[str] = None,
    user_context: Optional[UserContext] = None,
) -> AgentProfile:
    """Selects the agent profile based on authentication state and roles.

    Priority order: ADMIN > SELLER > INVENTORY > CLIENT > ANONYMOUS
    """

    if not auth_token or not user_context:
        logger.info("Router -> anonymous profile (no auth)")
        return anonymous_profile

    roles = [r.upper() for r in user_context.roles]

    if "ADMIN" in roles or "ROLE_ADMIN" in roles:
        logger.info(f"Router -> admin profile for {user_context.email}")
        return admin_profile

    if "SELLER" in roles or "ROLE_SELLER" in roles:
        logger.info(f"Router -> seller profile for {user_context.email}")
        return seller_profile

    if "INVENTORY" in roles or "ROLE_INVENTORY" in roles:
        logger.info(f"Router -> inventory profile for {user_context.email}")
        return inventory_profile

    if "CLIENT" in roles or "ROLE_CLIENT" in roles:
        logger.info(f"Router -> client profile for {user_context.email}")
        return client_profile

    # Default: authenticated but no matching role
    logger.info(f"Router -> anonymous profile (roles={roles} not matched)")
    return anonymous_profile
