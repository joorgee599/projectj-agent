import logging
from typing import Optional

from app.schemas.chat_schema import UserContext
from app.agents.profiles.base import AgentProfile
from app.agents.profiles.anonymous import anonymous_profile
from app.agents.profiles.client import client_profile

logger = logging.getLogger(__name__)


def resolve_profile(
    auth_token: Optional[str] = None,
    user_context: Optional[UserContext] = None,
) -> AgentProfile:
    """Selects the agent profile based on authentication state and roles."""

    if not auth_token or not user_context:
        logger.info("Router -> anonymous profile (no auth)")
        return anonymous_profile

    roles = [r.upper() for r in user_context.roles]

    if "CLIENT" in roles or "ROLE_CLIENT" in roles:
        logger.info(f"Router -> client profile for {user_context.email}")
        return client_profile

    # Default: authenticated but no matching client role
    logger.info(f"Router -> anonymous profile (roles={roles} not matched for client)")
    return anonymous_profile
