import uuid
import logging
from typing import AsyncGenerator

from langchain_core.messages import HumanMessage

from app.schemas.chat_schema import MessageRequest
from app.agents.router import resolve_profile
from app.agents.graph import get_graph
from app.services.java_api_client import resolve_client
from app.security.input_guard import check_input
from app.config.config import settings

logger = logging.getLogger(__name__)


class ChatService:

    async def _build_config(self, request: MessageRequest, thread_id: str) -> dict:
        """Build the RunnableConfig with auth context for the graph invocation."""
        profile = resolve_profile(request.auth_token, request.user_context)

        # Base prompt variables
        page_context = ""
        if request.current_page:
            page_context = f"\nEl usuario está navegando en la página: {request.current_page}"

        prompt_vars = {
            "agent_name": settings.AGENT_NAME,
            "page_context": page_context,
        }

        configurable = {"thread_id": thread_id}

        # Resolve client context for authenticated users
        if request.auth_token and request.user_context:
            prompt_vars["user_email"] = request.user_context.email
            configurable["auth_token"] = request.auth_token

            client_info = await resolve_client(
                request.auth_token, request.user_context.email
            )
            if client_info:
                configurable["client_id"] = client_info["client_id"]
                configurable["user_id"] = client_info["user_id"]

        # Render system prompt into config
        configurable["system_prompt"] = profile.build_prompt(**prompt_vars)

        return {
            "profile": profile,
            "config": {"configurable": configurable},
        }

    async def chat(self, request: MessageRequest) -> dict:
        """Process a message and return a complete response."""
        thread_id = request.thread_id or str(uuid.uuid4())

        if not check_input(request.message):
            return {
                "response": "No puedo procesar ese mensaje. ¿Puedo ayudarte con algo sobre nuestros productos?",
                "thread_id": thread_id,
                "profile": "blocked",
            }

        try:
            ctx = await self._build_config(request, thread_id)
            profile = ctx["profile"]
            config = ctx["config"]

            graph = get_graph(profile.name)
            result = await graph.ainvoke(
                {"messages": [HumanMessage(content=request.message)]},
                config,
            )

            last_message = result["messages"][-1].content
            logger.info(f"Chat completed: thread={thread_id}, profile={profile.name}")

            return {
                "response": last_message,
                "thread_id": thread_id,
                "profile": profile.name,
            }
        except Exception as e:
            logger.error(f"Chat error: thread={thread_id}, error={e}")
            raise

    async def chat_stream(
        self, request: MessageRequest
    ) -> AsyncGenerator[dict, None]:
        """Process a message and stream the response."""
        thread_id = request.thread_id or str(uuid.uuid4())

        if not check_input(request.message):
            yield {
                "type": "content",
                "data": "No puedo procesar ese mensaje. ¿Puedo ayudarte con algo sobre nuestros productos?",
                "thread_id": thread_id,
                "profile": "blocked",
            }
            yield {"type": "end", "thread_id": thread_id}
            return

        try:
            ctx = await self._build_config(request, thread_id)
            profile = ctx["profile"]
            config = ctx["config"]

            graph = get_graph(profile.name)

            async for event in graph.astream_events(
                {"messages": [HumanMessage(content=request.message)]},
                config=config,
                version="v2",
            ):
                kind = event["event"]

                if kind == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        yield {
                            "type": "content",
                            "data": content,
                            "thread_id": thread_id,
                            "profile": profile.name,
                        }

                elif kind == "on_tool_start":
                    yield {
                        "type": "tool_start",
                        "data": event["name"],
                        "thread_id": thread_id,
                    }

            logger.info(f"Stream completed: thread={thread_id}, profile={profile.name}")
            yield {"type": "end", "thread_id": thread_id, "profile": profile.name}

        except Exception as e:
            logger.error(f"Stream error: thread={thread_id}, error={e}")
            yield {"type": "error", "data": str(e), "thread_id": thread_id}
