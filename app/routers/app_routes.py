from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from app.agents.services.chat_service import ChatService

app_routes = APIRouter()
chat_service = ChatService()

# Definir un modelo de Pydantic para la solicitud
class MessageRequest(BaseModel):
    message: str

@app_routes.get("/hello")
async def say_hello():
    return {"message": "Hello from app_routes"}

@app_routes.post("/chat")
async def chat(message_request: MessageRequest):
    """
    Recibe un mensaje del usuario y devuelve una respuesta procesada por el agente.

    Args:
        message (str): El mensaje enviado por el usuario.

    Returns:
        dict: La respuesta generada por el agente.
    """
    try:
       
        response = await chat_service.chat(message_request.message)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
