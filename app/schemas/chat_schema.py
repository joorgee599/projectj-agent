from typing import Optional, List
from pydantic import BaseModel, Field
from langgraph.graph import MessagesState


class UserContext(BaseModel):
    """Contexto del usuario autenticado enviado por el frontend."""
    email: str
    roles: List[str] = []
    permissions: List[str] = []


class MessageRequest(BaseModel):
    """Solicitud de chat del frontend."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Mensaje del usuario",
    )
    thread_id: Optional[str] = Field(
        None,
        pattern=r'^[a-f0-9\-]{36}$',
        description="ID de sesión (UUID v4). Si no se proporciona, se crea uno nuevo",
    )
    auth_token: Optional[str] = Field(
        None,
        min_length=10,
        description="JWT del usuario autenticado",
    )
    user_context: Optional[UserContext] = Field(
        None,
        description="Contexto del usuario (email, roles, permisos)",
    )
    current_page: Optional[str] = Field(
        None,
        description="Página actual del usuario en el frontend",
    )


class ChatResponse(BaseModel):
    """Respuesta del agente al frontend."""
    response: str = Field(..., description="Respuesta del agente")
    thread_id: str = Field(..., description="ID de sesión para mantener el contexto")
    profile: str = Field(..., description="Perfil del agente utilizado (anonymous, client)")


class AgentState(MessagesState):
    """Estado del grafo LangGraph."""
    profile: str = ""
