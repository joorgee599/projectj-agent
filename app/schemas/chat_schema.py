from typing import List, TypedDict, Optional
from langgraph.graph import MessagesState 
from pydantic import BaseModel, Field

class AgentState(MessagesState):
    my_agent: str

class MessageRequest(BaseModel):
    """Schema para solicitudes de chat"""
    message: str = Field(
        ..., 
        min_length=1, 
        max_length=2000,
        description="Mensaje del usuario"
    )
    thread_id: Optional[str] = Field(
        None, 
        pattern=r'^[a-f0-9\-]{36}$',
        description="ID de sesión (UUID v4). Si no se proporciona, se crea uno nuevo"
    )

class ChatResponse(BaseModel):
    """Schema para respuestas de chat"""
    response: str = Field(..., description="Respuesta del agente")
    thread_id: str = Field(..., description="ID de sesión para mantener el contexto")
