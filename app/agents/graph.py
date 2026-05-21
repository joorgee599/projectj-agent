import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import tools_condition, ToolNode

from app.config.config import settings
from app.schemas.chat_schema import AgentState
from app.agents.profiles.base import AgentProfile
from app.agents.profiles.anonymous import anonymous_profile
from app.agents.profiles.client import client_profile
from app.agents.profiles.seller import seller_profile
from app.agents.profiles.inventory import inventory_profile
from app.agents.profiles.admin import admin_profile

logger = logging.getLogger(__name__)

# Shared checkpointer — thread_id isolates conversations, works across profile switches
_memory = MemorySaver()


def _create_llm():
    return ChatOpenAI(
        model=settings.OPENAI_MODEL if hasattr(settings, "OPENAI_MODEL") else "gpt-4o-mini",
        temperature=0,
        api_key=settings.OPENAI_API_KEY,
    )


def build_graph(profile: AgentProfile):
    """Build and compile a LangGraph for the given profile.

    The system prompt is injected at runtime via config["configurable"]["system_prompt"]
    so the same compiled graph can serve different users.
    """
    tools = profile.tools
    llm = _create_llm().bind_tools(tools, parallel_tool_calls=False)

    def assistant(state: AgentState, config: RunnableConfig):
        system_prompt = config.get("configurable", {}).get("system_prompt", "")
        system_msg = SystemMessage(content=system_prompt)
        return {"messages": [llm.invoke([system_msg] + state["messages"])]}

    builder = StateGraph(AgentState)
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")

    return builder.compile(checkpointer=_memory)


# Pre-built graphs — one per profile, reused across all requests
_GRAPHS = {
    "anonymous": build_graph(anonymous_profile),
    "client": build_graph(client_profile),
    "seller": build_graph(seller_profile),
    "inventory": build_graph(inventory_profile),
    "admin": build_graph(admin_profile),
}

logger.info(f"Graphs pre-built for profiles: {list(_GRAPHS.keys())}")


def get_graph(profile_name: str):
    """Return the pre-compiled graph for the given profile."""
    graph = _GRAPHS.get(profile_name)
    if not graph:
        raise ValueError(f"Unknown profile: {profile_name}")
    return graph
